import requests
from bs4 import BeautifulSoup 
import re
import json
from tqdm import tqdm
import os
import threading
import html.parser
import urllib.parse

dictionnary = {}

baseurl = "https://hshop.erista.me"


def get_games(url):
    home = requests.get(url)
    soupRegion = BeautifulSoup(home.content.decode('utf-8'), "html.parser")
    region = soupRegion.find("div", class_="list pre-top")
    regex = re.findall(r'href="([^"]+)',  str(region))
    nom = region.find_all("h3", class_ = "green bold")
    region = ([i.text for i in nom])
    for i in regex:
        url = baseurl+i+"?count=100&offset=0"
        offset = 0
        game_region = requests.get(url)
        soupOffset = BeautifulSoup(game_region.text, "html.parser")
        contenu = soupOffset.find("div", class_="list pre-top")
        maxoffset = int(contenu.find("div", class_ = "next-container").text.split("of ")[1].split("\n")[0])
        while offset < maxoffset:
            url = baseurl+i+"?count=100&offset="+str(offset)
            game_region = requests.get(url)
            soupGame = BeautifulSoup(game_region.text, "html.parser")
            jeu = soupGame.find("div", class_="list pre-top")
            game_list = re.findall(r'href="([^"]+)',  str(jeu))
            offset+=100
            download(game_list,i)

def download(urls,i):
    threads = [threading.Thread(target=download_game, args=(baseurl+u, i,)) for u in urls]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def download_game(url,i):
    game = requests.get(url)
    urls = re.findall(r'<a\s+class="btn btn-c3"\s+href="([^"]*)">Direct Download<\/a>', str(game.text))
    if len(urls) > 0:
        url = urls[0]
        response = requests.get(url, stream=True)
        filename = urllib.parse.unquote(response.headers.get('content-disposition').split('"')[-1])
        filename = re.sub(r'[<>:\"/\\\|\?\*]', '', filename)  # enlever les caractères invalides
        filename = filename.replace('%20', ' ')
        filename = filename.split('; filename=UTF-8')[1]
        if filename.startswith("'"):
            filename = filename[1:]
        filename = html_decode(filename) # Appel de la fonction de décodage HTML
        index_dernier_delimiteur = filename.rfind(".")
        chaine = [filename[:index_dernier_delimiteur], filename[index_dernier_delimiteur+1:]]
        tempfilename = chaine[0] + '~temp.' + chaine[-1]
        if not os.path.exists("[" + i.split('/')[-1] + "]"):
            os.makedirs("[" + i.split('/')[-1] + "]")
        with open("[" + i.split('/')[-1] + "]/" + tempfilename, 'wb') as f:
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in tqdm(response.iter_content(chunk_size=4096), total=total_length, unit='B', unit_scale=True):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    print("\r[%s%s]" % ('=' * done, ' ' * (50-done)), end='')
        os.rename("[" + i.split('/')[-1] + "]/" + tempfilename, "[" + i.split('/')[-1] + "]/" + filename)
    else:
        print("No download link found for game at URL:", url)

def html_decode(filename):
    # Insérez votre logique de décodage HTML ici
    filename = filename.replace('%3A', ':')
    filename = filename.replace('%2F', '/')
    filename = filename.replace('%2C', ',')
    filename = filename.replace('%5F', '_')
    filename = filename.replace('%28', '(')
    filename = filename.replace('%29', ')')
    filename = filename.replace("'", '')
    return filename

get_games(baseurl+"/c/dlc")