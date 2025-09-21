#!/usr/bin/env python3
"""
Playwright automation script for TC_LEAD_002: Update Existing Lead
"""

from playwright.sync_api import Page, expect
import time

def test_update_existing_lead(page: Page):
    """Test updating an existing lead with inline editing"""
    
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
        raise AssertionError("No leads found to update")
    
    # Get the first lead row
    first_lead = lead_rows[0]
    
    # Look for edit button or inline edit trigger
    edit_selectors = [
        'button:has-text("Edit")',
        'button[aria-label*="edit" i]',
        '[data-testid="edit-lead"]',
        'button:has(svg)',
        '.edit-button',
        '.action-button'
    ]
    
    edit_button = None
    for selector in edit_selectors:
        try:
            edit_button = first_lead.locator(selector).first
            if edit_button.is_visible():
                break
        except:
            continue
    
    if not edit_button or not edit_button.is_visible():
        # Try clicking on the lead name or email to trigger inline edit
        name_cell = first_lead.locator('td:first-child, .name-cell, .lead-name').first
        if name_cell.is_visible():
            name_cell.click()
            time.sleep(1)
            print("Clicked on lead name to trigger inline edit")
        else:
            raise AssertionError("No edit button or inline edit trigger found")
    
    # Wait for edit mode to activate
    time.sleep(2)
    
    # Look for editable fields
    editable_fields = [
        'input[name*="name" i]',
        'input[name*="email" i]',
        'input[name*="company" i]',
        'input[name*="phone" i]',
        'input[type="text"]',
        'input[type="email"]'
    ]
    
    updated_data = {
        "name": "Updated Lead Name",
        "email": "updated.lead@example.com",
        "company": "Updated Company Inc"
    }
    
    fields_updated = 0
    
    # Try to update name field
    name_field = None
    for selector in editable_fields:
        try:
            name_field = first_lead.locator(selector).first
            if name_field.is_visible() and name_field.is_enabled():
                name_field.clear()
                name_field.fill(updated_data["name"])
                fields_updated += 1
                print(f"Updated name field: {updated_data['name']}")
                break
        except:
            continue
    
    # Try to update email field
    email_field = first_lead.locator('input[type="email"]').first
    if email_field.is_visible() and email_field.is_enabled():
        email_field.clear()
        email_field.fill(updated_data["email"])
        fields_updated += 1
        print(f"Updated email field: {updated_data['email']}")
    
    # Try to update company field
    company_selectors = [
        'input[name*="company" i]',
        'input[placeholder*="company" i]'
    ]
    
    for selector in company_selectors:
        try:
            company_field = first_lead.locator(selector).first
            if company_field.is_visible() and company_field.is_enabled():
                company_field.clear()
                company_field.fill(updated_data["company"])
                fields_updated += 1
                print(f"Updated company field: {updated_data['company']}")
                break
        except:
            continue
    
    if fields_updated == 0:
        raise AssertionError("No editable fields found for inline editing")
    
    # Look for save button
    save_selectors = [
        'button:has-text("Save")',
        'button:has-text("Update")',
        'button[type="submit"]',
        '[data-testid="save-lead"]',
        'button:has(svg)'
    ]
    
    save_button = None
    for selector in save_selectors:
        try:
            save_button = first_lead.locator(selector).first
            if save_button.is_visible():
                break
        except:
            continue
    
    if save_button and save_button.is_visible():
        save_button.click()
        print("Clicked save button")
    else:
        # Try pressing Enter or clicking outside to save
        page.keyboard.press("Enter")
        print("Pressed Enter to save")
    
    # Wait for save to complete
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Verify the update was successful
    success_indicators = [
        'text="Lead updated successfully"',
        'text="Changes saved"',
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
    
    # Check if the updated data appears in the lead list
    if page.locator(f'text="{updated_data["name"]}"').is_visible():
        print("Updated lead name appears in the list")
        success_found = True
    
    if page.locator(f'text="{updated_data["email"]}"').is_visible():
        print("Updated lead email appears in the list")
        success_found = True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/leads_update.png")
    
    if success_found:
        return True
    else:
        raise AssertionError("Lead update success not confirmed")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_update_existing_lead(page)
            print("PASSED: TC_LEAD_002: Update Existing Lead")
        except Exception as e:
            print(f"FAILED: TC_LEAD_002: Update Existing Lead - {e}")
            page.screenshot(path="test-results/leads_update_failure.png")
        finally:
            browser.close()

