from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time

BASE_URL = os.getenv('UI_BASE_URL', 'http://localhost:5173')
EMAIL = os.getenv('UI_EMAIL', 'nodeit@node.com')
PASSWORD = os.getenv('UI_PASSWORD', 'NodeIT2024!')


def wait_visible(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def wait_clickable(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


def assert_token_present(driver):
    token = driver.execute_script("return window.localStorage.getItem('access_token');")
    assert token and len(token.split('.')) == 3, 'access_token not found in localStorage'


def find_input(driver):
    # Try several selectors for email/password
    selectors_email = [
        (By.ID, 'email'),
        (By.NAME, 'email'),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[placeholder*='email' i]")
    ]
    selectors_password = [
        (By.ID, 'password'),
        (By.NAME, 'password'),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[placeholder*='password' i]")
    ]
    email_el = None
    pwd_el = None
    for by, sel in selectors_email:
        try:
            email_el = wait_visible(driver, by, sel, 5)
            break
        except Exception:
            continue
    for by, sel in selectors_password:
        try:
            pwd_el = wait_visible(driver, by, sel, 5)
            break
        except Exception:
            continue
    if not email_el or not pwd_el:
        raise RuntimeError('Login inputs not found')
    return email_el, pwd_el


def test_login():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1400,900')

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    try:
        print('1) Open sign-in page')
        driver.get(f"{BASE_URL}/signin")
        # Some builds may redirect if already logged in
        time.sleep(1)

        # If email input not visible, try navigating to / and clicking a Sign In link
        try:
            wait_visible(driver, By.ID, 'email')
        except Exception:
            driver.get(BASE_URL)
            try:
                wait_clickable(driver, By.XPATH, "//a[contains(., 'Sign In') or contains(., 'Login') or contains(@href, '/signin')]").click()
            except Exception:
                pass
            wait_visible(driver, By.ID, 'email')

        print('2) Fill credentials and submit')
        email_input, pwd_input = find_input(driver)
        email_input.clear(); email_input.send_keys(EMAIL)
        pwd_input.clear(); pwd_input.send_keys(PASSWORD)

        # Click submit button
        try:
            wait_clickable(driver, By.XPATH, "//button[@type='submit']").click()
        except Exception:
            wait_clickable(driver, By.XPATH, "//button[contains(., 'Sign In') or contains(., 'Login')]").click()

        # Wait until app loads (route changes or token stored)
        WebDriverWait(driver, 20).until(lambda d: 'access_token' in d.execute_script('return Object.keys(window.localStorage);') or '/dashboard' in d.current_url or '/chat' in d.current_url)
        assert_token_present(driver)

        # Sanity: navigate to /chat to ensure authenticated route loads
        driver.get(f"{BASE_URL}/chat")
        WebDriverWait(driver, 15).until(lambda d: '/chat' in d.current_url)
        assert_token_present(driver)

        print('PASS: UI login succeeded and token stored')
    except Exception as e:
        print('FAIL:', e)
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    test_login()
