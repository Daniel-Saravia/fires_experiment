import subprocess
import threading
from scraper import scrape_website
from app import app

def start_scraper():
    scrape_website()

def start_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # Run the scraper
    scraper_thread = threading.Thread(target=start_scraper)
    scraper_thread.start()

    # Run the Flask app
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # Wait for both threads to complete
    scraper_thread.join()
    flask_thread.join()
