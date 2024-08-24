import os
import re
import requests
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configure logging for detailed information and error messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    return re.sub(r'[<>:\"/\\|?*\x00-\x1F]', '', filename)

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
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver:
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
    soup_region = BeautifulSoup(driver.page_source, "html.parser")
    region = soup_region.find("div", class_="list pre-top")
    subcategory_links = re.findall(r'href="([^"]+)', str(region))
    subcategory_names = [i.text for i in region.find_all("h3", class_="green bold")]

    sub_categories = {name: link for link, name in zip(subcategory_links, subcategory_names) if "/s/" in link}

    sub_category_list = list(sub_categories.items())
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
            soup_offset = BeautifulSoup(driver.page_source, "html.parser")
            content = soup_offset.find("div", class_="list pre-top")
            game_list = re.findall(r'href="([^"]+)', str(content))

            if not game_list:
                break

            download(driver, game_list, download_path)

            if len(game_list) < 100:
                break

            offset += 100

def download(driver, urls, download_path):
    """
    Download a list of games.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        urls (list): List of game URLs to download.
        download_path (str): The directory path to save downloaded games.
    """
    for url in urls:
        download_game(driver, BASE_URL + url, download_path)

def download_game(driver, url, download_path):
    """
    Download a single game and save it to disk.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        url (str): URL of the game to download.
        download_path (str): The directory path to save the downloaded game.
    """
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn.btn-c3"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        download_link = soup.find('a', class_='btn btn-c3')
        if download_link:
            download_url = download_link['href']
            response = requests.get(download_url, stream=True)
            
            game_id = url.split('/')[-1]
            content_disposition = response.headers.get('content-disposition')
            filename = (content_disposition.split('filename=')[1].split(';')[0].strip('\"')
                        if content_disposition and 'filename=' in content_disposition
                        else f"{game_id}.bin")
            
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
            
            with open(full_temp_path, 'wb') as f, tqdm(
                total=total_length,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"{filename} ({total_length/1024/1024:.2f} MB)"
            ) as bar:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    bar.update(len(data))

            os.rename(full_temp_path, full_final_path)
        else:
            logging.warning(f"Direct download link not found for {url}")

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