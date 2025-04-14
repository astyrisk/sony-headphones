# Sony Headphones Scraper

This script scrapes headphones information from the Sony website and saves it to a CSV file. It was developed primarily for job application demonstration purposes. 

## Important Note

When I first developed this script, I used `requests` and `BeautifulSoup`. After a while, I felt I have to provide another solution using `Selenium`. Because it's quite the standard of dealing with dynamic content. So, This repo contains both of the solutions. For selenium, please make sure to have `ChromeDriver` installed and in your system's PATH. I personally grabbed it from [here](https://github.com/dreamshao/chromedriver). Also, make sure that the version of `ChromeDriver` matches your Chrome browser version.

## Installation

1.  **Clone the Repo**
    ```bash
    git clone https://github.com/astyrisk/sony-headphones.git
    cd sony-headphones
    ```

2.  **Virtual Environment (for linux)**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Clone the Repo**
    ```bash
    git clone [https://github.com/astyrisk/sony-headphones.git](https://github.com/astyrisk/sony-headphones.git)
    cd sony-headphones
    ```
### Using Requests and BeautifulSoup
3.  **Install Dependencies**
    ```bash
    pip install requests beautifulsoup4
    ```
4.  **Run the Script**
    ```bash
    python main.py
    ```
### Using Selenium 
3. **Install Dependencies**
    ```bash
    pip install selenium
    ```
4. **Run the Script**
    ```bash
    python selenium_main.py
    ```

## Design Considerations

* **URL Inspecting:** After Insepecting the href tag both from the browser-rendered HTML and the `requests` fetch HTML, it was found that the href tag is not present in the fetched HTML. That is because the href tag is dynamically added by JavaScript. However, I have reverse-engineered the URL generation pattern from the JavaScript code and implemented it in the main script. The other solustion uses Selenium headless browser to handle the dynamic content. 

* **Error Handling:** Basic error handling for network requests and file operations is implemented to ensure stability. For production, more robust error handling (e.g., specific HTTP error codes, retry logic, detailed logging) would be recommended.

* **Price Selection:** For some products, the website offers multiple prices. The script targets the primary visible price. This can be adjusted based on the specific needs.

* **Waits and Timeouts:** Adjusments of the Timeout and waits should be considered as they vary from machine to machine.

## How it Works

1.  **Fetch & Parse:** Uses `requests` to fetch HTML from Sony UK headphone search results pages. `BeautifulSoup` parses the fetched HTML.

2.  **Targeted Data Extraction:** The script navigates the parsed HTML structure of each product container (`<sn-product-grid-item>`) to extract key details:
    * **Name:** Located within the `<a>` tag inside an element identified by the class `sn-product-grid__name`.
    * **Price:** Extracted from the text content of an element with class `cx-product-price`. The script cleans this text (removing '£', commas) and converts it to a float. *Note: If the site displayed multiple prices, this selector targets the primary visible price.*
    * **MPN:** Found within the text of an element with class `cx-sku`.
    * **URL:** Found within the `href` attribute of the `<a>` tag inside an element identified by the class `sn-product-grid__image-container`.

3.  **Product URL Construction (Reverse-Engineered):** Direct links to product pages were not simple `href` attributes in the listing (because it seems to be dynamically generated). Therefore, the site's client-side JavaScript responsible for handling product clicks was analyzed (tracing functions like `clickProduct` -> `redirectToPdp`). This revealed the URL generation pattern for standard products, which the script replicates: `{BASE_URL}/store/product/{mpn}/{product-name-slug}`. Here, `{BASE_URL}` is `https://www.sony.co.uk`, `{mpn}` is the extracted MPN, and `{product-name-slug}` is a URL-friendly version of the name.

4.  **Output** The extracted Name, Price, MPN, and the constructed URL for every headphone are compiled and written into a structured CSV file (`sony_headphones.csv`) or (`sony_headphones_selenium.csv`).

5. **Error Handling & Politeness:** The script includes basic error handling for HTTP requests and CSV writing. It also introduces a few-second delay between fetching consecutive pages to avoid overloading the server.

*Developed by Mohamed Abdelbary for job application purposes.*
