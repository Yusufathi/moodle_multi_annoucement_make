import logging
import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(filename="logs/moodle_topic_content_uploader_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')


def read_file(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return None


def read_lines(file_path):
    """Read multiple lines from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []


def get_content_files(content_dir):
    """Get all content files from a directory."""
    try:
        files = os.listdir(content_dir)
        if not files:
            logging.info("No content found. Skipping content upload.")
            return []
        return [os.path.abspath(os.path.join(content_dir, f)) for f in files]
    except FileNotFoundError:
        logging.error(f"Content folder '{content_dir}' not found.")
        return []


def login_to_moodle(driver):
    """Open Moodle and prompt user to log in manually."""
    driver.get("https://moodle.nu.edu.eg/")
    input("Please log in to Moodle, then press Enter to continue...")
    logging.info("User logged in manually.")
    print("User logged in manually.")


def enable_edit_mode(driver, course_url):
    """Enable edit mode in Moodle if not already enabled."""
    try:
        start_time = time.time()
        driver.get(course_url)
        time.sleep(3)
        edit_mode_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='checkbox' and contains(@id, 'editingswitch')]"))
        )
        if not edit_mode_checkbox.is_selected():
            edit_mode_checkbox.click()
            logging.info(f"Enabled edit mode on course: {course_url}")
            print(
                f"Enabled edit mode on course: {course_url} (Time taken: {time.time() - start_time:.2f} seconds)")
        else:
            logging.info(f"Edit mode already enabled on course: {course_url}")
            print(
                f"Edit mode already enabled on course: {course_url} (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to enable edit mode on course: {course_url} - Error: {e}")


def add_section(driver, course_url):
    """Add a new section and rename it using pyautogui."""
    try:
        start_time = time.time()
        add_section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.add-section"))
        )
        add_section_button.click()
        logging.info(f"Clicked 'Add section' button on course: {course_url}")
        time.sleep(3)

        # Rename the last section
        edit_section_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[@title='Edit section name']"))
        )
        last_edit_section_link = edit_section_links[-1]
        last_edit_section_link.click()
        logging.info(
            f"Clicked 'Edit section name' on the last section of course: {course_url}")

        time.sleep(2)
        pyautogui.write(TOPIC_NAME, interval=0.05)
        pyautogui.press('enter')
        logging.info(
            f"Renamed last section to '{TOPIC_NAME}' on course: {course_url}")
        print(
            f"Renamed section to '{TOPIC_NAME}' (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to create or rename section on course: {course_url} - Error: {e}")


def click_add_activity_or_resource(driver, course_url):
    """Click 'Add an activity or resource' in the last section."""
    try:
        start_time = time.time()
        add_content_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[@data-action='open-chooser']"))
        )
        last_add_content_button = add_content_buttons[-1]
        last_add_content_button.click()
        logging.info(
            f"Clicked 'Add an activity or resource' on the last section of course: {course_url}")
        time.sleep(2)
        print(
            f"Clicked 'Add an activity or resource' (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to click 'Add an activity or resource' on course: {course_url} - Error: {e}")


def add_folder_activity(driver, course_url):
    """Add a folder activity in the last section."""
    try:
        start_time = time.time()
        folder_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'modicon_folder')]"))
        )
        folder_option.click()
        logging.info(f"Clicked 'Add Folder' on course: {course_url}")
        time.sleep(3)
        print(
            f"Clicked 'Add Folder' option (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to click 'Add Folder' on course: {course_url} - Error: {e}")


def enter_folder_name(driver, course_url, folder_name):
    """Enter the name of the folder to be created."""
    try:
        start_time = time.time()
        folder_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_name"))
        )
        folder_name_input.send_keys(folder_name)
        logging.info(
            f"Entered folder name '{folder_name}' on course: {course_url}")
        print(
            f"Entered folder name '{folder_name}' (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to enter folder name on course: {course_url} - Error: {e}")


def upload_files(driver, content_files, course_url):
    """Upload files one by one with proper waiting."""
    for content in content_files:
        try:
            start_time = time.time()
            logging.info(f"Attempting to upload content: {content}")
            print(f"Attempting to upload content: {content}")

            # Click "Add..." button
            add_file_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.btn.btn-secondary"))
            )
            add_file_button.click()
            logging.info("Clicked 'Add...' button to open file upload dialog")
            print(
                f"Clicked 'Add...' button to open file upload dialog (Time taken: {time.time() - start_time:.2f} seconds)")

            # Wait for the file input to appear
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="file"]'))
            )
            file_input.send_keys(content)  # Send the file path
            logging.info(f"Uploaded content: {content}")
            print(
                f"Uploaded content: {content} (Time taken: {time.time() - start_time:.2f} seconds)")

            # Wait for the file to finish uploading
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "dndupload-uploadinprogress"))
            )
            logging.info(f"File upload finished: {content}")
            print(
                f"File upload finished: {content} (Time taken: {time.time() - start_time:.2f} seconds)")

            # Click "Upload this file" button
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button.fp-upload-btn'))
            )
            upload_button.click()
            logging.info(
                f"Clicked 'Upload this file' for {content} on course: {course_url}")
            print(
                f"Clicked 'Upload this file' for {content} on course: {course_url} (Time taken: {time.time() - start_time:.2f} seconds)")

            # Wait for the upload process to fully complete and ensure the dialog is closed
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "yui3-widget-mask"))
            )
            logging.info(f"Upload dialog closed for {content}")
            print(
                f"Upload dialog closed for {content} (Time taken: {time.time() - start_time:.2f} seconds)")

            # Now that the file is uploaded, wait for the "Add..." button to reappear for the next file
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.btn.btn-secondary"))
            )
            logging.info("Preparing for next file upload (if any)")
            print("Preparing for next file upload (if any)")
            time.sleep(2)  # Give UI time to reset

        except Exception as e:
            logging.error(
                f"Failed to upload content on course: {course_url} - Error: {e}")
            print(
                f"Failed to upload content on course: {course_url} - Error: {e}")
            continue


def save_and_return_to_course(driver, course_url):
    """Save the folder and return to the course page."""
    try:
        start_time = time.time()
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_submitbutton2"))
        )
        save_button.click()
        logging.info(
            f"Saved folder and returned to course on course: {course_url}")
        print(
            f"Saved folder and returned to course (Time taken: {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        logging.error(
            f"Failed to save folder on course: {course_url} - Error: {e}")


def process_course(driver, course_url, create_new_section, folder_name, content_files):
    """Process each course by uploading content."""
    enable_edit_mode(driver, course_url)

    if create_new_section:
        add_section(driver, course_url)

    click_add_activity_or_resource(driver, course_url)
    add_folder_activity(driver, course_url)
    enter_folder_name(driver, course_url, folder_name)
    upload_files(driver, content_files, course_url)
    save_and_return_to_course(driver, course_url)


def main():
    """Main function to execute the script."""
    CREATE_NEW_SECTION = True  # Set this to True if you want to create a new section

    # File paths
    course_links_file = "section/links.txt"
    topic_name_file = "section/name.txt"
    folder_name_file = "section/folder_name.txt"
    content_dir = "section/content"

    # Read data from files
    COURSE_LINKS = read_lines(course_links_file)
    global TOPIC_NAME
    TOPIC_NAME = read_file(topic_name_file)
    FOLDER_NAME = read_file(folder_name_file)
    content_files = get_content_files(content_dir)

    # Ensure required data is present
    if not COURSE_LINKS or not TOPIC_NAME or not FOLDER_NAME or not content_files:
        logging.error("Missing required data. Please check your input files.")
        print("Missing required data. Please check your input files.")
        return

    # Set up WebDriver
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Log in to Moodle
    login_to_moodle(driver)

    # Process each course link
    for course_url in COURSE_LINKS:
        process_course(driver, course_url, CREATE_NEW_SECTION,
                       FOLDER_NAME, content_files)

    # Close the browser once all content is uploaded
    driver.quit()
    logging.info("Browser closed. Script completed.")
    print("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
