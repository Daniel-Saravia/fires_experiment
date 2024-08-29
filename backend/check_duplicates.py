from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database import Event
from colorama import Fore, Style

DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def is_duplicate_event(event_data):
    """
    Checks if the given event data already exists in the database.
    
    Parameters:
    - event_data: dict containing the event details (title, location, datetime, channel, status)
    
    Returns:
    - True if a duplicate is found, False otherwise.
    """
    duplicate_event = session.query(Event).filter_by(
        title=event_data["title"],
        location=event_data["location"],
        datetime=event_data["datetime"],
        channel=event_data["channel"],
        status=event_data["status"]
    ).first()
    
    if duplicate_event:
        print(f"{Fore.YELLOW}[Duplicate Event Found]{Style.RESET_ALL}")
        print(f"  Title   : {event_data['title']}")
        print(f"  Location: {event_data['location']}")
        print(f"  Date/Time: {event_data['datetime']}")
        print(f"  Channel : {event_data['channel']}")
        print(f"  Status  : {event_data['status']}\n")
        return True
    return False

def insert_event_if_not_duplicate(event_data):
    """
    Inserts the event into the database if it is not a duplicate.
    
    Parameters:
    - event_data: dict containing the event details (title, location, datetime, channel, status)
    """
    if not is_duplicate_event(event_data):
        new_event = Event(
            title=event_data["title"],
            location=event_data["location"],
            datetime=event_data["datetime"],
            channel=event_data["channel"],
            status=event_data["status"]
        )
        session.add(new_event)
        session.commit()
        print(f"{Fore.GREEN}[Inserted Event]{Style.RESET_ALL}")
        print(f"  Title   : {event_data['title']}")
        print(f"  Location: {event_data['location']}")
        print(f"  Date/Time: {event_data['datetime']}")
        print(f"  Channel : {event_data['channel']}")
        print(f"  Status  : {event_data['status']}\n")
    else:
        print(f"{Fore.CYAN}[Skipped Duplicate]{Style.RESET_ALL}")
        print(f"  Title   : {event_data['title']}")
        print(f"  Location: {event_data['location']}\n")

if __name__ == "__main__":
    # Example event data to check and insert if not a duplicate
    example_event_data = {
        "title": "NATURAL GAS LEAK",
        "location": "200 E BASELINE RD ,TMP",
        "datetime": "2024-08-22 01:24:00",
        "channel": "Channel A7",
        "status": "E272:\u00a0On\u00a0Scene E273:\u00a0Command"
    }

    insert_event_if_not_duplicate(example_event_data)

    session.close()

