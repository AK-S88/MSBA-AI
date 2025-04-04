import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time
import csv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = 'https://www.uml.edu/msb/departments/operations-info-systems/programs/msba.aspx'
visited = set()
collected_links = []

def is_valid_internal_link(link):
    parsed_link = urlparse(link)
    return parsed_link.netloc == '' or parsed_link.netloc == urlparse(base_url).netloc

def crawl(url, depth=0, max_depth=3):
    if depth > max_depth or url in visited:
        return

    try:
        logging.info(f"Crawling: {url}")
        response = requests.get(url)
        time.sleep(1)  # Be polite

        if response.status_code != 200:
            logging.warning(f"Failed: {url} (status {response.status_code})")
            return

        visited.add(url)
        collected_links.append(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        for link_tag in soup.find_all('a', href=True):
            href = link_tag.get('href')
            full_url = urljoin(url, href)
            full_url = full_url.split('#')[0]  # Remove fragments

            if is_valid_internal_link(full_url) and full_url not in visited:
                crawl(full_url, depth + 1, max_depth)

    except Exception as e:
        logging.error(f"Error on {url}: {e}")

# Run crawler
crawl(base_url)

# Save links
with open('uml_msba_links.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for link in collected_links:
        writer.writerow([link])

logging.info(f"Total links collected: {len(collected_links)}")
