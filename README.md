
# Moodle Automation Scripts

## Overview

This repository contains scripts that automate various tasks on the Moodle platform. These tasks include:

1. **Section Uploader** - Automates the process of creating sections and uploading content to Moodle courses.
2. **Announcement Poster** - Automates the process of posting announcements to Moodle forums.
3. **Gradebook Setup** - Automates the process of setting up a gradebook, including adding categories and grade items.
4. Chromedriver link : <https://googlechromelabs.github.io/chrome-for-testing/>

---

## Script 1: Section Uploader (`section_uploader.py`)

### Description

This script automates the creation of sections and the uploading of content to Moodle courses. It reads the course links, section names, and content from a predefined folder structure, and creates sections in the course with the corresponding content.

### Folder Structure

```
section/
    links.txt         # Contains Moodle course links
    name.txt          # Contains the name of the section
    folder_name.txt   # Contains the folder name to be created
    content/          # Contains the content files to be uploaded
```

### Usage

1. Ensure that the required files and folder structure are in place.
2. Run the script, log in manually when prompted, and let the script automate the rest.

---

## Script 2: Announcement Poster (`announcer.py`)

### Description

This script automates the process of posting announcements to Moodle forums. It reads the forum links, subject, message, and attachments from predefined files, and posts the announcement to each forum.

### Folder Structure

```
input/
    links.txt      # Contains Moodle forum links
    subject.txt    # Contains the subject of the announcement
    message.txt    # Contains the body of the announcement
    attachments/   # Contains files to be uploaded as attachments
```

### Usage

1. Ensure that the required files and folder structure are in place.
2. Run the script, log in manually when prompted, and let the script automate the announcement posting process.

---

## Script 3: Gradebook Setup (`grade_book_setup.py`)

### Description

This script automates the process of setting up the gradebook for Moodle courses. It creates categories and grade items based on the structure provided in a JSON file.

### Folder Structure

```
grade_book/
    links.txt      # Contains Moodle course links
    gradebook.json # Contains the structure of the gradebook (categories, items, weights)
```

### JSON Structure Example

```json
{
    "Lectures": 5,
    "Tutorials": {
        "weight": 15,
        "Week1": 10,
        "Week2": 10
    },
    "Labs": {
        "weight": 15,
        "Lab1": 10,
        "Lab2": 10
    },
    "Quizzes": {
        "weight": 5,
        "Quiz1": 10
    },
    "Midterm": 10,
    "Final": 25
}
```

### Usage

1. Ensure that the required files and folder structure are in place.
2. Run the script, log in manually when prompted, and let the script automate the gradebook setup process.

---

## Logs

Each script generates logs that are stored in the `logs/` directory. These logs are useful for tracking the automation process and debugging issues.

---

## Requirements

- Python 3.x
- Selenium WebDriver
- Google Chrome
- Chromedriver (Ensure it's in the root directory of the project)

---

## Installation

1. Clone the repository.
2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Download and place the appropriate version of Chromedriver in the root directory.
4. Run the desired script by executing:

   ```
   python <script_name.py>
   ```

---

## License

This project is licensed under the MIT License.
