import time
import json
from datetime import datetime
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from flask_cors import CORS


app = Flask(__name__)
#Строка 16,поменять домен в случае если 17 строка не работает
#CORS(app, resources={r"/api/*": {"origins": "https://ваш-домен.ru"}})
CORS(app)

class SberMegaMarketParser:
    def __init__(self):
        self.driver = self._init_webdriver()
        self.base_url = "https://sbermegamarket.ru"
        
    def _init_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        stealth(driver,
                languages=["ru-RU", "ru"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        driver.maximize_window()
        return driver
    
    def _scrolldown(self, scroll_count=10):
        for _ in range(scroll_count):
            self.driver.execute_script('window.scrollBy(0, 500)')
            time.sleep(0.5)
    
    def _accept_cookies(self):
        try:
            cookie_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Принять")]')))
            cookie_btn.click()
            time.sleep(1)
        except:
            pass
    
    def _get_product_data(self, product_url):
        self.driver.get(product_url)
        time.sleep(2)
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Получаем основную информацию из JSON-LD
            script_data = soup.find('script', {'type': 'application/ld+json'})
            if not script_data:
                return None
                
            product_json = json.loads(script_data.string)
            
            # Дополнительные данные с страницы
            price_block = soup.find('div', {'class': 'item-price'})
            current_price = price_block.find('span', {'class': 'price__wrapper'}).get_text(strip=True) if price_block else ''
            
            # Характеристики товара
            specs = {}
            specs_block = soup.find('div', {'class': 'specs'})
            if specs_block:
                for row in specs_block.find_all('div', {'class': 'specs__row'}):
                    name = row.find('div', {'class': 'specs__name'}).get_text(strip=True)
                    value = row.find('div', {'class': 'specs__value'}).get_text(strip=True)
                    specs[name] = value
            
            return {
                'product_id': product_json.get('sku', ''),
                'name': product_json.get('name', ''),
                'description': product_json.get('description', ''),
                'price': current_price,
                'original_price': product_json.get('offers', {}).get('price', ''),
                'currency': product_json.get('offers', {}).get('priceCurrency', ''),
                'rating': product_json.get('aggregateRating', {}).get('ratingValue', ''),
                'review_count': product_json.get('aggregateRating', {}).get('reviewCount', ''),
                'image_url': product_json.get('image', ''),
                'url': product_url,
                'specifications': specs,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Ошибка при парсинге товара {product_url}: {str(e)}")
            return None
    
    def parse_main_page(self, max_products=20):
        """Парсим товары с главной страницы"""
        self.driver.get(self.base_url)
        time.sleep(3)
        self._accept_cookies()
        self._scrolldown(15)
        
        products = []
        
        try:
            # Блоки с товарами на главной странице
            sections = self.driver.find_elements(By.XPATH, '//div[contains(@class, "main-page__block")]')
            
            for section in sections[:3]:  # Берем первые 3 блока
                try:
                    section.find_element(By.XPATH, './/div[contains(@class, "swiper-container")]')
                    items = section.find_elements(By.XPATH, './/div[contains(@class, "swiper-slide")]')
                    
                    for item in items[:max_products]:
                        try:
                            link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            if link and len(products) < max_products:
                                product_data = self._get_product_data(link)
                                if product_data:
                                    products.append(product_data)
                        except:
                            continue
                except:
                    continue
                    
        except Exception as e:
            print(f"Ошибка при парсинге главной страницы: {str(e)}")
        
        return products
    
    def search_products(self, query, max_products=20):
        """Поиск товаров по запросу"""
        search_url = f"{self.base_url}/catalog/?q={query}"
        self.driver.get(search_url)
        time.sleep(3)
        self._accept_cookies()
        self._scrolldown(10)
        
        products = []
        
        try:
            product_cards = self.driver.find_elements(By.XPATH, '//div[contains(@class, "catalog-item")]')
            
            for card in product_cards[:max_products]:
                try:
                    link = card.find_element(By.CLASS_NAME, 'item-title').find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if link:
                        product_data = self._get_product_data(link)
                        if product_data:
                            products.append(product_data)
                except:
                    continue
                    
        except Exception as e:
            print(f"Ошибка при поиске товаров: {str(e)}")
        
        return products
    
    def parse_category(self, category_url, max_products=20):
        """Парсим товары из конкретной категории"""
        self.driver.get(category_url)
        time.sleep(3)
        self._accept_cookies()
        self._scrolldown(15)
        
        products = []
        
        try:
            product_cards = self.driver.find_elements(By.XPATH, '//div[contains(@class, "catalog-item")]')
            
            for card in product_cards[:max_products]:
                try:
                    link = card.find_element(By.CLASS_NAME, 'item-title').find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if link:
                        product_data = self._get_product_data(link)
                        if product_data:
                            products.append(product_data)
                except:
                    continue
                    
        except Exception as e:
            print(f"Ошибка при парсинге категории: {str(e)}")
        
        return products
    
    def close(self):
        """Закрытие драйвера"""
        self.driver.quit()

# Инициализация парсера
parser = SberMegaMarketParser()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/popular', methods=['GET'])
def get_popular_products():
    max_products = request.args.get('max', default=20, type=int)
    products = parser.parse_main_page(max_products=max_products)
    return jsonify(products)

@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('q', default='', type=str)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    max_products = request.args.get('max', default=20, type=int)
    products = parser.search_products(query, max_products=max_products)
    return jsonify(products)

@app.route('/api/category', methods=['GET'])
def get_category_products():
    category_url = request.args.get('url', default='', type=str)
    if not category_url:
        return jsonify({"error": "Parameter 'url' is required"}), 400
    
    max_products = request.args.get('max', default=20, type=int)
    products = parser.parse_category(category_url, max_products=max_products)
    return jsonify(products)

@app.route('/api/product', methods=['GET'])
def get_product():
    product_url = request.args.get('url', default='', type=str)
    if not product_url:
        return jsonify({"error": "Parameter 'url' is required"}), 400
    
    product_data = parser._get_product_data(product_url)
    if product_data:
        return jsonify(product_data)
    else:
        return jsonify({"error": "Product not found or error occurred"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.teardown_appcontext
def shutdown_parser(exception=None):
    parser.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)