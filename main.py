import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os


logging.basicConfig(filename="moodle_announcement_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')


FORUM_URLS = [
    "https://moodle.nu.edu.eg/mod/forum/view.php?id=157395",

]


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the entire file content and strip trailing spaces
            content = file.read().strip()
            return content
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return None


subject_file = "subject.txt"
ANNOUNCEMENT_SUBJECT = read_file(subject_file)


message_file = "message.txt"
ANNOUNCEMENT_MESSAGE = read_file(message_file)


if not ANNOUNCEMENT_SUBJECT or not ANNOUNCEMENT_MESSAGE:
    logging.error("Subject or message is missing. Exiting script.")
    exit()

service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.maximize_window()


driver.get("https://moodle.nu.edu.eg/")

input("Press Enter after you have logged in manually...")
logging.info("User logged in manually.")


for forum_url in FORUM_URLS:
    driver.get(forum_url)
    time.sleep(3)

    try:
        new_announcement_btn = driver.find_element(
            By.CSS_SELECTOR, "a.btn.btn-primary")
        new_announcement_btn.click()
        logging.info(f"Clicked 'Add discussion topic' on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find 'Add discussion topic' button on forum: {forum_url} - Error: {e}")
        continue

    time.sleep(3)

    try:
        subject_input = driver.find_element(By.ID, "id_subject")
        subject_input.send_keys(ANNOUNCEMENT_SUBJECT)
        logging.info(f"Entered subject on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the subject input on forum: {forum_url} - Error: {e}")
        continue

    try:
        message_input = driver.find_element(By.ID, "id_messageeditable")
        message_input.clear()  # Clear if needed
        # Type the announcement message
        message_input.send_keys(ANNOUNCEMENT_MESSAGE)
        logging.info(f"Entered message on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to find the message input on forum: {forum_url} - Error: {e}")
        continue

    try:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        submit_button = driver.find_element(By.ID, "id_submitbutton")
        submit_button.click()
        logging.info(f"Submitted the form on forum: {forum_url}")
    except Exception as e:
        logging.error(
            f"Failed to submit the form on forum: {forum_url} - Error: {e}")
        continue

    time.sleep(5)
    logging.info(f"Announcement posted successfully on forum: {forum_url}")


driver.quit()
logging.info("Browser closed. Script completed.")
