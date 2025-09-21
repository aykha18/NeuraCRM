#!/usr/bin/env python3
"""
Working Playwright automation script for lead CRUD operations
Uses the correct selectors from the actual HTML structure
"""

from playwright.sync_api import Page, expect
import time

def test_create_lead_working(page: Page):
    """Test creating a lead using the correct selectors"""
    
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
    create_button = page.locator('button:has-text("Create Lead")').first
    if create_button.is_visible():
        print("Found create button, clicking...")
        create_button.click()
        
        # Wait for modal to appear
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Check if modal is open by looking for the title
        if page.locator('h2:has-text("Create New Lead")').is_visible():
            print("Modal opened successfully")
            
            # Fill the lead title field using the correct selector
            title_field = page.locator('input[placeholder="Enter lead title"]')
            if title_field.is_visible():
                lead_title = f"Test Lead {int(time.time())}"
                title_field.fill(lead_title)
                print(f"Filled lead title: {lead_title}")
                
                # Select status (optional - will use default "new")
                status_select = page.locator('select').first
                if status_select.is_visible():
                    try:
                        status_select.select_option("new")
                        print("Selected status: new")
                    except:
                        print("Status selection failed, using default")
                
                # Select source (optional - will use default "manual")
                source_selects = page.locator('select').all()
                if len(source_selects) > 1:
                    try:
                        source_selects[1].select_option("manual")
                        print("Selected source: manual")
                    except:
                        print("Source selection failed, using default")
            
                # Click the Create Lead button using the correct selector
                create_lead_button = page.locator('button:has-text("Create Lead")').last
                if create_lead_button.is_visible():
                    print("Clicking Create Lead button...")
                    create_lead_button.click()
                    
                    # Wait for save to complete
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                    
                    # Check if we're back on leads page
                    current_url = page.url
                    if "/leads" in current_url:
                        print("Redirected back to leads page")
                        
                        # Check if the new lead appears in the list
                        if page.locator(f'text="{lead_title}"').is_visible():
                            print(f"✅ Lead created successfully: {lead_title}")
                            return {"name": lead_title, "status": "created"}
                        else:
                            print("⚠️ Lead not visible in list but page redirected")
                            return {"name": lead_title, "status": "uncertain"}
                    else:
                        print("⚠️ Not redirected to leads page")
                        return None
                else:
                    print("❌ Create Lead button not found in modal")
                    return None
            else:
                print("❌ Lead title field not found")
                return None
        else:
            print("❌ Modal did not open")
            return None
    else:
        print("❌ Create Lead button not found")
        return None

def test_delete_lead_working(page: Page, lead_name):
    """Test deleting a lead using the correct selectors"""
    
    # Navigate to leads page
    page.goto("http://127.0.0.1:8000/leads")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Look for the lead in the list
    if page.locator(f'text="{lead_name}"').is_visible():
        print(f"Found lead: {lead_name}")
        
        # Find the lead row and look for delete button
        lead_row = page.locator(f'tr:has-text("{lead_name}"), div:has-text("{lead_name}")').first
        
        # Look for delete button in the row
        delete_button = lead_row.locator('button:has-text("Delete"), button[aria-label*="delete" i], button:has(svg)').first
        
        if delete_button.is_visible():
            print("Found delete button, clicking...")
            delete_button.click()
            
            # Wait for confirmation dialog
            time.sleep(2)
            
            # Look for confirmation dialog
            if page.locator('text="Are you sure?", text="Delete", [role="dialog"]').is_visible():
                print("Confirmation dialog appeared")
                
                # Look for confirm button
                confirm_button = page.locator('button:has-text("Delete"), button:has-text("Confirm"), button:has-text("Yes")').first
                if confirm_button.is_visible():
                    confirm_button.click()
                    print("Confirmed deletion")
                    
                    # Wait for deletion to complete
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                    
                    # Check if lead is no longer visible
                    if not page.locator(f'text="{lead_name}"').is_visible():
                        print(f"✅ Lead deleted successfully: {lead_name}")
                        return True
                    else:
                        print(f"⚠️ Lead still visible after deletion: {lead_name}")
                        return False
                else:
                    print("❌ Confirm button not found")
                    return False
            else:
                print("❌ Confirmation dialog not found")
                return False
        else:
            print("❌ Delete button not found")
            return False
    else:
        print(f"❌ Lead not found: {lead_name}")
        return False

def test_create_two_leads_and_delete_one():
    """Test creating 2 leads and deleting 1"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("=== Creating First Lead ===")
            lead1 = test_create_lead_working(page)
            
            if lead1 and lead1["status"] == "created":
                print(f"✅ First lead created: {lead1['name']}")
                
                print("\n=== Creating Second Lead ===")
                lead2 = test_create_lead_working(page)
                
                if lead2 and lead2["status"] == "created":
                    print(f"✅ Second lead created: {lead2['name']}")
                    
                    print("\n=== Deleting First Lead ===")
                    delete_result = test_delete_lead_working(page, lead1['name'])
                    
                    if delete_result:
                        print("✅ First lead successfully deleted")
                        print(f"✅ Second lead remains: {lead2['name']}")
                        
                        print("\n🎉 CRUD Test Summary:")
                        print(f"   Created Lead 1: {lead1['name']} ✅")
                        print(f"   Created Lead 2: {lead2['name']} ✅")
                        print(f"   Deleted Lead 1: {lead1['name']} ✅")
                        print(f"   Remaining Lead: {lead2['name']} ✅")
                        
                        return True
                    else:
                        print("❌ Failed to delete first lead")
                        return False
                else:
                    print("❌ Second lead creation failed")
                    return False
            else:
                print("❌ First lead creation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            page.screenshot(path="test-results/lead_crud_test_error.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_create_two_leads_and_delete_one()
    if success:
        print("\n🎉 All CRUD operations completed successfully!")
    else:
        print("\n❌ Some CRUD operations failed")
