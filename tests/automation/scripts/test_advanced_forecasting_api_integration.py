#!/usr/bin/env python3
"""
Advanced Forecasting API Integration Test
Tests API calls and data loading for advanced forecasting
"""

from playwright.sync_api import sync_playwright
import time
import requests
import json

def test_advanced_forecasting_api_integration():
    """Test API integration for advanced forecasting"""
    
    print("📈 Testing Advanced Forecasting API Integration")
    print("=" * 50)
    
    # Test API endpoints directly
    print("\n🔌 Testing API endpoints directly...")
    
    base_url = "http://127.0.0.1:8000"
    api_endpoints = [
        "/api/forecasting-models",
        "/api/forecasting-models/{id}/forecasts",
        "/api/forecasting-models/{id}/retrain"
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
    
    # Test forecasting models endpoint
    print(f"\n📡 Testing /api/forecasting-models...")
    try:
        response = requests.get(f"{base_url}/api/forecasting-models", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ /api/forecasting-models - Status: {response.status_code}")
            print(f"  📊 Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"  ✅ Found {len(data)} forecasting models")
                
                if len(data) > 0:
                    # Check first model structure
                    first_model = data[0]
                    expected_keys = [
                        "id", "name", "description", "model_type", "data_source",
                        "model_algorithm", "model_parameters", "training_data_period",
                        "forecast_horizon", "accuracy_metrics", "is_active",
                        "last_trained", "created_at", "updated_at"
                    ]
                    
                    for key in expected_keys:
                        if key in first_model:
                            print(f"    ✅ Found expected key: {key}")
                        else:
                            print(f"    ❌ Missing expected key: {key}")
                    
                    # Test model forecasts endpoint
                    model_id = first_model["id"]
                    print(f"\n📡 Testing /api/forecasting-models/{model_id}/forecasts...")
                    try:
                        forecasts_response = requests.get(f"{base_url}/api/forecasting-models/{model_id}/forecasts", headers=headers, timeout=10)
                        if forecasts_response.status_code == 200:
                            forecasts_data = forecasts_response.json()
                            print(f"  ✅ /api/forecasting-models/{model_id}/forecasts - Status: {forecasts_response.status_code}")
                            print(f"  📊 Response type: {type(forecasts_data)}")
                            
                            if isinstance(forecasts_data, list):
                                print(f"  ✅ Found {len(forecasts_data)} forecasts")
                                
                                if len(forecasts_data) > 0:
                                    # Check first forecast structure
                                    first_forecast = forecasts_data[0]
                                    forecast_expected_keys = [
                                        "id", "model_id", "forecast_type", "forecast_period",
                                        "forecast_date", "forecasted_value", "confidence_interval_lower",
                                        "confidence_interval_upper", "actual_value", "accuracy_score",
                                        "trend_direction", "seasonality_factor", "anomaly_detected",
                                        "forecast_quality_score", "insights", "recommendations",
                                        "generated_at"
                                    ]
                                    
                                    for key in forecast_expected_keys:
                                        if key in first_forecast:
                                            print(f"    ✅ Found expected key: {key}")
                                        else:
                                            print(f"    ❌ Missing expected key: {key}")
                                else:
                                    print("  ⚠️ No forecasts found for this model")
                            else:
                                print(f"  ❌ Forecasts response is not a list: {type(forecasts_data)}")
                        else:
                            print(f"  ❌ /api/forecasting-models/{model_id}/forecasts - Status: {forecasts_response.status_code}")
                    except requests.exceptions.Timeout:
                        print(f"  ⏰ /api/forecasting-models/{model_id}/forecasts - Timeout")
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ /api/forecasting-models/{model_id}/forecasts - Error: {e}")
                    
                    # Test model retrain endpoint
                    print(f"\n📡 Testing /api/forecasting-models/{model_id}/retrain...")
                    try:
                        retrain_response = requests.post(f"{base_url}/api/forecasting-models/{model_id}/retrain", headers=headers, timeout=30)
                        if retrain_response.status_code == 200:
                            print(f"  ✅ /api/forecasting-models/{model_id}/retrain - Status: {retrain_response.status_code}")
                        else:
                            print(f"  ❌ /api/forecasting-models/{model_id}/retrain - Status: {retrain_response.status_code}")
                    except requests.exceptions.Timeout:
                        print(f"  ⏰ /api/forecasting-models/{model_id}/retrain - Timeout")
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ /api/forecasting-models/{model_id}/retrain - Error: {e}")
                else:
                    print("  ⚠️ No forecasting models found")
            else:
                print(f"  ❌ Response is not a list: {type(data)}")
        else:
            print(f"  ❌ /api/forecasting-models - Status: {response.status_code}")
            print(f"  📝 Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"  ⏰ /api/forecasting-models - Timeout")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ /api/forecasting-models - Error: {e}")
    
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
            
            # Navigate to advanced forecasting
            print("\n📈 Navigating to Advanced Forecasting page...")
            page.goto("http://127.0.0.1:8000/advanced-forecasting")
            page.wait_for_load_state("networkidle")
            
            # Monitor network requests
            print("\n📡 Monitoring network requests...")
            
            # Wait for API calls to complete
            time.sleep(5)
            
            # Check if error message is shown
            error_message = page.locator('.bg-red-50:has-text("Failed to fetch")')
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
            
            # Check for forecasting models
            models = page.locator('.space-y-4 > div, .grid > div')
            model_count = models.count()
            if model_count > 0:
                print(f"  ✅ Found {model_count} forecasting models in UI")
                
                # Test model selection
                first_model = models.first
                if first_model.is_visible():
                    first_model.click()
                    time.sleep(2)
                    print("  ✅ Selected first model")
                    
                    # Check for forecasts display
                    forecasts_section = page.locator('h3:has-text("Forecasts"), h2:has-text("Forecasts")')
                    if forecasts_section.is_visible():
                        print("  ✅ Forecasts section displayed")
                    else:
                        print("  ❌ Forecasts section not displayed")
                    
                    # Check for accuracy metrics
                    accuracy_section = page.locator('text=/Accuracy|MAPE|RMSE/')
                    if accuracy_section.is_visible():
                        print("  ✅ Accuracy metrics displayed")
                    else:
                        print("  ❌ Accuracy metrics not displayed")
                else:
                    print("  ❌ First model not visible")
            else:
                print("  ❌ No forecasting models found in UI")
            
            # Test model creation form (if available)
            print("\n📝 Testing model creation form...")
            create_button = page.locator('button:has-text("Create New Model")')
            if create_button.is_visible():
                create_button.click()
                time.sleep(1)
                print("  ✅ Clicked Create New Model button")
                
                # Check for form fields
                form_fields = page.locator('input, select, textarea')
                field_count = form_fields.count()
                if field_count > 0:
                    print(f"  ✅ Found {field_count} form fields")
                else:
                    print("  ❌ No form fields found")
            else:
                print("  ❌ Create New Model button not found")
            
            # Test data formatting
            print("\n📝 Testing data formatting...")
            
            # Check for currency formatting
            currency_elements = page.locator('text=/\\$[\\d,]+/')
            if currency_elements.count() > 0:
                print(f"  ✅ Found {currency_elements.count()} currency formatted values")
            else:
                print("  ❌ No currency formatted values found")
            
            # Check for percentage formatting
            percentage_elements = page.locator('text=/\\d+%/')
            if percentage_elements.count() > 0:
                print(f"  ✅ Found {percentage_elements.count()} percentage formatted values")
            else:
                print("  ❌ No percentage formatted values found")
            
            # Check for date formatting
            date_elements = page.locator('text=/\\w{3}\\s+\\d{1,2},\\s+\\d{4}/')
            if date_elements.count() > 0:
                print(f"  ✅ Found {date_elements.count()} date formatted values")
            else:
                print("  ❌ No date formatted values found")
            
            # Check for charts/visualizations
            print("\n📈 Checking for charts and visualizations...")
            charts = page.locator('.recharts-wrapper, .chart, canvas, svg')
            chart_count = charts.count()
            if chart_count > 0:
                print(f"  ✅ Found {chart_count} chart(s) or visualization(s)")
            else:
                print("  ❌ No charts or visualizations found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/advanced_forecasting_api_integration.png")
            print("✅ Screenshot saved as advanced_forecasting_api_integration.png")
            
            print("\n🎉 Advanced Forecasting API integration test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during UI test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_advanced_forecasting_api_integration()
    if success:
        print("\n✅ Advanced Forecasting API integration test passed!")
    else:
        print("\n❌ Advanced Forecasting API integration test failed.")

