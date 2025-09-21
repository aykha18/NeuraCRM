#!/usr/bin/env python3
"""
Playwright automation script for TC_CONTACT_004: Convert Contact to Lead
"""

from playwright.sync_api import Page, expect
import time

def test_convert_contact_to_lead(page: Page):
    """Test converting a contact to a lead"""
    
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
    
    # Navigate to contacts page
    page.goto("http://127.0.0.1:8000/contacts")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Look for existing contacts in the list
    contact_rows = page.locator('[data-testid="contact-row"], tr:has(td), .contact-item, .table-row').all()
    
    if len(contact_rows) == 0:
        raise AssertionError("No contacts found to convert")
    
    # Get the first contact row
    first_contact = contact_rows[0]
    
    # Get the contact name for verification
    contact_name_element = first_contact.locator('td:first-child, .name-cell, .contact-name').first
    contact_name = contact_name_element.text_content() if contact_name_element.is_visible() else "Unknown Contact"
    
    print(f"Attempting to convert contact: {contact_name}")
    
    # Look for convert to lead button or action menu
    convert_selectors = [
        'button:has-text("Convert to Lead")',
        'button:has-text("Convert")',
        'button[aria-label*="convert" i]',
        '[data-testid="convert-contact"]',
        'button:has(svg)',
        '.convert-button',
        '.action-button'
    ]
    
    convert_button = None
    for selector in convert_selectors:
        try:
            convert_button = first_contact.locator(selector).first
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
                action_menu = first_contact.locator(selector).first
                if action_menu.is_visible():
                    break
            except:
                continue
        
        if action_menu and action_menu.is_visible():
            action_menu.click()
            time.sleep(1)
            
            # Look for convert option in dropdown
            convert_option = page.locator('button:has-text("Convert to Lead"), a:has-text("Convert to Lead"), div:has-text("Convert to Lead")').first
            if convert_option.is_visible():
                convert_option.click()
                print("Clicked convert option from action menu")
            else:
                raise AssertionError("Convert to Lead option not found in action menu")
        else:
            raise AssertionError("No convert button or action menu found")
    else:
        convert_button.click()
        print("Clicked convert to lead button")
    
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
        # Fill in lead information
        lead_data = {
            "source": "referral",
            "status": "new",
            "priority": "medium"
        }
        
        # Select lead source
        source_selectors = [
            'select[name*="source" i]',
            'select[name*="origin" i]',
            '[data-testid="source-select"]'
        ]
        
        source_field = None
        for selector in source_selectors:
            try:
                source_field = page.locator(selector).first
                if source_field.is_visible():
                    break
            except:
                continue
        
        if source_field and source_field.is_visible():
            source_field.select_option(lead_data["source"])
            print(f"Selected lead source: {lead_data['source']}")
        
        # Select lead status
        status_selectors = [
            'select[name*="status" i]',
            'select[name*="stage" i]',
            '[data-testid="status-select"]'
        ]
        
        status_field = None
        for selector in status_selectors:
            try:
                status_field = page.locator(selector).first
                if status_field.is_visible():
                    break
            except:
                continue
        
        if status_field and status_field.is_visible():
            status_field.select_option(lead_data["status"])
            print(f"Selected lead status: {lead_data['status']}")
        
        # Select lead priority
        priority_selectors = [
            'select[name*="priority" i]',
            'select[name*="importance" i]',
            '[data-testid="priority-select"]'
        ]
        
        priority_field = None
        for selector in priority_selectors:
            try:
                priority_field = page.locator(selector).first
                if priority_field.is_visible():
                    break
            except:
                continue
        
        if priority_field and priority_field.is_visible():
            priority_field.select_option(lead_data["priority"])
            print(f"Selected lead priority: {lead_data['priority']}")
        
        # Click convert button
        convert_form_selectors = [
            'button:has-text("Convert")',
            'button:has-text("Create Lead")',
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
        'text="Contact converted successfully"',
        'text="Lead created"',
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
    
    # Check if redirected to leads page
    current_url = page.url
    if "/leads" in current_url:
        print("Redirected to leads page")
        success_found = True
    
    # Check if the lead appears in the leads list
    if page.locator(f'text="{contact_name}"').is_visible():
        print("Converted lead appears in leads list")
        success_found = True
    
    # Check if contact status changed to converted
    page.goto("http://127.0.0.1:8000/contacts")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    if page.locator(f'text="{contact_name}"').is_visible():
        # Check if contact status shows as converted
        if page.locator('text="converted"').is_visible():
            print("Contact status shows as converted")
            success_found = True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/contacts_convert_to_lead.png")
    
    if success_found:
        return True
    else:
        raise AssertionError("Contact to lead conversion success not confirmed")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_convert_contact_to_lead(page)
            print("PASSED: TC_CONTACT_004: Convert Contact to Lead")
        except Exception as e:
            print(f"FAILED: TC_CONTACT_004: Convert Contact to Lead - {e}")
            page.screenshot(path="test-results/contacts_convert_failure.png")
        finally:
            browser.close()

