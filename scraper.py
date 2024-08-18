import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import schedule
import time

# Database setup
DATABASE_URL = "sqlite:///data.db"
Base = declarative_base()

# Defines the Event table with columns for id, title, location, datetime, channel, and status.
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    location = Column(String)
    datetime = Column(DateTime)
    channel = Column(String)
    status = Column(String)

# Creates a database engine, sets up the database schema, and initializes a session for interacting with the database.
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Scraper function
def scrape_website():
    url = 'URL_OF_THE_WEBSITE'  # Replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue  # Skip rows that don't have enough columns

        title = cols[0].text.strip()
        location = cols[1].text.strip()
        datetime_str = cols[2].text.strip()
        channel = cols[3].text.strip()
        status = cols[4].text.strip()

        event_datetime = datetime.strptime(datetime_str, '%m/%d/%Y, %I:%M %p')

        event = Event(title=title, location=location, datetime=event_datetime, channel=channel, status=status)
        session.add(event)
        session.commit()

# Schedule the scraper to run every 10 minutes
schedule.every(10).minutes.do(scrape_website)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
