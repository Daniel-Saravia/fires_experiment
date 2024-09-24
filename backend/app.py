from flask import Flask, jsonify
from database import events_table
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)

@app.route('/events', methods=['GET'])
def get_events():
    """
    Endpoint to retrieve all events from the DynamoDB table.

    Returns:
        JSON: A list of events with title, location, datetime, channel, and status.
    """
    try:
        # Scan the table to get all items
        response = events_table.scan()
        events = response.get('Items', [])

        # Convert datetime strings back to desired format if necessary
        for event in events:
            event['datetime'] = event['datetime']  # Already a string in desired format

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)