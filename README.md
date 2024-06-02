# hShop Downloader

## Overview
https://github.com/Ghost0159/hShop-downloader/assets/66320002/1f61a252-d788-4f8d-8aaf-d89166e244e8

The **hShop Downloader** is a Python script designed to facilitate the downloading of games from the hShop website. It focuses on various categories such as games, updates, DLC, virtual console, DSiWare, videos, extras, and themes. The script employs web scraping techniques to gather information and provides a straightforward interface for downloading content directly to your local machine.

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

2. **Threaded Downloads:** To enhance performance, the script uses multiple threads to download games concurrently. This allows for faster retrieval of content.

3. **HTML Decoding:** The `html_decode` function handles HTML-encoded characters in filenames, ensuring accurate and readable file names.

4. **Download Progress:** The script displays a progress bar using `tqdm` to provide real-time feedback on the download process.

5. **Organized Directories:** The downloaded content is organized into directories based on their respective categories. Each item is stored in a dedicated folder for ease of access.

#### Technical Details
- **Web Scraping:** The script sends HTTP requests to the hShop website and parses the HTML response using BeautifulSoup. It then extracts relevant information such as download links and file names using regular expressions.
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

Install the required Python packages using:

```bash
pip install requests beautifulsoup4 tqdm
```

## Usage
1. Clone this repository:
```bash
git clone --recursive https://github.com/Ghost0159/hShop-downloader/
```
2. Open the `hshop_downloader.py` file.
3. Update the URL in the `get_games` function with the desired category URL (e.g., for DLC, use `baseurl+"/c/dlc"`).
4. Run the script:
```bash
python hshop_downloader.py
```

## Additional Functionality
The script can be extended and enhanced in several ways:

1. **User Interface:** Develop a graphical user interface (GUI) for a more user-friendly experience.

2. **Configuration File:** Implement a configuration file for easier customization of settings, such as the download directory and thread count.

3. **Error Handling:** Enhance error handling to gracefully manage unexpected scenarios during the download process.

4. **Logging:** Integrate a logging mechanism to keep track of download activities and any potential issues.

5. **Pause and Resume:** Add functionality to pause and resume downloads, especially useful for large files or intermittent internet connections.


## Credits
This script was developed by [Ghost0159](https://github.com/Ghost0159/).
Special thanks to [Léon Le Breton](https://github.com/LeonLeBreton).

## License
This project is licensed under the GNU General Public License Version 3.0. See the [LICENSE](LICENSE) file for details.

## Disclaimer
This script is intended for educational and personal use only. The act of web scraping may be subject to legal and ethical considerations, and it is important to ensure compliance with the relevant terms of service and policies of the website being scraped.

Downloading copyrighted material without proper authorization may infringe upon intellectual property rights and violate applicable laws. Users are solely responsible for their actions while using this script, and the developer assumes no liability for any misuse or unlawful activity.

It is crucial to emphasize that this script should only be used to download games that the user owns and has legally purchased. It is not intended to facilitate piracy or unauthorized distribution of copyrighted content. The developer strongly encourages users to respect intellectual property rights and only download games for which they have legitimate ownership.

By using this script, you agree to use it responsibly and in accordance with applicable laws and regulations. It is provided solely for educational purposes and to satisfy curiosity.
