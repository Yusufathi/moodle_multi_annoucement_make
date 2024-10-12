import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Set up logging in the logs/ folder
LOGS_PATH = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOGS_PATH, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOGS_PATH, "delete_gradebook_log.txt"), level=logging.INFO,
                    format='%(asctime)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')

# Function to read file lines


def read_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []

# Function to scroll and click using JavaScript


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element)

# Function to navigate to 'Gradebook setup'


def navigate_to_gradebook_setup(driver, course_url):
    try:
        driver.get(course_url)
        time.sleep(3)

        # Click on 'Grades' button
        grades_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'grade/report/index.php')]"))
        )
        grades_button.click()
        logging.info(f"Clicked 'Grades' button for course: {course_url}")
        print(f"Clicked 'Grades' button for course: {course_url}")

        # Click on 'Grader report' dropdown
        grader_report_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[role='combobox']"))
        )
        grader_report_dropdown.click()
        logging.info(
            f"Clicked 'Grader Report' dropdown for course: {course_url}")
        print(f"Clicked 'Grader Report' dropdown for course: {course_url}")

        # Select 'Gradebook setup' from the dropdown
        gradebook_setup_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[contains(@data-value, 'grade/edit/tree/index.php')]"))
        )
        js_click(driver, gradebook_setup_option)
        logging.info(f"Clicked 'Gradebook setup' for course: {course_url}")
        print(f"Clicked 'Gradebook setup' for course: {course_url}")

    except Exception as e:
        logging.error(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        print(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        return False
    return True

# Function to delete items or categories


def delete_item_or_category(driver):
    try:
        while True:
            # Fetch all action buttons
            action_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "button.btn-icon.cellmenubtn"))
            )

            # Skip the first button (representing the whole course) and the last button (Course Total)
            if len(action_buttons) > 2:
                for button_index in range(1, len(action_buttons) - 1):
                    try:
                        # Re-fetch action buttons after each deletion
                        action_buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, "button.btn-icon.cellmenubtn"))
                        )

                        js_click(driver, action_buttons[button_index])
                        logging.info(f"Clicked action button {button_index}.")
                        print(f"Clicked action button {button_index}.")
                        time.sleep(1)

                        # Look for any delete button in the dropdown and click it
                        delete_option = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//a[contains(@data-modal, 'confirmation') and contains(text(), 'Delete')]"))
                        )
                        js_click(driver, delete_option)
                        logging.info(
                            f"Clicked 'Delete' option from the dropdown.")
                        print(f"Clicked 'Delete' option from the dropdown.")
                        time.sleep(1)

                        # Confirm deletion in the dialog
                        confirm_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, "//button[@data-action='save']"))
                        )
                        js_click(driver, confirm_button)
                        logging.info("Confirmed deletion.")
                        print("Confirmed deletion.")
                        time.sleep(5)  # Wait for the page to refresh

                        logging.info(
                            "Item or category deleted. Refreshing the page.")
                        print("Item or category deleted. Refreshing the page.")
                        break  # Exit the for-loop to re-check after refresh

                    except Exception as e:
                        logging.error(
                            f"Failed to delete item or category - Error: {e}")
                        print(
                            f"Failed to delete item or category - Error: {e}")
                        continue

            else:
                # Check if only the "Course total" remains (or nothing more to delete)
                try:
                    course_total = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(text(), 'Course total')]"))
                    )
                    if course_total:
                        logging.info(
                            "Only 'Course total' remains. No more items or categories to delete.")
                        print(
                            "Only 'Course total' remains. No more items or categories to delete.")
                        break

                except Exception as e:
                    logging.error(f"Error checking for 'Course total' - {e}")
                    print(f"Error checking for 'Course total' - {e}")
                    break

    except Exception as e:
        logging.error(f"Failed to retrieve action buttons - Error: {e}")
        print(f"Failed to retrieve action buttons - Error: {e}")

# Function to check if user is logged in by detecting any greeting like 'Hi,'


def wait_for_login(driver):
    try:
        # Wait for the 'Hi,' greeting which is common for all users
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(text(), 'Hi,')]"))
        )
        print("Login successful.")
        logging.info("User logged in successfully.")
        return True
    except Exception as e:
        logging.error(
            f"Login not detected within the timeout period - Error: {e}")
        print(f"Login not detected - Error: {e}")
        return False

# Main execution


def main():
    course_links_file = "grade_book/links.txt"
    COURSE_LINKS = read_lines(course_links_file)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Open Moodle login page and wait for successful login detection
    driver.get("https://moodle.nu.edu.eg/")
    print("Waiting for login...")
    if not wait_for_login(driver):
        print("Login failed or not detected. Exiting...")
        return

    # Loop through each course link and navigate to the gradebook setup
    for course_url in COURSE_LINKS:
        if navigate_to_gradebook_setup(driver, course_url):
            print(f"Deleting items and categories for course: {course_url}")
            delete_item_or_category(driver)

    driver.quit()
    logging.info("Browser closed. Script completed.")
    print("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
