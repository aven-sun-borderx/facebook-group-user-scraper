import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def wait_for_human_captcha(driver):
    """
    Detects and waits for manual CAPTCHA resolution before continuing.
    """
    print("Checking for CAPTCHA...")

    while True:
        try:
            # Detect CAPTCHA text prompt
            captcha_prompt = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Enter the characters you see')]")
            captcha_input = driver.find_elements(By.XPATH, "//input[@type='text']")

            if captcha_prompt or captcha_input:
                print("CAPTCHA detected! Please enter the characters manually.")

                # Wait until CAPTCHA is solved
                while captcha_prompt or captcha_input:
                    time.sleep(5)
                    print("Waiting for CAPTCHA to be solved...")

                    # Re-check if CAPTCHA elements still exist
                    captcha_prompt = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Enter the characters you see')]")
                    captcha_input = driver.find_elements(By.XPATH, "//input[@type='text']")
                
                print("✅ CAPTCHA solved! Continuing...")  
                break

            # If CAPTCHA is not found, assume login successful or failed
            if "login" not in driver.current_url.lower():
                print("✅ No CAPTCHA detected. Login successful!")
                break

        except Exception as e:
            print(f"Error checking CAPTCHA: {e}")
            time.sleep(5)  # Keep checking



def login_facebook(driver, account, password):
    """
    Logs into Facebook with the given account and password.

    Args:
        driver: Selenium WebDriver instance.
        account: Facebook email or phone number.
        password: Facebook password.

    Returns:
        None
    """
    login_url = "https://www.facebook.com/"
    driver.get(login_url)

    try:
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to appear

        # Find the email input field
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(account)
        print("Entered email/phone successfully.")

        # Find the password input field
        password_input = wait.until(EC.presence_of_element_located((By.ID, "pass")))
        password_input.send_keys(password)
        print("Entered password successfully.")

        # Click the login button
        login_button = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
        login_button.click()
        print("Clicked login button.")

        # Wait for login process
        time.sleep(3)

        # Handle CAPTCHA if needed
        wait_for_human_captcha(driver)

        # Check if login was successful
        if "login" in driver.current_url.lower():
            print("Login may have failed. Check credentials or CAPTCHA.")
        else:
            print("Login successful!")

    except Exception as e:
        print(f"Error during login: {e}")
