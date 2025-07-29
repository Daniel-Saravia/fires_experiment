from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

# Import the insert function from check_duplicates.py
from check_duplicates import insert_event_if_not_duplicate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedFireScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.url = 'https://mapportal.phoenix.gov/pfd/apps/dashboards/60bc91a9f225469fb0194b9e9ff623e2'
        self.max_retries = 3
        
    def _get_chrome_options(self):
        """Configure Chrome options for maximum performance"""
        options = Options()
        
        # Enable headless mode for faster execution
        options.add_argument('--headless=new')
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Disable unnecessary features
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript-harmony-shipping')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--mute-audio')
        
        # Memory and CPU optimizations
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        options.add_argument('--aggressive-cache-discard')
        
        # Network optimizations
        options.add_argument('--aggressive')
        options.add_argument('--disable-background-networking')
        
        # Set user agent to avoid detection
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Disable logging for cleaner output
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Prefs for additional performance
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,  # Block popups
                "geolocation": 2,  # Block location sharing
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block media stream
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
        
    def _initialize_driver(self):
        """Initialize the Chrome driver with optimized settings"""
        try:
            options = self._get_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, 15)
            
            logger.info("Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def _wait_for_content_load(self):
        """Wait for the specific content to load instead of arbitrary sleep"""
        try:
            # Wait for external-html divs to be present
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "external-html"))
            )
            
            # Additional wait for JavaScript to populate tables
            time.sleep(2)  # Reduced from 9 seconds to 2 seconds
            
            logger.info("Content loaded successfully")
            return True
            
        except TimeoutException:
            logger.warning("Timeout waiting for content to load")
            return False
    
    def scrape_website(self):
        """Main scraping function with improved error handling and performance"""
        if not self.driver:
            if not self._initialize_driver():
                logger.error("Failed to initialize driver")
                return False
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starting scrape attempt {attempt + 1}/{self.max_retries}")
                
                # Navigate to the website
                self.driver.get(self.url)
                
                # Wait for content to load
                if not self._wait_for_content_load():
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Content load failed, retrying... ({attempt + 1}/{self.max_retries})")
                        continue
                    else:
                        logger.error("Failed to load content after all retries")
                        return False
                
                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                external_html_divs = soup.find_all('div', class_='external-html')
                
                if not external_html_divs:
                    logger.warning("No external-html divs found")
                    if attempt < self.max_retries - 1:
                        continue
                    return False
                
                logger.info(f"Found {len(external_html_divs)} 'external-html' divs")
                
                events_processed = 0
                
                for div_index, div in enumerate(external_html_divs):
                    table = div.find('table')
                    if table is None:
                        logger.warning(f"No table found in 'external-html' div {div_index + 1}")
                        continue
                    
                    rows = table.find_all('tr')
                    
                    for row_index, row in enumerate(rows):
                        cols = row.find_all('td')
                        if len(cols) < 5:
                            continue  # Skip header rows or incomplete rows
                        
                        try:
                            title = cols[0].text.strip()
                            location = cols[1].text.strip()
                            datetime_str = cols[2].text.strip()
                            channel = cols[3].text.strip()
                            status = cols[4].text.strip()
                            
                            # Skip empty rows
                            if not title or not datetime_str:
                                continue
                            
                            # Parse datetime with better error handling
                            event_datetime = self._parse_datetime(datetime_str)
                            if not event_datetime:
                                continue
                            
                            # Create event data
                            event_data = {
                                "title": title,
                                "location": location,
                                "datetime": event_datetime,
                                "channel": channel,
                                "status": status
                            }
                            
                            # Insert the event if it's not a duplicate
                            insert_event_if_not_duplicate(event_data)
                            events_processed += 1
                            
                        except Exception as e:
                            logger.warning(f"Error processing row {row_index + 1} in table {div_index + 1}: {e}")
                            continue
                
                logger.info(f"Scraping completed successfully. Processed {events_processed} events.")
                return True
                
            except WebDriverException as e:
                logger.error(f"WebDriver error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    self._restart_driver()
                    continue
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    continue
                else:
                    return False
        
        return False
    
    def _parse_datetime(self, datetime_str):
        """Parse datetime string with multiple format attempts"""
        formats = [
            '%m/%d/%Y, %I:%M %p',
            '%m/%d/%Y %I:%M %p',
            '%m-%d-%Y, %I:%M %p',
            '%m-%d-%Y %I:%M %p',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Date parsing failed for string: {datetime_str}")
        return None
    
    def _restart_driver(self):
        """Restart the driver in case of issues"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        self.driver = None
        self.wait = None
        time.sleep(1)  # Brief pause before restarting
        
    def start_scraping_interval(self, interval=600):
        """
        Starts the scraping process and continues to scrape every `interval` seconds.
        
        :param interval: Time in seconds between each scrape (default is 600 seconds, or 10 minutes).
        """
        logger.info(f"Starting scraping interval every {interval} seconds")
        
        try:
            while True:
                start_time = time.time()
                success = self.scrape_website()
                
                if not success:
                    logger.error("Scraping failed, will retry next interval")
                
                elapsed_time = time.time() - start_time
                logger.info(f"Scrape completed in {elapsed_time:.2f} seconds")
                
                # Sleep for the remaining interval time
                sleep_time = max(0, interval - elapsed_time)
                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.2f} seconds until next scrape")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in scraping loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

# Global scraper instance
scraper = OptimizedFireScraper()

def scrape_website():
    """Backwards compatibility function"""
    return scraper.scrape_website()

def start_scraping_interval(interval=600):
    """Backwards compatibility function"""
    return scraper.start_scraping_interval(interval)

if __name__ == '__main__':
    try:
        scraper.scrape_website()  # Initial scrape when script is run
        scraper.start_scraping_interval()  # Continue scraping every 10 minutes
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    finally:
        scraper.cleanup()
