import urllib.parse
import json
import requests
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurations
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')
CONFIG_FILE_PATH = "grade_book/modify.json"
CREDS_FILE_PATH = "creds.txt"

# Logging setup
logging.basicConfig(filename="logs/gradebook_modifier_log.txt", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None


def read_creds(file_path):
    creds = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                key, value = line.strip().split(':')
                creds[key] = value
        return creds.get('email'), creds.get('password')
    except Exception as e:
        logging.error(f"Error reading credentials: {e}")
        return None, None


def js_click(driver, element):
    """Clicks an element using JavaScript to avoid interception issues."""
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


def enable_edit_mode(driver):
    try:
        edit_mode_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='setmode' and @class='custom-control-input']"))
        )
        if not edit_mode_checkbox.is_selected():
            js_click(driver, edit_mode_checkbox)
            logging.info("Edit mode enabled.")
        else:
            logging.info("Edit mode already enabled.")
    except Exception as e:
        logging.error(f"Failed to enable edit mode: {e}")


def retrieve_sesskey(driver):
    """Extracts sesskey from Moodle after logging in."""
    try:
        sesskey = driver.execute_script("return M.cfg.sesskey;")
        logging.info(f"Retrieved sesskey: {sesskey}")
        print(f"Retrieved sesskey: {sesskey}")
        return sesskey
    except Exception as e:
        logging.error(f"Failed to retrieve sesskey: {e}")
        print(f"Failed to retrieve sesskey: {e}")
        return None


def retrieve_moodle_session_cookie(driver):
    """Retrieves the MoodleSession cookie after login."""
    try:
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'MoodleSession':
                moodle_session = cookie['value']
                logging.info("Retrieved MoodleSession cookie.")
                print("Retrieved MoodleSession cookie.")
                return moodle_session
        logging.error("MoodleSession cookie not found.")
        return None
    except Exception as e:
        logging.error(f"Failed to retrieve MoodleSession cookie: {e}")
        print(f"Failed to retrieve MoodleSession cookie: {e}")
        return None


def modify_grade_item_name(driver, old_name, new_name, category):
    try:
        print(f"Looking for grade item '{
              old_name}' in category '{category}'...")
        logging.info(f"Looking for grade item '{
                     old_name}' in category '{category}'.")

        # Locate the grade item row based on the old name and get the data-itemid attribute
        item_row = driver.find_element(
            By.XPATH, f"//span[@title='{old_name}']/ancestor::tr")
        data_itemid = item_row.get_attribute("data-itemid")

        if not data_itemid:
            print(f"Could not find data-itemid for grade item '{old_name}'.")
            logging.error(
                f"Could not find data-itemid for grade item '{old_name}'.")
            return False

        print(
            f"Found data-itemid '{data_itemid}' for grade item '{old_name}'.")
        logging.info(
            f"Found data-itemid '{data_itemid}' for grade item '{old_name}'.")

        # Retrieve sesskey and MoodleSession cookie
        sesskey = retrieve_sesskey(driver)
        moodle_session = retrieve_moodle_session_cookie(driver)

        if not sesskey or not moodle_session:
            print("Failed to retrieve sesskey or MoodleSession cookie.")
            logging.error(
                "Failed to retrieve sesskey or MoodleSession cookie.")
            return False

        # Retrieve the course ID from the current URL
        course_id = driver.current_url.split("id=")[-1].split("&")[0]

        # Define the API endpoint URL and headers
        url = f"https://moodle.nu.edu.eg/lib/ajax/service.php?sesskey={
            sesskey}&info=core_form_dynamic_form"
        headers = {
            # Change to x-www-form-urlencoded
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"MoodleSession={moodle_session}",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

        # URL-encode formdata and prepare payload
        formdata = urllib.parse.quote(
            f"id={data_itemid}&courseid={course_id}&itemid={data_itemid}&itemtype=manual&gpr_type=edit&gpr_plugin=tree&gpr_courseid={course_id}&sesskey={
                sesskey}&_qf__core_grades_form_add_item=1&itemname={new_name}&rescalegrades=&grademin=0.00&hidden=0&locked=0&aggregationcoef=0.0000"
        )
        payload = [
            {
                "index": 0,
                "methodname": "core_form_dynamic_form",
                "args": {
                    "formdata": formdata,
                    "form": "core_grades\\form\\add_item"
                }
            }
        ]

        # Convert cookies to requests-compatible format
        cookies = {cookie['name']: cookie['value']
                   for cookie in driver.get_cookies()}

        # Make the API call to modify the grade item name
        response = requests.post(url, headers=headers,
                                 data=json.dumps(payload), cookies=cookies)
        logging.info(response.text)
        # Check response status
        if response.status_code == 200:
            response_data = response.json()
            if response_data and isinstance(response_data, list) and "error" not in response_data[0]:
                print(f"Successfully changed '{old_name}' to '{new_name}'.")
                logging.info(f"Successfully changed '{
                             old_name}' to '{new_name}' via API.")
                return True
            else:
                print(f"Failed to modify '{old_name}' to '{
                      new_name}'. Response data: {response_data}")
                logging.error(f"Failed to modify '{old_name}' to '{
                              new_name}'. Response data: {response_data}")
                return False
        else:
            print(f"Failed to change '{old_name}' to '{
                  new_name}'. Status code: {response.status_code}")
            logging.error(f"Failed to change '{old_name}' to '{
                          new_name}'. Status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Failed to modify '{old_name}' to '{new_name}': {e}")
        logging.error(f"Failed to modify '{old_name}' to '{new_name}': {e}")
        return False


def modify_gradebook(driver, config):
    """Modify grade items in each course according to the provided configuration."""
    for course_url in config["courses"]:
        driver.get(course_url)
        time.sleep(3)
        logging.info(f"Accessed course gradebook: {course_url}")

        # Enable edit mode if not already enabled
        enable_edit_mode(driver)

        # Modify Tutorials category grade items
        if "Tutorials" in config:
            for old_name, new_name in config["Tutorials"].items():
                logging.info(f"Attempting to change {old_name} to {
                             new_name} in category Tutorials")
                success = modify_grade_item_name(
                    driver, old_name, new_name, "Tutorials")
                if success:
                    logging.info(f"Successfully changed {old_name} to {
                                 new_name} in Tutorials category.")
                else:
                    logging.error(f"Failed to change {old_name} to {
                                  new_name} in Tutorials category.")

        # Modify Labs category grade items
        if "Labs" in config:
            for old_name, new_name in config["Labs"].items():
                logging.info(f"Attempting to change {old_name} to {
                             new_name} in category Labs")
                success = modify_grade_item_name(
                    driver, old_name, new_name, "Labs")
                if success:
                    logging.info(f"Successfully changed {old_name} to {
                                 new_name} in Labs category.")
                else:
                    logging.error(f"Failed to change {old_name} to {
                                  new_name} in Labs category.")


def main():
    # Load configuration and credentials
    config = read_json(CONFIG_FILE_PATH)
    email, password = read_creds(CREDS_FILE_PATH)

    if not config or not email or not password:
        logging.error("Missing configuration or credentials. Exiting script.")
        return

    # Set up WebDriver
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Login to Moodle
    if not auto_login(driver, email, password):
        logging.error("Exiting script due to login failure.")
        driver.quit()
        return

    # # Retrieve the sesskey after logging in
    # try:
    #     # Get the sesskey from a hidden input field or a script tag
    #     sesskey = driver.execute_script("return M.cfg.sesskey;")
    #     print(f"Retrieved sesskey: {sesskey}")
    #     logging.info(f"Retrieved sesskey: {sesskey}")
    # except Exception as e:
    #     print(f"Failed to retrieve sesskey: {e}")
    #     logging.error(f"Failed to retrieve sesskey: {e}")
    #     sesskey = None

    # Process each course URL
    modify_gradebook(driver, config)

    # Close the driver
    driver.quit()
    logging.info("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
