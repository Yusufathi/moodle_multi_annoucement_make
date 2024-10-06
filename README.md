
# Moodle Automation Scripts

This repository contains two automation scripts developed for Moodle tasks using Selenium WebDriver. These scripts automate posting announcements on Moodle forums (`announcer.py`) and uploading content to specific sections of Moodle courses (`section_uploader.py`).

## Prerequisites

- Python 3.x
- Selenium (`pip install selenium`)
- Google Chrome
- ChromeDriver (download and ensure it's added to your PATH or specify the path directly in the scripts)

## Usage Instructions

### 1. Moodle Announcement Automation - `announcer.py`

This script automates the process of posting announcements on specified Moodle forums.

#### Configuration

1. Place your forum URLs in the file `input/links.txt`. Each URL should be on a new line.
2. Write the subject of the announcement in `input/subject.txt`.
3. Write the message body of the announcement in `input/message.txt`.
4. Optionally, place any attachments you wish to upload in the `input/attachments/` folder.

#### Execution

Run the script using:

```bash
python announcer.py
```

#### Workflow

1. The script opens Moodle and prompts you to log in manually.
2. After logging in, it iterates through each forum URL provided in `input/links.txt`.
3. It posts the subject and message, and if any attachments exist, it uploads them one by one.

#### Logging

- Log entries, including any errors, are saved in the `moodle_announcement_log.txt` file.

---

### 2. Moodle Section Content Uploader - `section_uploader.py`

This script uploads content to a specified section of a Moodle course, with an option to create a new section if required.

#### Configuration

1. Place your course URLs in the file `section/links.txt`. Each URL should be on a new line.
2. Specify the section name in `section/name.txt` (if creating a new section).
3. Specify the folder name to be created in `section/folder_name.txt`.
4. Place the content files you wish to upload in `section/content/`.

#### Execution

Run the script using:

```bash
python section_uploader.py
```

#### Workflow

1. The script logs you into Moodle manually and navigates to each course URL in `section/links.txt`.
2. It either creates a new section or uploads content to the last section based on your configuration.
3. The content files are uploaded one by one, and after each upload, the script ensures the file upload is complete before proceeding.

#### Logging

- Log entries, including the status of content uploads and any errors, are saved in the `moodle_topic_content_uploader_log.txt` file.

---

### Notes

- Ensure that the structure of the `input/` and `section/` folders is maintained as described.
- For smooth execution, use the latest version of Chrome and ChromeDriver.
