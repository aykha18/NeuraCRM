#!/usr/bin/env python3
"""
Playwright automation script for TC_LEAD_003: Delete Lead
"""

from playwright.sync_api import Page, expect
import time

def test_delete_lead(page: Page):
    """Test deleting a lead"""
    
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
        raise AssertionError("No leads found to delete")
    
    # Get the first lead row
    first_lead = lead_rows[0]
    
    # Get the lead name for verification
    lead_name_element = first_lead.locator('td:first-child, .name-cell, .lead-name').first
    lead_name = lead_name_element.text_content() if lead_name_element.is_visible() else "Unknown Lead"
    
    print(f"Attempting to delete lead: {lead_name}")
    
    # Look for delete button or action menu
    delete_selectors = [
        'button:has-text("Delete")',
        'button[aria-label*="delete" i]',
        '[data-testid="delete-lead"]',
        'button:has(svg)',
        '.delete-button',
        '.action-button'
    ]
    
    delete_button = None
    for selector in delete_selectors:
        try:
            delete_button = first_lead.locator(selector).first
            if delete_button.is_visible():
                break
        except:
            continue
    
    if not delete_button or not delete_button.is_visible():
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
            
            # Look for delete option in dropdown
            delete_option = page.locator('button:has-text("Delete"), a:has-text("Delete"), div:has-text("Delete")').first
            if delete_option.is_visible():
                delete_option.click()
                print("Clicked delete option from action menu")
            else:
                raise AssertionError("Delete option not found in action menu")
        else:
            raise AssertionError("No delete button or action menu found")
    else:
        delete_button.click()
        print("Clicked delete button")
    
    # Wait for confirmation dialog
    time.sleep(2)
    
    # Look for confirmation dialog
    confirmation_selectors = [
        'text="Are you sure?"',
        'text="Delete lead?"',
        'text="Confirm delete"',
        '[role="dialog"]',
        '.modal',
        '.confirmation-dialog'
    ]
    
    confirmation_found = False
    for selector in confirmation_selectors:
        if page.locator(selector).is_visible():
            confirmation_found = True
            print("Confirmation dialog appeared")
            break
    
    if confirmation_found:
        # Look for confirm button
        confirm_selectors = [
            'button:has-text("Delete")',
            'button:has-text("Confirm")',
            'button:has-text("Yes")',
            'button:has-text("OK")',
            '[data-testid="confirm-delete"]',
            'button[type="submit"]'
        ]
        
        confirm_button = None
        for selector in confirm_selectors:
            try:
                confirm_button = page.locator(selector).first
                if confirm_button.is_visible():
                    break
            except:
                continue
        
        if confirm_button and confirm_button.is_visible():
            confirm_button.click()
            print("Confirmed deletion")
        else:
            raise AssertionError("Confirm button not found in dialog")
    else:
        print("No confirmation dialog found, proceeding with deletion")
    
    # Wait for deletion to complete
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Verify the lead was deleted
    success_indicators = [
        'text="Lead deleted successfully"',
        'text="Lead removed"',
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
    
    # Check if the lead no longer appears in the list
    if not page.locator(f'text="{lead_name}"').is_visible():
        print("Lead no longer appears in the list")
        success_found = True
    
    # Check if the lead count decreased
    current_lead_rows = page.locator('[data-testid="lead-row"], tr:has(td), .lead-item, .table-row').all()
    if len(current_lead_rows) < len(lead_rows):
        print("Lead count decreased")
        success_found = True
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/leads_delete.png")
    
    if success_found:
        return True
    else:
        raise AssertionError("Lead deletion success not confirmed")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_delete_lead(page)
            print("PASSED: TC_LEAD_003: Delete Lead")
        except Exception as e:
            print(f"FAILED: TC_LEAD_003: Delete Lead - {e}")
            page.screenshot(path="test-results/leads_delete_failure.png")
        finally:
            browser.close()

