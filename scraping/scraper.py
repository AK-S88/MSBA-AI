# scraper.py
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from config import URL, DELAY_SECONDS, OUTPUT_CSV

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_driver():
    """Initialize and return the Selenium WebDriver."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode for performance
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info("Chrome WebDriver initialized successfully.")
        return driver
    except WebDriverException as e:
        logging.error(f"WebDriver initialization failed: {e}")
        raise

def scrape_webpage(driver, url):
    """Scrape the content of the specified URL and return extracted text blocks."""
    try:
        driver.get(url)
        time.sleep(DELAY_SECONDS)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract meaningful content blocks from the main content area
        content_div = soup.find("div", class_="content")
        if not content_div:
            logging.warning("Could not find main content div.")
            return []

        text_blocks = []
        for tag in content_div.find_all(["h1", "h2", "h3", "p", "li"]):
            text = tag.get_text(strip=True)
            if text:
                text_blocks.append({"tag": tag.name, "text": text})

        logging.info(f"Extracted {len(text_blocks)} text blocks from the page.")
        return text_blocks

    except TimeoutException as te:
        logging.error(f"Timeout occurred while loading {url}: {te}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        return []

def save_to_csv(data, filename):
    """Save extracted data to a CSV file."""
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Saved data to {filename}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")


def main():
    driver = initialize_driver()
    try:
        data = scrape_webpage(driver, URL)
        if data:
            save_to_csv(data, OUTPUT_CSV)
    finally:
        driver.quit()
        logging.info("Driver closed.")

if __name__ == "__main__":
    main()
