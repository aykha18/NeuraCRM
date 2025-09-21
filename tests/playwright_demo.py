#!/usr/bin/env python3
"""
Simple Playwright demo for NeuraCRM UI testing
"""

from playwright.sync_api import sync_playwright
import time

def test_login_ui():
    """Test login functionality in the browser"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("🌐 Testing NeuraCRM UI Login")
            print("=" * 40)
            
            # Navigate to login page
            print("1. Navigating to login page...")
            page.goto("http://127.0.0.1:8000/signin")
            page.wait_for_load_state("networkidle")
            print("   ✅ Login page loaded")
            
            # Check if we can find login form elements
            print("2. Checking login form elements...")
            
            # Try different selectors for email field
            email_selectors = [
                'input[type="email"]',
                'input[placeholder*="email" i]',
                'input[name*="email" i]',
                'input[id*="email" i]'
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = page.locator(selector).first
                    if email_field.is_visible():
                        break
                except:
                    continue
            
            if email_field and email_field.is_visible():
                print("   ✅ Email field found")
                email_field.fill("nodeit@node.com")
            else:
                print("   ⚠️ Email field not found - trying alternative approach")
                # Try to find any input field
                inputs = page.locator('input').all()
                if len(inputs) >= 2:
                    inputs[0].fill("nodeit@node.com")  # First input
                    print("   ✅ Filled first input field")
                else:
                    print("   ❌ No input fields found")
                    return False
            
            # Try different selectors for password field
            password_selectors = [
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[name*="password" i]',
                'input[id*="password" i]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = page.locator(selector).first
                    if password_field.is_visible():
                        break
                except:
                    continue
            
            if password_field and password_field.is_visible():
                print("   ✅ Password field found")
                password_field.fill("NodeIT2024!")
            else:
                print("   ⚠️ Password field not found - trying alternative approach")
                # Try to find second input field
                inputs = page.locator('input').all()
                if len(inputs) >= 2:
                    inputs[1].fill("NodeIT2024!")  # Second input
                    print("   ✅ Filled second input field")
                else:
                    print("   ❌ No second input field found")
                    return False
            
            # Try to find and click login button
            print("3. Looking for login button...")
            button_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Login")',
                'button:has-text("Log In")',
                'input[type="submit"]'
            ]
            
            login_button = None
            for selector in button_selectors:
                try:
                    login_button = page.locator(selector).first
                    if login_button.is_visible():
                        break
                except:
                    continue
            
            if login_button and login_button.is_visible():
                print("   ✅ Login button found")
                login_button.click()
                print("   ✅ Login button clicked")
            else:
                print("   ⚠️ Login button not found - trying Enter key")
                page.keyboard.press("Enter")
                print("   ✅ Pressed Enter key")
            
            # Wait for response
            print("4. Waiting for login response...")
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Give it a moment
            
            # Check if login was successful
            current_url = page.url
            print(f"   📍 Current URL: {current_url}")
            
            # Check for success indicators
            success_indicators = [
                "/dashboard",
                "/leads", 
                "/contacts",
                "dashboard",
                "welcome"
            ]
            
            login_successful = False
            for indicator in success_indicators:
                if indicator.lower() in current_url.lower():
                    print(f"   ✅ Login successful! Found indicator: {indicator}")
                    login_successful = True
                    break
            
            if not login_successful:
                # Check for error messages
                error_elements = page.locator('[class*="error"], [class*="alert"], .text-red-500, .text-red-600, [role="alert"]')
                if error_elements.count() > 0:
                    error_text = error_elements.first.text_content()
                    print(f"   ❌ Login failed with error: {error_text}")
                else:
                    # Check page content for clues
                    page_title = page.title()
                    print(f"   📄 Page title: {page_title}")
                    
                    # Look for any text that might indicate success
                    body_text = page.locator('body').text_content()
                    if any(word in body_text.lower() for word in ['dashboard', 'welcome', 'leads', 'contacts']):
                        print("   ✅ Login appears successful based on page content")
                        login_successful = True
                    else:
                        print("   ⚠️ Login status unclear - taking screenshot for analysis")
                        login_successful = False
            
            # Take screenshot
            import os
            os.makedirs("test-results", exist_ok=True)
            screenshot_path = "test-results/ui_login_test.png"
            page.screenshot(path=screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")
            
            return login_successful
            
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            return False
        finally:
            browser.close()

def main():
    """Main function"""
    print("🎭 NeuraCRM Playwright UI Test Demo")
    print("=" * 50)
    print("This demonstrates UI testing with Playwright")
    print("=" * 50)
    
    success = test_login_ui()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 UI test completed successfully!")
        print("✅ Login functionality works in the browser.")
    else:
        print("⚠️ UI test had issues.")
        print("🔧 Check the screenshot for details.")
    
    print("\n💡 This demonstrates:")
    print("1. Browser automation with Playwright")
    print("2. Element finding and interaction")
    print("3. Form filling and submission")
    print("4. Screenshot capture for debugging")
    print("5. Success/failure detection")

if __name__ == "__main__":
    main()
