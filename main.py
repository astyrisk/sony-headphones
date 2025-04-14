import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from requests.exceptions import RequestException

HEADPHONES_URL = "https://www.sony.co.uk/store/search?query=:relevance:normalSearch:true:category:gwx-audio:category:gwx-headphones"
BASE_URL = "https://www.sony.co.uk"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_page(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Check for "no results" message
            no_results = soup.find_all(lambda tag: tag.name == "span" 
                and "We could not find anything matching for" in tag.get_text(strip=True))
            if no_results:
                print(f"No products found at {url}")
                return []

            headphones = []
            product_items = soup.select("sn-product-grid-item")

            for item in product_items:
                # NAME
                name_tag = item.select_one(".sn-product-grid__name a")
                name = name_tag.get_text(strip=True) if name_tag else "N/A"

                # PRICE
                price_tag = item.select_one(".cx-product-price")
                price = 0.0
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    price_match = re.search(r"£([\d,.]+(?:\.\d{2})?)", price_text)
                    price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

                # MPN
                mpn_tag = item.select_one(".cx-sku")
                mpn = mpn_tag.get_text(strip=True) if mpn_tag else "N/A"

                # URL
                full_url = get_full_url(name, mpn)

                headphones.append({
                    "Name": name,
                    "Price": price,
                    "MPN": mpn,
                    "URL": full_url
                })
            return headphones

        except RequestException as e:
            print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt)) 
            continue
    print(f"Failed to fetch page {url} after {retries} attempts.")
    return []

def scrape_all_pages():
    all_headphones = []
    page = 0
    max_empty_pages = 2
    empty_page_count = 0

    while True:
        if page == 0:
            url = HEADPHONES_URL
        else:
            url = f"{HEADPHONES_URL}&currentPage={page}"

        print(f"Scraping page {page + 1}: {url}")
        headphones = scrape_page(url)

        if not headphones:
            empty_page_count += 1
            print(f"No headphones found on page {page + 1}. Empty page count: {empty_page_count}/{max_empty_pages}")
            if empty_page_count >= max_empty_pages:
                print(f"Reached {max_empty_pages} consecutive empty pages. Stopping.")
                break
        else:
            empty_page_count = 0
            all_headphones.extend(headphones)

        page += 1
        time.sleep(2)

    return all_headphones

def get_full_url(name, mpn):
    if name == "N/A" or mpn == "N/A":
        return "N/A"
    
    name_slug = re.sub(r'[^\w\s-]', '', name).replace(" ", "-").lower()
    return f"{BASE_URL}/store/product/{mpn.lower()}/{name_slug}"

def main():
    headphones = scrape_all_pages()
    csv_file = "sony_headphones.csv"
    
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