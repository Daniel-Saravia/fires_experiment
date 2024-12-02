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
