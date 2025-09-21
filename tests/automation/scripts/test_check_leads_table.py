#!/usr/bin/env python3
"""
Script to check the leads table and see if created leads are appearing
"""

from playwright.sync_api import Page, expect
import time

def check_leads_table(page: Page):
    """Check the leads table to see what leads are present"""
    
    # First, login to the system
    page.goto("http://127.0.0.1:8000/signin")
    page.wait_for_load_state("networkidle")
    
    # Login
    email_field = page.locator('input[type="email"]').or_(page.locator('input[placeholder*="email" i]')).first
    email_field.fill("nodeit@node.com")
    
    password_field = page.locator('input[type="password"]').or_(page.locator('input[placeholder*="password" i]')).first
    password_field.fill("NodeIT2024!")
    
    login_button = page.locator('button[type="submit"]').or_(page.locator('button:has-text("Sign In")')).first
    login_button.click()
    
    # Wait for login to complete
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Navigate to leads page
    page.goto("http://127.0.0.1:8000/leads")
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    print("🔍 Checking leads table...")
    
    # Take a screenshot first
    page.screenshot(path="test-results/leads_table_check.png")
    
    # Look for different table structures
    table_selectors = [
        'table',
        '[data-testid="leads-table"]',
        '.table',
        '.leads-table',
        'div[role="table"]',
        '.grid',
        '.list'
    ]
    
    table_found = False
    for selector in table_selectors:
        if page.locator(selector).is_visible():
            print(f"✅ Found table with selector: {selector}")
            table_found = True
            break
    
    if not table_found:
        print("❌ No table found, checking for other list structures...")
    
    # Look for lead rows in different formats
    row_selectors = [
        'tr',
        '[data-testid="lead-row"]',
        '.lead-item',
        '.table-row',
        'div[role="row"]',
        '.list-item'
    ]
    
    all_rows = []
    for selector in row_selectors:
        rows = page.locator(selector).all()
        if len(rows) > 0:
            print(f"✅ Found {len(rows)} rows with selector: {selector}")
            all_rows.extend(rows)
    
    if len(all_rows) == 0:
        print("❌ No rows found in any format")
        
        # Check if there's a "no data" message
        no_data_selectors = [
            'text="No leads found"',
            'text="No data"',
            'text="Empty"',
            'text="No records"',
            '.empty-state',
            '.no-data'
        ]
        
        for selector in no_data_selectors:
            if page.locator(selector).is_visible():
                print(f"📭 Found empty state: {selector}")
                break
    else:
        print(f"📊 Total rows found: {len(all_rows)}")
        
        # Check the first few rows for content
        for i, row in enumerate(all_rows[:5]):  # Check first 5 rows
            try:
                row_text = row.text_content()
                if row_text and row_text.strip():
                    print(f"   Row {i+1}: {row_text.strip()[:100]}...")
                else:
                    print(f"   Row {i+1}: [Empty or no text content]")
            except:
                print(f"   Row {i+1}: [Error reading content]")
    
    # Look for specific lead names we created
    test_lead_patterns = [
        'Test Lead',
        'testlead',
        'Test Company'
    ]
    
    for pattern in test_lead_patterns:
        if page.locator(f'text="{pattern}"').is_visible():
            print(f"✅ Found test lead with pattern: {pattern}")
        else:
            print(f"❌ No test lead found with pattern: {pattern}")
    
    # Check page content for any lead-related text
    page_content = page.locator('body').text_content()
    if 'lead' in page_content.lower():
        print("✅ Page contains 'lead' text")
    else:
        print("❌ Page does not contain 'lead' text")
    
    # Check for any error messages
    error_selectors = [
        '[class*="error"]',
        '[class*="alert"]',
        'text="Error"',
        'text="Failed"',
        '.error-message'
    ]
    
    errors_found = False
    for selector in error_selectors:
        if page.locator(selector).is_visible():
            error_text = page.locator(selector).first.text_content()
            print(f"⚠️ Error found: {error_text}")
            errors_found = True
    
    if not errors_found:
        print("✅ No error messages found")
    
    # Check the current URL
    current_url = page.url
    print(f"📍 Current URL: {current_url}")
    
    # Check if we're on the right page
    if "/leads" in current_url:
        print("✅ On leads page")
    else:
        print(f"⚠️ Not on leads page, current: {current_url}")
    
    return len(all_rows)

def test_leads_table_check():
    """Main test function"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("🔍 NeuraCRM Leads Table Check")
            print("=" * 50)
            
            row_count = check_leads_table(page)
            
            print(f"\n📊 Summary:")
            print(f"   Total rows found: {row_count}")
            
            if row_count > 0:
                print("✅ Leads table has data")
            else:
                print("❌ Leads table is empty")
                print("💡 Possible reasons:")
                print("   • Leads are created but not saved to database")
                print("   • Different user/organization context")
                print("   • Database connection issues")
                print("   • Frontend not refreshing data")
                print("   • API endpoint issues")
            
        except Exception as e:
            print(f"❌ Error during check: {e}")
            page.screenshot(path="test-results/leads_table_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    test_leads_table_check()

