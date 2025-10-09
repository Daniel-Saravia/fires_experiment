## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Daniel-Saravia/fires_experiment.git
    cd try_fires
    ```
2. **Create & Activate Virtual Environment**:
    ```bash
    python3 -m venv fires
    source fires/bin/activate # For Linux/macOS
    fires\Scripts\activate # For Windows
    ```

3. **Install Dependencies**:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
4. **Verify Installation**:

    ```bash
    pip list # Check installed packages
    ```

5. **Run Web Scraper**:

    ```bash
    python start.py
    ```

6. **Check Database**:

    ```bash
    sqlite3 data.db
    SELECT \* FROM events;
    .exit
    come back
    ``` 

## Tech Stack

- **Python 3.12** — core language for the scraper, API server, and data pipeline.
- **Flask + Flask-CORS** — lightweight web framework exposing the JSON API and serving the static frontend.
- **Selenium (Firefox headless)** — automates the Phoenix dashboard, with Selenium Manager provisioning `geckodriver` automatically when Firefox is available.
- **BeautifulSoup 4** — parses the rendered HTML tables to extract structured incident data.
- **SQLAlchemy** — ORM and engine management for SQLite, handling schema creation and queries.
- **SQLite** — lightweight relational database (`data.db`) storing the deduplicated fire events.
- **Colorama** — optional terminal colors for duplicate/insert logging feedback.

## How the Python Backend Works

- **`start.py`** is the entry point. It spins up the scraper in a background thread while Flask stays on the main thread so the API keeps serving requests during long-running scrapes.
- **`scraper.py`** hosts `OptimizedFireScraper`, which loads the Phoenix dashboard in a headless browser, waits for the data tables, parses them with BeautifulSoup, and dispatches event dictionaries. It prefers Firefox in the current setup (you can force Chrome with `FIRE_SCRAPER_BROWSER=chrome`) and retries failed scrapes before sleeping for the configured interval.
- **`check_duplicates.py`** receives each parsed event, checks SQLite for an identical row, and either inserts the new record or logs a color-coded “Skipped Duplicate” message.
- **`database.py`** defines the SQLAlchemy `Event` model plus the SQLite engine. Tables are created on import so any script that touches the module will ensure the schema exists.
- **`app.py`** exposes Flask routes. `/` serves the static frontend, while `/api/events`, `/api/events/latest/<limit>`, and `/api/stats` return JSON backed by SQLAlchemy queries.
- **Data flow**: `start.py` → scraper pulls records → duplicates filtered → SQLite storage → Flask endpoints provide the stored events for the frontend.
