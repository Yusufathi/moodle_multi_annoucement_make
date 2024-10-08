import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(filename="gradebook_setup_log.txt", level=logging.INFO,
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

# Function to set up the WebDriver
def setup_driver():
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver

# Function to log into Moodle
def login_moodle(driver):
    driver.get("https://moodle.nu.edu.eg/")
    input("Please log in to Moodle, then press Enter to continue...")
    logging.info("User logged in manually.")
    print("User logged in manually.")

# Function to navigate to the gradebook setup page
def navigate_to_gradebook_setup(driver, course_url):
    print(f"Navigating to course URL: {course_url}")
    driver.get(course_url)
    time.sleep(3)

    try:
        # Click on the "Grades" menu item
        grades_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'grade/report/index.php')]"))
        )
        grades_button.click()
        logging.info(f"Clicked 'Grades' button for course: {course_url}")
        print(f"Clicked 'Grades' button for course: {course_url}")
    except Exception as e:
        logging.error(f"Failed to click 'Grades' button for course: {course_url} - Error: {e}")
        print(f"Failed to click 'Grades' button for course: {course_url} - Error: {e}")
        return False

    try:
        # Click on the "Gradebook setup" item
        gradebook_setup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@data-value, 'grade/edit/tree/index.php')]"))
        )
        gradebook_setup_button.click()
        logging.info(f"Clicked 'Gradebook setup' for course: {course_url}")
        print(f"Clicked 'Gradebook setup' for course: {course_url}")
        return True
    except Exception as e:
        logging.error(f"Failed to click 'Gradebook setup' for course: {course_url} - Error: {e}")
        print(f"Failed to click 'Gradebook setup' for course: {course_url} - Error: {e}")
        return False

# Function to add a grade category
def add_category(driver, category_name, weight):
    try:
        # Click on "Add category"
        add_category_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-trigger='add-category-form']"))
        )
        add_category_button.click()
        logging.info(f"Clicked 'Add category' button.")
        print(f"Clicked 'Add category' button.")

        time.sleep(3)  # Wait for the form to load

        # Enter category name
        category_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='fullname']")
        category_name_input.send_keys(category_name)
        logging.info(f"Entered category name: {category_name}")
        print(f"Entered category name: {category_name}")

        # Enter weight
        weight_input = driver.find_element(By.CSS_SELECTOR, "input[name='grade_item_grademax']")
        weight_input.clear()
        weight_input.send_keys(str(weight))
        logging.info(f"Entered category weight: {weight}")
        print(f"Entered category weight: {weight}")

        # Click Save button
        save_button = driver.find_element(By.CSS_SELECTOR, "button[data-action='save']")
        save_button.click()
        logging.info(f"Saved category: {category_name}")
        print(f"Saved category: {category_name}")
    except Exception as e:
        logging.error(f"Failed to add category: {category_name} - Error: {e}")
        print(f"Failed to add category: {category_name} - Error: {e}")

# Main function to automate gradebook setup
def automate_gradebook_setup(course_links, gradebook_data):
    driver = setup_driver()
    login_moodle(driver)

    for course_url in course_links:
        if navigate_to_gradebook_setup(driver, course_url):
            for category, details in gradebook_data.items():
                if isinstance(details, dict) and 'weight' in details:
                    # It's a category, so add the category and its items
                    add_category(driver, category, details['weight'])
                else:
                    # It's a direct grading item
                    add_category(driver, category, details)

    driver.quit()
    logging.info("Browser closed. Script completed.")
    print("Browser closed. Script completed.")

# Read course links from grade_book/links.txt
course_links_file = "grade_book/links.txt"
COURSE_LINKS = read_lines(course_links_file)

# Read gradebook data from gradebook.json
import json
gradebook_file = "grade_book/gradebook.json"
GRADEBOOK_DATA = json.loads(read_file(gradebook_file))

# Run the automation
automate_gradebook_setup(COURSE_LINKS, GRADEBOOK_DATA)
