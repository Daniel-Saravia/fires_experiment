from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from database import engine, Event
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    """
    Serve the main frontend page.
    """
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Endpoint to retrieve all events from the database, ordered by most recent first.
    
    Returns:
        JSON: A list of events with id, title, location, datetime, channel, and status.
    """
    session = Session()
    try:
        # Query all events from the database, ordered by datetime descending
        events = session.query(Event).order_by(desc(Event.datetime)).all()

        # Convert the events into a list of dictionaries
        events_list = [
            {
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'datetime': event.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'datetime_readable': event.datetime.strftime('%B %d, %Y at %I:%M %p'),
                'channel': event.channel,
                'status': event.status
            }
            for event in events
        ]

        # Return the events as JSON
        return jsonify({
            'success': True,
            'count': len(events_list),
            'events': events_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        session.close()

@app.route('/api/events/latest/<int:limit>')
def get_latest_events(limit):
    """
    Endpoint to retrieve the latest N events.
    
    Args:
        limit (int): Number of latest events to retrieve
        
    Returns:
        JSON: A list of the latest events
    """
    session = Session()
    try:
        events = session.query(Event).order_by(desc(Event.datetime)).limit(limit).all()
        
        events_list = [
            {
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'datetime': event.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'datetime_readable': event.datetime.strftime('%B %d, %Y at %I:%M %p'),
                'channel': event.channel,
                'status': event.status
            }
            for event in events
        ]
        
        return jsonify({
            'success': True,
            'count': len(events_list),
            'events': events_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        session.close()

@app.route('/api/stats')
def get_stats():
    """
    Endpoint to get statistics about the events.
    
    Returns:
        JSON: Statistics including total count, status breakdown, etc.
    """
    session = Session()
    try:
        total_events = session.query(Event).count()
        
        # Get status breakdown
        status_counts = {}
        statuses = session.query(Event.status).distinct().all()
        for status_tuple in statuses:
            status = status_tuple[0]
            count = session.query(Event).filter(Event.status == status).count()
            status_counts[status] = count
        
        # Get recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_count = session.query(Event).filter(Event.datetime >= yesterday).count()
        
        return jsonify({
            'success': True,
            'total_events': total_events,
            'status_breakdown': status_counts,
            'recent_24h': recent_count
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        session.close()

# Backwards compatibility endpoints (without /api prefix)
@app.route('/events', methods=['GET'])
def get_events_legacy():
    """Legacy endpoint for backwards compatibility"""
    return get_events()

@app.route('/events/latest/<int:limit>')
def get_latest_events_legacy(limit):
    """Legacy endpoint for backwards compatibility"""
    return get_latest_events(limit)

@app.route('/stats')
def get_stats_legacy():
    """Legacy endpoint for backwards compatibility"""
    return get_stats()

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by returning JSON instead of HTML"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors by returning JSON instead of HTML"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)

