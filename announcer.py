import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(filename="logs/moodle_announcement_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')


def read_file(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return content
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return None


def read_lines(file_path):
    """Reads multiple lines from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
            return [line.strip() for line in content]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []


def get_attachments(attachments_dir):
    """Returns a list of attachments from a directory."""
    try:
        files = os.listdir(attachments_dir)
        if not files:
            logging.info("No attachments found. Skipping attachments.")
            return []
        logging.info(f"Attachments found: {files}")
        return [os.path.abspath(os.path.join(attachments_dir, f)) for f in files]
    except FileNotFoundError:
        logging.error(f"Attachments folder '{attachments_dir}' not found.")
        return []


def log_in_to_moodle(driver):
    """Logs in to Moodle manually."""
    driver.get("https://moodle.nu.edu.eg/")
    input("Press Enter after you have logged in manually...")
    logging.info("User logged in manually.")


def post_announcement(driver, forum_url, subject, message, attachments):
    """Posts an announcement with attachments on the specified forum."""
    driver.get(forum_url)
    time.sleep(3)

    # Click the 'Add discussion topic' button
    try:
        new_announcement_btn = driver.find_element(
            By.CSS_SELECTOR, "a.btn.btn-primary")
        new_announcement_btn.click()
        logging.info(f"Clicked 'Add discussion topic' on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find 'Add discussion topic' button on forum: {forum_url} - Error: {e}")
        return

    time.sleep(3)  # Wait for the form to load

    # Enter the subject
    try:
        subject_input = driver.find_element(By.ID, "id_subject")
        subject_input.send_keys(subject)
        logging.info(f"Entered subject on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the subject input on forum: {forum_url} - Error: {e}")
        return

    # Enter the message
    try:
        message_input = driver.find_element(By.ID, "id_messageeditable")
        message_input.clear()
        message_input.send_keys(message)
        logging.info(f"Entered message on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the message input on forum: {forum_url} - Error: {e}")
        return

    # Handle attachments(if any)
    if attachments:
        upload_attachments(driver, attachments)

    # Scroll to the submit button and ensure it's clickable
    try:
        # Scroll the page to the submit button
        submit_button = driver.find_element(By.ID, "id_submitbutton")
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(2)  # Let the scroll action take effect

        # Ensure no modal or overlay is blocking the click
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_submitbutton"))
        )

        # Use JavaScript to click the submit button if regular click fails
        driver.execute_script("arguments[0].click();", submit_button)
        logging.info(f"Submitted the form on forum: {forum_url}")
        print(f"Submitted the form on forum: {forum_url}")

    except Exception as e:
        logging.error(
            f"Failed to submit the form on forum: {forum_url} - Error: {e}")
        print(f"Failed to submit the form on forum: {forum_url} - Error: {e}")


def upload_attachments(driver, attachments):
    """Uploads attachments one by one, ensuring each is uploaded before proceeding."""
    try:
        # Click the "Advanced" button
        advanced_button = driver.find_element(
            By.ID, "id_advancedadddiscussion")
        advanced_button.click()
        logging.info("Clicked the 'Advanced' button.")
        time.sleep(3)

        # Loop through each attachment
        for attachment in attachments:
            try:
                # Open the file upload dialog
                add_file_button = driver.find_element(
                    By.CSS_SELECTOR, 'i.fa-file-o')
                add_file_button.click()
                logging.info("Clicked the 'Add file' button.")
                time.sleep(2)

                # Find the file input element and send the file path
                file_upload_element = driver.find_element(
                    By.CSS_SELECTOR, 'input[name="repo_upload_file"]')
                file_upload_element.send_keys(attachment)
                logging.info(f"Selected file: {attachment}")

                # Click the "Upload this file" button
                upload_button = driver.find_element(
                    By.CSS_SELECTOR, 'button.fp-upload-btn')
                upload_button.click()
                logging.info(f"Clicked 'Upload this file' for {attachment}")

                # Wait for the file to finish uploading
                WebDriverWait(driver, 30).until(
                    EC.invisibility_of_element((By.CSS_SELECTOR, 'div.fp-uploadinprogress')))
                logging.info(f"File upload finished: {attachment}")
                print(f"File upload finished: {attachment}")

                # After each file, reopen the "Add file" button to upload the next one
                time.sleep(2)

            except Exception as e:
                logging.error(
                    f"Failed to upload attachment: {attachment} - Error: {e}")
                continue

    except Exception as e:
        logging.error(f"Failed to upload attachment(s) - Error: {e}")


def main():
    # Read files
    links_file = "input/links.txt"
    subject_file = "input/subject.txt"
    message_file = "input/message.txt"
    attachments_dir = "input/attachments"

    FORUM_URLS = read_lines(links_file)
    ANNOUNCEMENT_SUBJECT = read_file(subject_file)
    ANNOUNCEMENT_MESSAGE = read_file(message_file)
    attachments = get_attachments(attachments_dir)

    if not FORUM_URLS:
        logging.error("No URLs found in links.txt. Exiting script.")
        return

    if not ANNOUNCEMENT_SUBJECT or not ANNOUNCEMENT_MESSAGE:
        logging.error("Subject or message is missing. Exiting script.")
        return

    # Set up WebDriver
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Log in to Moodle manually
    log_in_to_moodle(driver)

    # Loop through each forum URL to post the announcement
    for forum_url in FORUM_URLS:
        post_announcement(driver, forum_url, ANNOUNCEMENT_SUBJECT,
                          ANNOUNCEMENT_MESSAGE, attachments)

    # Close the browser once all announcements are posted
    driver.quit()
    logging.info("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
