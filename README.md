
# Moodle Multi-Task Automation

This repository holds two Python scripts to automate tasks in Moodle, specifically for announcements and content uploading.

## 1. `announcer.py`
This script automates the process of posting the same announcement across multiple courses on Moodle.

### Features:
- Automatically logs in to Moodle.
- Posts the same announcement to multiple course forums.
- Supports subject and message customization from external files.
- Allows attachment upload if files are present in the designated folder.

### Prerequisites:
- A Moodle account with access to the courses where announcements are to be posted.
- Chrome WebDriver (chromedriver.exe) placed in the root directory.
- Necessary Python packages: `selenium`, `logging`.

### Folder Structure:
- `input/links.txt`: Contains the list of course forum links where announcements are posted (one URL per line).
- `input/subject.txt`: Contains the subject of the announcement.
- `input/message.txt`: Contains the body of the announcement.
- `input/attachments/`: Folder that contains the files to be uploaded as attachments (if any).

### Usage:
1. Ensure all dependencies are installed:
    ```
    pip install selenium
    ```
2. Update `input/links.txt`, `input/subject.txt`, and `input/message.txt` with your content.
3. Place any attachments in the `input/attachments/` folder.
4. Run the script:
    ```
    python announcer.py
    ```
5. Follow the on-screen instructions to manually log in to Moodle.
6. The script will automatically post the announcement to all listed courses.

---

## 2. `section_uploader.py`
This script automates creating a new topic (section) in specific courses and uploading content to that section.

### Features:
- Automatically logs in to Moodle.
- Automatically enables edit mode in the specified courses.
- Adds a new section and renames it based on an external file.
- Creates a folder in the section and uploads content from the specified folder.

### Prerequisites:
- A Moodle account with access to the courses where content is to be uploaded.
- Chrome WebDriver (chromedriver.exe) placed in the root directory.
- Necessary Python packages: `selenium`, `pyautogui`, `logging`.

### Folder Structure:
- `section/links.txt`: Contains the list of course URLs where sections are to be created (one URL per line).
- `section/name.txt`: Contains the name of the new section to be created.
- `section/folder_name.txt`: Contains the name of the folder to be created inside the section.
- `section/content/`: Folder where the content to be uploaded is stored.

### Usage:
1. Ensure all dependencies are installed:
    ```
    pip install selenium pyautogui
    ```
2. Update `section/links.txt`, `section/name.txt`, and `section/folder_name.txt` with your content.
3. Place the content files inside the `section/content/` folder.
4. Run the script:
    ```
    python section_uploader.py
    ```
5. Follow the on-screen instructions to manually log in to Moodle.
6. The script will automatically enable edit mode, create a new section, rename it, and upload the content.

---

### Notes:
- Both scripts require manual login, but once logged in, the automation will handle the rest of the workflow.
- Make sure to use the correct paths for your `chromedriver` and any other resources.
- These scripts are built using Selenium WebDriver, so the Chrome browser and the appropriate WebDriver version are required.

### Requirements:
- Python 3.x
- Chrome browser
- Chrome WebDriver

### Installation:
1. Clone the repository:
    ```
    git clone https://github.com/Yusufathi/moodle_multi_annoucement_make.git
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

### License:
This project is licensed under the MIT License.
