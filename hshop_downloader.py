import os
import re
import requests
import urllib.parse
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

baseurl = "https://hshop.erista.me"

# Options for configuring Selenium
def get_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    return chrome_options

def get_main_categories(driver):
    driver.get(baseurl)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    categories = soup.find_all("a", href=re.compile(r'^/c/'))
    return categories

def sanitize_filename(filename):
    return re.sub(r'[<>:\"/\\|?*\x00-\x1F]', '', filename)

def get_games():
    options = get_chrome_options()
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        categories = get_main_categories(driver)
        print("Select main categories (comma separated, '*' for all):")
        for i, category in enumerate(categories, start=1):
            print(f"{i}. {category.text.strip()}")
        selections = input("Enter your selections: ")

        if selections.strip() == '*':
            selected_categories = categories
        else:
            selected_categories = []
            for selection in selections.split(','):
                selection = selection.strip()
                if not selection.isdigit() or int(selection) not in range(1, len(categories) + 1):
                    print(f"Invalid selection '{selection}', please try again. Example: 1,2,3")
                    return
                selected_categories.append(categories[int(selection) - 1])

        for selected_category in selected_categories:
            category_url = baseurl + selected_category['href']
            download_games_in_category(driver, category_url)

    finally:
        driver.quit()

def download_games_in_category(driver, category_url):
    driver.get(category_url)
    soupRegion = BeautifulSoup(driver.page_source, "html.parser")
    region = soupRegion.find("div", class_="list pre-top")
    regex = re.findall(r'href="([^"]+)', str(region))
    nom = region.find_all("h3", class_="green bold")
    region = ([i.text for i in nom])

    sub_categories = {}
    for i, j in zip(regex, region):
        if "/s/" in i:
            sub_categories[j] = i

    print(f"Select subcategories for {category_url.replace(baseurl + '/c/', '')} (comma separated, '*' for all):")
    sub_category_list = list(sub_categories.items())
    for i, (name, url) in enumerate(sub_category_list, start=1):
        print(f"{i}. {name}")
    selections = input("Enter your selections: ")

    if selections.strip() == '*':
        selected_sub_categories = sub_category_list
    else:
        selected_sub_categories = []
        for selection in selections.split(','):
            selection = selection.strip()
            if not selection.isdigit() or int(selection) not in range(1, len(sub_category_list) + 1):
                print(f"Invalid selection '{selection}', please try again. Example: 1,2,3")
                return
            selected_sub_category_name, selected_sub_category = sub_category_list[int(selection) - 1]
            selected_sub_categories.append((selected_sub_category_name, selected_sub_category))

    for selected_sub_category_name, selected_sub_category in selected_sub_categories:
        download_path = f"./downloads/{category_url.replace(baseurl + '/c/', '')}/{sanitize_filename(selected_sub_category_name)}"
        os.makedirs(download_path, exist_ok=True)

        offset = 0
        while True:
            url = baseurl + selected_sub_category + f"?count=100&offset={offset}"
            driver.get(url)
            soupOffset = BeautifulSoup(driver.page_source, "html.parser")
            content = soupOffset.find("div", class_="list pre-top")
            game_list = re.findall(r'href="([^"]+)', str(content))

            if not game_list:
                break

            download(driver, game_list, download_path)

            if len(game_list) < 100:
                break

            offset += 100

def download(driver, urls, download_path):
    for url in urls:
        download_game(driver, baseurl + url, download_path)

def download_game(driver, url, download_path):
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
            if content_disposition and 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].split(';')[0].strip('\"')
            else:
                filename = f"{game_id}.bin"
            
            filename = sanitize_filename(filename)
            filename = html_decode(filename)
            
            # Append hID to the filename
            filename_parts = filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}.[hID-{game_id}].{filename_parts[1]}"
            
            full_final_path = os.path.join(download_path, filename)
            tempfilename = f"{filename}.part"
            full_temp_path = os.path.join(download_path, tempfilename)
            
            total_length = int(response.headers.get('content-length', 0))
            
            if os.path.exists(full_final_path) and os.path.getsize(full_final_path) == total_length:
                print(f"{filename} already downloaded and matches the expected size.")
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
            print("Direct download link not found for", url)

    except requests.exceptions.RequestException as e:
        print("An error occurred while downloading the game:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

def html_decode(filename):
    filename = filename.replace('%3A', ':')
    filename = filename.replace('%2F', '/')
    filename = filename.replace('%2C', ',')
    filename = filename.replace('%5F', '_')
    filename = filename.replace('%28', '(')
    filename = filename.replace('%29', ')')
    filename = filename.replace("'", '')
    return filename

if __name__ == "__main__":
    try:
        get_games()
    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Exiting...")
        exit(0)