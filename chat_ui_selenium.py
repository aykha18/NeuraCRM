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


def find_login_inputs(driver):
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
    return email_el, pwd_el


def ensure_logged_in(driver):
    token = driver.execute_script("return window.localStorage.getItem('access_token');")
    if token:
        return
    driver.get(f"{BASE_URL}/signin")
    time.sleep(1)
    email_el, pwd_el = find_login_inputs(driver)
    if not email_el or not pwd_el:
        # fallback: click sign in link
        driver.get(BASE_URL)
        try:
            wait_clickable(driver, By.XPATH, "//a[contains(., 'Sign In') or contains(., 'Login') or contains(@href, '/signin')]").click()
        except Exception:
            pass
        email_el, pwd_el = find_login_inputs(driver)
    email_el.clear(); email_el.send_keys(EMAIL)
    pwd_el.clear(); pwd_el.send_keys(PASSWORD)
    try:
        wait_clickable(driver, By.XPATH, "//button[@type='submit']").click()
    except Exception:
        wait_clickable(driver, By.XPATH, "//button[contains(., 'Sign In') or contains(., 'Login')]").click()
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return !!window.localStorage.getItem('access_token');"))


def test_chat_flow():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,900")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    try:
        print("1) Ensure login")
        driver.get(BASE_URL)
        ensure_logged_in(driver)

        print("2) Go to Chat")
        driver.get(f"{BASE_URL}/chat")
        WebDriverWait(driver, 20).until(lambda d: "/chat" in d.current_url)
        time.sleep(1)

        print("3) Create room if needed")
        # Open modal
        modal_opened = False
        try:
            wait_clickable(driver, By.XPATH, "//div[contains(@class,'border-b')]/..//button[contains(@class,'rounded-full')]").click()
            wait_visible(driver, By.XPATH, "//div[contains(@class,'fixed') and .//h2[contains(., 'Create New Room')]]")
            modal_opened = True
            # Fill form
            name_in = wait_visible(driver, By.XPATH, "//label[contains(., 'Room Name')]/following::input[1]")
            name_in.clear(); name_in.send_keys("Selenium Room")
            desc = wait_visible(driver, By.XPATH, "//label[contains(., 'Description')]/following::textarea[1]")
            desc.clear(); desc.send_keys("Automated test")
            wait_clickable(driver, By.XPATH, "//button[contains(., 'Create Room')]").click()
            # Wait for modal backdrop to disappear
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class,'fixed') and contains(@class,'inset-0')]")))
            time.sleep(0.5)
        except Exception:
            # If modal not opened or not needed, ignore
            pass

        print("4) Select first room")
        # Scroll list into view and click
        room_btn = wait_clickable(driver, By.XPATH, "(//div[contains(@class,'space-y-1')]//button)[1]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", room_btn)
        room_btn.click()

        print("5) Send message")
        # Attempt to find message input (textarea or input)
        try:
            inp = wait_visible(driver, By.CSS_SELECTOR, "textarea")
        except Exception:
            inp = wait_visible(driver, By.XPATH, "//input[contains(@placeholder,'Message') or contains(@class,'message')]")
        inp.send_keys("Hello from Selenium")
        # Find a send button
        try:
            send_btn = wait_clickable(driver, By.XPATH, "//button[@type='submit' or contains(., 'Send')]")
        except Exception:
            send_btn = wait_clickable(driver, By.XPATH, "//button[.//svg or .//*[contains(text(),'Send')]]")
        send_btn.click()
        time.sleep(1)

        print("6) Verify message appears")
        msgs = driver.find_elements(By.XPATH, "//*[contains(text(),'Hello from Selenium')]")
        assert len(msgs) > 0, "Message not rendered"

        print("7) Refresh and verify persistence")
        driver.refresh()
        WebDriverWait(driver, 15).until(lambda d: "/chat" in d.current_url)
        rb = wait_clickable(driver, By.XPATH, "(//div[contains(@class,'space-y-1')]//button)[1]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rb)
        rb.click()
        time.sleep(1)
        msgs2 = driver.find_elements(By.XPATH, "//*[contains(text(),'Hello from Selenium')]")
        assert len(msgs2) > 0, "Message did not persist"

        print("SUCCESS: Chat UI E2E passed")
    except Exception as e:
        print("FAIL:", e)
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    test_chat_flow()
