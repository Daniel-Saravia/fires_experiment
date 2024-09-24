import boto3
from botocore.exceptions import ClientError
from database import events_table
from colorama import Fore, Style
import uuid
from datetime import datetime

def is_duplicate_event(event_data):
    """
    Checks if the given event data already exists in the DynamoDB table.

    Parameters:
    - event_data: dict containing the event details (title, location, datetime, channel, status)

    Returns:
    - True if a duplicate is found, False otherwise.
    """
    try:
        # DynamoDB doesn't support querying non-key attributes without a secondary index.
        # We'll scan the table instead (not efficient for large datasets).
        response = events_table.scan(
            FilterExpression=(
                'title = :title and location = :location and #dt = :datetime and channel = :channel and #st = :status'
            ),
            ExpressionAttributeNames={
                '#dt': 'datetime',
                '#st': 'status'
            },
            ExpressionAttributeValues={
                ':title': event_data['title'],
                ':location': event_data['location'],
                ':datetime': event_data['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                ':channel': event_data['channel'],
                ':status': event_data['status']
            }
        )
        items = response.get('Items', [])
        if items:
            print(f"{Fore.YELLOW}[Duplicate Event Found]{Style.RESET_ALL}")
            # Print event details...
            return True
        return False
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False

def insert_event_if_not_duplicate(event_data):
    """
    Inserts the event into the DynamoDB table if it is not a duplicate.

    Parameters:
    - event_data: dict containing the event details (title, location, datetime, channel, status)
    """
    if not is_duplicate_event(event_data):
        try:
            event_id = str(uuid.uuid4())
            events_table.put_item(
                Item={
                    'id': event_id,
                    'title': event_data['title'],
                    'location': event_data['location'],
                    'datetime': event_data['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'channel': event_data['channel'],
                    'status': event_data['status']
                }
            )
            print(f"{Fore.GREEN}[Inserted Event]{Style.RESET_ALL}")
            # Print event details...
        except ClientError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"{Fore.CYAN}[Skipped Duplicate]{Style.RESET_ALL}")
        # Print event details...

if __name__ == "__main__":
    # Example event data to check and insert if not a duplicate
    example_event_data = {
        "title": "NATURAL GAS LEAK",
        "location": "200 E BASELINE RD ,TMP",
        "datetime": datetime.now(),
        "channel": "Channel A7",
        "status": "E272: On Scene E273: Command"
    }

    insert_event_if_not_duplicate(example_event_data)
