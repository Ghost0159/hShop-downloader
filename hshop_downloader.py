import os
import re
import requests
import logging
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
import contextlib
import sys
import argparse

# Suppress TensorFlow and other libraries' verbose logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
parser = argparse.ArgumentParser(description='Download games with optional speed limit.')
parser.add_argument('--speed-limit', type=float, default=None, help='Download speed limit in bytes per second')
args = parser.parse_args()

speed_limit_glob = args.speed_limit

@contextlib.contextmanager
def suppress_stdout_stderr():
    """Suppress stdout and stderr."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Configure logging
log_level = logging.INFO  # Use INFO to show only necessary outputs
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL of the website to scrape
BASE_URL = os.getenv("BASE_URL", "https://hshop.erista.me")

def get_chrome_options():
    """Configure Chrome options for headless browsing."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    return options

def get_main_categories(driver):
    """Retrieve main categories from the homepage."""
    driver.get(BASE_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup.find_all("a", href=re.compile(r'^/c/'))

def sanitize_filename(filename):
    """Sanitize file names by removing invalid characters."""
    filename = re.sub(r'[<>:\"/\\|?*\x00-\x1F]', '', filename)
    return filename

def html_decode(filename):
    """Decode special HTML characters in file names."""
    replacements = {
        '%3A': ':',
        '%2F': '/',
        '%2C': ',',
        '%5F': '_',
        '%28': '(',
        '%29': ')',
        "'": ''
    }
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    return filename

def prompt_user_for_selection(items, prompt_message):
    """
    Prompt the user to select items from a list.

    Args:
        items (list): List of items to choose from.
        prompt_message (str): The message to display to the user.

    Returns:
        list: A list of selected items.
    """
    logging.info(prompt_message)
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item.text.strip() if hasattr(item, 'text') else item[0]}")
    selections = input("Enter your selections: ")

    if selections.strip() == '*':
        return items
    else:
        selected_items = []
        for selection in selections.split(','):
            selection = selection.strip()
            if not selection.isdigit() or int(selection) not in range(1, len(items) + 1):
                logging.error(f"Invalid selection '{selection}', please try again. Example: 1,2,3")
                exit(1)
            selected_items.append(items[int(selection) - 1])
        return selected_items

def get_games():
    """Retrieve games from selected categories and download them."""
    options = get_chrome_options()
    
    with suppress_stdout_stderr():
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    with driver:
        categories = get_main_categories(driver)
        selected_categories = prompt_user_for_selection(categories, "Select main categories (comma separated, '*' for all):")

        for selected_category in selected_categories:
            category_url = BASE_URL + selected_category['href']
            download_games_in_category(driver, category_url)

def download_games_in_category(driver, category_url):
    """
    Download games from a specific category.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        category_url (str): URL of the category to scrape.
    """
    driver.get(category_url)
    time.sleep(2)  # Wait for the page to load completely
    soup_region = BeautifulSoup(driver.page_source, "html.parser")
    
    # Find all subcategory links and names
    subcategory_elements = soup_region.find_all("a", class_="list-entry block-link")
    
    warning_displayed = False  # Track whether the warning has been displayed

    sub_categories = {}
    for element in subcategory_elements:
        subcategory_link = element['href']
        subcategory_name_element = element.find("h3", class_="green bold")
        
        if subcategory_name_element is None:
            if not warning_displayed:
                logging.warning(f"Some subcategories are missing <h3> elements.")
                warning_displayed = True
            continue
        
        subcategory_name = subcategory_name_element.text.strip()
        sub_categories[subcategory_name] = subcategory_link

    sub_category_list = list(sub_categories.items())
    
    # Prompt user for selection
    selected_sub_categories = prompt_user_for_selection(
        sub_category_list,
        f"Select subcategories for {category_url.replace(BASE_URL + '/c/', '')} (comma separated, '*' for all):"
    )

    for sub_category_name, sub_category_link in selected_sub_categories:
        download_path = os.path.join(
            "./downloads",
            category_url.replace(BASE_URL + '/c/', ''),
            sanitize_filename(sub_category_name)
        )
        os.makedirs(download_path, exist_ok=True)

        offset = 0
        while True:
            url = BASE_URL + sub_category_link + f"?count=100&offset={offset}"
            driver.get(url)
            time.sleep(2)  # Wait for the page to load completely
            soup_offset = BeautifulSoup(driver.page_source, "html.parser")
            
            # Find all content links with pattern /t/{id}
            game_links = [a['href'] for a in soup_offset.find_all('a', href=True) if re.match(r'^/t/\d+$', a['href'])]

            if not game_links:
                logging.info(f"No more content found at {url}.")
                break

            # For each game link, find the direct download link
            for game_link in game_links:
                game_url = BASE_URL + game_link
                driver.get(game_url)
                time.sleep(2)  # Wait for the page to load completely
                soup_game = BeautifulSoup(driver.page_source, "html.parser")

                # Find the direct download link
                direct_download_element = soup_game.find('a', string='Direct Download')
                if direct_download_element and direct_download_element['href']:
                    download_url = direct_download_element['href']
                    # Do not print the URL, just download
                    download_game(driver, download_url, download_path, speed_limit=speed_limit_glob)
                    #download_game(driver, download_url, download_path, speed_limit=None)
                else:
                    logging.warning(f"Direct download link not found for a game.")

            if len(game_links) < 100:
                break

            offset += 100

def download_game(driver, url, download_path, speed_limit=None):
    """
    Download a single game and save it to disk.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        url (str): URL of the game to download.
        download_path (str): The directory path to save the downloaded game.
    """
    try:
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:

            

            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=\"(.+)\"", content_disposition)[0]
            else:
                filename = url.split('/')[-1]

            game_id = url.split('/')[-1].split('?')[0]
            filename = sanitize_filename(filename)
            filename = html_decode(filename)

            filename_parts = filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}.[hID-{game_id}].{filename_parts[1]}"

            full_final_path = os.path.join(download_path, filename)
            tempfilename = f"{filename}.part"
            full_temp_path = os.path.join(download_path, tempfilename)

            total_length = int(response.headers.get('content-length', 0))

            if os.path.exists(full_final_path) and os.path.getsize(full_final_path) == total_length:
                logging.info(f"{filename} already downloaded and matches the expected size.")
                return
            chunk_size = 4096
            if speed_limit:
                chunk_time = chunk_size / speed_limit
            with open(full_temp_path, 'wb') as f, tqdm(
                total=total_length,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"{filename} ({total_length/1024/1024:.2f} MB)"
            ) as bar:
                start_time = time.time()
                for data in response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    bar.update(len(data))
                    if speed_limit:
                        elapsed = time.time() - start_time
                        if elapsed < chunk_time:
                            sleep(chunk_time - elapsed)
                        start_time = time.time()

            os.rename(full_temp_path, full_final_path)
        else:
            logging.warning(f"Failed to download from {url}")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while downloading the game: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        get_games()
    except KeyboardInterrupt:
        logging.info("Download interrupted by user. Exiting...")
        exit(0)