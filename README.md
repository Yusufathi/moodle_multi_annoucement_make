
# Moodle Announcement Automation Script

This script automates posting announcements on multiple Moodle forums using Selenium WebDriver. The script opens the Moodle login page, waits for manual login via Microsoft 365 SSO, and then posts announcements to each forum.

## Features

- Posts a custom subject and message to multiple Moodle forums.
- Supports manual login (you enter your credentials, and the script continues).
- Logs all actions and errors in a log file (`moodle_announcement_log.txt`).
- Reads the announcement subject from `subject.txt` and the message from `message.txt`.

## Prerequisites

- Python 3.x
- Selenium package
- Google Chrome installed
- ChromeDriver (compatible with your version of Chrome)

## Installation

1. **Clone the repository** or download the script files.
2. **Install the required Python packages** using pip:
   ```bash
   pip install selenium
   ```

3. **Download ChromeDriver** and place it in the project root directory. Ensure the version matches your installed Chrome browser version. [Download ChromeDriver](https://sites.google.com/chromium.org/driver/)

4. **Create `subject.txt` and `message.txt` files**:
   - **subject.txt**: The first line of this file should contain the announcement subject.
   - **message.txt**: The entire contents of this file will be treated as the message body. This can span multiple lines.

## Usage

1. **Run the script**:
   ```bash
   python script_name.py
   ```

2. **Manual Login**: The script will open the Moodle login page. You need to log in manually using your Microsoft 365 credentials.
3. **Posting Announcements**: After login, the script will automatically post the specified announcement to the provided Moodle forum URLs.

## Configuration

### Forum URLs
You can add or modify forum URLs in the `FORUM_URLS` list inside the script.

### Announcement Files
The script reads the announcement subject from `subject.txt` and the message from `message.txt`. Ensure these files exist in the same directory as the script.

### Logging

The script logs all activity (successful posts and errors) in `moodle_announcement_log.txt`. Check this file after the script runs to view the results.

## Troubleshooting

- Ensure you have the correct version of ChromeDriver that matches your installed Chrome browser.
- If the script fails to find elements on the page, ensure that the correct CSS selectors or IDs are being used.

## License

This project is licensed under the MIT License.
