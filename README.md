# Web Scraper Project

This project is a simple web scraper that scrapes a specific website every ten minutes and stores the scraped data in a SQLite database. The project includes a backend API using Flask and can be hosted on a local machine.

## Environment Setup

This project uses Conda for environment management. To set up the environment, use the provided `environment.yml` file.

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution)
- Python 3.12

### Setting Up the Environment

1. **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2. **Create and activate the Conda environment:**

    ```bash
    conda env create -f environment.yml
    conda activate web_scraper
    ```

### Running the Web Scraper

The web scraper is designed to run every 10 minutes and stores the scraped data in a SQLite database.

1. **Edit the `scraper.py` file:**
   - Replace `URL_OF_THE_WEBSITE` with the actual URL of the website you want to scrape.

2. **Run the scraper:**

    ```bash
    python scraper.py
    ```

### Project Structure

- **`scraper.py`**: The main script that scrapes the website and stores the data.
- **`environment.yml`**: The Conda environment configuration file.
- **`data.db`**: The SQLite database file (generated after running the scraper).

### Requirements

- Python 3.12
- Flask
- SQLAlchemy
- BeautifulSoup4
- Requests
- Schedule (installed via `pip`)

### Future Improvements

- Add a frontend to visualize the scraped data.
- Implement error handling for network issues and data inconsistencies.
- Extend the scraper to handle more complex websites.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

