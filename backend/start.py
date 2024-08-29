import threading
from scraper import start_scraping_interval
from app import app

def start_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    # Start the scraper in its own thread
    scraper_thread = threading.Thread(target=start_scraping_interval)
    scraper_thread.start()

    # Start the Flask app in the main thread
    start_flask()