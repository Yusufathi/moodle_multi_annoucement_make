import logging
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
LOGS_PATH = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOGS_PATH, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOGS_PATH, "assignment_poster_log.txt"), level=logging.INFO,
                    format='%(asctime)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')


def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON file '{file_path}' - {e}")
        return {}


def log_in_to_moodle(driver):
    """Logs in to Moodle using credentials from creds.txt."""
    try:
        with open("creds.txt", 'r') as file:
            username, password = file.read().splitlines()

        driver.get("https://moodle.nu.edu.eg/")
        time.sleep(2)

        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")

        username_input.send_keys(username)
        password_input.send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()

        logging.info("Login successful.")
        time.sleep(3)
    except Exception as e:
        logging.error(f"Login failed - Error: {e}")
        return False

    return True


def enable_editing_mode(driver):
    """Enable course editing mode if not already enabled."""
    try:
        editing_switch = driver.find_element(By.CSS_SELECTOR, "input[name='setmode']")
        if not editing_switch.is_selected():
            editing_switch.click()
            time.sleep(2)
            logging.info("Editing mode enabled.")
        else:
            logging.info("Editing mode already enabled.")
    except Exception as e:
        logging.error(f"Failed to enable editing mode - Error: {e}")


def create_assignment(driver, config):
    try:
        # Click on the last "Add an activity or resource" button
        add_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-action='open-chooser']")
        if not add_buttons:
            logging.error("No 'Add an activity or resource' button found.")
            return

        add_buttons[-1].click()
        logging.info("Clicked 'Add an activity or resource'.")
        time.sleep(2)

        # Click on "Assignment"
        assignment_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Add a new Assignment']"))
        )
        assignment_button.click()
        logging.info("Selected 'Assignment' from the popup.")
        time.sleep(3)

        # Fill in assignment details
        driver.find_element(By.ID, "id_name").send_keys(config["assignment_name"])
        driver.find_element(By.CSS_SELECTOR, "#id_introeditoreditable").send_keys(config["assignment_description"])
        driver.find_element(By.CSS_SELECTOR, "#id_activityeditoreditable").send_keys(config["activity_instructions"])

        # Set due date
        select_dropdown(driver, "id_duedate_day", str(config["due_day"]))
        select_dropdown(driver, "id_duedate_month", config["due_month"])
        select_dropdown(driver, "id_duedate_year", str(config["due_year"]))
        select_dropdown(driver, "id_duedate_hour", str(config["due_hour"]))
        select_dropdown(driver, "id_duedate_minute", str(config["due_minute"]))

        # Uncheck grading due date
        uncheck_checkbox(driver, "id_gradingduedate_enabled")

        # Set maximum number of files
        select_dropdown(driver, "id_maxfiles", str(config["maximum_num_of_files"]))

        # Choose accepted file types
        choose_file_types(driver, config["accepted_file_types"])

        # Submit the assignment
        driver.find_element(By.ID, "id_submitbutton2").click()
        logging.info("Assignment created and submitted.")

    except Exception as e:
        logging.error(f"Failed to create assignment - Error: {e}")


def select_dropdown(driver, dropdown_id, value):
    try:
        dropdown = driver.find_element(By.ID, dropdown_id)
        dropdown.click()
        option = dropdown.find_element(By.XPATH, f"//option[text()='{value}']")
        option.click()
        logging.info(f"Selected '{value}' from dropdown '{dropdown_id}'.")
    except Exception as e:
        logging.error(f"Failed to select '{value}' from dropdown '{dropdown_id}' - Error: {e}")


def uncheck_checkbox(driver, checkbox_id):
    try:
        checkbox = driver.find_element(By.ID, checkbox_id)
        if checkbox.is_selected():
            checkbox.click()
            logging.info(f"Unchecked '{checkbox_id}'.")
    except Exception as e:
        logging.error(f"Failed to uncheck '{checkbox_id}' - Error: {e}")


def choose_file_types(driver, file_type):
    try:
        choose_button = driver.find_element(By.ID, "yui_3_18_1_1_1730298020706_2565")
        choose_button.click()
        logging.info("Clicked 'Choose' button for file types.")
        time.sleep(2)

        # Find the file type by matching the config file
        file_type_checkbox = driver.find_element(By.XPATH, f"//strong[text()='{file_type}']/../input")
        if not file_type_checkbox.is_selected():
            file_type_checkbox.click()
            logging.info(f"Selected '{file_type}' as the accepted file type.")
        driver.find_element(By.CSS_SELECTOR, "button[data-action='save']").click()
        logging.info("Saved file type selection.")
    except Exception as e:
        logging.error(f"Failed to choose file type '{file_type}' - Error: {e}")


def main():
    config_file = "assignments/conf.json"
    config = read_json(config_file)
    if not config:
        logging.error("No valid configuration found. Exiting script.")
        return

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    if not log_in_to_moodle(driver):
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
