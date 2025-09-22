#!/usr/bin/env python3
"""
Predictive Analytics Page Load Test
Tests the basic loading and display of the predictive analytics page
"""

from playwright.sync_api import sync_playwright
import time

def test_predictive_analytics_page_load():
    """Test that the predictive analytics page loads correctly"""
    
    print("🧠 Testing Predictive Analytics Page Load")
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
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Predictive Analytics")')
            if title.is_visible():
                print("✅ Page title 'Predictive Analytics' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check AI-Powered badge
            print("\n🏷️ Checking AI-Powered badge...")
            ai_badge = page.locator('.bg-blue-100:has-text("AI-Powered")')
            if ai_badge.is_visible():
                print("✅ AI-Powered badge found")
            else:
                print("❌ AI-Powered badge not found")
            
            # Check demo mode warning
            print("\n⚠️ Checking demo mode warning...")
            demo_warning = page.locator('.bg-yellow-50:has-text("Demo Mode")')
            if demo_warning.is_visible():
                print("✅ Demo mode warning found")
            else:
                print("❌ Demo mode warning not found")
            
            # Check key metrics cards
            print("\n📊 Checking key metrics cards...")
            metrics_grid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-5')
            if metrics_grid.is_visible():
                print("✅ Key metrics grid found")
                
                # Check individual metrics
                metrics = [
                    "6M Forecasted Revenue",
                    "At-Risk Customers",
                    "High Risk", 
                    "Avg Deal Size",
                    "Opportunities"
                ]
                
                for metric in metrics:
                    metric_element = page.locator(f'text="{metric}"').first
                    if metric_element.is_visible():
                        print(f"  ✅ {metric} metric found")
                    else:
                        print(f"  ❌ {metric} metric not found")
            else:
                print("❌ Key metrics grid not found")
            
            # Check navigation tabs
            print("\n🗂️ Checking navigation tabs...")
            tabs = ["Overview", "Sales Forecast", "Churn Prediction", "Revenue Optimization", "Market Opportunities"]
            
            for tab in tabs:
                tab_element = page.locator(f'button:has-text("{tab}")')
                if tab_element.is_visible():
                    print(f"  ✅ {tab} tab found")
                else:
                    print(f"  ❌ {tab} tab not found")
            
            # Check if Overview tab is active by default
            print("\n🎯 Checking default active tab...")
            overview_tab = page.locator('button:has-text("Overview")')
            if overview_tab.is_visible():
                # Check if it has active styling
                class_attr = overview_tab.get_attribute('class')
                if 'bg-blue-100' in class_attr or 'text-blue-700' in class_attr:
                    print("✅ Overview tab is active by default")
                else:
                    print("⚠️ Overview tab found but may not be active")
            else:
                print("❌ Overview tab not found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/predictive_analytics_page_load.png")
            print("✅ Screenshot saved as predictive_analytics_page_load.png")
            
            print("\n🎉 Predictive Analytics page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_predictive_analytics_page_load()
    if success:
        print("\n✅ Predictive Analytics page load test passed!")
    else:
        print("\n❌ Predictive Analytics page load test failed.")
