from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time
import threading

# Import the database setup and Event model from database.py
from database import Session, Event

# Initialize the Chrome WebDriver with default options
driver = webdriver.Chrome()

def scrape_website():
    session = Session()  # Start a session to interact with the database
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

            event = Event(title=title, location=location, datetime=event_datetime, channel=channel, status=status)
            session.add(event)
            session.commit()

            print(f"Inserted event: {title} at {location} into the database.")

    print("Scraping completed successfully.")
    session.close()  # Close the session

def start_scraping_interval(interval=600):
    """
    Starts the scraping process immediately and continues to scrape every `interval` seconds.
    
    :param interval: Time in seconds between each scrape (default is 600 seconds, or 10 minutes).
    """
    while True:
        scrape_website()
        time.sleep(interval)

if __name__ == '__main__':
    start_scraping_interval()  # Start scraping immediately when running this script directly
    driver.quit()  # Ensure the browser is closed after scraping
