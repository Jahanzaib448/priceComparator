import os
import json
import requests
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

app = Flask(__name__)
CORS(app)

# Thread pool for concurrent scraping
executor = ThreadPoolExecutor(max_workers=5)

# Pure Python Lightweight Price Predictor (No ONNX/DLL dependencies)
class LightweightPricePredictor:
    def __init__(self):
        self.model = None
        self.is_fitted = False
        self.init_model()
    
    def init_model(self):
        """Initialize lightweight polynomial regression model"""
        self.model = make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            Ridge(alpha=1.0, random_state=42)
        )
        self.is_fitted = False
    
    def fit(self, X, y):
        """Fit the model with available data"""
        if len(X) >= 3:
            try:
                self.model.fit(X, y)
                self.is_fitted = True
            except Exception as e:
                print(f"Model fit error: {e}")
                self.is_fitted = False
    
    def predict_missing_price(self, known_prices):
        """Predict missing prices using polynomial regression or statistical fallback"""
        if len(known_prices) == 0:
            return 0.0
        
        if len(known_prices) >= 3:
            try:
                X = np.array(range(len(known_prices))).reshape(-1, 1)
                y = np.array(known_prices)
                self.fit(X, y)
                
                if self.is_fitted:
                    next_idx = np.array([[len(known_prices)]])
                    prediction = self.model.predict(next_idx)[0]
                    variance = np.std(known_prices) * 0.1
                    prediction += np.random.normal(0, variance)
                    return max(0.0, float(prediction))
            except Exception as e:
                print(f"Prediction error: {e}")
        
        return self._statistical_fallback(known_prices)
    
    def _statistical_fallback(self, prices):
        """Statistical prediction using median and variance"""
        if not prices:
            return 0.0
        
        median_price = np.median(prices)
        std_price = np.std(prices) if len(prices) > 1 else median_price * 0.1
        variation = np.random.normal(0, std_price * 0.15)
        prediction = median_price + variation
        lower_bound = median_price * 0.8
        upper_bound = median_price * 1.2
        prediction = np.clip(prediction, lower_bound, upper_bound)
        return float(prediction)

price_predictor = LightweightPricePredictor()

class PriceScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)
        
    def fetch_price(self, url, selectors, marketplace):
        """Fetch price from specific marketplace (SYNCHRONOUS)"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try multiple selectors
            price_elem = None
            for selector in selectors:
                try:
                    price_elem = soup.select_one(selector)
                    if price_elem:
                        break
                except:
                    continue
            
            if price_elem:
                price_text = price_elem.get_text().strip()
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    return {
                        'price': float(price_match.group()),
                        'currency': self._detect_currency(price_text),
                        'marketplace': marketplace,
                        'url': url,
                        'last_updated': datetime.now().isoformat(),
                        'confidence': 'high',
                        'method': 'scraped'
                    }
            return None
            
        except Exception as e:
            print(f"Error fetching {marketplace}: {str(e)}")
            return None
    
    def _detect_currency(self, price_text):
        """Detect currency from price text"""
        if '₹' in price_text or 'INR' in price_text:
            return 'INR'
        elif '€' in price_text or 'EUR' in price_text:
            return 'EUR'
        elif '£' in price_text or 'GBP' in price_text:
            return 'GBP'
        elif '$' in price_text or 'USD' in price_text:
            return 'USD'
        return 'USD'
    
    def search_all_marketplaces(self, query):
        """Search multiple marketplaces concurrently using threads"""
        query = query.strip().lower()
        
        marketplaces = {
            'amazon': {
                'url': f"https://www.amazon.com/s?k={quote_plus(query)}",
                'selectors': ['.a-price-whole', '.a-price .a-offscreen', '.a-price-range']
            },
            'ebay': {
                'url': f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(query)}",
                'selectors': ['.notranslate', '.s-item__price', '.u-flL.condText']
            },
            'walmart': {
                'url': f"https://www.walmart.com/search?q={quote_plus(query)}",
                'selectors': ['[data-automation-id="product-price"]', '.price-main', '.price-current']
            },
            'target': {
                'url': f"https://www.target.com/s?searchTerm={quote_plus(query)}",
                'selectors': ['[data-test="product-price"]', '.h-padding-r-x2', '.PriceTag']
            }
        }
        
        results = []
        prices = []
        
        # Use ThreadPoolExecutor for concurrent scraping
        future_to_marketplace = {
            executor.submit(
                self.fetch_price, 
                config['url'], 
                config['selectors'], 
                name
            ): name 
            for name, config in marketplaces.items()
        }
        
        for future in as_completed(future_to_marketplace):
            marketplace = future_to_marketplace[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    prices.append(result['price'])
            except Exception as e:
                print(f"Error in {marketplace}: {e}")
        
        # AI Gap Filling
        if len(prices) > 0:
            successful_marketplaces = {r['marketplace'] for r in results}
            missing_marketplaces = set(marketplaces.keys()) - successful_marketplaces
            
            for mp_name in missing_marketplaces:
                predicted_price = price_predictor.predict_missing_price(prices)
                results.append({
                    'price': round(predicted_price, 2),
                    'currency': 'USD',
                    'marketplace': mp_name,
                    'url': marketplaces[mp_name]['url'],
                    'last_updated': datetime.now().isoformat(),
                    'confidence': 'ai_predicted',
                    'method': 'ai_gap_fill',
                    'note': f'AI predicted based on {len(prices)} marketplace(s)',
                    'prediction_confidence': 'medium' if len(prices) >= 3 else 'low'
                })
        
        return results

scraper = PriceScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    """SYNCHRONOUS route to avoid Flask async issues"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Check cache
    cache_key = query.lower().strip()
    if cache_key in scraper.cache:
        cached_data, timestamp = scraper.cache[cache_key]
        if datetime.now() - timestamp < scraper.cache_duration:
            return jsonify({
                'query': query,
                'results': cached_data,
                'cached': True,
                'timestamp': datetime.now().isoformat(),
                'ai_enhanced': any(r.get('method') == 'ai_gap_fill' for r in cached_data)
            })
    
    try:
        # Fetch data (synchronous)
        results = scraper.search_all_marketplaces(query)
        
        if not results:
            return jsonify({
                'query': query,
                'results': [],
                'message': 'No results found. Try a more specific search term.',
                'timestamp': datetime.now().isoformat()
            })
        
        # Sort by price
        results.sort(key=lambda x: x['price'])
        
        # Calculate savings
        if len(results) > 1:
            best_price = results[0]['price']
            for result in results[1:]:
                if result['confidence'] != 'ai_predicted':
                    result['savings'] = round(result['price'] - best_price, 2)
                    result['savings_percent'] = round(((result['price'] - best_price) / result['price']) * 100, 1)
        
        # Cache results
        scraper.cache[cache_key] = (results, datetime.now())
        
        return jsonify({
            'query': query,
            'results': results,
            'cached': False,
            'timestamp': datetime.now().isoformat(),
            'total_marketplaces': len(results),
            'ai_enhanced': any(r.get('method') == 'ai_gap_fill' for r in results),
            'scraped_count': sum(1 for r in results if r.get('method') == 'scraped'),
            'predicted_count': sum(1 for r in results if r.get('method') == 'ai_gap_fill')
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'error': 'Search failed',
            'message': str(e),
            'query': query
        }), 500

@app.route('/api/trends')
def trends():
    """Get trending searches"""
    trending = [
        {'query': 'iPhone 15 Pro', 'searches': 12500, 'category': 'Electronics'},
        {'query': 'Sony WH-1000XM5', 'searches': 8300, 'category': 'Audio'},
        {'query': 'MacBook Air M2', 'searches': 6700, 'category': 'Computers'},
        {'query': 'Nintendo Switch OLED', 'searches': 5400, 'category': 'Gaming'},
        {'query': 'AirPods Pro 2', 'searches': 4900, 'category': 'Audio'},
        {'query': 'Samsung Galaxy S24', 'searches': 4200, 'category': 'Electronics'}
    ]
    return jsonify(trending)

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'predictor': 'scikit-learn Ridge Regression',
        'mode': 'synchronous',
        'version': '2.1.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
