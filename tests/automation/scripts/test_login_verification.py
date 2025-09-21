#!/usr/bin/env python3
"""
Playwright test script to verify login functionality
"""

from playwright.sync_api import sync_playwright, expect
import time

def test_login_verification():
    """Test login with the provided credentials"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("🌐 Navigating to login page...")
            page.goto("http://localhost:5173/signin")
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")
            
            print("📝 Filling login form...")
            # Fill email field
            email_field = page.get_by_placeholder("Email").or_(page.get_by_label("Email"))
            email_field.fill("nodeit@node.com")
            
            # Fill password field
            password_field = page.get_by_placeholder("Password").or_(page.get_by_label("Password"))
            password_field.fill("NodeIT2024!")
            
            print("🔐 Submitting login form...")
            # Click login button
            login_button = page.get_by_role("button", name="Sign In").or_(page.get_by_text("Login"))
            login_button.click()
            
            # Wait for navigation or success message
            print("⏳ Waiting for login response...")
            page.wait_for_load_state("networkidle")
            
            # Check if we're redirected to dashboard or if there's a success message
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Check for success indicators
            if "/dashboard" in current_url or "/leads" in current_url:
                print("✅ Login successful! Redirected to dashboard/leads page.")
                return True
            elif page.get_by_text("Welcome").is_visible():
                print("✅ Login successful! Welcome message displayed.")
                return True
            elif page.get_by_text("Dashboard").is_visible():
                print("✅ Login successful! Dashboard content visible.")
                return True
            else:
                # Check for error messages
                error_elements = page.locator("[class*='error'], [class*='alert'], .text-red-500, .text-red-600")
                if error_elements.count() > 0:
                    error_text = error_elements.first.text_content()
                    print(f"❌ Login failed with error: {error_text}")
                else:
                    print("❌ Login failed - no clear success or error indicator found")
                    print("🔍 Page content preview:")
                    print(page.content()[:500] + "...")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            return False
        finally:
            # Take screenshot for debugging
            page.screenshot(path="test-results/login_test_screenshot.png")
            print("📸 Screenshot saved: test-results/login_test_screenshot.png")
            
            browser.close()

def main():
    """Main function"""
    print("🧪 NeuraCRM Login Verification Test")
    print("=" * 50)
    print("Email: nodeit@node.com")
    print("Password: NodeIT2024!")
    print("=" * 50)
    
    # Create results directory
    import os
    os.makedirs("test-results", exist_ok=True)
    
    success = test_login_verification()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Login verification test PASSED!")
        print("✅ Credentials are working correctly in the browser.")
    else:
        print("❌ Login verification test FAILED!")
        print("🔧 Please check the screenshot and fix any issues.")
    
    return success

if __name__ == "__main__":
    main()

