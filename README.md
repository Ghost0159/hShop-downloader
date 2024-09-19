# hShop Downloader

## Overview
https://github.com/Ghost0159/hShop-downloader/assets/66320002/1f61a252-d788-4f8d-8aaf-d89166e244e8

The **hShop Downloader** is a Python script designed to facilitate the downloading of games and related content from the hShop website. It supports various categories such as games, updates, DLC, virtual console, DSiWare, videos, extras, and themes. The script leverages web scraping techniques to gather information and provides a streamlined interface for downloading content directly to your local machine.

## Features

### Supported Categories

- DLC
- DSiWare
- Extras
- Games
- Themes
- Updates
- Videos
- Virtual Console

### How It Works

1. **Web Scraping:** The script utilizes the `requests` library along with `BeautifulSoup` for web scraping. It extracts relevant information, such as download links and file names, from the hShop website.

2. **Selenium for Dynamic Content:** For web pages that load content dynamically using JavaScript, the script utilizes Selenium to interact with the webpage and retrieve the necessary data.

3. **Threaded Downloads:** To enhance performance, the script uses multiple threads to download games concurrently. This allows for faster retrieval of content.

4. **HTML Decoding:** The `html_decode` function handles HTML-encoded characters in filenames, ensuring accurate and readable file names.

5. **Download Progress:** The script displays a progress bar using `tqdm` to provide real-time feedback on the download process.

6. **Organized Directories:** The downloaded content is organized into directories based on their respective categories. Each item is stored in a dedicated folder for ease of access.

7. **Limiting Download Speed:** The download speed can be limited so you can have it running in the background without it consuming all your network bandwith allowing you to do other activities such as gaming or video streaming.
The limit can be set during the script call:
```
python hshop_downloader.py --speed-limit 1048576  # Sets speed limit to 1 MB/s
```
The speed-limit argument can be omitted to use the full speed of your connection.


#### Technical Details
- **Web Scraping:** The script sends HTTP requests to the hShop website and parses the HTML response using BeautifulSoup. It then extracts relevant information such as download links and file names using regular expressions.
- **Selenium Integration:** For web pages with content that loads dynamically via JavaScript, the script uses Selenium, a powerful browser automation tool, to navigate the site, interact with elements, and extract data. Selenium simulates a real user interacting with the browser, making it ideal for scraping content that isn’t immediately available in the initial HTML response.
- **Threaded Downloads:** The script utilizes Python's ``threading`` module to create multiple threads for downloading games concurrently. This helps in maximizing bandwidth utilization and reducing download times, especially when downloading multiple files.
- **HTML Decoding:** The ``html_decode`` function handles HTML-encoded characters in filenames by replacing percent-encoded characters with their corresponding ASCII characters. This ensures that filenames are correctly decoded and readable.
- **Download Progress:** The script uses ``tqdm``, a Python library for creating progress bars, to display real-time download progress. This gives users visibility into the download process and estimated time remaining.
- **Organized Directories:** The script organizes downloaded content into directories based on their categories. This helps in keeping the downloaded files well-organized and easily accessible.

## Prerequisites

Ensure you have the following dependencies installed:

- Python 3
- `requests`
- `BeautifulSoup`
- `tqdm`
- `Selenium`
- A WebDriver for your browser (e.g., `chromedriver` for Chrome)

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

## Usage
1. **Clone this repository:**
```bash
git clone https://github.com/Ghost0159/hShop-downloader/
```
2. **Navigate to the project directory:**
```bash
cd hShop-downloader
```
3. **Run the Script:**
Execute the script with the following command:
```bash
python hshop_downloader.py
```
4. **Follow the On-Screen Instructions:**
    - After running the script, you will be prompted to select the main categories from which you want to download games. Enter the numbers corresponding to your desired categories, separated by commas, or type `*` to select all.
    - Next, you will choose the subcategories of the games you want to download using a similar selection process.
    - The files will be downloaded and organized into directories based on the categories you selected.
    

## Additional Functionality
The script can be extended and enhanced in several ways:

1. **User Interface:** Develop a graphical user interface (GUI) for a more user-friendly experience.

2. **Configuration File:** Implement a configuration file for easier customization of settings, such as the download directory and thread count.

3. **Error Handling:** Enhance error handling to gracefully manage unexpected scenarios during the download process.

4. **Logging:** Integrate a logging mechanism to keep track of download activities and any potential issues.

5. **Pause and Resume:** Add functionality to pause and resume downloads, especially useful for large files or intermittent internet connections.


## Credits
This script was developed by [Ghost0159](https://github.com/Ghost0159/).<br>
Special thanks to [Léon Le Breton](https://github.com/LeonLeBreton) for the help with the first version<br>
and to Kloklojul for the Download Limiter.

## License
This project is licensed under the GNU General Public License Version 3.0. See the [LICENSE](LICENSE) file for details.

## Disclaimer
This script is intended for educational and personal use only. The act of web scraping may be subject to legal and ethical considerations, and it is important to ensure compliance with the relevant terms of service and policies of the website being scraped.

Downloading copyrighted material without proper authorization may infringe upon intellectual property rights and violate applicable laws. Users are solely responsible for their actions while using this script, and the developer assumes no liability for any misuse or unlawful activity.

It is crucial to emphasize that this script should only be used to download games that the user owns and has legally purchased. It is not intended to facilitate piracy or unauthorized distribution of copyrighted content. The developer strongly encourages users to respect intellectual property rights and only download games for which they have legitimate ownership.

By using this script, you agree to use it responsibly and in accordance with applicable laws and regulations. It is provided solely for educational purposes and to satisfy curiosity.
