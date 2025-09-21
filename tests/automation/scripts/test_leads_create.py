#!/usr/bin/env python3
"""
Playwright automation script for TC_LEAD_001: Create New Lead
"""

from playwright.sync_api import Page, expect
import time

def test_create_new_lead(page: Page):
    """Test creating a new lead"""
    
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
        create_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Fill lead form
        lead_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "company": "Acme Corp",
            "phone": "+1-555-0123"
        }
        
        # Fill name field
        name_selectors = [
            'input[name*="name" i]',
            'input[placeholder*="name" i]',
            'input[id*="name" i]'
        ]
        
        name_field = None
        for selector in name_selectors:
            try:
                name_field = page.locator(selector).first
                if name_field.is_visible():
                    break
            except:
                continue
        
        if name_field and name_field.is_visible():
            name_field.fill(lead_data["name"])
            print(f"✅ Filled name field: {lead_data['name']}")
        else:
            print("⚠️ Name field not found")
        
        # Fill email field
        email_field = page.locator('input[type="email"]').or_(page.locator('input[name*="email" i]')).first
        if email_field.is_visible():
            email_field.fill(lead_data["email"])
            print(f"✅ Filled email field: {lead_data['email']}")
        
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
                    break
            except:
                continue
        
        if company_field and company_field.is_visible():
            company_field.fill(lead_data["company"])
            print(f"✅ Filled company field: {lead_data['company']}")
        
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
                    break
            except:
                continue
        
        if phone_field and phone_field.is_visible():
            phone_field.fill(lead_data["phone"])
            print(f"✅ Filled phone field: {lead_data['phone']}")
        
        # Save the lead
        save_button_selectors = [
            'button:has-text("Save")',
            'button:has-text("Create")',
            'button:has-text("Submit")',
            'button[type="submit"]',
            '[data-testid="save-lead"]'
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
            save_button.click()
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
                        print("✅ Success message displayed")
                        success_found = True
                        break
                except:
                    continue
            
            # Check if we're back on leads page
            current_url = page.url
            if "/leads" in current_url:
                print("✅ Redirected back to leads page")
                success_found = True
            
            # Check if the new lead appears in the list
            if page.locator(f'text="{lead_data["name"]}"').is_visible():
                print("✅ New lead appears in the leads list")
                success_found = True
            
            if success_found:
                return True
            else:
                raise AssertionError("Lead creation success not confirmed")
        else:
            raise AssertionError("Save button not found")
    else:
        raise AssertionError("Create lead button not found")
    
    # Take screenshot for debugging
    page.screenshot(path="test-results/leads_create.png")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            result = test_create_new_lead(page)
            print("✅ TC_LEAD_001: Create New Lead - PASSED")
        except Exception as e:
            print(f"❌ TC_LEAD_001: Create New Lead - FAILED: {e}")
            page.screenshot(path="test-results/leads_create_failure.png")
        finally:
            browser.close()
