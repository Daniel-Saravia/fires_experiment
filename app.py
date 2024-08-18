from flask import Flask, jsonify
from sqlalchemy.orm import sessionmaker
from scraper import engine, Event

app = Flask(__name__)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/events', methods=['GET'])
def get_events():
    events = session.query(Event).all()
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
    return jsonify(events_list)

if __name__ == '__main__':
    app.run(debug=True)
