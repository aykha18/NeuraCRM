#!/usr/bin/env python3
"""
Simple UI test for sentiment analysis
"""
from playwright.sync_api import sync_playwright
import time

def test_sentiment_ui():
    """Test sentiment analysis UI"""

    print("Testing Sentiment Analysis UI")
    print("=" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            print("Logging in...")
            page.goto("http://127.0.0.1:8000/signin")
            page.wait_for_load_state("networkidle")

            page.fill('input[type="email"]', "nodeit@node.com")
            page.fill('input[type="password"]', "NodeIT2024!")
            page.click('button[type="submit"]')
            page.wait_for_url("**/dashboard", timeout=10000)
            print("Login successful")

            # Navigate to sentiment analysis
            print("Navigating to Sentiment Analysis...")
            page.goto("http://127.0.0.1:8000/sentiment-analysis")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Check if page loaded
            page_title = page.locator('h1:has-text("Sentiment Analysis")')
            if page_title.is_visible():
                print("Page title found")
            else:
                print("Page title not found")

            # Check for overall sentiment section
            sentiment_section = page.locator('.bg-white.rounded-lg.shadow-sm.border').first
            if sentiment_section.is_visible():
                print("Overall sentiment section displayed")

                # Check for emoji
                emoji = page.locator('.text-4xl.font-bold')
                if emoji.is_visible():
                    emoji_text = emoji.text_content()
                    print(f"Sentiment emoji: {emoji_text}")

                # Check for label
                label = page.locator('.text-2xl.font-bold').first
                if label.is_visible():
                    label_text = label.text_content()
                    print(f"Sentiment label: {label_text}")

                # Check for score
                score = page.locator('.text-sm.text-gray-600:has-text("Score:")')
                if score.is_visible():
                    print("Sentiment score displayed")
                else:
                    print("Sentiment score not displayed")

            else:
                print("Overall sentiment section not displayed")

            # Check for tabs
            tabs = page.locator('button:has-text("Overview"), button:has-text("Support Tickets"), button:has-text("Chat Messages"), button:has-text("Activities")')
            tab_count = tabs.count()
            print(f"Found {tab_count} tabs")

            # Test tab switching
            tickets_tab = page.locator('button:has-text("Support Tickets")')
            if tickets_tab.is_visible():
                tickets_tab.click()
                time.sleep(2)
                print("Switched to Support Tickets tab")

                # Check for table
                table = page.locator('table')
                if table.is_visible():
                    rows = page.locator('tbody tr')
                    row_count = rows.count()
                    print(f"Found {row_count} rows in tickets table")
                else:
                    print("No table found in tickets tab")

            # Take screenshot
            page.screenshot(path="test_sentiment_ui.png")
            print("Screenshot saved")

            print("UI test completed successfully")
            return True

        except Exception as e:
            print(f"Error during UI test: {e}")
            return False

        finally:
            browser.close()

if __name__ == "__main__":
    test_sentiment_ui()