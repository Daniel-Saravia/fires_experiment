# Web Scraper Project

This project is a Python-based web scraper that periodically scrapes a specific website to collect data and stores it in a SQLite database. The scraper is configured to run using Selenium with ChromeDriver, managed automatically by `webdriver-manager`, making it easy to deploy on different machines.

## Features

- **Automated Data Collection**: The scraper automatically extracts data from a dynamically loaded website and stores it in a relational SQLite database.
- **Portability**: The project is fully portable across different machines, with dependencies managed through Conda and WebDriver handled by `webdriver-manager`.
- **Database Storage**: Data is stored in an SQLite database, allowing easy querying and analysis.

## Environment Setup

This project uses Conda for environment management. All dependencies, including Selenium and `webdriver-manager`, are specified in the `environment.yml` file.

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution)
- Google Chrome (or Chromium) installed

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

3. **Verify the installation:**

    Ensure that all dependencies are installed correctly by running:

    ```bash
    conda list
    ```

## Running the Web Scraper

The web scraper uses Selenium to interact with the website and BeautifulSoup to parse the HTML content.

1. **Run the scraper:**

    ```bash
    python scraper.py
    ```

    The scraper will:
    - Open the specified website in a headless Chrome browser.
    - Extract the relevant data from the webpage.
    - Store the extracted data in the `data.db` SQLite database.

2. **Check the database:**

    You can inspect the stored data using SQLite's command-line interface:

    ```bash
    sqlite3 data.db
    ```

    Then run SQL queries, such as:

    ```sql
    SELECT * FROM events;
    ```

## Deployment

To deploy this scraper on another machine:

1. **Copy the project directory to the target machine.**
2. **Ensure Miniconda or Anaconda is installed.**
3. **Set up the environment as described in the "Setting Up the Environment" section.**
4. **Run the scraper as described above.**

## Future Improvements

- **Automated Scheduling**: Use `cron` jobs or another scheduling tool to run the scraper periodically.
- **Error Handling**: Enhance the script with more robust error handling and logging.
- **Data Visualization**: Develop a front-end application to visualize the collected data.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
