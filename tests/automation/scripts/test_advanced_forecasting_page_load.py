#!/usr/bin/env python3
"""
Advanced Forecasting Page Load Test
Tests the basic loading and display of the advanced forecasting page
"""

from playwright.sync_api import sync_playwright
import time

def test_advanced_forecasting_page_load():
    """Test that the advanced forecasting page loads correctly"""
    
    print("📈 Testing Advanced Forecasting Page Load")
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
            
            # Navigate to advanced forecasting
            print("\n📈 Navigating to Advanced Forecasting page...")
            page.goto("http://127.0.0.1:8000/advanced-forecasting")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to advanced forecasting page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Advanced Forecasting")')
            if title.is_visible():
                print("✅ Page title 'Advanced Forecasting' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check page description
            print("\n📝 Checking page description...")
            description = page.locator('.text-gray-600:has-text("ML-powered sales forecasting")')
            if description.is_visible():
                print("✅ Page description found")
            else:
                print("❌ Page description not found")
            
            # Check forecasting models section
            print("\n📊 Checking forecasting models section...")
            models_section = page.locator('.bg-white.rounded-lg.shadow-lg')
            if models_section.is_visible():
                print("✅ Forecasting models section found")
                
                # Check for models heading
                models_heading = page.locator('h2:has-text("Forecasting Models")')
                if models_heading.is_visible():
                    print("  ✅ Forecasting Models heading found")
                else:
                    print("  ❌ Forecasting Models heading not found")
                
                # Check for create model button
                create_button = page.locator('button:has-text("Create New Model")')
                if create_button.is_visible():
                    print("  ✅ Create New Model button found")
                else:
                    print("  ❌ Create New Model button not found")
            else:
                print("❌ Forecasting models section not found")
            
            # Check for forecasting models
            print("\n📈 Checking for forecasting models...")
            models = page.locator('.space-y-4 > div, .grid > div')
            model_count = models.count()
            if model_count > 0:
                print(f"✅ Found {model_count} forecasting models")
                
                # Check first model for required elements
                first_model = models.first
                if first_model.is_visible():
                    # Check for model name
                    model_name = first_model.locator('h3.font-semibold, .font-semibold')
                    if model_name.is_visible():
                        name_text = model_name.text_content()
                        print(f"  ✅ First model name: {name_text}")
                    else:
                        print("  ❌ Model name not found")
                    
                    # Check for model description
                    model_desc = first_model.locator('.text-sm.text-gray-600, .text-gray-600')
                    if model_desc.is_visible():
                        print("  ✅ Model description found")
                    else:
                        print("  ❌ Model description not found")
                    
                    # Check for model type
                    model_type = first_model.locator('.px-2.py-1.rounded-full, .badge')
                    if model_type.is_visible():
                        type_text = model_type.text_content()
                        print(f"  ✅ Model type badge: {type_text}")
                    else:
                        print("  ❌ Model type badge not found")
                    
                    # Check for model algorithm
                    algorithm = first_model.locator('text=/ARIMA|Prophet|Linear_Regression|Exponential_Smoothing/')
                    if algorithm.is_visible():
                        print("  ✅ Model algorithm found")
                    else:
                        print("  ❌ Model algorithm not found")
                    
                    # Check for accuracy metrics
                    accuracy = first_model.locator('text=/Accuracy|MAPE|RMSE/')
                    if accuracy.is_visible():
                        print("  ✅ Accuracy metrics found")
                    else:
                        print("  ❌ Accuracy metrics not found")
                    
                    # Check for last trained date
                    last_trained = first_model.locator('text=/Last trained|Updated/')
                    if last_trained.is_visible():
                        print("  ✅ Last trained date found")
                    else:
                        print("  ❌ Last trained date not found")
                else:
                    print("❌ First model not visible")
            else:
                print("❌ No forecasting models found")
            
            # Check for forecasts display section
            print("\n📊 Checking forecasts display section...")
            forecasts_section = page.locator('.bg-white.rounded-lg.shadow-lg.border')
            if forecasts_section.is_visible():
                print("✅ Forecasts display section found")
                
                # Check for forecasts heading
                forecasts_heading = page.locator('h3:has-text("Forecasts"), h2:has-text("Forecasts")')
                if forecasts_heading.is_visible():
                    print("  ✅ Forecasts heading found")
                else:
                    print("  ❌ Forecasts heading not found")
            else:
                print("❌ Forecasts display section not found")
            
            # Check for charts/visualizations
            print("\n📈 Checking for charts and visualizations...")
            charts = page.locator('.recharts-wrapper, .chart, canvas, svg')
            chart_count = charts.count()
            if chart_count > 0:
                print(f"✅ Found {chart_count} chart(s) or visualization(s)")
            else:
                print("❌ No charts or visualizations found")
            
            # Check for model creation form (if available)
            print("\n📝 Checking for model creation form...")
            form = page.locator('form, .form')
            if form.is_visible():
                print("✅ Model creation form found")
                
                # Check for form fields
                form_fields = page.locator('input, select, textarea')
                field_count = form_fields.count()
                if field_count > 0:
                    print(f"  ✅ Found {field_count} form fields")
                else:
                    print("  ❌ No form fields found")
            else:
                print("⚠️ Model creation form not found (may be in modal)")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-bar-chart, .lucide-trending-up, .lucide-brain, .lucide-zap')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/advanced_forecasting_page_load.png")
            print("✅ Screenshot saved as advanced_forecasting_page_load.png")
            
            print("\n🎉 Advanced Forecasting page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_advanced_forecasting_page_load()
    if success:
        print("\n✅ Advanced Forecasting page load test passed!")
    else:
        print("\n❌ Advanced Forecasting page load test failed.")

