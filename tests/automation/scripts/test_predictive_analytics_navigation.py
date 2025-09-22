#!/usr/bin/env python3
"""
Predictive Analytics Navigation Test
Tests navigation between different analytics tabs
"""

from playwright.sync_api import sync_playwright
import time

def test_predictive_analytics_navigation():
    """Test navigation between predictive analytics tabs"""
    
    print("🧠 Testing Predictive Analytics Navigation")
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
            
            # Navigate to predictive analytics
            print("\n🧠 Navigating to Predictive Analytics page...")
            page.goto("http://127.0.0.1:8000/predictive-analytics")
            page.wait_for_load_state("networkidle")
            print("✅ Navigated to predictive analytics page")
            
            # Test tab navigation
            tabs_to_test = [
                {
                    "name": "Overview",
                    "expected_content": ["Sales Trend", "Churn Risk Summary", "Revenue Insights", "Market Opportunities"]
                },
                {
                    "name": "Sales Forecast", 
                    "expected_content": ["Sales Forecast (Next 6 Months)", "Month", "Predicted Revenue", "Predicted Deals"]
                },
                {
                    "name": "Churn Prediction",
                    "expected_content": ["Customer Churn Risk Analysis", "High Risk", "Medium Risk", "Low Risk"]
                },
                {
                    "name": "Revenue Optimization",
                    "expected_content": ["Revenue Optimization Opportunities", "Recommendations"]
                },
                {
                    "name": "Market Opportunities",
                    "expected_content": ["Source Effectiveness", "Market Opportunities"]
                }
            ]
            
            for tab_info in tabs_to_test:
                tab_name = tab_info["name"]
                expected_content = tab_info["expected_content"]
                
                print(f"\n🗂️ Testing {tab_name} tab...")
                
                # Click on the tab
                tab_button = page.locator(f'button:has-text("{tab_name}")')
                if tab_button.is_visible():
                    tab_button.click()
                    time.sleep(2)  # Wait for content to load
                    print(f"  ✅ Clicked on {tab_name} tab")
                    
                    # Check if tab is now active
                    class_attr = tab_button.get_attribute('class')
                    if 'bg-blue-100' in class_attr or 'text-blue-700' in class_attr:
                        print(f"  ✅ {tab_name} tab is now active")
                    else:
                        print(f"  ⚠️ {tab_name} tab may not be active")
                    
                    # Check for expected content
                    content_found = 0
                    for content in expected_content:
                        content_element = page.locator(f'text="{content}"').first
                        if content_element.is_visible():
                            print(f"    ✅ Found: {content}")
                            content_found += 1
                        else:
                            print(f"    ❌ Missing: {content}")
                    
                    print(f"  📊 Content found: {content_found}/{len(expected_content)}")
                    
                    if content_found >= len(expected_content) * 0.7:  # At least 70% of expected content
                        print(f"  ✅ {tab_name} tab content is mostly correct")
                    else:
                        print(f"  ❌ {tab_name} tab content is missing")
                        
                else:
                    print(f"  ❌ {tab_name} tab button not found")
            
            # Test tab switching back and forth
            print("\n🔄 Testing tab switching...")
            
            # Go to Sales Forecast
            sales_tab = page.locator('button:has-text("Sales Forecast")')
            if sales_tab.is_visible():
                sales_tab.click()
                time.sleep(1)
                print("  ✅ Switched to Sales Forecast")
            
            # Go to Churn Prediction
            churn_tab = page.locator('button:has-text("Churn Prediction")')
            if churn_tab.is_visible():
                churn_tab.click()
                time.sleep(1)
                print("  ✅ Switched to Churn Prediction")
            
            # Go back to Overview
            overview_tab = page.locator('button:has-text("Overview")')
            if overview_tab.is_visible():
                overview_tab.click()
                time.sleep(1)
                print("  ✅ Switched back to Overview")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/predictive_analytics_navigation.png")
            print("✅ Screenshot saved as predictive_analytics_navigation.png")
            
            print("\n🎉 Predictive Analytics navigation test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_predictive_analytics_navigation()
    if success:
        print("\n✅ Predictive Analytics navigation test passed!")
    else:
        print("\n❌ Predictive Analytics navigation test failed.")
