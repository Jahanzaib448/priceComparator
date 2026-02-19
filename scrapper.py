import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class PriceScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.setup_logging()
        self.session = requests.Session()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename='logs/scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_random_headers(self):
        """Get random headers to avoid blocking"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def scrape_all_sites(self, product_name, websites):
        """Scrape all websites for product"""
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            if 'amazon' in websites:
                futures.append(executor.submit(self.scrape_amazon, product_name))
            if 'daraz' in websites:
                futures.append(executor.submit(self.scrape_daraz, product_name))
            if 'priceoye' in websites:
                futures.append(executor.submit(self.scrape_priceoye, product_name))
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.extend(result)
                except Exception as e:
                    self.logger.error(f"Scraping error: {str(e)}")
        
        # Sort by price
        results.sort(key=lambda x: x.get('price', float('inf')))
        return results
    
    def scrape_amazon(self, product_name):
        """Scrape Amazon products"""
        try:
            self.logger.info(f"Scraping Amazon for: {product_name}")
            
            # Use Selenium for Amazon (more reliable)
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.ua.random}')
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            search_url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
            driver.get(search_url)
            
            time.sleep(random.uniform(2, 4))
            
            products = []
            items = driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')[:5]
            
            for item in items:
                try:
                    title = item.find_element(By.CSS_SELECTOR, 'h2 a span').text
                    price_elem = item.find_elements(By.CSS_SELECTOR, '.a-price .a-offscreen')
                    
                    price = None
                    if price_elem:
                        price_text = price_elem[0].text
                        price = float(re.sub(r'[^\d.]', '', price_text))
                    
                    rating = item.find_elements(By.CSS_SELECTOR, '.a-icon-alt')
                    rating = rating[0].text.split()[0] if rating else 'N/A'
                    
                    link = item.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                    
                    products.append({
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'price': price,
                        'rating': rating,
                        'website': 'Amazon',
                        'link': link,
                        'image': 'https://via.placeholder.com/150?text=Amazon'
                    })
                except Exception as e:
                    continue
            
            driver.quit()
            self.logger.info(f"Found {len(products)} products on Amazon")
            return products
            
        except Exception as e:
            self.logger.error(f"Amazon scraping error: {str(e)}")
            return []
    
    def scrape_daraz(self, product_name):
        """Scrape Daraz products"""
        try:
            self.logger.info(f"Scraping Daraz for: {product_name}")
            
            headers = self.get_random_headers()
            url = f"https://www.daraz.pk/catalog/?q={product_name.replace(' ', '+')}"
            
            response = self.session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            products = []
            items = soup.select('.c1_t2i')[:5] or soup.select('.product-item')[:5]
            
            for item in items:
                try:
                    title_elem = item.select_one('.title') or item.select_one('.name')
                    title = title_elem.text.strip() if title_elem else 'N/A'
                    
                    price_elem = item.select_one('.price') or item.select_one('.current-price')
                    price_text = price_elem.text.strip() if price_elem else '0'
                    price = float(re.sub(r'[^\d.]', '', price_text)) if price_text else None
                    
                    link_elem = item.select_one('a')
                    link = 'https:' + link_elem['href'] if link_elem and link_elem.get('href') else '#'
                    
                    products.append({
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'price': price,
                        'rating': 'N/A',
                        'website': 'Daraz',
                        'link': link,
                        'image': 'https://via.placeholder.com/150?text=Daraz'
                    })
                except Exception as e:
                    continue
            
            self.logger.info(f"Found {len(products)} products on Daraz")
            return products
            
        except Exception as e:
            self.logger.error(f"Daraz scraping error: {str(e)}")
            return []
    
    def scrape_priceoye(self, product_name):
        """Scrape PriceOye products"""
        try:
            self.logger.info(f"Scraping PriceOye for: {product_name}")
            
            headers = self.get_random_headers()
            url = f"https://priceoye.pk/search?q={product_name.replace(' ', '%20')}"
            
            response = self.session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            products = []
            items = soup.select('.productBox')[:5] or soup.select('.product-card')[:5]
            
            for item in items:
                try:
                    title_elem = item.select_one('.product-title') or item.select_one('.name')
                    title = title_elem.text.strip() if title_elem else 'N/A'
                    
                    price_elem = item.select_one('.price') or item.select_one('.product-price')
                    price_text = price_elem.text.strip() if price_elem else '0'
                    price = float(re.sub(r'[^\d.]', '', price_text)) if price_text else None
                    
                    link_elem = item.select_one('a')
                    link = 'https://priceoye.pk' + link_elem['href'] if link_elem and link_elem.get('href') else '#'
                    
                    products.append({
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'price': price,
                        'rating': 'N/A',
                        'website': 'PriceOye',
                        'link': link,
                        'image': 'https://via.placeholder.com/150?text=PriceOye'
                    })
                except Exception as e:
                    continue
            
            self.logger.info(f"Found {len(products)} products on PriceOye")
            return products
            
        except Exception as e:
            self.logger.error(f"PriceOye scraping error: {str(e)}")
            return []
