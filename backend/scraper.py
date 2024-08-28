"""
Web Scraper for Public Incident Dashboard

This script is designed to scrape data from a public incident dashboard using Selenium and BeautifulSoup.
The scraped data is then stored in a SQLite database for later retrieval and analysis.

Features:
- Uses Selenium to automate a Chrome browser and load JavaScript-rendered content.
- Parses HTML content with BeautifulSoup to extract specific data from tables.
- Stores extracted data in a relational SQLite database using SQLAlchemy ORM.

Requirements:
- Google Chrome must be installed on the system.
- Python packages: selenium, webdriver-manager, beautifulsoup4, sqlalchemy

Setup:
1. Install dependencies using Conda:
    conda env create -f environment.yml
    conda activate web_scraper

2. Run the script:
    python scraper.py

Environment:
- The environment.yml file should include all necessary Python packages, and ChromeDriver is managed automatically by WebDriver Manager.

Usage:
- The script will open the specified webpage, wait for JavaScript to load, and then scrape data from tables within div elements.
- Extracted data is stored in a SQLite database named 'data.db'.
- Each run of the script will insert new data into the database.

Database Schema:
- Table: events
  - id (Integer): Primary key
  - title (String): Title of the event
  - location (String): Location of the event
  - datetime (DateTime): Date and time of the event
  - channel (String): Communication channel associated with the event
  - status (String): Status of the event

Author: Your Name
Date: YYYY-MM-DD
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import time

# Set Chrome options to avoid extra windows and suppress the automation info bar
chrome_options = Options()
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize the Chrome WebDriver using the defined options
driver = webdriver.Chrome(options=chrome_options)

# Database setup
DATABASE_URL = "sqlite:///data.db"
Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    location = Column(String)
    datetime = Column(DateTime)
    channel = Column(String)
    status = Column(String)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def scrape_website():
    url = 'https://mapportal.phoenix.gov/pfd/apps/dashboards/60bc91a9f225469fb0194b9e9ff623e2'
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load content

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

if __name__ == '__main__':
    scrape_website()
    driver.quit()  # Ensure the browser is closed after scraping

