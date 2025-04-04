import requests
from bs4 import BeautifulSoup
import logging
import csv
import os
import json
import time
import random
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

# Configuration
PROGRESS_FILE = 'progress.json'
CSV_OUTPUT_FILE = 'scraped_data.csv'
LINKS_INPUT_FILE = 'links.csv'  # CSV file containing the 400 links
REQUEST_DELAY_MIN = 1  # Minimum delay in seconds
REQUEST_DELAY_MAX = 3  # Maximum delay in seconds
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


def load_links_from_csv(csv_file):
    """Load links from a CSV file"""
    links = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0].startswith('http'):  # Simple validation
                    links.append(row[0])
    except Exception as e:
        logging.error(f"Error loading links from CSV: {e}")
        raise
    
    logging.info(f"Loaded {len(links)} links from {csv_file}")
    return links


def load_progress():
    """Load progress from a previous run"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as file:
            return json.load(file)
    return {"last_scraped_index": 0}


def save_progress(last_scraped_index):
    """Save progress to a file"""
    with open(PROGRESS_FILE, 'w') as file:
        json.dump({"last_scraped_index": last_scraped_index}, file)


def get_domain(url):
    """Extract domain from URL"""
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


def scrape_page(url):
    """Scrape a single page and extract relevant content"""
    try:
        # Add delay to avoid being blocked
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
        
        # Set up headers for the request
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Send a GET request to the page
        logging.info(f"Fetching page: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        # Check if the request was successful
        if response.status_code != 200:
            logging.error(f"Failed to fetch page. Status code: {response.status_code}")
            return None

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        domain = get_domain(url)
        
        # Extract title of the page
        page_title = soup.title.string.strip() if soup.title else "No title found"
        
        # Extract all paragraphs
        paragraphs = soup.find_all('p')
        paragraph_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Extract headings (h1, h2, h3)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        headings_text = ' '.join([heading.get_text().strip() for heading in headings if heading.get_text().strip()])
        
        # Try multiple approaches to find program info
        program_text = "No program info found"
        
        # Method 1: Look for element with id containing 'program'
        program_elements = soup.find_all(id=lambda x: x and 'program' in x.lower())
        if program_elements:
            program_text = ' '.join([el.get_text().strip() for el in program_elements])
        
        # Method 2: Look for sections/divs with 'program' in class names
        if not program_text or program_text == "No program info found":
            program_classes = soup.find_all(class_=lambda x: x and 'program' in x.lower())
            if program_classes:
                program_text = ' '.join([el.get_text().strip() for el in program_classes])
        
        # Method 3: Look for sections containing "program" in heading
        if not program_text or program_text == "No program info found":
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                if 'program' in heading.get_text().lower():
                    # Get the next sibling elements until the next heading
                    content = []
                    for sibling in heading.find_next_siblings():
                        if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                            break
                        if sibling.get_text().strip():
                            content.append(sibling.get_text().strip())
                    if content:
                        program_text = ' '.join(content)
                        break

        # Return structured data
        return {
            'url': url,
            'domain': domain,
            'title': page_title,
            'headings': headings_text,
            'content': paragraph_text,
            'program_info': program_text
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}", exc_info=True)
        return None


def save_to_csv(scraped_data):
    """Save scraped data to CSV"""
    file_exists = os.path.exists(CSV_OUTPUT_FILE)
    try:
        with open(CSV_OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['URL', 'Domain', 'Title', 'Headings', 'Content', 'Program Info'])
            writer.writerow([
                scraped_data['url'],
                scraped_data['domain'],
                scraped_data['title'],
                scraped_data['headings'],
                scraped_data['content'],
                scraped_data['program_info']
            ])
        logging.info(f"Data saved to {CSV_OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")


def scrape_all_links():
    """Main function to scrape all links with progress tracking"""
    # Load links from CSV
    links = load_links_from_csv(LINKS_INPUT_FILE)
    if not links:
        logging.error("No links found in the CSV file.")
        return
    
    # Load progress
    progress = load_progress()
    last_scraped_index = progress["last_scraped_index"]
    
    try:
        for i, link in enumerate(links[last_scraped_index:], start=last_scraped_index):
            logging.info(f"Scraping link {i + 1}/{len(links)}: {link}")
            
            # Skip empty links
            if not link.strip():
                logging.warning(f"Skipping empty link at index {i}")
                save_progress(i + 1)
                continue
                
            # Scrape the page
            scraped_data = scrape_page(link)
            
            if scraped_data:
                save_to_csv(scraped_data)
            else:
                logging.warning(f"No data scraped for link: {link}")
            
            # Save progress after each link
            save_progress(i + 1)
            
            # Log remaining links
            if (i + 1) % 20 == 0:
                logging.info(f"Progress: {i + 1}/{len(links)} links processed ({(i + 1)/len(links)*100:.1f}%)")
    
    except KeyboardInterrupt:
        logging.info("Scraping interrupted. Progress saved.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("Scraping process finished!")


if __name__ == "__main__":
    logging.info("=== Web Scraper Started ===")
    scrape_all_links()
