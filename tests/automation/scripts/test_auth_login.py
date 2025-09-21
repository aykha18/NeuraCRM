#!/usr/bin/env python3
"""
Playwright automation script for TC_AUTH_001: Valid User Login
"""

from playwright.sync_api import Page, expect
import time

def test_valid_user_login(page: Page):
    """Test valid user login functionality"""
    
    # Navigate to login page
    page.goto("http://127.0.0.1:8000/signin")
    page.wait_for_load_state("networkidle")
    
    # Fill email field
    email_field = page.locator('input[type="email"]').or_(page.locator('input[placeholder*="email" i]')).first
    email_field.fill("nodeit@node.com")
    
    # Fill password field
    password_field = page.locator('input[type="password"]').or_(page.locator('input[placeholder*="password" i]')).first
    password_field.fill("NodeIT2024!")
    
    # Click login button
    login_button = page.locator('button[type="submit"]').or_(page.locator('button:has-text("Sign In")')).first
    login_button.click()
    
    # Wait for navigation or success
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Verify successful login
    current_url = page.url
    success_indicators = ["/dashboard", "/leads", "/contacts", "dashboard"]
    
    login_successful = any(indicator in current_url.lower() for indicator in success_indicators)
    
    if not login_successful:
        # Check for error messages
        error_elements = page.locator('[class*="error"], [class*="alert"], .text-red-500, .text-red-600')
        if error_elements.count() > 0:
            error_text = error_elements.first.text_content()
            raise AssertionError(f"Login failed with error: {error_text}")
        else:
            # Check page content for success indicators
            body_text = page.locator('body').text_content()
            if not any(word in body_text.lower() for word in ['dashboard', 'welcome', 'leads', 'contacts']):
                raise AssertionError("Login status unclear - no success indicators found")
    
    # Take screenshot for verification
    page.screenshot(path="test-results/auth_login_success.png")
    
    return True

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_valid_user_login(page)
            print("✅ TC_AUTH_001: Valid User Login - PASSED")
        except Exception as e:
            print(f"❌ TC_AUTH_001: Valid User Login - FAILED: {e}")
            page.screenshot(path="test-results/auth_login_failure.png")
        finally:
            browser.close()

