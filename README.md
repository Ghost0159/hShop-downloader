# hShop Downloader

## Overview

The **hShop Downloader** is a Python script designed to facilitate the downloading of content from the hShop webSite. It focuses on various categories such as DLC, DSiWare, extras, games, themes, updates, videos, and virtual console. The script employs web scraping techniques to gather information and provides a straightforward interface for downloading content directly to your local machine.

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
1. Open the `hshop_downloader.py` file.
2. Update the URL in the `get_games` function with the desired category URL (e.g., for DLC, use `baseurl+"/c/dlc"`).
3. Run the script:
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
Please be aware that web scraping may be subject to legal and ethical considerations. Ensure compliance with relevant terms of service and policies before using this script.