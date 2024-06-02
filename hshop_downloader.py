import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import os
import urllib.parse

baseurl = "https://hshop.erista.me"

def get_main_categories():
    home = requests.get(baseurl)
    soup = BeautifulSoup(home.content, "html.parser")
    categories = soup.find_all("a", href=re.compile(r'^/c/'))
    return categories

def get_games():
    # Retrieve main categories
    categories = get_main_categories()

    # Display main categories to select
    print("Select main categories (comma separated, e.g., 1,2,3):")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category.text.strip()}")
    selections = input("Enter your selections: ")

    # Check that the selections are valid
    selected_categories = []
    for selection in selections.split(','):
        selection = selection.strip()
        if not selection.isdigit() or int(selection) not in range(1, len(categories) + 1):
            print(f"Invalid selection '{selection}', please try again. Example: 1,2,3")
            return
        selected_categories.append(categories[int(selection) - 1])

    for selected_category in selected_categories:
        category_url = baseurl + selected_category['href']
        download_games_in_category(category_url)

def download_games_in_category(category_url):
    home = requests.get(category_url)
    soupRegion = BeautifulSoup(home.content.decode('utf-8'), "html.parser")
    region = soupRegion.find("div", class_="list pre-top")
    regex = re.findall(r'href="([^"]+)', str(region))
    nom = region.find_all("h3", class_="green bold")
    region = ([i.text for i in nom])

    # Retrieve the list of subcategories for the selected main category
    sub_categories = {}
    for i, j in zip(regex, region):
        if "/s/" in i:
            sub_categories[j] = i

    # Display a menu to select subcategories
    if sub_categories:
        print(f"Select subcategories for {category_url.replace(baseurl + '/c/', '')} (comma separated, e.g., 1,2,3):")
        sub_category_list = list(sub_categories.items())
        for i, (name, url) in enumerate(sub_category_list, start=1):
            print(f"{i}. {name}")
        selections = input("Enter your selections: ")

        selected_sub_categories = []
        for selection in selections.split(','):
            selection = selection.strip()
            if not selection.isdigit() or int(selection) not in range(1, len(sub_category_list) + 1):
                print(f"Invalid selection '{selection}', please try again. Example: 1,2,3")
                return
            selected_sub_category_name, selected_sub_category = sub_category_list[int(selection) - 1]
            selected_sub_categories.append((selected_sub_category_name, selected_sub_category))
    else:
        selected_sub_categories = [(category_url.replace(baseurl + '/c/', ''), category_url)]

    for selected_sub_category_name, selected_sub_category in selected_sub_categories:
        download_path = f"./downloads/{category_url.replace(baseurl + '/c/', '')}/{selected_sub_category_name}"
        os.makedirs(download_path, exist_ok=True)

        offset = 0
        while True:
            url = baseurl + selected_sub_category + f"?count=100&offset={offset}"
            game_region = requests.get(url)
            soupOffset = BeautifulSoup(game_region.text, "html.parser")
            content = soupOffset.find("div", class_="list pre-top")
            game_list = re.findall(r'href="([^"]+)', str(content))

            if not game_list:
                break

            download(game_list, download_path)

            if len(game_list) < 100:
                break

            offset += 100

def download(urls, download_path):
    for url in urls:
        download_game(baseurl + url, download_path)

def download_game(url, download_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        game = requests.get(url, headers=headers)
        urls = re.findall(r'<a\s+class="btn btn-c3"\s+href="([^"]*)">Direct Download<\/a>', str(game.text))
        if len(urls) > 0:
            url = urls[0]
            response = requests.get(url, stream=True)
            filename = urllib.parse.unquote(response.headers.get('content-disposition').split('"')[-1])
            filename = re.sub(r'[<>:\"/\\\|\?\*]', '', filename)  # Remove invalid characters
            filename = filename.replace('%20', ' ')
            filename = filename.split('; filename=UTF-8')[1]
            if filename.startswith("'"):
                filename = filename[1:]
            filename = html_decode(filename)  # Call the HTML decoding function
            
            # Construct the temporary filename with .part extension
            extension = filename.split('.')[-1]
            tempfilename = filename.replace(f'.{extension}', f'.{extension}.part')
            
            full_temp_path = os.path.join(download_path, tempfilename)
            full_final_path = os.path.join(download_path, filename)
            
            total_length = int(response.headers.get('content-length', 0))
            
            # Check if the file already exists and its size
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
    except requests.exceptions.RequestException as e:
        print("An error occurred while downloading the game:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

def html_decode(filename):
    # Insert your HTML decoding logic here
    filename = filename.replace('%3A', ':')
    filename = filename.replace('%2F', '/')
    filename = filename.replace('%2C', ',')
    filename = filename.replace('%5F', '_')
    filename = filename.replace('%28', '(')
    filename = filename.replace('%29', ')')
    filename = filename.replace("'", '')
    return filename

if __name__ == "__main__":
    get_games()
