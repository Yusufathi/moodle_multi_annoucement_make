import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Set up logging
logging.basicConfig(filename="moodle_announcement_log.txt", level=logging.INFO,
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

# Function to check if the attachments folder is empty or contains files


def get_attachments(attachments_dir):
    try:
        # Get list of files in attachments folder
        files = os.listdir(attachments_dir)
        if len(files) == 0:
            logging.info("No attachments found. Skipping attachments.")
            return []
        else:
            # Convert to absolute paths
            logging.info(f"Attachments found: {files}")
            # Return absolute paths
            return [os.path.abspath(os.path.join(attachments_dir, f)) for f in files]
    except FileNotFoundError:
        logging.error(f"Attachments folder '{attachments_dir}' not found.")
        return []


# Read links from input/links.txt
links_file = "input/links.txt"
FORUM_URLS = read_lines(links_file)
print("Forum URLs loaded:", FORUM_URLS)

# Read subject from input/subject.txt
subject_file = "input/subject.txt"
ANNOUNCEMENT_SUBJECT = read_file(subject_file)
print("Announcement Subject:", ANNOUNCEMENT_SUBJECT)

# Read message from input/message.txt
message_file = "input/message.txt"
ANNOUNCEMENT_MESSAGE = read_file(message_file)
print("Announcement Message:", ANNOUNCEMENT_MESSAGE)

# Get attachments from input/attachments/ folder
attachments_dir = "input/attachments"
attachments = get_attachments(attachments_dir)
print("Attachments:", attachments)

# Check if subject and message were read correctly
if not FORUM_URLS:
    logging.error("No URLs found in links.txt. Exiting script.")
    print("No URLs found in links.txt. Exiting script.")
    exit()

if not ANNOUNCEMENT_SUBJECT or not ANNOUNCEMENT_MESSAGE:
    logging.error("Subject or message is missing. Exiting script.")
    print("Subject or message is missing. Exiting script.")
    exit()

# Set up WebDriver to use the local Chromedriver with Service object
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Open Moodle and wait for manual login
driver.get("https://moodle.nu.edu.eg/")
input("Press Enter after you have logged in manually...")
logging.info("User logged in manually.")
print("User logged in manually.")

# Loop through each forum URL to post the announcement
for forum_url in FORUM_URLS:
    print(f"Navigating to forum URL: {forum_url}")
    driver.get(forum_url)
    time.sleep(3)

    # Try to locate the "Add discussion topic" button by class
    try:
        new_announcement_btn = driver.find_element(
            By.CSS_SELECTOR, "a.btn.btn-primary")
        new_announcement_btn.click()
        logging.info(f"Clicked 'Add discussion topic' on forum: {forum_url}")
        print(f"Clicked 'Add discussion topic' on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find 'Add discussion topic' button on forum: {forum_url} - Error: {e}")
        print(
            f"Failed to find 'Add discussion topic' button on forum: {forum_url} - Error: {e}")
        continue

    # Wait for the new announcement form to load
    time.sleep(3)

    # Enter the subject
    try:
        subject_input = driver.find_element(By.ID, "id_subject")
        subject_input.send_keys(ANNOUNCEMENT_SUBJECT)
        logging.info(f"Entered subject on forum: {forum_url}")
        print(f"Entered subject on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the subject input on forum: {forum_url} - Error: {e}")
        print(
            f"Failed to find the subject input on forum: {forum_url} - Error: {e}")
        continue

    # Enter the message into the contenteditable div
    try:
        message_input = driver.find_element(By.ID, "id_messageeditable")
        message_input.clear()  # Clear if needed
        # Type the announcement message
        message_input.send_keys(ANNOUNCEMENT_MESSAGE)
        logging.info(f"Entered message on forum: {forum_url}")
        print(f"Entered message on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the message input on forum: {forum_url} - Error: {e}")
        print(
            f"Failed to find the message input on forum: {forum_url} - Error: {e}")
        continue

    # Upload attachments (if there are any)
    if attachments:
        try:
            # Click the "Advanced" button using its ID
            advanced_button = driver.find_element(
                By.ID, "id_advancedadddiscussion")
            advanced_button.click()
            logging.info("Clicked the 'Advanced' button.")
            print("Clicked the 'Advanced' button.")

            time.sleep(3)  # Wait for the advanced form to load

            # Click on the "Add file" button (identified by the icon)
            add_file_button = driver.find_element(
                By.CSS_SELECTOR, 'i.fa-file-o')
            add_file_button.click()
            logging.info("Clicked the 'Add file' button.")
            print("Clicked the 'Add file' button.")

            time.sleep(2)  # Wait for the file picker to open

            # Upload each attachment
            for attachment in attachments:
                file_upload_element = driver.find_element(
                    By.CSS_SELECTOR, 'input[name="repo_upload_file"]')
                file_upload_element.send_keys(attachment)
                logging.info(f"Selected file: {attachment}")
                print(f"Selected file: {attachment}")

            # Click the "Upload this file" button
            upload_button = driver.find_element(
                By.CSS_SELECTOR, 'button.fp-upload-btn')
            upload_button.click()
            logging.info("Clicked 'Upload this file'.")
            print("Clicked 'Upload this file'.")

        except Exception as e:
            logging.error(
                f"Failed to upload attachment(s) on forum: {forum_url} - Error: {e}")
            print(
                f"Failed to upload attachment(s) on forum: {forum_url} - Error: {e}")

    # Scroll down and submit the form
    try:
        # Wait for the lightbox overlay to disappear before clicking the "Post to forum" button
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element(
                (By.CSS_SELECTOR, 'div.yui3-widget-mask'))
        )

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        submit_button = driver.find_element(By.ID, "id_submitbutton")
        submit_button.click()
        logging.info(f"Submitted the form on forum: {forum_url}")
        print(f"Submitted the form on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to submit the form on forum: {forum_url} - Error: {e}")
        print(f"Failed to submit the form on forum: {forum_url} - Error: {e}")
        continue

    # Wait for the announcement to be posted
    time.sleep(5)
    logging.info(f"Announcement posted successfully on forum: {forum_url}")
    print(f"Announcement posted successfully on forum: {forum_url}")

# Close the browser once all announcements are posted
driver.quit()
logging.info("Browser closed. Script completed.")
print("Browser closed. Script completed.")
