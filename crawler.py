from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import time
import random
# database.py에서 함수 임포트
from database import get_db_connection, create_table, insert_products

# 올리브영 메인 페이지 URL
URL = "https://www.oliveyoung.co.kr/store/main/main.do"

def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def fetch_page(main_page_url):
    """ Selenium을 사용하여 페이지 내용을 가져옵니다. """
    driver = None
    try:
        driver = setup_driver()
        
        print(f"Visiting main page: {main_page_url}")
        driver.get(main_page_url)
        
        # "랭킹" 링크를 찾아 클릭합니다.
        # 이 부분은 실제 웹사이트 구조에 따라 변경해야 할 수 있습니다.
        # 예를 들어, 링크 텍스트가 "랭킹"이 아니거나 다른 선택자를 사용해야 할 수 있습니다.
        print("Finding and clicking the 'Ranking' link...")
        ranking_link_selector = (By.PARTIAL_LINK_TEXT, "랭킹")
        
        wait = WebDriverWait(driver, 20)
        ranking_link = wait.until(EC.element_to_be_clickable(ranking_link_selector))
        ranking_link.click()

        # 랭킹 페이지가 로드될 때까지 대기
        print("Waiting for ranking page to load...")
        product_list_selector = (By.CSS_SELECTOR, "ul.cate_prd_list")
        wait.until(EC.presence_of_element_located(product_list_selector))
        
        # 페이지가 로드된 후, 스크롤하여 더 많은 상품을 로드
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(random.uniform(0.5, 1.5))
        
        return driver.page_source
        
    except TimeoutException:
        print("Timeout waiting for page or element to load.")
        if driver:
            screenshot_path = "timeout_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            print("Page source at timeout:")
            print(driver.page_source)
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        if driver:
            screenshot_path = "error_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        return None
    finally:
        if driver:
            driver.quit()


def clean_text(text):
    """ 텍스트에서 숫자만 추출하고, 비어있으면 0을 반환합니다. """
    if not text:
        return 0
    # 숫자와 소수점만 남기고 제거
    cleaned_text = re.sub(r'[^\d.]', '', text)
    return cleaned_text if cleaned_text else 0

def parse_products(html):
    """ HTML을 파싱하여 상품 정보 리스트를 반환합니다. """
    if not html:
        return []
        
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.select("ul.cate_prd_list li") 
    
    if not products:
        print("No products found. Check CSS Selector.")
        return []
    
    # --- 최종 디버깅을 위해 첫 번째 상품의 HTML을 출력합니다. ---
    print("--- HTML of the first product item for debugging ---")
    print(products[0].prettify())
    print("----------------------------------------------------")
    # ---------------------------------------------------------

    print(f"Found {len(products)} products on the page.")
    
    product_list = []
    for item in products:
        try:
            # 상품 ID 선택자 변경
            product_anchor = item.select_one('a.prd_thumb')
            product_id = product_anchor.get('data-ref-goodsno', '') if product_anchor else ''

            if not product_id:
                continue

            brand_name = item.select_one("span.tx_brand").text.strip()
            product_name = item.select_one("p.tx_name").text.strip()
            
            original_price_tag = item.select_one("span.tx_org")
            original_price_text = original_price_tag.text.strip() if original_price_tag else "0"
            original_price = int(float(clean_text(original_price_text)))

            sale_price_tag = item.select_one("span.tx_cur")
            sale_price_text = sale_price_tag.text.strip() if sale_price_tag else "0"
            sale_price = int(float(clean_text(sale_price_text)))
            
            # 할인가가 없으면 원가를 할인가로 사용
            if sale_price == 0 and original_price != 0:
                sale_price = original_price

            # 평점 (rating_score) 파싱 로직 최종 수정
            rating_tag = item.select_one("span.point")
            rating_score = 0.0
            if rating_tag and 'style' in rating_tag.attrs:
                style_attr = rating_tag['style']
                width_match = re.search(r'width\s*:\s*(\d+)%', style_attr)
                if width_match:
                    percentage = int(width_match.group(1))
                    rating_score = round((percentage / 100) * 5, 1)
            
            # 리뷰 수 (review_count) 파싱 로직 수정
            review_tag = item.select_one("span.tx_rev")
            review_count = int(clean_text(review_tag.text)) if review_tag else 0

            product_info = {
                'product_id': product_id,
                'brand_name': brand_name,
                'product_name': product_name,
                'original_price': original_price,
                'sale_price': sale_price,
                'rating_score': rating_score,
                'review_count': review_count
            }
            
            product_list.append(product_info)
            
        except Exception as e:
            product_id_val = item.select_one('a.prd_thumb').get('data-ref-goodsno', 'N/A') if item.select_one('a.prd_thumb') else 'N/A'
            print(f"Error parsing item with product_id {product_id_val}: {e}")
            continue
    
    return product_list


if __name__ == "__main__":
    print("Starting the crawler with Selenium...")
    html_content = fetch_page(URL)
    
    if not html_content:
        print("\nFailed to fetch HTML content. Exiting.")
        exit()

    print("\nSuccessfully fetched HTML content.")
    products_data = parse_products(html_content)
    print(f"\nTotal products extracted: {len(products_data)}")

    if not products_data:
        print("No data to process. Exiting.")
        exit()

    # --- 데이터 확인을 위해 JSON 파일로 저장 ---
    output_filename = 'products.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)
    print(f"\nExtracted data saved to '{output_filename}'")
    # -----------------------------------------

    # 데이터베이스 연동
    conn = get_db_connection()
    if conn:
        try:
            # 테이블 생성
            create_table(conn)
            # 데이터 삽입
            insert_products(conn, products_data)
        finally:
            conn.close()
            print("Database connection closed.")
    else:
        print("Failed to connect to the database.")