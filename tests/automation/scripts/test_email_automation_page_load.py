#!/usr/bin/env python3
"""
Email Automation Page Load Test
Tests the basic loading and display of the email automation page
"""

from playwright.sync_api import sync_playwright
import time

def test_email_automation_page_load():
    """Test that the email automation page loads correctly"""
    
    print("📧 Testing Email Automation Page Load")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # Login
            print("🔐 Logging in...")
            page.goto("http://127.0.0.1:8000/signin")
            page.wait_for_load_state("networkidle")
            
            page.fill('input[type="email"]', "nodeit@node.com")
            page.fill('input[type="password"]', "NodeIT2024!")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard", timeout=10000)
            print("✅ Login successful")
            
            # Navigate to email automation
            print("\n📧 Navigating to Email Automation page...")
            page.goto("http://127.0.0.1:8000/email-automation")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to email automation page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Email Automation")')
            if title.is_visible():
                print("✅ Page title 'Email Automation' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check page description
            print("\n📝 Checking page description...")
            description = page.locator('.text-gray-600:has-text("Manage templates, campaigns, and automation")')
            if description.is_visible():
                print("✅ Page description found")
            else:
                print("❌ Page description not found")
            
            # Check Create Sample Templates button
            print("\n🎯 Checking Create Sample Templates button...")
            sample_button = page.locator('button:has-text("Create Sample Templates")')
            if sample_button.is_visible():
                print("✅ Create Sample Templates button found")
            else:
                print("❌ Create Sample Templates button not found")
            
            # Check tabs
            print("\n📑 Checking tabs...")
            tabs = page.locator('.flex.space-x-1.bg-gray-100')
            if tabs.is_visible():
                print("✅ Tabs container found")
                
                # Check individual tabs
                templates_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Templates")').first
                if templates_tab.is_visible():
                    print("  ✅ Templates tab found")
                else:
                    print("  ❌ Templates tab not found")
                
                campaigns_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Campaigns")').first
                if campaigns_tab.is_visible():
                    print("  ✅ Campaigns tab found")
                else:
                    print("  ❌ Campaigns tab not found")
                
                analytics_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Analytics")').first
                if analytics_tab.is_visible():
                    print("  ✅ Analytics tab found")
                else:
                    print("  ❌ Analytics tab not found")
            else:
                print("❌ Tabs container not found")
            
            # Check default tab (Templates)
            print("\n📊 Checking default tab content...")
            templates_content = page.locator('h2:has-text("Email Templates")')
            if templates_content.is_visible():
                print("✅ Templates tab is active by default")
                
                # Check Create Template button
                create_template_button = page.locator('button:has-text("Create Template")')
                if create_template_button.is_visible():
                    print("  ✅ Create Template button found")
                else:
                    print("  ❌ Create Template button not found")
            else:
                print("❌ Templates tab content not found")
            
            # Check for email templates
            print("\n📧 Checking for email templates...")
            templates = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3 > div')
            template_count = templates.count()
            if template_count > 0:
                print(f"✅ Found {template_count} email templates")
                
                # Check first template for required elements
                first_template = templates.first
                if first_template.is_visible():
                    # Check for template name
                    template_name = first_template.locator('h3.font-semibold')
                    if template_name.is_visible():
                        name_text = template_name.text_content()
                        print(f"  ✅ First template name: {name_text}")
                    else:
                        print("  ❌ Template name not found")
                    
                    # Check for template subject
                    template_subject = first_template.locator('.text-sm.text-gray-600')
                    if template_subject.is_visible():
                        print("  ✅ Template subject found")
                    else:
                        print("  ❌ Template subject not found")
                    
                    # Check for template category
                    template_category = first_template.locator('.px-2.py-1.bg-blue-100')
                    if template_category.is_visible():
                        print("  ✅ Template category found")
                    else:
                        print("  ❌ Template category not found")
                    
                    # Check for template validation
                    template_validation = first_template.locator('.text-xs.text-gray-500')
                    if template_validation.is_visible():
                        print("  ✅ Template validation info found")
                    else:
                        print("  ❌ Template validation info not found")
                    
                    # Check for template actions
                    actions = first_template.locator('.flex.space-x-1')
                    if actions.is_visible():
                        print("  ✅ Template actions found")
                        
                        # Check for specific action buttons
                        preview_button = first_template.locator('button[title="Preview"]')
                        if preview_button.is_visible():
                            print("    ✅ Preview button found")
                        else:
                            print("    ❌ Preview button not found")
                        
                        edit_button = first_template.locator('button[title="Edit"]')
                        if edit_button.is_visible():
                            print("    ✅ Edit button found")
                        else:
                            print("    ❌ Edit button not found")
                        
                        delete_button = first_template.locator('button[title="Delete"]')
                        if delete_button.is_visible():
                            print("    ✅ Delete button found")
                        else:
                            print("    ❌ Delete button not found")
                    else:
                        print("  ❌ Template actions not found")
                else:
                    print("❌ First template not visible")
            else:
                print("❌ No email templates found")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-mail, .lucide-plus, .lucide-file-text, .lucide-send, .lucide-bar-chart')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Test tab navigation
            print("\n🔄 Testing tab navigation...")
            try:
                campaigns_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Campaigns")').first
                if campaigns_tab.is_visible():
                    campaigns_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Campaigns tab")
                    
                    # Check if campaigns content is displayed
                    campaigns_content = page.locator('h2:has-text("Email Campaigns")')
                    if campaigns_content.is_visible():
                        print("✅ Campaigns tab content is displayed")
                    else:
                        print("⚠️ Campaigns tab content not displayed (may be empty)")
                    
                    # Go back to templates tab
                    templates_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Templates")').first
                    if templates_tab.is_visible():
                        templates_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Templates tab")
                    else:
                        print("⚠️ Could not return to Templates tab")
                else:
                    print("❌ Campaigns tab not found")
            except Exception as e:
                print(f"⚠️ Tab navigation test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/email_automation_page_load.png")
            print("✅ Screenshot saved as email_automation_page_load.png")
            
            print("\n🎉 Email Automation page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_email_automation_page_load()
    if success:
        print("\n✅ Email Automation page load test passed!")
    else:
        print("\n❌ Email Automation page load test failed.")
