#!/usr/bin/env python3
"""
Playwright automation script for TC_LEAD_004: Convert Lead to Deal
"""

from playwright.sync_api import Page, expect
import time

def test_convert_lead_to_deal(page: Page):
    """Test converting a lead to a deal"""
    
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
    time.sleep(2)
    
    # Look for existing leads in the list
    lead_rows = page.locator('[data-testid="lead-row"], tr:has(td), .lead-item, .table-row').all()
    
    if len(lead_rows) == 0:
        raise AssertionError("No leads found to convert")
    
    # Get the first lead row
    first_lead = lead_rows[0]
    
    # Get the lead name for verification
    lead_name_element = first_lead.locator('td:first-child, .name-cell, .lead-name').first
    lead_name = lead_name_element.text_content() if lead_name_element.is_visible() else "Unknown Lead"
    
    print(f"Attempting to convert lead: {lead_name}")
    
    # Look for convert to deal button or action menu
    convert_selectors = [
        'button:has-text("Convert to Deal")',
        'button:has-text("Convert")',
        'button[aria-label*="convert" i]',
        '[data-testid="convert-lead"]',
        'button:has(svg)',
        '.convert-button',
        '.action-button'
    ]
    
    convert_button = None
    for selector in convert_selectors:
        try:
            convert_button = first_lead.locator(selector).first
            if convert_button.is_visible():
                break
        except:
            continue
    
    if not convert_button or not convert_button.is_visible():
        # Try looking for a dropdown menu or action menu
        action_menu_selectors = [
            'button:has-text("Actions")',
            'button:has-text("More")',
            '[data-testid="action-menu"]',
            '.action-menu',
            'button:has(svg)'
        ]
        
        action_menu = None
        for selector in action_menu_selectors:
            try:
                action_menu = first_lead.locator(selector).first
                if action_menu.is_visible():
                    break
            except:
                continue
        
        if action_menu and action_menu.is_visible():
            action_menu.click()
            time.sleep(1)
            
            # Look for convert option in dropdown
            convert_option = page.locator('button:has-text("Convert to Deal"), a:has-text("Convert to Deal"), div:has-text("Convert to Deal")').first
            if convert_option.is_visible():
                convert_option.click()
                print("Clicked convert option from action menu")
            else:
                raise AssertionError("Convert to Deal option not found in action menu")
        else:
            raise AssertionError("No convert button or action menu found")
    else:
        convert_button.click()
        print("Clicked convert to deal button")
    
    # Wait for conversion form/modal to open
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Look for conversion form
    form_selectors = [
        '[data-testid="convert-form"]',
        '.conversion-form',
        '.modal',
        '[role="dialog"]',
        'form'
    ]
    
    form_found = False
    for selector in form_selectors:
        if page.locator(selector).is_visible():
            form_found = True
            print("Conversion form opened")
            break
    
    if form_found:
        # Fill in deal information
        deal_data = {
            "title": f"Deal for {lead_name}",
            "value": "50000",
            "closeDate": "2025-06-15",
            "stage": "proposal"
        }
        
        # Fill deal title
        title_selectors = [
            'input[name*="title" i]',
            'input[name*="name" i]',
            'input[placeholder*="title" i]',
            'input[placeholder*="deal" i]'
        ]
        
        title_field = None
        for selector in title_selectors:
            try:
                title_field = page.locator(selector).first
                if title_field.is_visible():
                    break
            except:
                continue
        
        if title_field and title_field.is_visible():
            title_field.fill(deal_data["title"])
            print(f"Filled deal title: {deal_data['title']}")
        
        # Fill deal value
        value_selectors = [
            'input[name*="value" i]',
            'input[name*="amount" i]',
            'input[placeholder*="value" i]',
            'input[placeholder*="amount" i]',
            'input[type="number"]'
        ]
        
        value_field = None
        for selector in value_selectors:
            try:
                value_field = page.locator(selector).first
                if value_field.is_visible():
                    break
            except:
                continue
        
        if value_field and value_field.is_visible():
            value_field.fill(deal_data["value"])
            print(f"Filled deal value: {deal_data['value']}")
        
        # Fill close date
        date_selectors = [
            'input[name*="date" i]',
            'input[name*="close" i]',
            'input[type="date"]',
            'input[placeholder*="date" i]'
        ]
        
        date_field = None
        for selector in date_selectors:
            try:
                date_field = page.locator(selector).first
                if date_field.is_visible():
                    break
            except:
                continue
        
        if date_field and date_field.is_visible():
            date_field.fill(deal_data["closeDate"])
            print(f"Filled close date: {deal_data['closeDate']}")
        
        # Select deal stage
        stage_selectors = [
            'select[name*="stage" i]',
            'select[name*="status" i]',
            '[data-testid="stage-select"]'
        ]
        
        stage_field = None
        for selector in stage_selectors:
            try:
                stage_field = page.locator(selector).first
                if stage_field.is_visible():
                    break
            except:
                continue
        
        if stage_field and stage_field.is_visible():
            stage_field.select_option(deal_data["stage"])
            print(f"Selected deal stage: {deal_data['stage']}")
        
        # Click convert button
        convert_form_selectors = [
            'button:has-text("Convert")',
            'button:has-text("Create Deal")',
            'button:has-text("Submit")',
            'button[type="submit"]',
            '[data-testid="convert-submit"]'
        ]
        
        convert_submit = None
        for selector in convert_form_selectors:
            try:
                convert_submit = page.locator(selector).first
                if convert_submit.is_visible():
                    break
            except:
                continue
        
        if convert_submit and convert_submit.is_visible():
            convert_submit.click()
            print("Clicked convert submit button")
        else:
            raise AssertionError("Convert submit button not found")
    else:
        print("No conversion form found, proceeding with direct conversion")
    
    # Wait for conversion to complete
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Verify the conversion was successful
    success_indicators = [
        'text="Lead converted successfully"',
        'text="Deal created"',
        'text="Conversion successful"',
        'text="Success"',
        '[class*="success"]',
        '[role="alert"]'
    ]
    
    success_found = False
    for indicator in success_indicators:
        try:
            if page.locator(indicator).is_visible():
                print("Success message displayed")
                success_found = True
                break
        except:
            continue
    
    # Check if redirected to deals page
    current_url = page.url
    if "/deals" in current_url or "/kanban" in current_url:
        print("Redirected to deals page")
        success_found = True
    
    # Check if the deal appears in the deals list
    if page.locator(f'text="{deal_data["title"]}"').is_visible():
        print("Converted deal appears in deals list")
        success_found = True
    
    # Check if lead status changed to converted
    page.goto("http://127.0.0.1:8000/leads")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    if page.locator(f'text="{lead_name}"').is_visible():
        # Check if lead status shows as converted
        if page.locator('text="converted"').is_visible():
            print("Lead status shows as converted")
            success_found = True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/leads_convert_to_deal.png")
    
    if success_found:
        return True
    else:
        raise AssertionError("Lead to deal conversion success not confirmed")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_convert_lead_to_deal(page)
            print("PASSED: TC_LEAD_004: Convert Lead to Deal")
        except Exception as e:
            print(f"FAILED: TC_LEAD_004: Convert Lead to Deal - {e}")
            page.screenshot(path="test-results/leads_convert_failure.png")
        finally:
            browser.close()

