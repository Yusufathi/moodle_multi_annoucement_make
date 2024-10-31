import logging
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(filename="logs/assignment_poster_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')

# Helper functions


def read_json(file_path):
    """Reads and parses JSON configuration file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file '{file_path}' not found.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON file '{file_path}' - {e}")
        return {}


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


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element)


def auto_login(driver, email, password):
    """Logs into Moodle using SSO with email and password."""
    try:
        driver.get("https://moodle.nu.edu.eg/")
        time.sleep(3)

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        email_input.clear()
        email_input.send_keys(email)
        next_button = driver.find_element(By.ID, "idSIButton9")
        js_click(driver, next_button)
        logging.info("Entered email and clicked next for SSO.")

        retries = 3
        for attempt in range(retries):
            try:
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "i0118"))
                )
                password_input.clear()
                password_input.send_keys(password)
                sign_in_button = driver.find_element(By.ID, "idSIButton9")
                js_click(driver, sign_in_button)
                logging.info("Entered password and clicked sign in for SSO.")
                break
            except Exception as e:
                if attempt < retries - 1:
                    logging.warning(
                        f"Retry {attempt + 1} for password entry due to error: {e}")
                    time.sleep(2)
                else:
                    raise e

        stay_signed_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        js_click(driver, stay_signed_in_button)
        logging.info("Clicked 'Yes' for staying signed in.")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(text(), 'Hi,')]"))
        )
        logging.info("Login successful.")
        print("Login successful.")
        return True
    except Exception as e:
        logging.error(f"Login process failed - Error: {e}")
        print(f"Login process failed - Error: {e}")
        return False


def enable_editing_mode(driver):
    """Enables editing mode if it is not already enabled."""
    try:
        # Check if the editing mode checkbox is already enabled
        edit_mode_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name='setmode']"))
        )

        # Check if the checkbox is already checked
        if not edit_mode_checkbox.is_selected():
            # Use JavaScript to click the checkbox
            driver.execute_script("arguments[0].click();", edit_mode_checkbox)
            logging.info("Edit mode enabled.")
            print("Edit mode enabled.")
            time.sleep(3)  # Give Moodle some time to apply the change
        else:
            logging.info("Edit mode is already enabled.")
            print("Edit mode is already enabled.")

    except Exception as e:
        logging.error(f"Failed to enable edit mode - Error: {e}")
        print(f"Failed to enable edit mode - Error: {e}")


def create_assignment(driver, config):
    """Creates an assignment in the course with settings from config."""
    try:
        add_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@data-action='open-chooser']"))
        )
        js_click(driver, add_button)
        logging.info("Clicked 'Add an activity or resource'.")

        assignment_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@title, 'Add a new Assignment')]"))
        )
        js_click(driver, assignment_button)
        logging.info("Selected 'Assignment' from options.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_name"))
        ).send_keys(config["assignment_name"])
        logging.info("Entered assignment name.")

        driver.find_element(By.ID, "id_introeditoreditable").send_keys(
            config["assignment_description"])
        logging.info("Entered assignment description.")

        driver.find_element(By.ID, "id_activityeditoreditable").send_keys(
            config["activity_instructions"])
        logging.info("Entered activity instructions.")

        upload_attachments(driver, get_attachments("assignments/attachments"))

        # Set due date
        select_option(driver, "id_duedate_day", str(config["due_day"]))
        select_option(driver, "id_duedate_month", config["due_month"])
        select_option(driver, "id_duedate_year", str(config["due_year"]))
        select_option(driver, "id_duedate_hour", str(config["due_hour"]))
        select_option(driver, "id_duedate_minute", str(config["due_minute"]))

        # Uncheck grading due date
        grading_due_checkbox = driver.find_element(
            By.ID, "id_gradingduedate_enabled")
        if grading_due_checkbox.is_selected():
            js_click(driver, grading_due_checkbox)
            logging.info("Unchecked grading due date.")

        # Set max number of files and file types
        select_option(driver, "id_maxfiles", str(
            config["maximum_num_of_files"]))
        set_accepted_file_types(driver, config["accepted_file_types"])

        save_button = driver.find_element(By.ID, "id_submitbutton2")
        js_click(driver, save_button)
        logging.info("Saved and returned to course.")
    except Exception as e:
        logging.error(f"Failed to create assignment - Error: {e}")


def upload_attachments(driver, attachments):
    """Uploads attachments one by one."""
    for attachment in attachments:
        try:
            add_file_button = driver.find_element(
                By.CSS_SELECTOR, 'i.fa-file-o')
            js_click(driver, add_file_button)
            file_upload_element = driver.find_element(
                By.CSS_SELECTOR, 'input[name="repo_upload_file"]')
            file_upload_element.send_keys(attachment)
            upload_button = driver.find_element(
                By.CSS_SELECTOR, 'button.fp-upload-btn')
            js_click(driver, upload_button)
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element(
                    (By.CSS_SELECTOR, 'div.fp-uploadinprogress'))
            )
            logging.info(f"File upload finished: {attachment}")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to upload attachment: {
                          attachment} - Error: {e}")


def select_option(driver, element_id, value_text):
    """Selects an option by visible text."""
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        for option in select_element.find_elements(By.TAG_NAME, "option"):
            if option.text == value_text:
                option.click()
                logging.info(f"Selected option '{
                             value_text}' for element '{element_id}'.")
                break
    except Exception as e:
        logging.error(f"Failed to select option '{
                      value_text}' for element '{element_id}' - Error: {e}")


def set_accepted_file_types(driver, file_type):
    """Sets the accepted file types for assignment submissions."""
    try:
        choose_button = driver.find_element(
            By.CSS_SELECTOR, 'input[data-filetypeswidget="browsertrigger"]')
        js_click(driver, choose_button)
        time.sleep(2)
        file_type_checkbox = driver.find_element(
            By.XPATH, f"//strong[text()='{file_type}']/preceding-sibling::input")
        if not file_type_checkbox.is_selected():
            js_click(driver, file_type_checkbox)
        save_button = driver.find_element(
            By.XPATH, "//button[@data-action='save']")
        js_click(driver, save_button)
        logging.info(f"Selected accepted file type: {file_type}")
    except Exception as e:
        logging.error(f"Failed to set accepted file type '{
                      file_type}' - Error: {e}")


def main():
    config_file = "assignments/conf.json"
    config = read_json(config_file)
    if not config:
        logging.error("No valid configuration found. Exiting script.")
        return

    try:
        # Read credentials from creds.txt in "key:value" format
        with open('creds.txt', 'r') as creds_file:
            creds = {}
            for line in creds_file:
                key, value = line.strip().split(':')
                creds[key.strip()] = value.strip()
            email = creds.get("email")
            password = creds.get("password")

            if not email or not password:
                logging.error(
                    "Email or password not found in creds.txt. Exiting script.")
                return
    except FileNotFoundError:
        logging.error("creds.txt file not found. Exiting script.")
        return
    except ValueError:
        logging.error(
            "Invalid format in creds.txt. Each line should be in 'key:value' format. Exiting script.")
        return

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    if not auto_login(driver, email, password):
        logging.error("Exiting script due to failed login.")
        driver.quit()
        return

    for course_url in config["courses"]:
        driver.get(course_url)
        time.sleep(3)
        enable_editing_mode(driver)
        create_assignment(driver, config)

    driver.quit()
    logging.info("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
