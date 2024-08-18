from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import time

# Automatically manage the ChromeDriver binary
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Database setup
DATABASE_URL = "sqlite:///data.db"
Base = declarative_base()

# Define the Event table
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    location = Column(String)
    datetime = Column(DateTime)
    channel = Column(String)
    status = Column(String)

# Create the database engine and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def scrape_website():
    url = 'https://mapportal.phoenix.gov/pfd/apps/dashboards/60bc91a9f225469fb0194b9e9ff623e2'
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load content
    
    # Parse the fully rendered page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all divs with the class 'external-html' which contain the tables
    external_html_divs = soup.find_all('div', class_='external-html')
    
    print(f"Found {len(external_html_divs)} 'external-html' divs.")
    
    for div_index, div in enumerate(external_html_divs):
        table = div.find('table')
        if table is None:
            print(f"No table found in 'external-html' div {div_index + 1}.")
            continue
        
        print(f"Processing table in 'external-html' div {div_index + 1}.")
        
        rows = table.find_all('tr')
        
        for row_index, row in enumerate(rows):
            cols = row.find_all('td')
            if len(cols) < 5:
                print(f"Skipping row {row_index + 1} in table {div_index + 1} due to insufficient columns.")
                continue  # Skip rows that don't have enough columns
            
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
    driver.quit()

