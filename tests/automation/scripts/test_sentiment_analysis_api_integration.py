#!/usr/bin/env python3
"""
Sentiment Analysis API Integration Test
Tests API calls and data loading for sentiment analysis
"""

from playwright.sync_api import sync_playwright
import time
import requests
import json

def test_sentiment_analysis_api_integration():
    """Test API integration for sentiment analysis"""
    
    print("😊 Testing Sentiment Analysis API Integration")
    print("=" * 50)
    
    # Test API endpoints directly
    print("\n🔌 Testing API endpoints directly...")
    
    base_url = "http://127.0.0.1:8000"
    api_endpoints = [
        "/api/sentiment-analysis/overview",
        "/api/sentiment-analysis/support-tickets",
        "/api/sentiment-analysis/chat-messages",
        "/api/sentiment-analysis/activities"
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
    
    # Test each endpoint
    for endpoint in api_endpoints:
        print(f"\n📡 Testing {endpoint}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {endpoint} - Status: {response.status_code}")
                print(f"  📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Check for specific data structure
                if endpoint == "/api/sentiment-analysis/overview":
                    expected_keys = ["overall_score", "overall_label", "support_tickets", "chat_messages", "activities"]
                    for key in expected_keys:
                        if key in data:
                            print(f"    ✅ Found expected key: {key}")
                        else:
                            print(f"    ❌ Missing expected key: {key}")
                
                elif endpoint == "/api/sentiment-analysis/support-tickets":
                    if "tickets" in data:
                        tickets = data["tickets"]
                        if isinstance(tickets, list):
                            print(f"    ✅ Found {len(tickets)} support tickets")
                        else:
                            print(f"    ❌ Tickets is not a list: {type(tickets)}")
                    else:
                        print(f"    ❌ No 'tickets' key in response")
                
                elif endpoint == "/api/sentiment-analysis/chat-messages":
                    if "messages" in data:
                        messages = data["messages"]
                        if isinstance(messages, list):
                            print(f"    ✅ Found {len(messages)} chat messages")
                        else:
                            print(f"    ❌ Messages is not a list: {type(messages)}")
                    else:
                        print(f"    ❌ No 'messages' key in response")
                
                elif endpoint == "/api/sentiment-analysis/activities":
                    if "activities" in data:
                        activities = data["activities"]
                        if isinstance(activities, list):
                            print(f"    ✅ Found {len(activities)} activities")
                        else:
                            print(f"    ❌ Activities is not a list: {type(activities)}")
                    else:
                        print(f"    ❌ No 'activities' key in response")
                
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
                print(f"  📝 Response: {response.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  ⏰ {endpoint} - Timeout")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
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
            
            # Navigate to sentiment analysis
            print("\n😊 Navigating to Sentiment Analysis page...")
            page.goto("http://127.0.0.1:8000/sentiment-analysis")
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
            
            # Check for overall sentiment data
            sentiment_section = page.locator('.bg-white.rounded-lg.shadow-sm.border').first
            if sentiment_section.is_visible():
                print("  ✅ Overall sentiment section displayed")
                
                # Check for sentiment emoji
                emoji = page.locator('.text-4xl.font-bold')
                if emoji.is_visible():
                    emoji_text = emoji.text_content()
                    if emoji_text in ['😊', '😞', '😐']:
                        print(f"  ✅ Sentiment emoji displayed: {emoji_text}")
                    else:
                        print(f"  ⚠️ Unexpected emoji: {emoji_text}")
                
                # Check for sentiment label
                label = page.locator('.text-2xl.font-bold').first
                if label.is_visible():
                    label_text = label.text_content()
                    if label_text in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
                        print(f"  ✅ Sentiment label displayed: {label_text}")
                    else:
                        print(f"  ⚠️ Unexpected label: {label_text}")
                
                # Check for sentiment score
                score = page.locator('.text-sm.text-gray-600:has-text("Score:")')
                if score.is_visible():
                    print("  ✅ Sentiment score displayed")
                else:
                    print("  ❌ Sentiment score not displayed")
            else:
                print("  ❌ Overall sentiment section not displayed")
            
            # Check for charts
            charts = page.locator('.recharts-wrapper')
            if charts.count() > 0:
                print(f"  ✅ Found {charts.count()} chart(s)")
            else:
                print("  ❌ No charts found")
            
            # Check for summary cards
            summary_cards = page.locator('.bg-white.rounded-lg.shadow-sm.border.border-gray-200.p-6')
            if summary_cards.count() >= 3:
                print(f"  ✅ Found {summary_cards.count()} summary cards")
            else:
                print(f"  ❌ Expected at least 3 summary cards, found {summary_cards.count()}")
            
            # Test tab switching to trigger more API calls
            print("\n🗂️ Testing tab switching for API calls...")
            
            tabs = ["Support Tickets", "Chat Messages", "Activities"]
            for tab in tabs:
                tab_button = page.locator(f'button:has-text("{tab}")')
                if tab_button.is_visible():
                    tab_button.click()
                    time.sleep(2)
                    print(f"  ✅ Switched to {tab} tab")
                    
                    # Check for table data
                    table = page.locator('table')
                    if table.is_visible():
                        rows = page.locator('tbody tr')
                        row_count = rows.count()
                        if row_count > 0:
                            print(f"    ✅ Found {row_count} rows in {tab} table")
                        else:
                            print(f"    ⚠️ No rows found in {tab} table")
                    else:
                        print(f"    ❌ No table found in {tab} tab")
            
            # Test sentiment analysis functionality
            print("\n🧠 Testing sentiment analysis functionality...")
            
            # Check for sentiment icons
            sentiment_icons = page.locator('.lucide-check-circle, .lucide-x-circle, .lucide-alert-triangle')
            if sentiment_icons.count() > 0:
                print(f"  ✅ Found {sentiment_icons.count()} sentiment icons")
            else:
                print("  ❌ No sentiment icons found")
            
            # Check for sentiment scores in tables
            sentiment_scores = page.locator('text=/\\d+\\.\\d{2}/')
            if sentiment_scores.count() > 0:
                print(f"  ✅ Found {sentiment_scores.count()} sentiment scores")
            else:
                print("  ❌ No sentiment scores found")
            
            # Check for sentiment labels
            sentiment_labels = page.locator('text="positive", text="negative", text="neutral"')
            if sentiment_labels.count() > 0:
                print(f"  ✅ Found {sentiment_labels.count()} sentiment labels")
            else:
                print("  ❌ No sentiment labels found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/sentiment_analysis_api_integration.png")
            print("✅ Screenshot saved as sentiment_analysis_api_integration.png")
            
            print("\n🎉 Sentiment Analysis API integration test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during UI test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_sentiment_analysis_api_integration()
    if success:
        print("\n✅ Sentiment Analysis API integration test passed!")
    else:
        print("\n❌ Sentiment Analysis API integration test failed.")
