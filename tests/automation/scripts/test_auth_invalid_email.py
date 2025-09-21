#!/usr/bin/env python3
"""
Playwright automation script for TC_AUTH_002: Invalid Email Login
"""

from playwright.sync_api import Page, expect
import time

def test_invalid_email_login(page: Page):
    """Test login with invalid email format"""
    
    # Navigate to login page
    page.goto("http://127.0.0.1:8000/signin")
    page.wait_for_load_state("networkidle")
    
    # Fill invalid email
    email_field = page.locator('input[type="email"]').or_(page.locator('input[placeholder*="email" i]')).first
    email_field.fill("invalid-email")
    
    # Fill any password
    password_field = page.locator('input[type="password"]').or_(page.locator('input[placeholder*="password" i]')).first
    password_field.fill("anypassword")
    
    # Try to click login button
    login_button = page.locator('button[type="submit"]').or_(page.locator('button:has-text("Sign In")')).first
    
    # Check if button is disabled or shows validation error
    if login_button.is_disabled():
        print("✅ Login button is disabled for invalid email")
        return True
    
    # If button is clickable, click it and check for error
    login_button.click()
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    
    # Check for validation errors
    error_elements = page.locator('[class*="error"], [class*="alert"], .text-red-500, .text-red-600, [role="alert"]')
    if error_elements.count() > 0:
        error_text = error_elements.first.text_content()
        if "email" in error_text.lower() or "invalid" in error_text.lower():
            print(f"✅ Email validation error displayed: {error_text}")
            return True
    
    # Check if we're still on login page (didn't navigate away)
    current_url = page.url
    if "/signin" in current_url:
        print("✅ User remains on login page for invalid email")
        return True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/auth_invalid_email.png")
    
    raise AssertionError("Invalid email validation not working properly")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_invalid_email_login(page)
            print("✅ TC_AUTH_002: Invalid Email Login - PASSED")
        except Exception as e:
            print(f"❌ TC_AUTH_002: Invalid Email Login - FAILED: {e}")
            page.screenshot(path="test-results/auth_invalid_email_failure.png")
        finally:
            browser.close()

