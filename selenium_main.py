from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import csv
import re
import time

HEADPHONES_URL = "https://www.sony.co.uk/store/search?query=:relevance:normalSearch:true:category:gwx-audio:category:gwx-headphones"
BASE_URL = "https://www.sony.co.uk"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver



def scrape_page(driver, url):
    try:
        driver.get(url)
        # wait for product grid or no-results message
        WebDriverWait(driver, 30).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "sn-product-grid-item") or 
                      d.find_elements(By.XPATH, "//span[contains(text(), 'We could not find anything matching for')]")
        )

        # if no product 
        if driver.find_elements(By.XPATH, "//span[contains(text(), 'We could not find anything matching for')]"):
            print(f"No products found at {url}")
            return []

        # scroll down to load it all
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  

        headphones = []
        while True:
            product_items = driver.find_elements(By.CSS_SELECTOR, "sn-product-grid-item")
            if not product_items:
                break

            for index in range(len(product_items)):
                try:
                    item = driver.find_elements(By.CSS_SELECTOR, "sn-product-grid-item")[index]

                    # NAME
                    name = "N/A"
                    try:
                        name_element = WebDriverWait(item, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".sn-product-grid__name a"))
                        )
                        name = name_element.text.strip()
                    except (TimeoutException, StaleElementReferenceException) as e:
                        print(f"Name error on item {index}: {e}")

                    # PRICE
                    price = 0.0
                    try:
                        price_element = WebDriverWait(item, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".cx-product-price"))
                        )
                        price_text = price_element.text.strip()
                        price_match = re.search(r"£([\d,.]+(?:\.\d{2})?)", price_text)
                        price = float(price_match.group(1).replace(",", "")) if price_match else 0.0
                    except (TimeoutException, StaleElementReferenceException) as e:
                        print(f"Price error on item {index}: {e}")

                    # MPN
                    mpn = "N/A"
                    try:
                        mpn_element = WebDriverWait(item, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".cx-sku"))
                        )
                        mpn = mpn_element.text.strip()
                    except (TimeoutException, StaleElementReferenceException) as e:
                        print(f"MPN error on item {index}: {e}")

                    # URL
                    full_url = "N/A"
                    try:
                        url_element = WebDriverWait(item, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".sn-product-grid__image-container a"))
                        )
                        href = url_element.get_attribute("href")
                        if href:
                            full_url = f"{href}"
                    except (TimeoutException, StaleElementReferenceException) as e:
                        print(f"URL error on item {index}: {e}")

                    headphones.append({
                        "Name": name,
                        "Price": price,
                        "MPN": mpn,
                        "URL": full_url
                    })

                except Exception as e:
                    print(f"Unexpected error on item {index}: {e}")
            break 

        return headphones

    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        # driver.save_screenshot(f"error_page_screenshot.png")
        return []

def scrape_all_pages():
    driver = setup_driver()
    all_headphones = []
    page = 0
    
    try:
        while True:
            if page == 0:
                url = HEADPHONES_URL
            else:
                url = f"{HEADPHONES_URL}&currentPage={page}"
            
            print(f"Scraping page {page + 1}: {url}")
            headphones = scrape_page(driver, url)
            
            if not headphones:
                print(f"No headphones found on page {page + 1}. Stopping.")
                break
                
            all_headphones.extend(headphones)
            page += 1
            time.sleep(2)
    
    finally:
        driver.quit()
    
    return all_headphones

def main():
    headphones = scrape_all_pages()
    csv_file = "sony_headphones_selenium.csv"
    
    try:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Name", "Price", "MPN", "URL"])
            writer.writeheader()
            for headphone in headphones:
                writer.writerow(headphone)
        
        print(f"Data has been saved to {csv_file}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

if __name__ == "__main__":
    main()