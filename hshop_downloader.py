import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
import os
import html.parser
import urllib.parse

dictionary = {}

baseurl = "https://hshop.erista.me"

def get_games(url):
    # Retrieve the list of main categories
    categories = ["/c/games", "/c/updates", "/c/dlc", "/c/virtual-console", "/c/dsiware", "/c/videos", "/c/extras", "/c/themes"]

    # Display a menu to select a main category
    print("Select a main category:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category.replace('/c/', '').replace('/', ' ').capitalize()}")
    selection = input("Enter your selection: ")

    # Check that the selection is valid
    if not selection.isdigit() or int(selection) not in range(1, len(categories) + 1):
        print("Invalid selection, please try again.")
        return

    # Select the corresponding main category
    selected_category = categories[int(selection) - 1]
    category_url = baseurl + selected_category
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

    # Display a menu to select a subcategory
    if sub_categories:
        print(f"Select a subcategory for {selected_category.replace('/c/', '')}:")
        sub_category_list = list(sub_categories.items())
        for i, (name, url) in enumerate(sub_category_list, start=1):
            print(f"{i}. {name}")
        selection = input("Enter your selection: ")

        if not selection.isdigit() or int(selection) not in range(1, len(sub_category_list) + 1):
            print("Invalid selection, please try again.")
            return

        selected_sub_category = sub_category_list[int(selection) - 1][1]
        url = baseurl + selected_sub_category + "?count=100&offset=0"
    else:
        url = baseurl + f"{selected_category}?count=100&offset=0"

    offset = 0
    while True:
        game_region = requests.get(url)
        soupOffset = BeautifulSoup(game_region.text, "html.parser")
        content = soupOffset.find("div", class_="list pre-top")
        game_list = re.findall(r'href="([^"]+)', str(content))
        download(game_list)
        next_page = soupOffset.find("a", {"class": "next"})
        if next_page is None or offset >= int(next_page.text):
            break
        url = baseurl + next_page["href"]
        offset += 100

def download(urls):
    for url in urls:
        download_game(baseurl + url)

def download_game(url):
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
            last_delimiter_index = filename.rfind(".")
            parts = [filename[:last_delimiter_index], filename[last_delimiter_index + 1:]]
            tempfilename = parts[0] + '~temp.' + parts[-1]
            if not os.path.exists("[" + parts[0].split('/')[-1] + "]"):
                os.makedirs("[" + parts[0].split('/')[-1] + "]")
            with open("[" + parts[0].split('/')[-1] + "]/" + tempfilename, 'wb') as f:
                total_length = response.headers.get('content-length')
                if total_length is None:
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in tqdm(response.iter_content(chunk_size=4096), total=total_length, unit='B',
                                     unit_scale=True):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        print("\r[%s%s]" % ('=' * done, ' ' * (50 - done)), end='')
            os.rename("[" + parts[0].split('/')[-1] + "]/" + tempfilename, "[" + parts[0].split('/')[-1] + "]/" + filename)
        else:
            print("No download link found for game at URL:", url)
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
    get_games(baseurl + "/c/games")
