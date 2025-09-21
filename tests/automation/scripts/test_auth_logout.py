#!/usr/bin/env python3
"""
Playwright automation script for TC_AUTH_005: User Logout
"""

from playwright.sync_api import Page, expect
import time

def test_user_logout(page: Page):
    """Test user logout functionality"""
    
    # First, login to the system
    page.goto("http://127.0.0.1:8000/signin")
    page.wait_for_load_state("networkidle")
    
    # Fill login credentials
    email_field = page.locator('input[type="email"]').or_(page.locator('input[placeholder*="email" i]')).first
    email_field.fill("nodeit@node.com")
    
    password_field = page.locator('input[type="password"]').or_(page.locator('input[placeholder*="password" i]')).first
    password_field.fill("NodeIT2024!")
    
    # Click login button
    login_button = page.locator('button[type="submit"]').or_(page.locator('button:has-text("Sign In")')).first
    login_button.click()
    
    # Wait for login to complete
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Now test logout functionality
    # Look for user profile menu or logout button
    logout_selectors = [
        'button:has-text("Logout")',
        'button:has-text("Sign Out")',
        'button:has-text("Log Out")',
        '[data-testid="logout"]',
        '[aria-label*="logout" i]',
        '[aria-label*="sign out" i]'
    ]
    
    logout_button = None
    for selector in logout_selectors:
        try:
            logout_button = page.locator(selector).first
            if logout_button.is_visible():
                break
        except:
            continue
    
    if logout_button and logout_button.is_visible():
        logout_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Check if redirected to login page
        current_url = page.url
        if "/signin" in current_url or "/login" in current_url:
            print("✅ Successfully logged out and redirected to login page")
            return True
        else:
            raise AssertionError(f"Logout failed - still on page: {current_url}")
    else:
        # Try looking for user profile dropdown
        profile_selectors = [
            '[data-testid="user-menu"]',
            '[aria-label*="user" i]',
            '[aria-label*="profile" i]',
            'button:has-text("Profile")',
            'div:has-text("nodeit@node.com")'
        ]
        
        profile_element = None
        for selector in profile_selectors:
            try:
                profile_element = page.locator(selector).first
                if profile_element.is_visible():
                    break
            except:
                continue
        
        if profile_element and profile_element.is_visible():
            profile_element.click()
            time.sleep(1)
            
            # Look for logout option in dropdown
            logout_option = page.locator('button:has-text("Logout"), a:has-text("Logout"), div:has-text("Logout")').first
            if logout_option.is_visible():
                logout_option.click()
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                
                current_url = page.url
                if "/signin" in current_url or "/login" in current_url:
                    print("✅ Successfully logged out via profile menu")
                    return True
        
        # If no logout button found, try keyboard shortcut or direct navigation
        print("⚠️ No logout button found, trying alternative methods")
        
        # Try going directly to logout endpoint
        page.goto("http://127.0.0.1:8000/logout")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        current_url = page.url
        if "/signin" in current_url or "/login" in current_url:
            print("✅ Successfully logged out via direct navigation")
            return True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/auth_logout.png")
    
    raise AssertionError("Logout functionality not found or not working")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_user_logout(page)
            print("✅ TC_AUTH_005: User Logout - PASSED")
        except Exception as e:
            print(f"❌ TC_AUTH_005: User Logout - FAILED: {e}")
            page.screenshot(path="test-results/auth_logout_failure.png")
        finally:
            browser.close()

