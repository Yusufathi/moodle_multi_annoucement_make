import logging
import pyautogui  # For keystrokes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Set up logging
logging.basicConfig(filename="moodle_topic_content_uploader_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Path to Chromedriver (local to the project root directory)
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')

# Function to read file content


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the entire file content and strip trailing spaces
            content = file.read().strip()
            return content
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return None

# Function to read multiple lines (used for links.txt)


def read_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()  # Read all lines from file
            return [line.strip() for line in content]  # Return a list of URLs
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []

# Function to check if the content folder is empty or contains files


def get_content(content_dir):
    try:
        # Get list of files in the content folder
        files = os.listdir(content_dir)
        if len(files) == 0:
            logging.info("No content found. Skipping content upload.")
            return []
        else:
            # Convert to absolute paths
            logging.info(f"Content files found: {files}")
            # Return absolute paths
            return [os.path.abspath(os.path.join(content_dir, f)) for f in files]
    except FileNotFoundError:
        logging.error(f"Content folder '{content_dir}' not found.")
        return []


# Read course links from topic/links.txt
course_links_file = "topic/links.txt"
COURSE_LINKS = read_lines(course_links_file)

# Read topic name from topic/name.txt
topic_name_file = "topic/name.txt"
TOPIC_NAME = read_file(topic_name_file)

# Read folder name from topic/folder_name.txt
folder_name_file = "topic/folder_name.txt"
FOLDER_NAME = read_file(folder_name_file)

# Get content files from topic/content/ folder
content_dir = "topic/content"
content_files = get_content(content_dir)

# Check if course links, topic name, and folder name were read correctly
if not COURSE_LINKS:
    logging.error("No course links found in links.txt. Exiting script.")
    print("No course links found in links.txt. Exiting script.")
    exit()

if not TOPIC_NAME:
    logging.error("Topic name is missing. Exiting script.")
    print("Topic name is missing. Exiting script.")
    exit()

if not FOLDER_NAME:
    logging.error("Folder name is missing. Exiting script.")
    print("Folder name is missing. Exiting script.")
    exit()

# Set up WebDriver to use the local Chromedriver with Service object
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Open Moodle and wait for manual login
driver.get("https://moodle.nu.edu.eg/")
# User manually logs in
input("Please log in to Moodle, then press Enter to continue...")
logging.info("User logged in manually.")
print("User logged in manually.")

# Loop through each course URL to enable edit mode, create the topic, and upload content
for course_url in COURSE_LINKS:
    print(f"Navigating to course URL: {course_url}")
    driver.get(course_url)
    time.sleep(3)

    # Enable edit mode if not already enabled
    try:
        edit_mode_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='checkbox' and contains(@id, 'editingswitch')]"))
        )

        if not edit_mode_checkbox.is_selected():
            edit_mode_checkbox.click()  # Enable edit mode by clicking the checkbox
            logging.info(f"Enabled edit mode on course: {course_url}")
            print(f"Enabled edit mode on course: {course_url}")
        else:
            logging.info(f"Edit mode already enabled on course: {course_url}")
            print(f"Edit mode already enabled on course: {course_url}")
    except Exception as e:
        logging.error(
            f"Failed to enable edit mode on course: {course_url} - Error: {e}")
        print(
            f"Failed to enable edit mode on course: {course_url} - Error: {e}")
        continue

    # Click "Add section" button to create a new section
    try:
        add_section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.add-section"))
        )
        add_section_button.click()
        logging.info(f"Clicked 'Add section' button on course: {course_url}")
        print(f"Clicked 'Add section' button on course: {course_url}")
    except Exception as e:
        logging.error(
            f"Failed to click 'Add section' on course: {course_url} - Error: {e}")
        print(
            f"Failed to click 'Add section' on course: {course_url} - Error: {e}")
        continue

    time.sleep(3)  # Wait for the new section to be added

    # Rename the last section using pyautogui for keystrokes
    try:
        # Find all "Edit section name" links and select the last one
        edit_section_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[@title='Edit section name']"))
        )
        # Select the last section
        last_edit_section_link = edit_section_links[-1]
        last_edit_section_link.click()
        logging.info(
            f"Clicked 'Edit section name' on the last section of course: {course_url}")
        print(
            f"Clicked 'Edit section name' on the last section of course: {course_url}")

        # Use pyautogui to send the topic name and press Enter
        time.sleep(2)  # Wait briefly to ensure the input field is focused
        # Type the topic name slowly
        pyautogui.write(TOPIC_NAME, interval=0.05)
        pyautogui.press('enter')  # Press Enter to submit the name change

        logging.info(
            f"Renamed last section to '{TOPIC_NAME}' using pyautogui on course: {course_url}")
        print(
            f"Renamed last section to '{TOPIC_NAME}' using pyautogui on course: {course_url}")

    except Exception as e:
        logging.error(
            f"Failed to rename the last section on course: {course_url} - Error: {e}")
        print(
            f"Failed to rename the last section on course: {course_url} - Error: {e}")
        continue

        # Click "Add an activity or resource" button in the last section
    try:
        add_content_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[@data-action='open-chooser']"))
        )
        last_add_content_button = add_content_buttons[-1]  # Get the last one
        last_add_content_button.click()
        logging.info(
            f"Clicked 'Add an activity or resource' on the last section of course: {course_url}")
        print(
            f"Clicked 'Add an activity or resource' on the last section of course: {course_url}")

        # Wait for the modal window to load
        time.sleep(5)  # Adjust this value if necessary to wait for the modal

        # Click the Folder icon to add a folder
        folder_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'modicon_folder')]"))
        )
        folder_option.click()
        logging.info(f"Clicked 'Add Folder' option on course: {course_url}")
        print(f"Clicked 'Add Folder' option on course: {course_url}")

    except Exception as e:
        logging.error(
            f"Failed to add Folder activity on course: {course_url} - Error: {e}")
        print(
            f"Failed to add Folder activity on course: {course_url} - Error: {e}")
        continue

    # Fill in the folder name
    try:
        folder_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_name"))
        )
        folder_name_input.send_keys(FOLDER_NAME)
        logging.info(
            f"Entered folder name '{FOLDER_NAME}' on course: {course_url}")
        print(f"Entered folder name '{FOLDER_NAME}' on course: {course_url}")

        # Click the "Add..." button to open the file upload dialog
        add_file_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.btn.btn-secondary"))
        )
        add_file_button.click()
        logging.info(
            f"Clicked 'Add...' button to upload files on course: {course_url}")
        print(
            f"Clicked 'Add...' button to upload files on course: {course_url}")

        # Upload files
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[type="file"]'))
        )
        for content in content_files:
            file_input.send_keys(content)  # Send the file path
            logging.info(f"Uploaded content: {content}")
            print(f"Uploaded content: {content}")

            # Click "Upload this file" button
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button.fp-upload-btn'))
            )
            upload_button.click()
            logging.info(f"Clicked 'Upload this file' on course: {course_url}")
            print(f"Clicked 'Upload this file' on course: {course_url}")

    except Exception as e:
        logging.error(
            f"Failed to upload content on course: {course_url} - Error: {e}")
        print(f"Failed to upload content on course: {course_url} - Error: {e}")
        continue

    # Save the folder and return to the course
    try:
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_submitbutton2"))
        )
        save_button.click()
        logging.info(
            f"Saved folder and returned to course on course: {course_url}")
        print(f"Saved folder and returned to course on course: {course_url}")

    except Exception as e:
        logging.error(
            f"Failed to save folder on course: {course_url} - Error: {e}")
        print(f"Failed to save folder on course: {course_url} - Error: {e}")

    # Wait for the action to complete
    time.sleep(5)

# Close the browser once all content is uploaded
driver.quit()
logging.info("Browser closed. Script completed.")
print("Browser closed. Script completed.")
