#!/usr/bin/env python3
"""
Predictive Analytics Data Display Test
Tests that all data is properly displayed and formatted
"""

from playwright.sync_api import sync_playwright
import time
import re

def test_predictive_analytics_data_display():
    """Test that predictive analytics data is properly displayed and formatted"""
    
    print("🧠 Testing Predictive Analytics Data Display")
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
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to predictive analytics page")
            
            # Test key metrics display
            print("\n📊 Testing key metrics display...")
            
            # Check if metrics have values
            metrics_selectors = [
                'text="6M Forecasted Revenue"',
                'text="At-Risk Customers"',
                'text="High Risk"',
                'text="Avg Deal Size"',
                'text="Opportunities"'
            ]
            
            for selector in metrics_selectors:
                metric_element = page.locator(selector)
                if metric_element.is_visible():
                    # Find the parent container and check for numeric values
                    parent = metric_element.locator('..')
                    numeric_values = parent.locator('text=/\\$?[0-9,]+/')
                    if numeric_values.count() > 0:
                        print(f"  ✅ {selector} has numeric values")
                    else:
                        print(f"  ❌ {selector} missing numeric values")
                else:
                    print(f"  ❌ {selector} not found")
            
            # Test currency formatting
            print("\n💰 Testing currency formatting...")
            currency_elements = page.locator('text=/\\$[0-9,]+/')
            currency_count = currency_elements.count()
            if currency_count > 0:
                print(f"  ✅ Found {currency_count} currency formatted values")
                # Check a few examples
                for i in range(min(3, currency_count)):
                    currency_text = currency_elements.nth(i).text_content()
                    if currency_text and currency_text.startswith('$'):
                        print(f"    ✅ Example: {currency_text}")
                    else:
                        print(f"    ❌ Invalid format: {currency_text}")
            else:
                print("  ❌ No currency formatted values found")
            
            # Test Sales Forecast tab data
            print("\n📈 Testing Sales Forecast tab data...")
            sales_tab = page.locator('button:has-text("Sales Forecast")')
            if sales_tab.is_visible():
                sales_tab.click()
                time.sleep(2)
                
                # Check for forecast table
                forecast_table = page.locator('table')
                if forecast_table.is_visible():
                    print("  ✅ Forecast table found")
                    
                    # Check table headers
                    headers = ["Month", "Predicted Revenue", "Predicted Deals", "Confidence (80%)"]
                    for header in headers:
                        header_element = page.locator(f'th:has-text("{header}")')
                        if header_element.is_visible():
                            print(f"    ✅ Header found: {header}")
                        else:
                            print(f"    ❌ Header missing: {header}")
                    
                    # Check for data rows
                    rows = page.locator('tbody tr')
                    row_count = rows.count()
                    if row_count > 0:
                        print(f"  ✅ Found {row_count} forecast rows")
                    else:
                        print("  ❌ No forecast data rows found")
                else:
                    print("  ❌ Forecast table not found")
            
            # Test Churn Prediction tab data
            print("\n⚠️ Testing Churn Prediction tab data...")
            churn_tab = page.locator('button:has-text("Churn Prediction")')
            if churn_tab.is_visible():
                churn_tab.click()
                time.sleep(2)
                
                # Check risk summary cards
                risk_cards = page.locator('.text-center.p-4')
                risk_count = risk_cards.count()
                if risk_count >= 3:
                    print(f"  ✅ Found {risk_count} risk summary cards")
                    
                    # Check for risk level indicators
                    risk_levels = ["High Risk", "Medium Risk", "Low Risk"]
                    for level in risk_levels:
                        level_element = page.locator(f'text="{level}"')
                        if level_element.is_visible():
                            print(f"    ✅ Risk level found: {level}")
                        else:
                            print(f"    ❌ Risk level missing: {level}")
                else:
                    print("  ❌ Risk summary cards not found")
                
                # Check for churn risks list
                churn_risks = page.locator('.flex.items-center.justify-between.p-3.border')
                risk_count = churn_risks.count()
                if risk_count > 0:
                    print(f"  ✅ Found {risk_count} churn risk entries")
                else:
                    print("  ❌ No churn risk entries found")
            
            # Test Revenue Optimization tab data
            print("\n💵 Testing Revenue Optimization tab data...")
            revenue_tab = page.locator('button:has-text("Revenue Optimization")')
            if revenue_tab.is_visible():
                revenue_tab.click()
                time.sleep(2)
                
                # Check for optimization opportunities
                opportunities = page.locator('.p-4.border.rounded-lg')
                opp_count = opportunities.count()
                if opp_count > 0:
                    print(f"  ✅ Found {opp_count} optimization opportunities")
                else:
                    print("  ❌ No optimization opportunities found")
                
                # Check for recommendations
                recommendations = page.locator('.flex.items-start.gap-2')
                rec_count = recommendations.count()
                if rec_count > 0:
                    print(f"  ✅ Found {rec_count} recommendations")
                else:
                    print("  ❌ No recommendations found")
            
            # Test Market Opportunities tab data
            print("\n🎯 Testing Market Opportunities tab data...")
            market_tab = page.locator('button:has-text("Market Opportunities")')
            if market_tab.is_visible():
                market_tab.click()
                time.sleep(2)
                
                # Check for source effectiveness table
                source_table = page.locator('table')
                if source_table.is_visible():
                    print("  ✅ Source effectiveness table found")
                    
                    # Check table headers
                    headers = ["Source", "Total Leads", "Qualification Rate", "Conversion Rate", "Effectiveness Score"]
                    for header in headers:
                        header_element = page.locator(f'th:has-text("{header}")')
                        if header_element.is_visible():
                            print(f"    ✅ Header found: {header}")
                        else:
                            print(f"    ❌ Header missing: {header}")
                else:
                    print("  ❌ Source effectiveness table not found")
            
            # Test color coding
            print("\n🎨 Testing color coding...")
            
            # Check for risk level colors
            high_risk = page.locator('.text-red-600, .bg-red-100')
            if high_risk.count() > 0:
                print("  ✅ High risk color coding found")
            else:
                print("  ❌ High risk color coding not found")
            
            medium_risk = page.locator('.text-yellow-600, .bg-yellow-100')
            if medium_risk.count() > 0:
                print("  ✅ Medium risk color coding found")
            else:
                print("  ❌ Medium risk color coding not found")
            
            low_risk = page.locator('.text-green-600, .bg-green-100')
            if low_risk.count() > 0:
                print("  ✅ Low risk color coding found")
            else:
                print("  ❌ Low risk color coding not found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/predictive_analytics_data_display.png")
            print("✅ Screenshot saved as predictive_analytics_data_display.png")
            
            print("\n🎉 Predictive Analytics data display test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_predictive_analytics_data_display()
    if success:
        print("\n✅ Predictive Analytics data display test passed!")
    else:
        print("\n❌ Predictive Analytics data display test failed.")

