#!/usr/bin/env python3
"""
Predictive Analytics API Integration Test
Tests API calls and data loading for predictive analytics
"""

from playwright.sync_api import sync_playwright
import time
import requests
import json

def test_predictive_analytics_api_integration():
    """Test API integration for predictive analytics"""
    
    print("🧠 Testing Predictive Analytics API Integration")
    print("=" * 50)
    
    # Test API endpoints directly
    print("\n🔌 Testing API endpoints directly...")
    
    base_url = "http://127.0.0.1:8000"
    api_endpoints = [
        "/api/predictive-analytics/health-check",
        "/api/predictive-analytics/dashboard-insights",
        "/api/predictive-analytics/sales-forecast",
        "/api/predictive-analytics/churn-prediction",
        "/api/predictive-analytics/revenue-optimization",
        "/api/predictive-analytics/market-opportunities"
    ]
    
    # First, get auth token
    auth_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    })
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return False
    
    # Test each endpoint
    for endpoint in api_endpoints:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {endpoint} - Status: {response.status_code}")
                print(f"  📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
                print(f"  📝 Response: {response.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  ⏰ {endpoint} - Timeout")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    # Test UI integration
    print("\n🖥️ Testing UI integration...")
    
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
            
            # Monitor network requests
            print("\n📡 Monitoring network requests...")
            
            # Wait for API calls to complete
            time.sleep(5)
            
            # Check if demo mode warning is shown (indicates fallback data)
            demo_warning = page.locator('.bg-yellow-50:has-text("Demo Mode")')
            if demo_warning.is_visible():
                print("  ⚠️ Demo mode warning shown - using fallback data")
            else:
                print("  ✅ No demo mode warning - API data may be loaded")
            
            # Check if error message is shown
            error_message = page.locator('.bg-red-50:has-text("API Error")')
            if error_message.is_visible():
                print("  ❌ API error message shown")
            else:
                print("  ✅ No API error message")
            
            # Check if data is displayed
            print("\n📊 Checking data display...")
            
            # Check for loading spinner
            loading_spinner = page.locator('.animate-spin')
            if loading_spinner.is_visible():
                print("  ⏳ Loading spinner still visible")
            else:
                print("  ✅ Loading spinner not visible")
            
            # Check for key metrics
            metrics_found = 0
            metrics = ["6M Forecasted Revenue", "At-Risk Customers", "High Risk", "Avg Deal Size", "Opportunities"]
            for metric in metrics:
                metric_element = page.locator(f'text="{metric}"').first
                if metric_element.is_visible():
                    metrics_found += 1
            
            print(f"  📈 Key metrics displayed: {metrics_found}/{len(metrics)}")
            
            # Check for numeric values
            numeric_values = page.locator('text=/\\$?[0-9,]+/')
            numeric_count = numeric_values.count()
            print(f"  🔢 Numeric values found: {numeric_count}")
            
            if numeric_count > 0:
                print("  ✅ Data is being displayed")
            else:
                print("  ❌ No numeric data found")
            
            # Test tab switching to trigger more API calls
            print("\n🗂️ Testing tab switching for API calls...")
            
            tabs = ["Sales Forecast", "Churn Prediction", "Revenue Optimization", "Market Opportunities"]
            for tab in tabs:
                tab_button = page.locator(f'button:has-text("{tab}")')
                if tab_button.is_visible():
                    tab_button.click()
                    time.sleep(2)
                    print(f"  ✅ Switched to {tab} tab")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/predictive_analytics_api_integration.png")
            print("✅ Screenshot saved as predictive_analytics_api_integration.png")
            
            print("\n🎉 Predictive Analytics API integration test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during UI test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_predictive_analytics_api_integration()
    if success:
        print("\n✅ Predictive Analytics API integration test passed!")
    else:
        print("\n❌ Predictive Analytics API integration test failed.")
