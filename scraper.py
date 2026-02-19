import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import re

class PriceScraper:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename='logs/scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def scrape_all_sites(self, product_name, websites):
        """Scrape all websites for product"""
        self.logger.info(f"Searching for: {product_name}")
        
        # Mock data for testing (with REAL images)
        results = self.generate_mock_data(product_name)
        
        return results
    
    def get_product_image(self, product_name):
        """Get relevant product image from free image APIs"""
        
        # Product categories with direct image URLs (100% working)
        images = {
            # Electronics
            'iphone': 'https://fdn2.gsmarena.com/vv/pics/apple/apple-iphone-15-1.jpg',
            'samsung': 'https://fdn2.gsmarena.com/vv/pics/samsung/samsung-galaxy-s24-1.jpg',
            'laptop': 'https://m.media-amazon.com/images/I/81KoSSAwH2L._AC_SL1500_.jpg',
            'dell': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-13-9315/media-gallery/notebook-xps-13-9315-typec-cpu-hero.jpg',
            'hp': 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c08581835.png',
            'lenovo': 'https://p3-ofp.static.pub/fes/cms/2023/09/22/9p45rqtpr995t52k6z36r4fc7x467u775724.png',
            'headphones': 'https://m.media-amazon.com/images/I/61CGHv6kmWL._AC_SL1500_.jpg',
            'earphones': 'https://m.media-amazon.com/images/I/61f1YfTkTDL._AC_SL1500_.jpg',
            'airpods': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1660803972361',
            'smartwatch': 'https://m.media-amazon.com/images/I/71f5n9LISvL._AC_SL1500_.jpg',
            'watch': 'https://m.media-amazon.com/images/I/71f5n9LISvL._AC_SL1500_.jpg',
            'camera': 'https://m.media-amazon.com/images/I/61n-At5oBaL._AC_SL1500_.jpg',
            'dslr': 'https://m.media-amazon.com/images/I/61n-At5oBaL._AC_SL1500_.jpg',
            'tablet': 'https://m.media-amazon.com/images/I/61b2rPz1CwL._AC_SL1500_.jpg',
            'ipad': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-12-11-select-202210?wid=940&hei=1112&fmt=png-alpha&.v=1664912408566',
            
            # Fashion
            'shoes': 'https://m.media-amazon.com/images/I/71S7O37CQgL._AC_SY695_.jpg',
            'sneakers': 'https://m.media-amazon.com/images/I/71S7O37CQgL._AC_SY695_.jpg',
            'bag': 'https://m.media-amazon.com/images/I/81p1Z96ZxML._AC_SL1500_.jpg',
            'backpack': 'https://m.media-amazon.com/images/I/81p1Z96ZxML._AC_SL1500_.jpg',
            'clothes': 'https://m.media-amazon.com/images/I/61L5QgPvgqL._AC_SY879_.jpg',
            'shirt': 'https://m.media-amazon.com/images/I/61L5QgPvgqL._AC_SY879_.jpg',
            't-shirt': 'https://m.media-amazon.com/images/I/61L5QgPvgqL._AC_SY879_.jpg',
            
            # Home
            'furniture': 'https://m.media-amazon.com/images/I/81UtlXpVh1L._AC_SL1500_.jpg',
            'chair': 'https://m.media-amazon.com/images/I/71HkPgtsNKL._AC_SL1500_.jpg',
            'table': 'https://m.media-amazon.com/images/I/81UtlXpVh1L._AC_SL1500_.jpg',
            'sofa': 'https://m.media-amazon.com/images/I/81UtlXpVh1L._AC_SL1500_.jpg',
            'bed': 'https://m.media-amazon.com/images/I/71HkPgtsNKL._AC_SL1500_.jpg',
            'kitchen': 'https://m.media-amazon.com/images/I/71HkPgtsNKL._AC_SL1500_.jpg',
            
            # Books
            'book': 'https://m.media-amazon.com/images/I/41SH-SvWPxL.jpg',
            'novel': 'https://m.media-amazon.com/images/I/41SH-SvWPxL.jpg',
            
            # Sports
            'ball': 'https://m.media-amazon.com/images/I/61Uo4Kj9RdL._AC_SY450_.jpg',
            'football': 'https://m.media-amazon.com/images/I/61Uo4Kj9RdL._AC_SY450_.jpg',
            'cricket': 'https://m.media-amazon.com/images/I/61Uo4Kj9RdL._AC_SY450_.jpg',
        }
        
        # Default image (if product not found in above list)
        default_image = 'https://m.media-amazon.com/images/I/71S7O37CQgL._AC_SY695_.jpg'
        
        # Check if product name matches any key
        product_lower = product_name.lower()
        for key, img_url in images.items():
            if key in product_lower:
                return img_url
        
        # Return default if no match
        return default_image
    
    def generate_mock_data(self, product):
        """Generate mock data with REAL images"""
        products = []
        websites = ['Amazon', 'Daraz', 'PriceOye', 'AliExpress', 'eBay']
        
        # Get real image for this product
        product_image = self.get_product_image(product)
        
        # Different models/versions
        models = ['Pro', 'Max', 'Lite', 'Plus', 'Ultra', 'Premium', 'Elite']
        years = ['2023', '2024']
        conditions = ['New', 'Latest', 'Original', 'Genuine']
        
        for i in range(8):
            website = random.choice(websites)
            price = random.randint(10000, 200000)
            
            # Generate random rating
            rating = round(random.uniform(3.0, 5.0), 1)
            
            # Generate random reviews
            reviews = random.randint(10, 1000)
            
            # Create product title
            title = f"{product.title()} {random.choice(models)} {random.choice(years)} - {random.choice(conditions)}"
            
            # Slightly vary image for different products (add query params)
            image_variation = f"{product_image}?v={random.randint(1,100)}"
            
            product_data = {
                'title': title,
                'price': price,
                'original_price': price + random.randint(5000, 50000),
                'rating': rating,
                'reviews_count': reviews,
                'website': website,
                'link': f"https://www.{website.lower()}.com/products/{product.replace(' ', '-')}-{i}",
                'image': product_image,  # Same image for same product (clean)
                'image_fallback': 'https://m.media-amazon.com/images/I/71S7O37CQgL._AC_SY695_.jpg',
                'availability': random.choice(['In Stock', 'Limited Stock', 'Out of Stock']),
                'shipping': random.choice(['Free Shipping', 'Paid Shipping']),
                'seller_rating': round(random.uniform(4.0, 5.0), 1),
                'warranty': f"{random.choice([6,12,24])} months"
            }
            products.append(product_data)
        
        # Sort by price
        products.sort(key=lambda x: x['price'])
        
        # Add best price tag
        if products:
            products[0]['best_price'] = True
        
        self.logger.info(f"Generated {len(products)} mock products with images")
        return products
    
    def scrape_amazon(self, product_name):
        """Mock Amazon scrape"""
        time.sleep(random.uniform(1, 3))
        return self.generate_mock_data(product_name)[:3]
    
    def scrape_daraz(self, product_name):
        """Mock Daraz scrape"""
        time.sleep(random.uniform(1, 3))
        return self.generate_mock_data(product_name)[:3]
    
    def scrape_priceoye(self, product_name):
        """Mock PriceOye scrape"""
        time.sleep(random.uniform(1, 3))
        return self.generate_mock_data(product_name)[:3]

# Test the scraper
if __name__ == "__main__":
    scraper = PriceScraper()
    
    # Test with different products
    test_products = ['iPhone', 'Samsung', 'laptop', 'shoes', 'watch']
    
    for product in test_products:
        print(f"\n=== Testing: {product} ===")
        results = scraper.scrape_all_sites(product, ['amazon', 'daraz'])
        for r in results[:3]:
            print(f"{r['website']}: {r['title']}")
            print(f"Image: {r['image']}")
            print(f"Price: Rs. {r['price']}\n")
