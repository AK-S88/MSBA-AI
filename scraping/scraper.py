# Scraper using Selenium
from selenium import webdriver

# Setup driver (headless)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def scrape(url):
    driver.get(url)
    return driver.page_source
