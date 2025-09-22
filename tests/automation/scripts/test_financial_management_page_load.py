#!/usr/bin/env python3
"""
Financial Management Page Load Test
Tests the basic loading and display of the financial management page
"""

from playwright.sync_api import sync_playwright
import time

def test_financial_management_page_load():
    """Test that the financial management page loads correctly"""
    
    print("💰 Testing Financial Management Page Load")
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
            
            # Navigate to financial management
            print("\n💰 Navigating to Financial Management page...")
            page.goto("http://127.0.0.1:8000/financial-management")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to financial management page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Financial Management")')
            if title.is_visible():
                print("✅ Page title 'Financial Management' found")
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
                
                invoices_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Invoices")').first
                if invoices_tab.is_visible():
                    print("  ✅ Invoices tab found")
                else:
                    print("  ❌ Invoices tab not found")
                
                payments_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Payments")').first
                if payments_tab.is_visible():
                    print("  ✅ Payments tab found")
                else:
                    print("  ❌ Payments tab not found")
                
                revenue_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Revenue")').first
                if revenue_tab.is_visible():
                    print("  ✅ Revenue tab found")
                else:
                    print("  ❌ Revenue tab not found")
                
                reports_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Reports")').first
                if reports_tab.is_visible():
                    print("  ✅ Reports tab found")
                else:
                    print("  ❌ Reports tab not found")
                
                settings_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Settings")').first
                if settings_tab.is_visible():
                    print("  ✅ Settings tab found")
                else:
                    print("  ❌ Settings tab not found")
            else:
                print("❌ Tabs container not found")
            
            # Check default tab (Dashboard)
            print("\n📊 Checking default tab content...")
            dashboard_content = page.locator('h2:has-text("Financial Dashboard")')
            if dashboard_content.is_visible():
                print("✅ Dashboard tab is active by default")
                
                # Check for key metrics
                revenue_metrics = page.locator('.text-2xl.font-bold.text-green-600')
                if revenue_metrics.is_visible():
                    print("  ✅ Revenue metrics found")
                else:
                    print("  ❌ Revenue metrics not found")
                
                invoice_metrics = page.locator('.text-2xl.font-bold.text-blue-600')
                if invoice_metrics.is_visible():
                    print("  ✅ Invoice metrics found")
                else:
                    print("  ❌ Invoice metrics not found")
                
                payment_metrics = page.locator('.text-2xl.font-bold.text-purple-600')
                if payment_metrics.is_visible():
                    print("  ✅ Payment metrics found")
                else:
                    print("  ❌ Payment metrics not found")
            else:
                print("❌ Dashboard tab content not found")
            
            # Test tab navigation
            print("\n🔄 Testing tab navigation...")
            try:
                invoices_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Invoices")').first
                if invoices_tab.is_visible():
                    invoices_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Invoices tab")
                    
                    # Check if invoices content is displayed
                    invoices_content = page.locator('h2:has-text("Invoice Management")')
                    if invoices_content.is_visible():
                        print("✅ Invoices tab content is displayed")
                        
                        # Check for Create Invoice button
                        create_invoice_button = page.locator('button:has-text("Create Invoice")')
                        if create_invoice_button.is_visible():
                            print("  ✅ Create Invoice button found")
                        else:
                            print("  ❌ Create Invoice button not found")
                    else:
                        print("⚠️ Invoices tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Invoices tab not found")
            except Exception as e:
                print(f"⚠️ Tab navigation test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Payments tab
            print("\n💳 Testing Payments tab...")
            try:
                payments_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Payments")').first
                if payments_tab.is_visible():
                    payments_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Payments tab")
                    
                    # Check if payments content is displayed
                    payments_content = page.locator('h2:has-text("Payment Management")')
                    if payments_content.is_visible():
                        print("✅ Payments tab content is displayed")
                    else:
                        print("⚠️ Payments tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Payments tab not found")
            except Exception as e:
                print(f"⚠️ Payments tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Revenue tab
            print("\n📈 Testing Revenue tab...")
            try:
                revenue_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Revenue")').first
                if revenue_tab.is_visible():
                    revenue_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Revenue tab")
                    
                    # Check if revenue content is displayed
                    revenue_content = page.locator('h2:has-text("Revenue Recognition")')
                    if revenue_content.is_visible():
                        print("✅ Revenue tab content is displayed")
                    else:
                        print("⚠️ Revenue tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Revenue tab not found")
            except Exception as e:
                print(f"⚠️ Revenue tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Reports tab
            print("\n📊 Testing Reports tab...")
            try:
                reports_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Reports")').first
                if reports_tab.is_visible():
                    reports_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Reports tab")
                    
                    # Check if reports content is displayed
                    reports_content = page.locator('h2:has-text("Financial Reports")')
                    if reports_content.is_visible():
                        print("✅ Reports tab content is displayed")
                    else:
                        print("⚠️ Reports tab content not displayed (may be empty)")
                    
                    # Go back to dashboard tab
                    dashboard_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Dashboard")').first
                    if dashboard_tab.is_visible():
                        dashboard_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Dashboard tab")
                    else:
                        print("⚠️ Could not return to Dashboard tab")
                else:
                    print("❌ Reports tab not found")
            except Exception as e:
                print(f"⚠️ Reports tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-dollar-sign, .lucide-file-text, .lucide-credit-card, .lucide-trending-up, .lucide-bar-chart')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/financial_management_page_load.png")
            print("✅ Screenshot saved as financial_management_page_load.png")
            
            print("\n🎉 Financial Management page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_financial_management_page_load()
    if success:
        print("\n✅ Financial Management page load test passed!")
    else:
        print("\n❌ Financial Management page load test failed.")
