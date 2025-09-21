#!/usr/bin/env python3
"""
Test script for deleting leads via API and UI
"""

import requests
import json
import time

def test_delete_lead_api():
    """Test deleting a lead via API"""
    
    print("🗑️ Testing Lead Deletion via API")
    print("=" * 50)
    
    # Login to get token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    }
    
    try:
        print("🔐 Logging in...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get existing leads
            print("📋 Getting existing leads...")
            leads_url = "http://127.0.0.1:8000/api/leads"
            leads_response = requests.get(leads_url, headers=headers, timeout=10)
            
            if leads_response.status_code == 200:
                leads_data = leads_response.json()
                if isinstance(leads_data, list) and len(leads_data) > 0:
                    print(f"📊 Found {len(leads_data)} leads")
                    
                    # Get the first lead to delete
                    lead_to_delete = leads_data[0]
                    lead_id = lead_to_delete.get("id")
                    lead_title = lead_to_delete.get("title")
                    
                    print(f"🎯 Selected lead for deletion:")
                    print(f"   ID: {lead_id}")
                    print(f"   Title: {lead_title}")
                    
                    # Delete the lead
                    delete_url = f"http://127.0.0.1:8000/api/leads/{lead_id}"
                    print(f"🗑️ Deleting lead {lead_id}...")
                    
                    delete_response = requests.delete(delete_url, headers=headers, timeout=10)
                    
                    print(f"📊 Delete response status: {delete_response.status_code}")
                    print(f"📋 Delete response: {delete_response.text}")
                    
                    if delete_response.status_code == 200:
                        print("✅ Lead deleted successfully via API!")
                        
                        # Verify deletion by checking leads list
                        print("🔍 Verifying deletion...")
                        verify_response = requests.get(leads_url, headers=headers, timeout=10)
                        
                        if verify_response.status_code == 200:
                            updated_leads = verify_response.json()
                            if isinstance(updated_leads, list):
                                print(f"📊 Updated leads count: {len(updated_leads)}")
                                
                                # Check if the deleted lead is gone
                                lead_found = False
                                for lead in updated_leads:
                                    if lead.get("id") == lead_id:
                                        lead_found = True
                                        break
                                
                                if not lead_found:
                                    print(f"✅ Lead {lead_id} successfully removed from database")
                                    return True
                                else:
                                    print(f"❌ Lead {lead_id} still exists in database")
                                    return False
                            else:
                                print(f"⚠️ Unexpected response format: {type(updated_leads)}")
                                return False
                        else:
                            print(f"❌ Failed to verify deletion: {verify_response.status_code}")
                            return False
                    else:
                        print(f"❌ Lead deletion failed with status: {delete_response.status_code}")
                        return False
                else:
                    print("❌ No leads found to delete")
                    return False
            else:
                print(f"❌ Failed to get leads: {leads_response.status_code}")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_delete_lead_ui():
    """Test deleting a lead via UI"""
    
    print("\n🗑️ Testing Lead Deletion via UI")
    print("=" * 50)
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Login to the system
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
            
            # Look for leads in the table
            print("🔍 Looking for leads in the table...")
            
            # Get the first lead row (skip header)
            lead_rows = page.locator('tr').all()
            if len(lead_rows) > 1:  # More than just header
                print(f"📊 Found {len(lead_rows) - 1} lead rows")
                
                # Get the first lead's title for reference
                first_lead_row = lead_rows[1]  # Skip header row
                lead_title = first_lead_row.locator('td').first.text_content()
                print(f"🎯 First lead title: {lead_title}")
                
                # Look for delete button in the first lead row
                delete_button = first_lead_row.locator('button:has-text("Delete"), button[aria-label*="delete" i], button:has(svg)').first
                
                if delete_button.is_visible():
                    print("✅ Found delete button, clicking...")
                    delete_button.click()
                    
                    # Wait for confirmation dialog
                    time.sleep(2)
                    
                    # Look for confirmation dialog
                    if page.locator('text="Are you sure?", text="Delete", [role="dialog"]').is_visible():
                        print("✅ Confirmation dialog appeared")
                        
                        # Look for confirm button
                        confirm_button = page.locator('button:has-text("Delete"), button:has-text("Confirm"), button:has-text("Yes")').first
                        if confirm_button.is_visible():
                            confirm_button.click()
                            print("✅ Confirmed deletion")
                            
                            # Wait for deletion to complete
                            page.wait_for_load_state("networkidle")
                            time.sleep(3)
                            
                            # Check if lead is no longer visible
                            if not page.locator(f'text="{lead_title}"').is_visible():
                                print(f"✅ Lead '{lead_title}' successfully deleted via UI")
                                return True
                            else:
                                print(f"⚠️ Lead '{lead_title}' still visible after deletion")
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
                print("❌ No leads found in table")
                return False
                
        except Exception as e:
            print(f"❌ Error during UI test: {e}")
            page.screenshot(path="test-results/lead_delete_ui_error.png")
            return False
        finally:
            browser.close()

def test_lead_delete_comprehensive():
    """Comprehensive test for lead deletion"""
    
    print("🚀 Comprehensive Lead Deletion Test")
    print("=" * 60)
    
    # Test API deletion first
    api_success = test_delete_lead_api()
    
    # Test UI deletion
    ui_success = test_delete_lead_ui()
    
    print(f"\n📊 Test Results:")
    print(f"   API Deletion: {'✅ Success' if api_success else '❌ Failed'}")
    print(f"   UI Deletion: {'✅ Success' if ui_success else '❌ Failed'}")
    
    if api_success and ui_success:
        print("\n🎉 All lead deletion tests passed!")
        print("✅ DELETE operation working via both API and UI")
    elif api_success or ui_success:
        print("\n⚠️ Partial success - some deletion methods working")
    else:
        print("\n❌ All lead deletion tests failed")
    
    return api_success and ui_success

if __name__ == "__main__":
    success = test_lead_delete_comprehensive()
    if success:
        print("\n🎉 Lead deletion functionality is working perfectly!")
    else:
        print("\n❌ Lead deletion needs attention.")

