from flask import Flask, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine, Event

app = Flask(__name__)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/events', methods=['GET'])
def get_events():
    """
    Endpoint to retrieve all events from the database.
    
    Returns:
        JSON: A list of events with title, location, datetime, channel, and status.
    """
    # Query all events from the database
    events = session.query(Event).all()

    # Convert the events into a list of dictionaries
    events_list = [
        {
            'title': event.title,
            'location': event.location,
            'datetime': event.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'channel': event.channel,
            'status': event.status
        }
        for event in events
    ]

    # Return the events as JSON
    return jsonify(events_list)

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)

