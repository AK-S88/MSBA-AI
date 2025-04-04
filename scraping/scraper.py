import requests
from bs4 import BeautifulSoup
import logging

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

        # Example: Extract all paragraph texts
        paragraphs = soup.find_all('p')
        if not paragraphs:
            logging.warning("No paragraphs found on the page.")
        for p in paragraphs:
            print(p.get_text())

        # Example: Extracting headings (h1, h2, h3)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        if not headings:
            logging.warning("No headings found on the page.")
        for heading in headings:
            print(heading.get_text())

        # Example of handling a specific element (e.g., by ID or class)
        # Adjust this section as needed based on the webpage's structure
        try:
            # If the program has a specific section with ID "program-info"
            program_info = soup.find(id='program-info')
            if program_info:
                logging.info("Program info section found.")
                print(program_info.get_text())
            else:
                logging.warning("No program info section found.")
        except AttributeError as e:
            logging.error(f"Error while searching for program info section: {e}")

        return soup  # Return the parsed soup for further processing

    except requests.exceptions.RequestException as e:
        # Handle network-related issues (e.g., connectivity problems, invalid URL)
        logging.error(f"Error during request to {url}: {e}")
        return None

    except Exception as e:
        # Catch all other exceptions and log them
        logging.error(f"An unexpected error occurred: {e}")
        return None

# Example usage
url = 'https://www.uml.edu/msb/departments/operations-info-systems/programs/msba.aspx'
scrape_page(url)
