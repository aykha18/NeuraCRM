#!/usr/bin/env python3
"""
Test Kanban Layout Improvements
Tests the improved layout with narrower columns and better scrolling
"""

from playwright.sync_api import sync_playwright
import time

def test_kanban_layout_improvements():
    """Test the improved Kanban layout"""
    
    print("🎨 Testing Kanban Layout Improvements")
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
            
            # Navigate to deals
            print("\n📋 Navigating to deals (Kanban) page...")
            page.goto("http://127.0.0.1:8000/kanban")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector('[data-rbd-droppable-id], .flex-shrink-0.w-64', timeout=15000)
            print("✅ Navigated to deals page")
            
            # Check for improved layout elements
            print("\n🔍 Checking layout improvements...")
            
            # Check for narrower columns (w-64 instead of w-72)
            narrow_columns = page.locator('.w-64')
            if narrow_columns.count() > 0:
                print(f"✅ Found {narrow_columns.count()} narrow columns (w-64)")
            else:
                print("❌ Narrow columns not found")
            
            # Check for improved scrollbar styling
            kanban_container = page.locator('.overflow-x-auto')
            if kanban_container.count() > 0:
                print("✅ Found improved scrollbar container")
            else:
                print("❌ Improved scrollbar container not found")
            
            # Check for gradient fade indicator
            gradient_fade = page.locator('.bg-gradient-to-l')
            if gradient_fade.count() > 0:
                print("✅ Found gradient fade indicator for scrolling")
            else:
                print("❌ Gradient fade indicator not found")
            
            # Check for compact deal cards
            compact_cards = page.locator('.p-3')  # Reduced padding
            if compact_cards.count() > 0:
                print(f"✅ Found {compact_cards.count()} compact deal cards (p-3)")
            else:
                print("❌ Compact deal cards not found")
            
            # Check for smaller text sizes
            small_text = page.locator('.text-xs')
            if small_text.count() > 0:
                print(f"✅ Found {small_text.count()} elements with smaller text (text-xs)")
            else:
                print("❌ Smaller text elements not found")
            
            # Test horizontal scrolling
            print("\n🔄 Testing horizontal scrolling...")
            
            # Get initial scroll position
            initial_scroll = page.evaluate("document.querySelector('.overflow-x-auto').scrollLeft")
            print(f"📊 Initial scroll position: {initial_scroll}")
            
            # Scroll right
            page.evaluate("document.querySelector('.overflow-x-auto').scrollLeft += 200")
            time.sleep(1)
            
            new_scroll = page.evaluate("document.querySelector('.overflow-x-auto').scrollLeft")
            print(f"📊 After scroll: {new_scroll}")
            
            if new_scroll > initial_scroll:
                print("✅ Horizontal scrolling is working")
            else:
                print("❌ Horizontal scrolling not working")
            
            # Check if all stages are visible
            stages = page.locator('[data-rbd-droppable-id], .flex-shrink-0.w-64')
            stage_count = stages.count()
            print(f"📊 Found {stage_count} stages")
            
            if stage_count >= 8:
                print("✅ All 8 stages are present")
            else:
                print(f"⚠️ Only {stage_count} stages found (expected 8)")
            
            # Take a screenshot to see the improved layout
            print("\n📸 Taking screenshot of improved layout...")
            page.screenshot(path="kanban_improved_layout.png")
            print("✅ Screenshot saved as kanban_improved_layout.png")
            
            print("\n🎉 Layout improvements test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during layout test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_kanban_layout_improvements()
    if success:
        print("\n✅ Kanban layout improvements test completed!")
    else:
        print("\n❌ Kanban layout improvements test failed.")
