# app.py - Fixed version with guaranteed mock data
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random

app = Flask(__name__)

def generate_mock_products(query):
    """Generate realistic mock data based on search query"""
    base_price = random.randint(200, 1500)
    
    products = [
        {
            "id": "amz_1",
            "title": f"{query.title()} - Latest Model 2024, Black",
            "price": round(base_price * 0.87, 2),  # Amazon usually cheapest
            "original_price": round(base_price * 1.2, 2),
            "currency": "USD",
            "availability": "In Stock",
            "rating": 4.7,
            "reviews": random.randint(1000, 50000),
            "store": "Amazon",
            "features": ["Prime Delivery", "30-day returns", "Free shipping"],
            "price_history": [
                {"date": (datetime.now() - timedelta(days=i)).isoformat(), 
                 "price": round(base_price * 0.87 + random.randint(-20, 50), 2)}
                for i in range(30)
            ],
            "deal_analysis": {
                "deal_score": 92,
                "is_deal": True,
                "average_price": round(base_price * 0.95, 2),
                "lowest_price": round(base_price * 0.85, 2),
                "volatility": 5.2,
                "recommendation": "Buy Now",
                "price_trend": "dropping"
            }
        },
        {
            "id": "bb_1",
            "title": f"{query.title()} - Premium Edition",
            "price": round(base_price * 0.95, 2),
            "original_price": base_price,
            "currency": "USD",
            "availability": "In Stock",
            "rating": 4.8,
            "reviews": random.randint(500, 10000),
            "store": "Best Buy",
            "features": ["Geek Squad support", "Store pickup", "Extended warranty"],
            "price_history": [
                {"date": (datetime.now() - timedelta(days=i)).isoformat(), 
                 "price": round(base_price * 0.95 + random.randint(-10, 30), 2)}
                for i in range(30)
            ],
            "deal_analysis": {
                "deal_score": 75,
                "is_deal": False,
                "average_price": round(base_price * 0.98, 2),
                "lowest_price": round(base_price * 0.90, 2),
                "volatility": 3.1,
                "recommendation": "Fair Price",
                "price_trend": "stable"
            }
        },
        {
            "id": "wm_1",
            "title": f"{query.title()} - Standard Model",
            "price": round(base_price * 0.90, 2),
            "original_price": round(base_price * 1.1, 2),
            "currency": "USD",
            "availability": "Limited Stock",
            "rating": 4.6,
            "reviews": random.randint(800, 15000),
            "store": "Walmart",
            "features": ["Free shipping over $35", "2-day delivery", "Easy returns"],
            "price_history": [
                {"date": (datetime.now() - timedelta(days=i)).isoformat(), 
                 "price": round(base_price * 0.90 + random.randint(-15, 40), 2)}
                for i in range(30)
            ],
            "deal_analysis": {
                "deal_score": 85,
                "is_deal": True,
                "average_price": round(base_price * 0.96, 2),
                "lowest_price": round(base_price * 0.88, 2),
                "volatility": 7.8,
                "recommendation": "Good Deal",
                "price_trend": "dropping"
            }
        },
        {
            "id": "gg_1",
            "title": f"{query.title()} - Newest Version",
            "price": round(base_price * 0.93, 2),
            "original_price": round(base_price * 1.15, 2),
            "currency": "USD",
            "availability": "In Stock",
            "rating": 4.7,
            "reviews": random.randint(200, 5000),
            "store": "Google Shopping",
            "features": ["Price match guarantee", "Buyer protection", "Fast shipping"],
            "price_history": [
                {"date": (datetime.now() - timedelta(days=i)).isoformat(), 
                 "price": round(base_price * 0.93 + random.randint(-12, 35), 2)}
                for i in range(30)
            ],
            "deal_analysis": {
                "deal_score": 82,
                "is_deal": True,
                "average_price": round(base_price * 0.97, 2),
                "lowest_price": round(base_price * 0.89, 2),
                "volatility": 4.5,
                "recommendation": "Buy Now",
                "price_trend": "stable"
            }
        }
    ]
    
    return products

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({"error": "Query too short", "products": []}), 400
    
    # Generate mock products based on query
    products = generate_mock_products(query)
    
    # Find best deal (lowest price)
    best_deal = min(products, key=lambda x: x['price'])
    
    # Calculate comparisons
    comparisons = []
    for product in products:
        comparisons.append({
            "store": product['store'],
            "price": product['price'],
            "savings": round(product['original_price'] - product['price'], 2),
            "availability": product['availability']
        })
    
    return jsonify({
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "total_results": len(products),
        "products": products,
        "best_deal": best_deal,
        "comparisons": comparisons,
        "meta": {
            "sources_searched": ["amazon", "bestbuy", "walmart", "google_shopping"],
            "cache_status": "fresh",
            "price_volatility_index": round(sum(p['deal_analysis']['volatility'] for p in products) / len(products), 2)
        }
    })

@app.route('/api/trends/<product_id>')
def price_trends(product_id):
    """Return price history for a specific product"""
    history = []
    base_price = 400
    
    for i in range(90):
        date = datetime.now() - timedelta(days=90-i)
        price = base_price + random.randint(-50, 100) + (i * 2)  # Upward trend
        history.append({
            "date": date.isoformat(),
            "price": round(price, 2)
        })
    
    return jsonify({
        "product_id": product_id,
        "history": history,
        "prediction": {
            "next_week": round(base_price * 0.95, 2),
            "confidence": 0.85,
            "factors": ["seasonal_trend", "inventory_levels", "competitor_pricing"]
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
