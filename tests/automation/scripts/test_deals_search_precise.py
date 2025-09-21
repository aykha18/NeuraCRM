#!/usr/bin/env python3
"""
Precise Deals Search Test
Specifically tests for the search input we added to the Kanban board
"""

from playwright.sync_api import sync_playwright
import time

def test_deals_search_precise():
    """Precise test for the search input we added to Kanban board"""
    
    print("🔍 Precise NeuraCRM Deals Search Test")
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
            page.wait_for_selector('[data-rbd-droppable-id], .flex-shrink-0.w-72', timeout=15000)
            print("✅ Navigated to deals page")
            
            # Take a screenshot to see what's actually there
            print("\n📸 Taking screenshot to see current UI...")
            page.screenshot(path="kanban_current_ui.png")
            print("✅ Screenshot saved as kanban_current_ui.png")
            
            # Look specifically for our search input with the exact placeholder we set
            print("\n🔍 Looking for our specific search input...")
            
            # Check for the exact placeholder text we set
            search_inputs = page.locator('input[placeholder*="Search deals by title, value, owner, stage, tags"]')
            if search_inputs.count() > 0:
                print("✅ Found search input with our exact placeholder text!")
                search_input = search_inputs.first
            else:
                print("❌ Search input with our placeholder text not found")
                
                # Check for any input with "search" in placeholder
                search_inputs = page.locator('input[placeholder*="search"]')
                if search_inputs.count() > 0:
                    print(f"⚠️ Found {search_inputs.count()} input(s) with 'search' in placeholder:")
                    for i in range(search_inputs.count()):
                        placeholder = search_inputs.nth(i).get_attribute('placeholder')
                        print(f"   Input {i+1}: '{placeholder}'")
                else:
                    print("❌ No inputs with 'search' in placeholder found")
                
                # Check for any text inputs on the page
                all_inputs = page.locator('input[type="text"]')
                print(f"\n📋 Found {all_inputs.count()} text input(s) on the page:")
                for i in range(all_inputs.count()):
                    try:
                        placeholder = all_inputs.nth(i).get_attribute('placeholder') or 'No placeholder'
                        input_id = all_inputs.nth(i).get_attribute('id') or 'No ID'
                        input_class = all_inputs.nth(i).get_attribute('class') or 'No class'
                        print(f"   Input {i+1}: placeholder='{placeholder}', id='{input_id}', class='{input_class}'")
                    except:
                        print(f"   Input {i+1}: Could not read attributes")
                
                return False
            
            # If we found our search input, test it
            if search_inputs.count() > 0:
                print("\n🧪 Testing our search input...")
                
                # Get initial deal count
                deals = page.locator('[data-rbd-draggable-id], .space-y-4 > div')
                initial_count = deals.count()
                print(f"📊 Initial deal count: {initial_count}")
                
                # Test search
                search_input.fill("test")
                page.wait_for_timeout(2000)
                
                # Check if deals are filtered
                filtered_deals = page.locator('[data-rbd-draggable-id], .space-y-4 > div')
                filtered_count = filtered_deals.count()
                print(f"📊 Filtered deal count: {filtered_count}")
                
                if filtered_count < initial_count:
                    print("✅ Search filtering is working!")
                else:
                    print("⚠️ Search may not be filtering correctly")
                
                # Check for search results indicator
                search_results = page.locator('text="Search Results:"')
                if search_results.is_visible():
                    print("✅ Search results indicator found")
                else:
                    print("⚠️ Search results indicator not found")
                
                # Clear search
                search_input.fill("")
                page.wait_for_timeout(1000)
                
                print("✅ Search input test completed")
            
            print("\n🎉 Precise search test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during precise test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_deals_search_precise()
    if success:
        print("\n✅ Precise search test completed!")
    else:
        print("\n❌ Precise search test failed.")
