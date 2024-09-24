from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

# Import the insert function from check_duplicates.py
from check_duplicates import insert_event_if_not_duplicate

def scrape_website():
    # Configure Selenium to use headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0")
    chrome_options.binary_location = "/opt/chrome/chrome"  # Update path as needed

    # Path to Chromedriver
    chromedriver_path = "/opt/chromedriver"  # Update path as needed

    # Initialize the Chrome WebDriver with options
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    try:
        url = 'https://mapportal.phoenix.gov/pfd/apps/dashboards/60bc91a9f225469fb0194b9e9ff623e2'
        driver.get(url)
        time.sleep(9)  # Wait for JavaScript to load content

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        external_html_divs = soup.find_all('div', class_='external-html')

        print(f"Found {len(external_html_divs)} 'external-html' divs.")

        for div_index, div in enumerate(external_html_divs):
            table = div.find('table')
            if table is None:
                print(f"No table found in 'external-html' div {div_index + 1}.")
                continue

            rows = table.find_all('tr')

            for row_index, row in enumerate(rows):
                cols = row.find_all('td')
                if len(cols) < 5:
                    print(f"Skipping row {row_index + 1} in table {div_index + 1} due to insufficient columns.")
                    continue

                title = cols[0].text.strip()
                location = cols[1].text.strip()
                datetime_str = cols[2].text.strip()
                channel = cols[3].text.strip()
                status = cols[4].text.strip()

                try:
                    event_datetime = datetime.strptime(datetime_str, '%m/%d/%Y, %I:%M %p')
                except ValueError:
                    print(f"Date parsing failed for string: {datetime_str}")
                    continue

                # Create a dictionary for the event data
                event_data = {
                    "title": title,
                    "location": location,
                    "datetime": event_datetime,
                    "channel": channel,
                    "status": status
                }

                # Insert the event if it's not a duplicate
                insert_event_if_not_duplicate(event_data)

        print("Scraping completed successfully.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        # Ensure the browser is closed after scraping
        driver.quit()

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    scrape_website()
    return {
        'statusCode': 200,
        'body': 'Scraping completed successfully.'
    }
