#!/usr/bin/env python3
"""
Sentiment Analysis Navigation Test
Tests navigation between different sentiment analysis tabs
"""

from playwright.sync_api import sync_playwright
import time

def test_sentiment_analysis_navigation():
    """Test navigation between sentiment analysis tabs"""
    
    print("😊 Testing Sentiment Analysis Navigation")
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
            
            # Navigate to sentiment analysis
            print("\n😊 Navigating to Sentiment Analysis page...")
            page.goto("http://127.0.0.1:8000/sentiment-analysis")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to sentiment analysis page")
            
            # Test tab navigation
            tabs_to_test = [
                {
                    "name": "Overview",
                    "expected_content": ["Sentiment Distribution", "Overall Sentiment Breakdown", "Support Tickets", "Chat Messages", "Activities"]
                },
                {
                    "name": "Support Tickets", 
                    "expected_content": ["Support Ticket Sentiment Analysis", "Ticket", "Title", "Sentiment", "Status", "Created"]
                },
                {
                    "name": "Chat Messages",
                    "expected_content": ["Chat Message Sentiment Analysis", "Room", "Message", "Sentiment", "Created"]
                },
                {
                    "name": "Activities",
                    "expected_content": ["Activity Sentiment Analysis", "Type", "Message", "Sentiment", "Created"]
                }
            ]
            
            for tab_info in tabs_to_test:
                tab_name = tab_info["name"]
                expected_content = tab_info["expected_content"]
                
                print(f"\n🗂️ Testing {tab_name} tab...")
                
                # Click on the tab
                tab_button = page.locator(f'button:has-text("{tab_name}")')
                if tab_button.is_visible():
                    tab_button.click()
                    time.sleep(2)  # Wait for content to load
                    print(f"  ✅ Clicked on {tab_name} tab")
                    
                    # Check if tab is now active
                    class_attr = tab_button.get_attribute('class')
                    if 'border-blue-500' in class_attr or 'text-blue-600' in class_attr:
                        print(f"  ✅ {tab_name} tab is now active")
                    else:
                        print(f"  ⚠️ {tab_name} tab may not be active")
                    
                    # Check for expected content
                    content_found = 0
                    for content in expected_content:
                        content_element = page.locator(f'text="{content}"').first
                        if content_element.is_visible():
                            print(f"    ✅ Found: {content}")
                            content_found += 1
                        else:
                            print(f"    ❌ Missing: {content}")
                    
                    print(f"  📊 Content found: {content_found}/{len(expected_content)}")
                    
                    if content_found >= len(expected_content) * 0.6:  # At least 60% of expected content
                        print(f"  ✅ {tab_name} tab content is mostly correct")
                    else:
                        print(f"  ❌ {tab_name} tab content is missing")
                        
                else:
                    print(f"  ❌ {tab_name} tab button not found")
            
            # Test tab switching back and forth
            print("\n🔄 Testing tab switching...")
            
            # Go to Support Tickets
            tickets_tab = page.locator('button:has-text("Support Tickets")')
            if tickets_tab.is_visible():
                tickets_tab.click()
                time.sleep(1)
                print("  ✅ Switched to Support Tickets")
            
            # Go to Chat Messages
            chats_tab = page.locator('button:has-text("Chat Messages")')
            if chats_tab.is_visible():
                chats_tab.click()
                time.sleep(1)
                print("  ✅ Switched to Chat Messages")
            
            # Go to Activities
            activities_tab = page.locator('button:has-text("Activities")')
            if activities_tab.is_visible():
                activities_tab.click()
                time.sleep(1)
                print("  ✅ Switched to Activities")
            
            # Go back to Overview
            overview_tab = page.locator('button:has-text("Overview")')
            if overview_tab.is_visible():
                overview_tab.click()
                time.sleep(1)
                print("  ✅ Switched back to Overview")
            
            # Test specific content in each tab
            print("\n📋 Testing specific tab content...")
            
            # Test Support Tickets tab content
            print("\n🎫 Testing Support Tickets tab content...")
            tickets_tab.click()
            time.sleep(2)
            
            # Check for table headers
            table_headers = ["Ticket", "Title", "Sentiment", "Status", "Created"]
            for header in table_headers:
                header_element = page.locator(f'th:has-text("{header}")')
                if header_element.is_visible():
                    print(f"  ✅ Table header found: {header}")
                else:
                    print(f"  ❌ Table header missing: {header}")
            
            # Check for sentiment icons and colors
            sentiment_elements = page.locator('.flex.items-center')
            sentiment_count = sentiment_elements.count()
            if sentiment_count > 0:
                print(f"  ✅ Found {sentiment_count} sentiment elements")
            else:
                print("  ❌ No sentiment elements found")
            
            # Test Chat Messages tab content
            print("\n💬 Testing Chat Messages tab content...")
            chats_tab.click()
            time.sleep(2)
            
            # Check for table headers
            chat_headers = ["Room", "Message", "Sentiment", "Created"]
            for header in chat_headers:
                header_element = page.locator(f'th:has-text("{header}")')
                if header_element.is_visible():
                    print(f"  ✅ Table header found: {header}")
                else:
                    print(f"  ❌ Table header missing: {header}")
            
            # Test Activities tab content
            print("\n📝 Testing Activities tab content...")
            activities_tab.click()
            time.sleep(2)
            
            # Check for table headers
            activity_headers = ["Type", "Message", "Sentiment", "Created"]
            for header in activity_headers:
                header_element = page.locator(f'th:has-text("{header}")')
                if header_element.is_visible():
                    print(f"  ✅ Table header found: {header}")
                else:
                    print(f"  ❌ Table header missing: {header}")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/sentiment_analysis_navigation.png")
            print("✅ Screenshot saved as sentiment_analysis_navigation.png")
            
            print("\n🎉 Sentiment Analysis navigation test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_sentiment_analysis_navigation()
    if success:
        print("\n✅ Sentiment Analysis navigation test passed!")
    else:
        print("\n❌ Sentiment Analysis navigation test failed.")

