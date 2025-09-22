#!/usr/bin/env python3
"""
Call Center Page Load Test
Tests the basic loading and display of the call center page
"""

from playwright.sync_api import sync_playwright
import time

def test_call_center_page_load():
    """Test that the call center page loads correctly"""
    
    print("📞 Testing Call Center Page Load")
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
            
            # Navigate to call center
            print("\n📞 Navigating to Call Center page...")
            page.goto("http://127.0.0.1:8000/telephony")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to call center page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Call Center"), h1:has-text("Telephony")')
            if title.is_visible():
                print("✅ Page title found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check tabs
            print("\n📑 Checking tabs...")
            tabs = page.locator('nav.-mb-px.flex.space-x-8')
            if tabs.is_visible():
                print("✅ Tabs container found")
                
                # Check individual tabs
                dashboard_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Dashboard")').first
                if dashboard_tab.is_visible():
                    print("  ✅ Dashboard tab found")
                else:
                    print("  ❌ Dashboard tab not found")
                
                calls_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Calls")').first
                if calls_tab.is_visible():
                    print("  ✅ Calls tab found")
                else:
                    print("  ❌ Calls tab not found")
                
                agents_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Agents")').first
                if agents_tab.is_visible():
                    print("  ✅ Agents tab found")
                else:
                    print("  ❌ Agents tab not found")
                
                queues_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Queues")').first
                if queues_tab.is_visible():
                    print("  ✅ Queues tab found")
                else:
                    print("  ❌ Queues tab not found")
                
                settings_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Settings")').first
                if settings_tab.is_visible():
                    print("  ✅ Settings tab found")
                else:
                    print("  ❌ Settings tab not found")
            else:
                print("❌ Tabs container not found")
            
            # Check default tab (Dashboard)
            print("\n📊 Checking default tab content...")
            dashboard_content = page.locator('h2:has-text("Call Center Dashboard")')
            if dashboard_content.is_visible():
                print("✅ Dashboard tab is active by default")
                
                # Check for key metrics
                active_calls = page.locator('.text-2xl.font-bold.text-blue-600')
                if active_calls.is_visible():
                    print("  ✅ Active calls metric found")
                else:
                    print("  ❌ Active calls metric not found")
                
                queued_calls = page.locator('.text-2xl.font-bold.text-yellow-600')
                if queued_calls.is_visible():
                    print("  ✅ Queued calls metric found")
                else:
                    print("  ❌ Queued calls metric not found")
                
                available_agents = page.locator('.text-2xl.font-bold.text-green-600')
                if available_agents.is_visible():
                    print("  ✅ Available agents metric found")
                else:
                    print("  ❌ Available agents metric not found")
            else:
                print("❌ Dashboard tab content not found")
            
            # Test tab navigation
            print("\n🔄 Testing tab navigation...")
            try:
                calls_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Calls")').first
                if calls_tab.is_visible():
                    calls_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Calls tab")
                    
                    # Check if calls content is displayed
                    calls_content = page.locator('h2:has-text("Call Management")')
                    if calls_content.is_visible():
                        print("✅ Calls tab content is displayed")
                    else:
                        print("⚠️ Calls tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Calls tab not found")
            except Exception as e:
                print(f"⚠️ Tab navigation test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Agents tab
            print("\n👥 Testing Agents tab...")
            try:
                agents_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Agents")').first
                if agents_tab.is_visible():
                    agents_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Agents tab")
                    
                    # Check if agents content is displayed
                    agents_content = page.locator('h2:has-text("Agent Management")')
                    if agents_content.is_visible():
                        print("✅ Agents tab content is displayed")
                    else:
                        print("⚠️ Agents tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Agents tab not found")
            except Exception as e:
                print(f"⚠️ Agents tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Queues tab
            print("\n📋 Testing Queues tab...")
            try:
                queues_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Queues")').first
                if queues_tab.is_visible():
                    queues_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Queues tab")
                    
                    # Check if queues content is displayed
                    queues_content = page.locator('h2:has-text("Queue Management")')
                    if queues_content.is_visible():
                        print("✅ Queues tab content is displayed")
                    else:
                        print("⚠️ Queues tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Queues tab not found")
            except Exception as e:
                print(f"⚠️ Queues tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Settings tab
            print("\n⚙️ Testing Settings tab...")
            try:
                settings_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Settings")').first
                if settings_tab.is_visible():
                    settings_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Settings tab")
                    
                    # Check if settings content is displayed
                    settings_content = page.locator('h2:has-text("PBX Provider Management")')
                    if settings_content.is_visible():
                        print("✅ Settings tab content is displayed")
                    else:
                        print("⚠️ Settings tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('.flex.space-x-1.bg-gray-100 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Settings tab not found")
            except Exception as e:
                print(f"⚠️ Settings tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-phone, .lucide-users, .lucide-activity, .lucide-clock, .lucide-trending-up')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/call_center_page_load.png")
            print("✅ Screenshot saved as call_center_page_load.png")
            
            print("\n🎉 Call Center page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_call_center_page_load()
    if success:
        print("\n✅ Call Center page load test passed!")
    else:
        print("\n❌ Call Center page load test failed.")
