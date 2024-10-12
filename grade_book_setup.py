import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json

LOGS_PATH = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOGS_PATH, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOGS_PATH, "grade_book_setup_log.txt"), level=logging.INFO,
                    format='%(asctime)s - %(message)s')

CHROMEDRIVER_PATH = os.path.join(os.getcwd(), 'chromedriver.exe')


def read_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        return []


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


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element)


def click_gradebook_setup(driver, course_url):
    try:
        gradebook_setup_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//li[contains(@data-value, 'grade/edit/tree/index.php')]"))
        )
        js_click(driver, gradebook_setup_option)
        logging.info(
            f"Clicked 'Gradebook setup' using JavaScript for course: {course_url}")
        print(
            f"Clicked 'Gradebook setup' using JavaScript for course: {course_url}")
        return True
    except Exception as e:
        logging.error(
            f"Failed to click 'Gradebook setup' for course: {course_url} - Error: {e}")
        print(
            f"Failed to click 'Gradebook setup' for course: {course_url} - Error: {e}")
        return False


def handle_recalculation_page(driver):
    try:
        recalculation_text = "Recalculating"
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), recalculation_text)
        )
        print("Detected recalculation page. Waiting for recalculation to complete.")
        continue_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Continue')]"))
        )
        js_click(driver, continue_button)
        print("Clicked 'Continue' on recalculation page.")
        WebDriverWait(driver, 20).until(
            EC.url_contains('grade/edit/tree/index.php')
        )
        print("Recalculation completed and returned to grade setup.")
    except Exception as e:
        print(f"No recalculation page detected or failed to handle it: {e}")


def category_exists(driver, category_name):
    try:
        # Check if the category exists on the page
        category_elements = driver.find_elements(
            By.XPATH, f"//option[text()='{category_name}']")
        return len(category_elements) > 0
    except Exception as e:
        print(
            f"Failed to check for existing category '{category_name}' - Error: {e}")
        return False


def navigate_to_gradebook_setup(driver, course_url):
    try:
        driver.get(course_url)
        time.sleep(3)

        grades_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'grade/report/index.php')]"))
        )
        grades_button.click()

        grader_report_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[role='combobox']"))
        )
        grader_report_dropdown.click()

        return click_gradebook_setup(driver, course_url)
    except Exception as e:
        logging.error(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        print(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        return False


def create_category(driver, category_name, weight, course_url):
    if category_exists(driver, category_name):
        print(f"Category '{category_name}' already exists. Skipping creation.")
        return

    try:
        print(f"Creating category: {category_name} with weight: {weight}")
        add_menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@id, 'action-menu-toggle')]"))
        )
        js_click(driver, add_menu_button)

        add_category_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@data-trigger, 'add-category-form')]"))
        )
        js_click(driver, add_category_button)

        time.sleep(3)

        category_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='fullname']"))
        )
        category_name_input.send_keys(category_name)

        weight_input = driver.find_element(
            By.XPATH, "//input[@name='grade_item_grademax']")
        weight_input.clear()
        weight_input.send_keys(str(weight))

        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-action='save']"))
        )
        js_click(driver, save_button)

        logging.info(
            f"Saved category '{category_name}' with weight '{weight}'")
        print(f"Saved category '{category_name}' with weight '{weight}'")

        handle_recalculation_page(driver)

    except Exception as e:
        logging.error(
            f"Failed to create category '{category_name}' for course: {course_url} - Error: {e}")
        print(
            f"Failed to create category '{category_name}' for course: {course_url} - Error: {e}")


def create_grade_item(driver, item_name, item_grade, category_name, course_url):
    if category_name and not category_exists(driver, category_name):
        print(
            f"Category '{category_name}' does not exist. Skipping grade item creation for '{item_name}'.")
        return

    try:
        print(
            f"Creating grade item: {item_name} with grade: {item_grade} in category: {category_name or 'None'}")
        add_menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@id, 'action-menu-toggle')]"))
        )
        js_click(driver, add_menu_button)

        add_grade_item_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@data-trigger, 'add-item-form')]"))
        )
        js_click(driver, add_grade_item_button)

        time.sleep(3)

        item_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='itemname']"))
        )
        item_name_input.send_keys(item_name)

        grade_input = driver.find_element(
            By.XPATH, "//input[@name='grademax']")
        grade_input.clear()
        grade_input.send_keys(str(item_grade))

        if category_name:
            category_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//select[@name='parentcategory']"))
            )
            category_dropdown.send_keys(category_name)

        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-action='save']"))
        )
        js_click(driver, save_button)

        logging.info(
            f"Created grade item '{item_name}' with grade '{item_grade}' in category '{category_name}'")
        print(
            f"Created grade item '{item_name}' with grade '{item_grade}' in category '{category_name}'")

        handle_recalculation_page(driver)

    except Exception as e:
        logging.error(
            f"Failed to create grade item '{item_name}' for course: {course_url} - Error: {e}")
        print(
            f"Failed to create grade item '{item_name}' for course: {course_url} - Error: {e}")


def main():
    course_links_file = "grade_book/links.txt"
    gradebook_json_file = "grade_book/gradebook.json"

    COURSE_LINKS = read_lines(course_links_file)
    GRADEBOOK_STRUCTURE = read_json(gradebook_json_file)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    driver.get("https://moodle.nu.edu.eg/")
    input("Press Enter after you have logged in manually...")
    logging.info("User logged in manually.")
    print("User logged in manually.")

    for course_url in COURSE_LINKS:
        if navigate_to_gradebook_setup(driver, course_url):
            for category, details in GRADEBOOK_STRUCTURE.items():
                if isinstance(details, dict):
                    create_category(driver, category,
                                    details['weight'], course_url)
                    for item_name, item_grade in details.items():
                        if item_name != 'weight':
                            create_grade_item(
                                driver, item_name, item_grade, category, course_url)
                else:
                    create_grade_item(driver, category,
                                      details, None, course_url)

    driver.quit()
    logging.info("Browser closed. Script completed.")
    print("Browser closed. Script completed.")


if __name__ == "__main__":
    main()
