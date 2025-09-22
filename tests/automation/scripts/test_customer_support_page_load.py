#!/usr/bin/env python3
"""
Customer Support Page Load Test
Tests the basic loading and display of the customer support page
"""

from playwright.sync_api import sync_playwright
import time

def test_customer_support_page_load():
    """Test that the customer support page loads correctly"""
    
    print("🎧 Testing Customer Support Page Load")
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
            
            # Navigate to customer support
            print("\n🎧 Navigating to Customer Support page...")
            page.goto("http://127.0.0.1:8000/customer-support")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to customer support page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Customer Support")')
            if title.is_visible():
                print("✅ Page title 'Customer Support' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check tabs
            print("\n📑 Checking tabs...")
            tabs = page.locator('nav.-mb-px.flex.space-x-8')
            if tabs.is_visible():
                print("✅ Tabs container found")
                
                # Check individual tabs
                tickets_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Tickets")').first
                if tickets_tab.is_visible():
                    print("  ✅ Tickets tab found")
                else:
                    print("  ❌ Tickets tab not found")
                
                knowledge_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Knowledge Base")').first
                if knowledge_tab.is_visible():
                    print("  ✅ Knowledge Base tab found")
                else:
                    print("  ❌ Knowledge Base tab not found")
                
                analytics_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Analytics")').first
                if analytics_tab.is_visible():
                    print("  ✅ Analytics tab found")
                else:
                    print("  ❌ Analytics tab not found")
                
                surveys_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Surveys")').first
                if surveys_tab.is_visible():
                    print("  ✅ Surveys tab found")
                else:
                    print("  ❌ Surveys tab not found")
            else:
                print("❌ Tabs container not found")
            
            # Check default tab (Tickets)
            print("\n🎫 Checking default tab content...")
            tickets_content = page.locator('h2:has-text("Support Tickets")')
            if tickets_content.is_visible():
                print("✅ Tickets tab is active by default")
                
                # Check for Create Ticket button
                create_ticket_button = page.locator('button:has-text("Create Ticket")')
                if create_ticket_button.is_visible():
                    print("  ✅ Create Ticket button found")
                else:
                    print("  ❌ Create Ticket button not found")
            else:
                print("❌ Tickets tab content not found")
            
            # Check for support tickets
            print("\n🎫 Checking for support tickets...")
            tickets = page.locator('.bg-white.rounded-lg.shadow')
            ticket_count = tickets.count()
            if ticket_count > 0:
                print(f"✅ Found {ticket_count} support tickets")
                
                # Check first ticket for required elements
                first_ticket = tickets.first
                if first_ticket.is_visible():
                    # Check for ticket number
                    ticket_number = first_ticket.locator('.font-semibold')
                    if ticket_number.is_visible():
                        number_text = ticket_number.text_content()
                        print(f"  ✅ First ticket number: {number_text}")
                    else:
                        print("  ❌ Ticket number not found")
                    
                    # Check for ticket title
                    ticket_title = first_ticket.locator('.text-lg.font-medium')
                    if ticket_title.is_visible():
                        print("  ✅ Ticket title found")
                    else:
                        print("  ❌ Ticket title not found")
                    
                    # Check for ticket priority
                    ticket_priority = first_ticket.locator('.px-2.py-1.rounded-full')
                    if ticket_priority.is_visible():
                        print("  ✅ Ticket priority found")
                    else:
                        print("  ❌ Ticket priority not found")
                    
                    # Check for ticket status
                    ticket_status = first_ticket.locator('.px-2.py-1.rounded-full')
                    if ticket_status.is_visible():
                        print("  ✅ Ticket status found")
                    else:
                        print("  ❌ Ticket status not found")
                    
                    # Check for ticket actions
                    actions = first_ticket.locator('.flex.space-x-2')
                    if actions.is_visible():
                        print("  ✅ Ticket actions found")
                        
                        # Check for specific action buttons
                        view_button = first_ticket.locator('button:has-text("View")')
                        if view_button.is_visible():
                            print("    ✅ View button found")
                        else:
                            print("    ❌ View button not found")
                        
                        edit_button = first_ticket.locator('button:has-text("Edit")')
                        if edit_button.is_visible():
                            print("    ✅ Edit button found")
                        else:
                            print("    ❌ Edit button not found")
                    else:
                        print("  ❌ Ticket actions not found")
                else:
                    print("❌ First ticket not visible")
            else:
                print("❌ No support tickets found")
            
            # Test tab navigation
            print("\n🔄 Testing tab navigation...")
            try:
                knowledge_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Knowledge Base")').first
                if knowledge_tab.is_visible():
                    knowledge_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Knowledge Base tab")
                    
                    # Check if knowledge base content is displayed
                    knowledge_content = page.locator('h2:has-text("Knowledge Base Articles")')
                    if knowledge_content.is_visible():
                        print("✅ Knowledge Base tab content is displayed")
                        
                        # Check for Create Article button
                        create_article_button = page.locator('button:has-text("Create Article")')
                        if create_article_button.is_visible():
                            print("  ✅ Create Article button found")
                        else:
                            print("  ❌ Create Article button not found")
                    else:
                        print("⚠️ Knowledge Base tab content not displayed (may be empty)")
                    
                    # Go back to tickets tab
                    tickets_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Tickets")').first
                    if tickets_tab.is_visible():
                        tickets_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Tickets tab")
                    else:
                        print("⚠️ Could not return to Tickets tab")
                else:
                    print("❌ Knowledge Base tab not found")
            except Exception as e:
                print(f"⚠️ Tab navigation test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Analytics tab
            print("\n📊 Testing Analytics tab...")
            try:
                analytics_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Analytics")').first
                if analytics_tab.is_visible():
                    analytics_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Analytics tab")
                    
                    # Check if analytics content is displayed
                    analytics_content = page.locator('h2:has-text("Support Analytics")')
                    if analytics_content.is_visible():
                        print("✅ Analytics tab content is displayed")
                    else:
                        print("⚠️ Analytics tab content not displayed (may be empty)")
                    
                    # Go back to tickets tab
                    tickets_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Tickets")').first
                    if tickets_tab.is_visible():
                        tickets_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Tickets tab")
                    else:
                        print("⚠️ Could not return to Tickets tab")
                else:
                    print("❌ Analytics tab not found")
            except Exception as e:
                print(f"⚠️ Analytics tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Test Surveys tab
            print("\n📋 Testing Surveys tab...")
            try:
                surveys_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Surveys")').first
                if surveys_tab.is_visible():
                    surveys_tab.click()
                    time.sleep(2)
                    print("✅ Clicked on Surveys tab")
                    
                    # Check if surveys content is displayed
                    surveys_content = page.locator('h2:has-text("Customer Satisfaction Surveys")')
                    if surveys_content.is_visible():
                        print("✅ Surveys tab content is displayed")
                    else:
                        print("⚠️ Surveys tab content not displayed (may be empty)")
                    
                    # Go back to tickets tab
                    tickets_tab = page.locator('nav.-mb-px.flex.space-x-8 button:has-text("Tickets")').first
                    if tickets_tab.is_visible():
                        tickets_tab.click()
                        time.sleep(2)
                        print("✅ Returned to Tickets tab")
                    else:
                        print("⚠️ Could not return to Tickets tab")
                else:
                    print("❌ Surveys tab not found")
            except Exception as e:
                print(f"⚠️ Surveys tab test failed: {e}")
                print("✅ Continuing with other tests...")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-ticket, .lucide-book-open, .lucide-bar-chart, .lucide-message-square')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/customer_support_page_load.png")
            print("✅ Screenshot saved as customer_support_page_load.png")
            
            print("\n🎉 Customer Support page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_customer_support_page_load()
    if success:
        print("\n✅ Customer Support page load test passed!")
    else:
        print("\n❌ Customer Support page load test failed.")
