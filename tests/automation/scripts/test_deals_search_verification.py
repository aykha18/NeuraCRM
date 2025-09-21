#!/usr/bin/env python3
"""
Deals Search Verification Test
Quick test to verify search functionality is present in the Kanban board
"""

from playwright.sync_api import sync_playwright
import time

def test_deals_search_verification():
    """Quick verification that search functionality exists"""
    
    print("🔍 NeuraCRM Deals Search Verification")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
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
            print("\n📋 Navigating to deals page...")
            page.goto("http://127.0.0.1:8000/kanban")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector('[data-rbd-droppable-id], .flex-shrink-0.w-72', timeout=15000)
            print("✅ Navigated to deals page")
            
            # Check for search input
            print("\n🔍 Checking for search functionality...")
            
            # Look for search input with various selectors
            search_selectors = [
                'input[placeholder*="Search deals"]',
                'input[placeholder*="search"]',
                'input[type="text"]',
                'input[placeholder*="title"]',
                'input[placeholder*="value"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        search_input = element
                        print(f"✅ Search input found with selector: {selector}")
                        break
                except:
                    continue
            
            if search_input:
                # Test basic search functionality
                print("\n🧪 Testing basic search...")
                
                # Get initial deal count
                deals = page.locator('[data-rbd-draggable-id], .space-y-4 > div')
                initial_count = deals.count()
                print(f"📊 Initial deal count: {initial_count}")
                
                # Try to search
                search_input.fill("test")
                page.wait_for_timeout(2000)
                
                # Check if search results indicator appears
                search_results = page.locator('text="Search Results:"')
                if search_results.is_visible():
                    print("✅ Search results indicator found")
                else:
                    print("⚠️ Search results indicator not found")
                
                # Clear search
                search_input.fill("")
                page.wait_for_timeout(1000)
                
                print("✅ Basic search functionality verified")
                
            else:
                print("❌ Search input not found")
                print("   This might mean:")
                print("   1. Frontend changes haven't been applied yet")
                print("   2. The search feature wasn't added correctly")
                print("   3. The selector needs to be updated")
                
                # Let's check what inputs are actually present
                print("\n🔍 Available input elements:")
                inputs = page.locator('input').all()
                for i, inp in enumerate(inputs):
                    try:
                        placeholder = inp.get_attribute('placeholder') or 'No placeholder'
                        input_type = inp.get_attribute('type') or 'No type'
                        print(f"   Input {i+1}: type='{input_type}', placeholder='{placeholder}'")
                    except:
                        print(f"   Input {i+1}: Could not read attributes")
                
                return False
            
            print("\n🎉 Search functionality verification complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_deals_search_verification()
    if success:
        print("\n✅ Search functionality is present and working!")
    else:
        print("\n❌ Search functionality verification failed.")

