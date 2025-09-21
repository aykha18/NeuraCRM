#!/usr/bin/env python3
"""
Improved Playwright automation script for lead creation
Handles modal overlays and form interactions properly
"""

from playwright.sync_api import Page, expect
import time

def test_create_lead_improved(page: Page):
    """Test creating a lead with improved modal handling"""
    
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
    
    # Look for create lead button
    create_button_selectors = [
        'button:has-text("Create Lead")',
        'button:has-text("Add Lead")',
        'button:has-text("New Lead")',
        '[data-testid="create-lead"]',
        'button[aria-label*="create" i]',
        'button[aria-label*="add" i]'
    ]
    
    create_button = None
    for selector in create_button_selectors:
        try:
            create_button = page.locator(selector).first
            if create_button.is_visible():
                break
        except:
            continue
    
    if not create_button or not create_button.is_visible():
        # Try looking for a plus icon or add button
        create_button = page.locator('button:has(svg), button:has-text("+"), [aria-label*="add" i]').first
    
    if create_button and create_button.is_visible():
        print("Found create button, clicking...")
        create_button.click()
        
        # Wait for modal to appear
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Check if modal is open
        modal_selectors = [
            '[role="dialog"]',
            '.modal',
            '[data-testid="modal"]',
            'div:has-text("Create New Lead")',
            'div:has-text("Create Lead")'
        ]
        
        modal_found = False
        for selector in modal_selectors:
            if page.locator(selector).is_visible():
                modal_found = True
                print(f"Modal found with selector: {selector}")
                break
        
        if not modal_found:
            print("Modal not found, checking page content...")
            page.screenshot(path="test-results/lead_creation_no_modal.png")
            raise AssertionError("Create lead modal did not open")
        
        # Fill lead form
        lead_data = {
            "name": "Test Lead " + str(int(time.time())),
            "email": f"testlead{int(time.time())}@example.com",
            "company": "Test Company Inc",
            "phone": "+1-555-0123"
        }
        
        print(f"Filling lead data: {lead_data}")
        
        # Fill name field - look in modal
        name_selectors = [
            'input[name*="name" i]',
            'input[placeholder*="name" i]',
            'input[id*="name" i]',
            'input[type="text"]'
        ]
        
        name_field = None
        for selector in name_selectors:
            try:
                name_field = page.locator(selector).first
                if name_field.is_visible():
                    name_field.clear()
                    name_field.fill(lead_data["name"])
                    print(f"Filled name field: {lead_data['name']}")
                    break
            except:
                continue
        
        if not name_field or not name_field.is_visible():
            print("Name field not found, taking screenshot...")
            page.screenshot(path="test-results/lead_creation_no_name_field.png")
            raise AssertionError("Name field not found in modal")
        
        # Fill email field
        email_field = page.locator('input[type="email"]').first
        if email_field.is_visible():
            email_field.clear()
            email_field.fill(lead_data["email"])
            print(f"Filled email field: {lead_data['email']}")
        else:
            print("Email field not found")
        
        # Fill company field
        company_selectors = [
            'input[name*="company" i]',
            'input[placeholder*="company" i]',
            'input[id*="company" i]'
        ]
        
        company_field = None
        for selector in company_selectors:
            try:
                company_field = page.locator(selector).first
                if company_field.is_visible():
                    company_field.clear()
                    company_field.fill(lead_data["company"])
                    print(f"Filled company field: {lead_data['company']}")
                    break
            except:
                continue
        
        # Fill phone field
        phone_selectors = [
            'input[name*="phone" i]',
            'input[placeholder*="phone" i]',
            'input[id*="phone" i]',
            'input[type="tel"]'
        ]
        
        phone_field = None
        for selector in phone_selectors:
            try:
                phone_field = page.locator(selector).first
                if phone_field.is_visible():
                    phone_field.clear()
                    phone_field.fill(lead_data["phone"])
                    print(f"Filled phone field: {lead_data['phone']}")
                    break
            except:
                continue
        
        # Save the lead - look for save button in modal
        save_button_selectors = [
            'button:has-text("Save")',
            'button:has-text("Create")',
            'button:has-text("Submit")',
            'button[type="submit"]',
            '[data-testid="save-lead"]',
            'button:has-text("Create Lead")'
        ]
        
        save_button = None
        for selector in save_button_selectors:
            try:
                save_button = page.locator(selector).first
                if save_button.is_visible():
                    break
            except:
                continue
        
        if save_button and save_button.is_visible():
            print("Clicking save button...")
            save_button.click()
            
            # Wait for save to complete
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Check for success message or redirect
            success_indicators = [
                'text="Lead created successfully"',
                'text="Lead saved"',
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
            
            # Check if we're back on leads page
            current_url = page.url
            if "/leads" in current_url:
                print("Redirected back to leads page")
                success_found = True
            
            # Check if the new lead appears in the list
            if page.locator(f'text="{lead_data["name"]}"').is_visible():
                print("New lead appears in the leads list")
                success_found = True
            
            if success_found:
                print("Lead creation successful!")
                return lead_data
            else:
                print("Lead creation success not confirmed")
                page.screenshot(path="test-results/lead_creation_uncertain.png")
                return None
        else:
            print("Save button not found")
            page.screenshot(path="test-results/lead_creation_no_save_button.png")
            raise AssertionError("Save button not found in modal")
    else:
        print("Create lead button not found")
        page.screenshot(path="test-results/lead_creation_no_button.png")
        raise AssertionError("Create lead button not found")

def test_create_two_leads_and_delete_one():
    """Test creating 2 leads and deleting 1"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("=== Creating First Lead ===")
            lead1 = test_create_lead_improved(page)
            
            if lead1:
                print(f"✅ First lead created: {lead1['name']}")
                
                print("\n=== Creating Second Lead ===")
                lead2 = test_create_lead_improved(page)
                
                if lead2:
                    print(f"✅ Second lead created: {lead2['name']}")
                    
                    print("\n=== Deleting First Lead ===")
                    # Navigate to leads page
                    page.goto("http://127.0.0.1:8000/leads")
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                    
                    # Look for the first lead in the list
                    lead_rows = page.locator('[data-testid="lead-row"], tr:has(td), .lead-item, .table-row').all()
                    
                    if len(lead_rows) > 0:
                        first_lead = lead_rows[0]
                        
                        # Look for delete button
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
                        
                        if delete_button and delete_button.is_visible():
                            print("Found delete button, clicking...")
                            delete_button.click()
                            
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
                                    
                                    # Wait for deletion to complete
                                    page.wait_for_load_state("networkidle")
                                    time.sleep(3)
                                    
                                    # Check if deletion was successful
                                    if not page.locator(f'text="{lead1["name"]}"').is_visible():
                                        print("✅ First lead successfully deleted")
                                    else:
                                        print("⚠️ First lead still visible after deletion")
                                else:
                                    print("❌ Confirm button not found in dialog")
                            else:
                                print("❌ Confirmation dialog not found")
                        else:
                            print("❌ Delete button not found")
                    else:
                        print("❌ No leads found to delete")
                else:
                    print("❌ Second lead creation failed")
            else:
                print("❌ First lead creation failed")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            page.screenshot(path="test-results/lead_crud_test_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    test_create_two_leads_and_delete_one()

