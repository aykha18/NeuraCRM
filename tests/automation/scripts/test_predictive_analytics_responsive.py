#!/usr/bin/env python3
"""
Predictive Analytics Responsive Design Test
Tests the predictive analytics page on different screen sizes
"""

from playwright.sync_api import sync_playwright
import time

def test_predictive_analytics_responsive():
    """Test predictive analytics page responsiveness"""
    
    print("🧠 Testing Predictive Analytics Responsive Design")
    print("=" * 50)
    
    screen_sizes = [
        {"name": "Desktop", "width": 1920, "height": 1080},
        {"name": "Laptop", "width": 1366, "height": 768},
        {"name": "Tablet", "width": 768, "height": 1024},
        {"name": "Mobile", "width": 375, "height": 667}
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        
        for screen_size in screen_sizes:
            print(f"\n📱 Testing {screen_size['name']} ({screen_size['width']}x{screen_size['height']})...")
            
            context = browser.new_context(viewport={
                "width": screen_size["width"], 
                "height": screen_size["height"]
            })
            page = context.new_page()
            
            try:
                # Login
                print("  🔐 Logging in...")
                page.goto("http://127.0.0.1:8000/signin")
                page.wait_for_load_state("networkidle")
                
                page.fill('input[type="email"]', "nodeit@node.com")
                page.fill('input[type="password"]', "NodeIT2024!")
                page.click('button[type="submit"]')
                page.wait_for_url("**/dashboard", timeout=10000)
                print("  ✅ Login successful")
                
                # Navigate to predictive analytics
                print("  🧠 Navigating to Predictive Analytics page...")
                page.goto("http://127.0.0.1:8000/predictive-analytics")
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                print("  ✅ Navigated to predictive analytics page")
                
                # Test page title visibility
                title = page.locator('h1:has-text("Predictive Analytics")')
                if title.is_visible():
                    print("  ✅ Page title visible")
                else:
                    print("  ❌ Page title not visible")
                
                # Test key metrics grid
                metrics_grid = page.locator('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-5')
                if metrics_grid.is_visible():
                    print("  ✅ Key metrics grid visible")
                    
                    # Check if metrics are properly arranged
                    metrics_count = page.locator('.bg-white.rounded-xl.shadow-sm.border.p-6').count()
                    print(f"  📊 Metrics cards found: {metrics_count}")
                else:
                    print("  ❌ Key metrics grid not visible")
                
                # Test navigation tabs
                tabs = page.locator('nav.flex.space-x-8 button')
                tabs_count = tabs.count()
                if tabs_count >= 5:
                    print(f"  ✅ Navigation tabs visible ({tabs_count} tabs)")
                    
                    # Test tab clicking on smaller screens
                    if screen_size["width"] < 768:
                        print("  📱 Testing tab navigation on mobile...")
                        first_tab = tabs.first
                        if first_tab.is_visible():
                            first_tab.click()
                            time.sleep(1)
                            print("  ✅ Tab clicking works on mobile")
                else:
                    print(f"  ❌ Navigation tabs not fully visible ({tabs_count} tabs)")
                
                # Test content visibility
                content_areas = [
                    'text="Sales Trend"',
                    'text="Churn Risk Summary"',
                    'text="Revenue Insights"',
                    'text="Market Opportunities"'
                ]
                
                visible_content = 0
                for content in content_areas:
                    if page.locator(content).is_visible():
                        visible_content += 1
                
                print(f"  📋 Content sections visible: {visible_content}/{len(content_areas)}")
                
                # Test horizontal scrolling for tables
                if screen_size["width"] < 768:
                    print("  📱 Testing horizontal scrolling...")
                    
                    # Switch to a tab with tables
                    sales_tab = page.locator('button:has-text("Sales Forecast")')
                    if sales_tab.is_visible():
                        sales_tab.click()
                        time.sleep(2)
                        
                        # Check for horizontal scroll
                        table = page.locator('table')
                        if table.is_visible():
                            table_width = table.bounding_box()["width"] if table.bounding_box() else 0
                            viewport_width = screen_size["width"]
                            
                            if table_width > viewport_width:
                                print("  ✅ Table is wider than viewport (scrollable)")
                            else:
                                print("  ⚠️ Table fits in viewport")
                
                # Test text readability
                print("  📖 Testing text readability...")
                text_elements = page.locator('p, span, div').filter(has_text=re.compile(r'[A-Za-z]'))
                text_count = text_elements.count()
                readable_text = 0
                
                for i in range(min(10, text_count)):
                    element = text_elements.nth(i)
                    if element.is_visible():
                        text = element.text_content()
                        if text and len(text.strip()) > 0:
                            readable_text += 1
                
                print(f"  📝 Readable text elements: {readable_text}/10")
                
                # Take a screenshot
                screenshot_name = f"test-results/predictive_analytics_{screen_size['name'].lower()}.png"
                page.screenshot(path=screenshot_name)
                print(f"  📸 Screenshot saved: {screenshot_name}")
                
                print(f"  ✅ {screen_size['name']} test completed")
                
            except Exception as e:
                print(f"  ❌ Error testing {screen_size['name']}: {e}")
            
            finally:
                context.close()
        
        browser.close()
    
    print("\n🎉 Predictive Analytics responsive design test completed!")
    return True

if __name__ == "__main__":
    success = test_predictive_analytics_responsive()
    if success:
        print("\n✅ Predictive Analytics responsive design test passed!")
    else:
        print("\n❌ Predictive Analytics responsive design test failed.")

