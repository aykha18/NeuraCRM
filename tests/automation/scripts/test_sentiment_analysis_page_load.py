#!/usr/bin/env python3
"""
Sentiment Analysis Page Load Test
Tests the basic loading and display of the sentiment analysis page
"""

from playwright.sync_api import sync_playwright
import time

def test_sentiment_analysis_page_load():
    """Test that the sentiment analysis page loads correctly"""
    
    print("😊 Testing Sentiment Analysis Page Load")
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
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Sentiment Analysis")')
            if title.is_visible():
                print("✅ Page title 'Sentiment Analysis' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check page description
            print("\n📝 Checking page description...")
            description = page.locator('.text-gray-600:has-text("Analyze customer sentiment")')
            if description.is_visible():
                print("✅ Page description found")
            else:
                print("❌ Page description not found")
            
            # Check overall sentiment section
            print("\n📊 Checking overall sentiment section...")
            sentiment_section = page.locator('.bg-white.rounded-lg.shadow-sm.border').first
            if sentiment_section.is_visible():
                print("✅ Overall sentiment section found")
                
                # Check for sentiment emoji
                emoji = page.locator('.text-4xl.font-bold')
                if emoji.is_visible():
                    emoji_text = emoji.text_content()
                    if emoji_text in ['😊', '😞', '😐']:
                        print(f"  ✅ Sentiment emoji found: {emoji_text}")
                    else:
                        print(f"  ⚠️ Unexpected emoji: {emoji_text}")
                else:
                    print("  ❌ Sentiment emoji not found")
                
                # Check for sentiment label
                label = page.locator('.text-2xl.font-bold').first
                if label.is_visible():
                    label_text = label.text_content()
                    if label_text in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
                        print(f"  ✅ Sentiment label found: {label_text}")
                    else:
                        print(f"  ⚠️ Unexpected label: {label_text}")
                else:
                    print("  ❌ Sentiment label not found")
                
                # Check for sentiment score
                score = page.locator('.text-sm.text-gray-600:has-text("Score:")')
                if score.is_visible():
                    print("  ✅ Sentiment score found")
                else:
                    print("  ❌ Sentiment score not found")
                
                # Check for total interactions
                interactions = page.locator('.text-2xl.font-bold.text-gray-900')
                if interactions.is_visible():
                    print("  ✅ Total interactions count found")
                else:
                    print("  ❌ Total interactions count not found")
            else:
                print("❌ Overall sentiment section not found")
            
            # Check navigation tabs
            print("\n🗂️ Checking navigation tabs...")
            tabs = ["Overview", "Support Tickets", "Chat Messages", "Activities"]
            
            for tab in tabs:
                tab_element = page.locator(f'button:has-text("{tab}")')
                if tab_element.is_visible():
                    print(f"  ✅ {tab} tab found")
                else:
                    print(f"  ❌ {tab} tab not found")
            
            # Check if Overview tab is active by default
            print("\n🎯 Checking default active tab...")
            overview_tab = page.locator('button:has-text("Overview")')
            if overview_tab.is_visible():
                # Check if it has active styling
                class_attr = overview_tab.get_attribute('class')
                if 'border-blue-500' in class_attr or 'text-blue-600' in class_attr:
                    print("✅ Overview tab is active by default")
                else:
                    print("⚠️ Overview tab found but may not be active")
            else:
                print("❌ Overview tab not found")
            
            # Check for charts in Overview tab
            print("\n📈 Checking charts in Overview tab...")
            bar_chart = page.locator('.recharts-wrapper')
            if bar_chart.count() > 0:
                print(f"  ✅ Found {bar_chart.count()} chart(s)")
            else:
                print("  ❌ No charts found")
            
            # Check for summary cards
            print("\n📋 Checking summary cards...")
            summary_cards = page.locator('.bg-white.rounded-lg.shadow-sm.border.border-gray-200.p-6')
            card_count = summary_cards.count()
            if card_count >= 3:
                print(f"  ✅ Found {card_count} summary cards")
            else:
                print(f"  ❌ Expected at least 3 summary cards, found {card_count}")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/sentiment_analysis_page_load.png")
            print("✅ Screenshot saved as sentiment_analysis_page_load.png")
            
            print("\n🎉 Sentiment Analysis page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_sentiment_analysis_page_load()
    if success:
        print("\n✅ Sentiment Analysis page load test passed!")
    else:
        print("\n❌ Sentiment Analysis page load test failed.")
