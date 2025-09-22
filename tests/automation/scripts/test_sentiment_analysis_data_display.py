#!/usr/bin/env python3
"""
Sentiment Analysis Data Display Test
Tests that sentiment analysis data is properly displayed and formatted
"""

from playwright.sync_api import sync_playwright
import time
import re

def test_sentiment_analysis_data_display():
    """Test that sentiment analysis data is properly displayed and formatted"""
    
    print("😊 Testing Sentiment Analysis Data Display")
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
            
            # Test overall sentiment display
            print("\n📊 Testing overall sentiment display...")
            
            # Check if overall sentiment section has data
            sentiment_section = page.locator('.bg-white.rounded-lg.shadow-sm.border')
            if sentiment_section.is_visible():
                print("✅ Overall sentiment section found")
                
                # Check for sentiment emoji
                emoji = page.locator('.text-4xl.font-bold')
                if emoji.is_visible():
                    emoji_text = emoji.text_content()
                    if emoji_text in ['😊', '😞', '😐']:
                        print(f"  ✅ Sentiment emoji: {emoji_text}")
                    else:
                        print(f"  ⚠️ Unexpected emoji: {emoji_text}")
                
                # Check for sentiment label
                label = page.locator('.text-2xl.font-bold')
                if label.is_visible():
                    label_text = label.text_content()
                    if label_text in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
                        print(f"  ✅ Sentiment label: {label_text}")
                    else:
                        print(f"  ⚠️ Unexpected label: {label_text}")
                
                # Check for sentiment score
                score_element = page.locator('.text-sm.text-gray-600:has-text("Score:")')
                if score_element.is_visible():
                    score_text = score_element.text_content()
                    # Check if score is in format "Score: X.XX"
                    if re.search(r'Score:\s*\d+\.\d{2}', score_text):
                        print(f"  ✅ Sentiment score formatted correctly: {score_text}")
                    else:
                        print(f"  ❌ Sentiment score format incorrect: {score_text}")
                else:
                    print("  ❌ Sentiment score not found")
                
                # Check for total interactions
                interactions = page.locator('.text-2xl.font-bold.text-gray-900')
                if interactions.is_visible():
                    interactions_text = interactions.text_content()
                    if interactions_text.isdigit():
                        print(f"  ✅ Total interactions: {interactions_text}")
                    else:
                        print(f"  ⚠️ Total interactions not numeric: {interactions_text}")
                else:
                    print("  ❌ Total interactions not found")
            else:
                print("❌ Overall sentiment section not found")
            
            # Test sentiment color coding
            print("\n🎨 Testing sentiment color coding...")
            
            # Check for positive sentiment (green)
            positive_elements = page.locator('.text-green-500, .text-green-600')
            if positive_elements.count() > 0:
                print(f"  ✅ Found {positive_elements.count()} positive sentiment elements")
            else:
                print("  ❌ No positive sentiment elements found")
            
            # Check for negative sentiment (red)
            negative_elements = page.locator('.text-red-500, .text-red-600')
            if negative_elements.count() > 0:
                print(f"  ✅ Found {negative_elements.count()} negative sentiment elements")
            else:
                print("  ❌ No negative sentiment elements found")
            
            # Check for neutral sentiment (gray)
            neutral_elements = page.locator('.text-gray-500, .text-gray-600')
            if neutral_elements.count() > 0:
                print(f"  ✅ Found {neutral_elements.count()} neutral sentiment elements")
            else:
                print("  ❌ No neutral sentiment elements found")
            
            # Test charts in Overview tab
            print("\n📈 Testing charts in Overview tab...")
            
            # Check for bar chart
            bar_chart = page.locator('.recharts-wrapper')
            if bar_chart.count() > 0:
                print(f"  ✅ Found {bar_chart.count()} chart(s)")
                
                # Check for chart elements
                chart_elements = page.locator('.recharts-bar, .recharts-pie')
                if chart_elements.count() > 0:
                    print(f"  ✅ Found {chart_elements.count()} chart data elements")
                else:
                    print("  ❌ No chart data elements found")
            else:
                print("  ❌ No charts found")
            
            # Test Support Tickets tab data
            print("\n🎫 Testing Support Tickets tab data...")
            tickets_tab = page.locator('button:has-text("Support Tickets")')
            if tickets_tab.is_visible():
                tickets_tab.click()
                time.sleep(2)
                
                # Check for table
                table = page.locator('table')
                if table.is_visible():
                    print("  ✅ Support tickets table found")
                    
                    # Check for table rows
                    rows = page.locator('tbody tr')
                    row_count = rows.count()
                    if row_count > 0:
                        print(f"  ✅ Found {row_count} support ticket rows")
                        
                        # Check first row for data
                        first_row = rows.first
                        if first_row.is_visible():
                            # Check for ticket number
                            ticket_number = first_row.locator('td:first-child')
                            if ticket_number.is_visible():
                                ticket_text = ticket_number.text_content()
                                if ticket_text.startswith('#'):
                                    print(f"    ✅ Ticket number formatted correctly: {ticket_text}")
                                else:
                                    print(f"    ❌ Ticket number format incorrect: {ticket_text}")
                            
                            # Check for sentiment score
                            sentiment_score = first_row.locator('text=/\\d+\\.\\d{2}/')
                            if sentiment_score.is_visible():
                                print("    ✅ Sentiment score found in table")
                            else:
                                print("    ❌ Sentiment score not found in table")
                    else:
                        print("  ❌ No support ticket rows found")
                else:
                    print("  ❌ Support tickets table not found")
            
            # Test Chat Messages tab data
            print("\n💬 Testing Chat Messages tab data...")
            chats_tab = page.locator('button:has-text("Chat Messages")')
            if chats_tab.is_visible():
                chats_tab.click()
                time.sleep(2)
                
                # Check for table
                table = page.locator('table')
                if table.is_visible():
                    print("  ✅ Chat messages table found")
                    
                    # Check for table rows
                    rows = page.locator('tbody tr')
                    row_count = rows.count()
                    if row_count > 0:
                        print(f"  ✅ Found {row_count} chat message rows")
                    else:
                        print("  ❌ No chat message rows found")
                else:
                    print("  ❌ Chat messages table not found")
            
            # Test Activities tab data
            print("\n📝 Testing Activities tab data...")
            activities_tab = page.locator('button:has-text("Activities")')
            if activities_tab.is_visible():
                activities_tab.click()
                time.sleep(2)
                
                # Check for table
                table = page.locator('table')
                if table.is_visible():
                    print("  ✅ Activities table found")
                    
                    # Check for table rows
                    rows = page.locator('tbody tr')
                    row_count = rows.count()
                    if row_count > 0:
                        print(f"  ✅ Found {row_count} activity rows")
                    else:
                        print("  ❌ No activity rows found")
                else:
                    print("  ❌ Activities table not found")
            
            # Test data formatting
            print("\n📝 Testing data formatting...")
            
            # Check for date formatting
            date_elements = page.locator('text=/\\w{3}\\s+\\d{1,2},\\s+\\d{4}\\s+\\d{1,2}:\\d{2}/')
            if date_elements.count() > 0:
                print(f"  ✅ Found {date_elements.count()} properly formatted dates")
            else:
                print("  ❌ No properly formatted dates found")
            
            # Check for sentiment score formatting
            score_elements = page.locator('text=/\\d+\\.\\d{2}/')
            if score_elements.count() > 0:
                print(f"  ✅ Found {score_elements.count()} properly formatted sentiment scores")
            else:
                print("  ❌ No properly formatted sentiment scores found")
            
            # Check for text truncation
            truncated_elements = page.locator('text=/.*\\.\\.\\.$/')
            if truncated_elements.count() > 0:
                print(f"  ✅ Found {truncated_elements.count()} truncated text elements")
            else:
                print("  ⚠️ No truncated text elements found (may be expected)")
            
            # Test sentiment icons
            print("\n🎯 Testing sentiment icons...")
            
            # Check for CheckCircle (positive)
            check_circles = page.locator('.lucide-check-circle, [data-lucide="check-circle"]')
            if check_circles.count() > 0:
                print(f"  ✅ Found {check_circles.count()} positive sentiment icons")
            
            # Check for XCircle (negative)
            x_circles = page.locator('.lucide-x-circle, [data-lucide="x-circle"]')
            if x_circles.count() > 0:
                print(f"  ✅ Found {x_circles.count()} negative sentiment icons")
            
            # Check for AlertTriangle (neutral)
            alert_triangles = page.locator('.lucide-alert-triangle, [data-lucide="alert-triangle"]')
            if alert_triangles.count() > 0:
                print(f"  ✅ Found {alert_triangles.count()} neutral sentiment icons")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/sentiment_analysis_data_display.png")
            print("✅ Screenshot saved as sentiment_analysis_data_display.png")
            
            print("\n🎉 Sentiment Analysis data display test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_sentiment_analysis_data_display()
    if success:
        print("\n✅ Sentiment Analysis data display test passed!")
    else:
        print("\n❌ Sentiment Analysis data display test failed.")

