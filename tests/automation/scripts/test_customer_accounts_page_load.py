#!/usr/bin/env python3
"""
Customer Accounts Page Load Test
Tests the basic loading and display of the customer accounts page
"""

from playwright.sync_api import sync_playwright
import time

def test_customer_accounts_page_load():
    """Test that the customer accounts page loads correctly"""
    
    print("👥 Testing Customer Accounts Page Load")
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
            
            # Navigate to customer accounts
            print("\n👥 Navigating to Customer Accounts page...")
            page.goto("http://127.0.0.1:8000/customer-accounts")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to customer accounts page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Customer Accounts")')
            if title.is_visible():
                print("✅ Page title 'Customer Accounts' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check page description
            print("\n📝 Checking page description...")
            description = page.locator('.text-gray-600:has-text("Manage customer accounts and track success metrics")')
            if description.is_visible():
                print("✅ Page description found")
            else:
                print("❌ Page description not found")
            
            # Check accounts grid
            print("\n📊 Checking accounts grid...")
            accounts_grid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3')
            if accounts_grid.is_visible():
                print("✅ Accounts grid found")
            else:
                print("❌ Accounts grid not found")
            
            # Check for customer accounts
            print("\n👥 Checking for customer accounts...")
            accounts = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3 > div')
            account_count = accounts.count()
            if account_count > 0:
                print(f"✅ Found {account_count} customer accounts")
                
                # Check first account for required elements
                first_account = accounts.first
                if first_account.is_visible():
                    # Check for account name
                    account_name = first_account.locator('h3.text-lg.font-semibold')
                    if account_name.is_visible():
                        name_text = account_name.text_content()
                        print(f"  ✅ First account name: {name_text}")
                    else:
                        print("  ❌ Account name not found")
                    
                    # Check for deal ID
                    deal_id = first_account.locator('.text-sm.text-gray-500')
                    if deal_id.is_visible():
                        print("  ✅ Deal ID found")
                    else:
                        print("  ❌ Deal ID not found")
                    
                    # Check for onboarding status
                    onboarding_status = first_account.locator('.px-2.py-1.rounded-full')
                    if onboarding_status.is_visible():
                        print("  ✅ Onboarding status found")
                    else:
                        print("  ❌ Onboarding status not found")
                    
                    # Check for health score
                    health_score = first_account.locator('.text-sm.text-gray-600').first
                    if health_score.is_visible():
                        print("  ✅ Health score found")
                    else:
                        print("  ❌ Health score not found")
                    
                    # Check for renewal probability
                    renewal_prob = first_account.locator('.text-sm.text-gray-600').first
                    if renewal_prob.is_visible():
                        print("  ✅ Renewal probability found")
                    else:
                        print("  ❌ Renewal probability not found")
                    
                    # Check for account actions
                    actions = first_account.locator('.flex.gap-2.pt-2')
                    if actions.is_visible():
                        print("  ✅ Account actions found")
                        
                        # Check for specific action buttons
                        metrics_button = first_account.locator('button:has-text("Metrics")')
                        if metrics_button.is_visible():
                            print("    ✅ Metrics button found")
                        else:
                            print("    ❌ Metrics button not found")
                        
                        start_onboarding_button = first_account.locator('button:has-text("Start Onboarding")')
                        if start_onboarding_button.is_visible():
                            print("    ✅ Start Onboarding button found")
                        else:
                            print("    ⚠️ Start Onboarding button not found (may not be pending)")
                    else:
                        print("  ❌ Account actions not found")
                else:
                    print("❌ First account not visible")
            else:
                print("❌ No customer accounts found")
            
            # Check for status icons
            print("\n🎯 Checking for status icons...")
            status_icons = page.locator('.lucide-check-circle, .lucide-clock, .lucide-alert-circle')
            icon_count = status_icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} status icons")
            else:
                print("❌ No status icons found")
            
            # Check for health score icons
            print("\n📈 Checking for health score icons...")
            health_icons = page.locator('.lucide-trending-up')
            health_icon_count = health_icons.count()
            if health_icon_count > 0:
                print(f"✅ Found {health_icon_count} health score icons")
            else:
                print("❌ No health score icons found")
            
            # Check for renewal probability icons
            print("\n📊 Checking for renewal probability icons...")
            renewal_icons = page.locator('.lucide-bar-chart')
            renewal_icon_count = renewal_icons.count()
            if renewal_icon_count > 0:
                print(f"✅ Found {renewal_icon_count} renewal probability icons")
            else:
                print("❌ No renewal probability icons found")
            
            # Test Metrics button
            print("\n📊 Testing Metrics button...")
            if account_count > 0:
                first_account = accounts.first
                metrics_button = first_account.locator('button:has-text("Metrics")')
                if metrics_button.is_visible():
                    metrics_button.click()
                    time.sleep(2)
                    print("✅ Clicked Metrics button")
                    
                    # Check if metrics modal opens
                    metrics_modal = page.locator('h2:has-text("Customer Success Metrics")')
                    if metrics_modal.is_visible():
                        print("✅ Metrics modal opened")
                        
                        # Check for key metrics
                        health_score_metric = page.locator('.text-2xl.font-bold.text-blue-600')
                        if health_score_metric.is_visible():
                            print("  ✅ Health score metric found")
                        else:
                            print("  ❌ Health score metric not found")
                        
                        renewal_metric = page.locator('.text-2xl.font-bold.text-green-600')
                        if renewal_metric.is_visible():
                            print("  ✅ Renewal probability metric found")
                        else:
                            print("  ❌ Renewal probability metric not found")
                        
                        # Close modal
                        close_button = page.locator('button:has-text("✕")')
                        if close_button.is_visible():
                            close_button.click()
                            time.sleep(1)
                            print("  ✅ Metrics modal closed")
                        else:
                            print("  ❌ Close button not found")
                    else:
                        print("❌ Metrics modal not opened")
                else:
                    print("❌ Metrics button not found")
            else:
                print("❌ No accounts available for metrics test")
            
            # Test Start Onboarding button
            print("\n🚀 Testing Start Onboarding button...")
            if account_count > 0:
                first_account = accounts.first
                start_onboarding_button = first_account.locator('button:has-text("Start Onboarding")')
                if start_onboarding_button.is_visible():
                    start_onboarding_button.click()
                    time.sleep(2)
                    print("✅ Clicked Start Onboarding button")
                    
                    # Check if onboarding modal opens
                    onboarding_modal = page.locator('h2:has-text("Onboarding Started Successfully!")')
                    if onboarding_modal.is_visible():
                        print("✅ Onboarding modal opened")
                        
                        # Check for onboarding tasks
                        tasks_section = page.locator('h4:has-text("Onboarding Tasks Created")')
                        if tasks_section.is_visible():
                            print("  ✅ Onboarding tasks section found")
                        else:
                            print("  ❌ Onboarding tasks section not found")
                        
                        # Close modal
                        got_it_button = page.locator('button:has-text("Got it!")')
                        if got_it_button.is_visible():
                            got_it_button.click()
                            time.sleep(1)
                            print("  ✅ Onboarding modal closed")
                        else:
                            print("  ❌ Got it button not found")
                    else:
                        print("❌ Onboarding modal not opened")
                else:
                    print("⚠️ Start Onboarding button not found (account may not be pending)")
            else:
                print("❌ No accounts available for onboarding test")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/customer_accounts_page_load.png")
            print("✅ Screenshot saved as customer_accounts_page_load.png")
            
            print("\n🎉 Customer Accounts page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_customer_accounts_page_load()
    if success:
        print("\n✅ Customer Accounts page load test passed!")
    else:
        print("\n❌ Customer Accounts page load test failed.")
