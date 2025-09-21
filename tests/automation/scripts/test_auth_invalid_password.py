#!/usr/bin/env python3
"""
Playwright automation script for TC_AUTH_003: Invalid Password Login
"""

from playwright.sync_api import Page, expect
import time

def test_invalid_password_login(page: Page):
    """Test login with incorrect password"""
    
    # Navigate to login page
    page.goto("http://127.0.0.1:8000/signin")
    page.wait_for_load_state("networkidle")
    
    # Fill valid email
    email_field = page.locator('input[type="email"]').or_(page.locator('input[placeholder*="email" i]')).first
    email_field.fill("nodeit@node.com")
    
    # Fill incorrect password
    password_field = page.locator('input[type="password"]').or_(page.locator('input[placeholder*="password" i]')).first
    password_field.fill("wrongpassword")
    
    # Click login button
    login_button = page.locator('button[type="submit"]').or_(page.locator('button:has-text("Sign In")')).first
    login_button.click()
    
    # Wait for response
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Check for error message
    error_elements = page.locator('[class*="error"], [class*="alert"], .text-red-500, .text-red-600, [role="alert"]')
    if error_elements.count() > 0:
        error_text = error_elements.first.text_content()
        if any(word in error_text.lower() for word in ['invalid', 'incorrect', 'wrong', 'credentials', 'password']):
            print(f"✅ Invalid credentials error displayed: {error_text}")
            return True
    
    # Check if we're still on login page
    current_url = page.url
    if "/signin" in current_url:
        print("✅ User remains on login page for invalid password")
        return True
    
    # Check if password field is cleared or highlighted
    password_value = password_field.input_value()
    if password_value == "":
        print("✅ Password field was cleared after failed login")
        return True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/auth_invalid_password.png")
    
    raise AssertionError("Invalid password handling not working properly")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_invalid_password_login(page)
            print("✅ TC_AUTH_003: Invalid Password Login - PASSED")
        except Exception as e:
            print(f"❌ TC_AUTH_003: Invalid Password Login - FAILED: {e}")
            page.screenshot(path="test-results/auth_invalid_password_failure.png")
        finally:
            browser.close()

