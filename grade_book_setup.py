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
        gradebook_setup_url = course_url.replace(
            "course/view.php", "grade/edit/tree/index.php")
        driver.get(gradebook_setup_url)
        time.sleep(3)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[@id='grade_edit_tree_table']"))
        )
        logging.info(
            f"Successfully navigated to Gradebook Setup for course: {course_url}")
        print(
            f"Successfully navigated to Gradebook Setup for course: {course_url}")
        return True
    except Exception as e:
        logging.error(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        print(
            f"Failed to navigate to Gradebook Setup for course: {course_url} - Error: {e}")
        return False


def create_category(driver, category_name, weight, course_url):
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


def auto_login(driver, email, password):
    try:
        # Step 1: Go to the Moodle login page
        driver.get("https://moodle.nu.edu.eg/")
        time.sleep(3)

        # Step 2: Enter email for SSO login
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "i0116"))
            )
            email_input.clear()  # Ensure the field is empty before typing
            email_input.send_keys(email)
            next_button = driver.find_element(By.ID, "idSIButton9")
            js_click(driver, next_button)
            logging.info("Entered email and clicked next for SSO.")
        except Exception as e:
            logging.error(f"Failed to enter email - Error: {e}")
            print(f"Failed to enter email - Error: {e}")
            return False

        # Step 3: Wait for password field and enter the password
        try:
            # Adding retries in case of a stale element reference
            retries = 3
            for attempt in range(retries):
                try:
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "i0118"))
                    )
                    password_input.clear()  # Ensure the field is empty
                    password_input.send_keys(password)
                    sign_in_button = driver.find_element(By.ID, "idSIButton9")
                    js_click(driver, sign_in_button)
                    logging.info(
                        "Entered password and clicked sign in for SSO.")
                    break  # Break out of retry loop if successful
                except Exception as e:
                    if attempt < retries - 1:
                        logging.warning(
                            f"Retry {attempt + 1} for password entry due to error: {e}")
                        print(
                            f"Retry {attempt + 1} for password entry due to error: {e}")
                        time.sleep(2)  # Brief wait before retrying
                    else:
                        raise e  # Reraise the last exception if all retries fail
        except Exception as e:
            logging.error(f"Failed to enter password - Error: {e}")
            print(f"Failed to enter password - Error: {e}")
            return False

        # Step 4: Handle "Stay signed in?" prompt
        try:
            stay_signed_in_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            js_click(driver, stay_signed_in_button)
            logging.info("Clicked 'Yes' for staying signed in.")
        except Exception as e:
            logging.error(f"Failed to click 'Stay signed in' - Error: {e}")
            print(f"Failed to click 'Stay signed in' - Error: {e}")
            return False

        # Step 5: Wait for Moodle homepage to confirm successful login
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[contains(text(), 'Hi,')]"))
            )
            logging.info("Login successful.")
            print("Login successful.")
            return True
        except Exception as e:
            logging.error(f"Failed to confirm login - Error: {e}")
            print(f"Failed to confirm login - Error: {e}")
            return False

    except Exception as e:
        logging.error(f"Login process failed - Error: {e}")
        print(f"Login process failed - Error: {e}")
        return False


def main():
    course_links_file = "grade_book/links.txt"
    gradebook_json_file = "grade_book/gradebook.json"
    creds_file = "creds.txt"

    COURSE_LINKS = read_lines(course_links_file)
    GRADEBOOK_STRUCTURE = read_json(gradebook_json_file)

    # Read credentials from creds.txt
    try:
        with open(creds_file, 'r', encoding='utf-8') as file:
            creds = {line.split(":")[0]: line.split(
                ":")[1].strip() for line in file}
            email = creds.get("email")
            password = creds.get("password")
    except FileNotFoundError:
        logging.error(f"File '{creds_file}' not found.")
        print("Credentials file not found.")
        return

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Automatic login
    print("Attempting automatic login...")
    if not auto_login(driver, email, password):
        print("Automatic login failed. Exiting...")
        driver.quit()
        return

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
