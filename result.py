from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from playsound import playsound
import time
import os


def load_url_until_success(url, max_attempts=1000, wait_time=3):
    driver = webdriver.Chrome()  # Assuming Chrome; adjust if using a different browser

    for attempt in range(max_attempts):
        try:
            driver.get(url)

            # Wait for any element to be present on the page
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Check if '503' is not in the page source
            if "503" not in driver.page_source:
                print(f"Successfully loaded the page on attempt {attempt + 1}")

                # Play success sound
                sound_file = os.path.join(os.path.dirname(__file__), "success.wav")
                playsound(sound_file)

                return driver

            print(f"Attempt {attempt + 1}: 503 error encountered. Retrying...")
            time.sleep(wait_time)

        except TimeoutException:
            print(f"Attempt {attempt + 1}: Timeout. Retrying...")

    print("Max attempts reached. Unable to load the page successfully.")
    driver.quit()
    return None


def fill_form_and_submit(driver, max_attempts=100, wait_time=1):
    # Find the input field with name "login"
    login_input = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.NAME, "login"))
    )

    # Clear any existing value and enter the number
    login_input.clear()
    login_input.send_keys("21070126119")

    initial_url = driver.current_url

    for attempt in range(max_attempts):
        try:
            # Find and click the submit button
            submit_button = driver.find_element(By.NAME, "Submit")
            submit_button.click()

            # Wait for the URL to change
            WebDriverWait(driver, 0).until(EC.url_changes(initial_url))

            print(f"Form submitted successfully and new page loaded on attempt {attempt + 1}.")
            return True

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            print(f"Attempt {attempt + 1}: Failed to submit form or load new page. Retrying...")
            time.sleep(wait_time)
i
    print("Max attempts reached. Unable to submit form and load new page.")
    return False


# Usage
url = "https://siuexam.siu.edu.in/forms/resultview.html"
driver = load_url_until_success(url)

if driver:
    # Fill form and submit
    if fill_form_and_submit(driver):
        print("Form submitted and new page loaded successfully.")
    else:
        print("Failed to submit form and load new page.")

    # Keep the browser window open
    print("Process completed. Press Enter to close the browser...")
    input()

    # Close the browser when Enter is pressed
    driver.quit()
else:
    print("Failed to load the initial page.")