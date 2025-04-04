import requests
from bs4 import BeautifulSoup
import logging
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape_page(url):
    try:
        # Send a GET request to the page
        logging.info(f"Fetching the page: {url}")
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            logging.error(f"Failed to fetch the page. Status code: {response.status_code}")
            return None

        # Parse the content using BeautifulSoup
        logging.info("Parsing the page content...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title of the page
        page_title = soup.title.string if soup.title else "No title found"
        logging.info(f"Page Title: {page_title}")

        # Extract all paragraphs
        paragraphs = soup.find_all('p')
        paragraph_texts = []
        if not paragraphs:
            logging.warning("No paragraphs found on the page.")
        for p in paragraphs:
            paragraph_texts.append(p.get_text())

        # Extract all headings (h1, h2, h3)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        heading_texts = []
        if not headings:
            logging.warning("No headings found on the page.")
        for heading in headings:
            heading_texts.append(heading.get_text())

        # Extract specific section (e.g., program info by ID)
        program_info = soup.find(id='program-info')
        program_info_text = program_info.get_text() if program_info else "No program info found"

        # Save the scraped data to a CSV file
        save_to_csv(page_title, paragraph_texts, heading_texts, program_info_text)

        return soup  # Return the parsed soup for further processing

    except requests.exceptions.RequestException as e:
        # Handle network-related issues (e.g., connectivity problems, invalid URL)
        logging.error(f"Error during request to {url}: {e}")
        return None

    except Exception as e:
        # Catch all other exceptions and log them
        logging.error(f"An unexpected error occurred: {e}")
        return None

def save_to_csv(page_title, paragraphs, headings, program_info):
    # Define the file path where you want to save the data
    csv_file = 'scraped_data.csv'
    
    # Check if the file already exists, if not, create the file with headers
    try:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write the header only if the file is empty (this helps in appending data)
            if file.tell() == 0:
                writer.writerow(['Page Title', 'Paragraph Texts', 'Headings', 'Program Info'])

            # Write the scraped data into the CSV
            writer.writerow([page_title, ' '.join(paragraphs), ' '.join(headings), program_info])
            logging.info("Data saved to CSV.")
    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")

# Example usage
url = 'https://www.uml.edu/msb/departments/operations-info-systems/programs/msba.aspx'
scrape_page(url)
