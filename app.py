from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from scraper import PriceScraper
import json
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)
scraper = PriceScraper()

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search for products"""
    try:
        data = request.json
        product_name = data.get('product', '')
        websites = data.get('websites', ['amazon', 'daraz', 'priceoye'])
        
        if not product_name:
            return jsonify({'error': 'Product name required'}), 400
        
        # Scrape products
        results = scraper.scrape_all_sites(product_name, websites)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/search_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'filename': filename
        })
    
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    """Get search history"""
    try:
        files = os.listdir('data')
        searches = []
        for f in sorted(files, reverse=True)[:10]:  # Last 10 searches
            if f.endswith('.json'):
                with open(f'data/{f}', 'r') as file:
                    data = json.load(file)
                    searches.append({
                        'filename': f,
                        'timestamp': f.replace('search_', '').replace('.json', ''),
                        'count': len(data)
                    })
        return jsonify(searches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download search results"""
    try:
        return send_file(f'data/{filename}', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/compare', methods=['POST'])
def compare_products():
    """Compare selected products"""
    try:
        data = request.json
        products = data.get('products', [])
        
        # Find best price
        best_price = min(products, key=lambda x: x.get('price', float('inf')))
        best_deal = {
            'product': best_price,
            'savings': calculate_savings(products, best_price)
        }
        
        return jsonify({
            'success': True,
            'best_deal': best_deal,
            'products': products
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_savings(products, best):
    """Calculate savings compared to average"""
    prices = [p.get('price', 0) for p in products if p.get('price')]
    if not prices:
        return 0
    
    avg_price = sum(prices) / len(prices)
    if best.get('price'):
        return round(avg_price - best['price'], 2)
    return 0

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)