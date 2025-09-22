#!/usr/bin/env python3
"""
Customer Segmentation API Integration Test
Tests API calls and data loading for customer segmentation
"""

from playwright.sync_api import sync_playwright
import time
import requests
import json

def test_customer_segmentation_api_integration():
    """Test API integration for customer segmentation"""
    
    print("👥 Testing Customer Segmentation API Integration")
    print("=" * 50)
    
    # Test API endpoints directly
    print("\n🔌 Testing API endpoints directly...")
    
    base_url = "http://127.0.0.1:8000"
    api_endpoints = [
        "/api/customer-segments",
        "/api/customer-segments/{id}/members",
        "/api/customer-segments/{id}/refresh"
    ]
    
    # First, get auth token
    auth_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    })
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return False
    
    # Test customer segments endpoint
    print(f"\n📡 Testing /api/customer-segments...")
    try:
        response = requests.get(f"{base_url}/api/customer-segments", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ /api/customer-segments - Status: {response.status_code}")
            print(f"  📊 Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"  ✅ Found {len(data)} customer segments")
                
                if len(data) > 0:
                    # Check first segment structure
                    first_segment = data[0]
                    expected_keys = [
                        "id", "name", "description", "segment_type", 
                        "customer_count", "total_deal_value", "avg_deal_value",
                        "conversion_rate", "insights", "recommendations",
                        "risk_score", "opportunity_score", "is_active",
                        "last_updated", "created_at"
                    ]
                    
                    for key in expected_keys:
                        if key in first_segment:
                            print(f"    ✅ Found expected key: {key}")
                        else:
                            print(f"    ❌ Missing expected key: {key}")
                    
                    # Test segment members endpoint
                    segment_id = first_segment["id"]
                    print(f"\n📡 Testing /api/customer-segments/{segment_id}/members...")
                    try:
                        members_response = requests.get(f"{base_url}/api/customer-segments/{segment_id}/members", headers=headers, timeout=10)
                        if members_response.status_code == 200:
                            members_data = members_response.json()
                            print(f"  ✅ /api/customer-segments/{segment_id}/members - Status: {members_response.status_code}")
                            print(f"  📊 Response type: {type(members_data)}")
                            
                            if isinstance(members_data, list):
                                print(f"  ✅ Found {len(members_data)} segment members")
                                
                                if len(members_data) > 0:
                                    # Check first member structure
                                    first_member = members_data[0]
                                    member_expected_keys = [
                                        "id", "contact_id", "contact_name", "contact_email",
                                        "contact_company", "membership_score", "segment_engagement_score",
                                        "added_at"
                                    ]
                                    
                                    for key in member_expected_keys:
                                        if key in first_member:
                                            print(f"    ✅ Found expected key: {key}")
                                        else:
                                            print(f"    ❌ Missing expected key: {key}")
                                else:
                                    print("  ⚠️ No members found for this segment")
                            else:
                                print(f"  ❌ Members response is not a list: {type(members_data)}")
                        else:
                            print(f"  ❌ /api/customer-segments/{segment_id}/members - Status: {members_response.status_code}")
                    except requests.exceptions.Timeout:
                        print(f"  ⏰ /api/customer-segments/{segment_id}/members - Timeout")
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ /api/customer-segments/{segment_id}/members - Error: {e}")
                    
                    # Test segment refresh endpoint
                    print(f"\n📡 Testing /api/customer-segments/{segment_id}/refresh...")
                    try:
                        refresh_response = requests.post(f"{base_url}/api/customer-segments/{segment_id}/refresh", headers=headers, timeout=10)
                        if refresh_response.status_code == 200:
                            print(f"  ✅ /api/customer-segments/{segment_id}/refresh - Status: {refresh_response.status_code}")
                        else:
                            print(f"  ❌ /api/customer-segments/{segment_id}/refresh - Status: {refresh_response.status_code}")
                    except requests.exceptions.Timeout:
                        print(f"  ⏰ /api/customer-segments/{segment_id}/refresh - Timeout")
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ /api/customer-segments/{segment_id}/refresh - Error: {e}")
                else:
                    print("  ⚠️ No customer segments found")
            else:
                print(f"  ❌ Response is not a list: {type(data)}")
        else:
            print(f"  ❌ /api/customer-segments - Status: {response.status_code}")
            print(f"  📝 Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"  ⏰ /api/customer-segments - Timeout")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ /api/customer-segments - Error: {e}")
    
    # Test UI integration
    print("\n🖥️ Testing UI integration...")
    
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
            
            # Navigate to customer segmentation
            print("\n👥 Navigating to Customer Segmentation page...")
            page.goto("http://127.0.0.1:8000/customer-segmentation")
            page.wait_for_load_state("networkidle")
            
            # Monitor network requests
            print("\n📡 Monitoring network requests...")
            
            # Wait for API calls to complete
            time.sleep(5)
            
            # Check if error message is shown
            error_message = page.locator('.bg-red-50:has-text("Failed to fetch")')
            if error_message.is_visible():
                print("  ❌ API error message shown")
            else:
                print("  ✅ No API error message")
            
            # Check if data is displayed
            print("\n📊 Checking data display...")
            
            # Check for loading spinner
            loading_spinner = page.locator('.animate-spin')
            if loading_spinner.is_visible():
                print("  ⏳ Loading spinner still visible")
            else:
                print("  ✅ Loading spinner not visible")
            
            # Check for segments
            segments = page.locator('.space-y-4 > div')
            segment_count = segments.count()
            if segment_count > 0:
                print(f"  ✅ Found {segment_count} customer segments in UI")
                
                # Test segment selection
                first_segment = segments.first
                if first_segment.is_visible():
                    first_segment.click()
                    time.sleep(2)
                    print("  ✅ Selected first segment")
                    
                    # Check for segment details
                    overview_section = page.locator('h3:has-text("Segment Overview")')
                    if overview_section.is_visible():
                        print("  ✅ Segment details displayed")
                    else:
                        print("  ❌ Segment details not displayed")
                    
                    # Check for segment members
                    members_section = page.locator('h3:has-text("Segment Members")')
                    if members_section.is_visible():
                        print("  ✅ Segment members section displayed")
                    else:
                        print("  ❌ Segment members section not displayed")
                else:
                    print("  ❌ First segment not visible")
            else:
                print("  ❌ No customer segments found in UI")
            
            # Test segment refresh functionality
            print("\n🔄 Testing segment refresh functionality...")
            if segment_count > 0:
                first_segment = segments.first
                refresh_button = first_segment.locator('button')
                if refresh_button.is_visible():
                    refresh_button.click()
                    time.sleep(2)
                    print("  ✅ Clicked refresh button")
                    
                    # Check if refresh completed
                    loading_spinner = first_segment.locator('.animate-spin')
                    if not loading_spinner.is_visible():
                        print("  ✅ Refresh completed")
                    else:
                        print("  ⏳ Refresh still in progress")
                else:
                    print("  ❌ Refresh button not found")
            
            # Test data formatting
            print("\n📝 Testing data formatting...")
            
            # Check for currency formatting
            currency_elements = page.locator('text=/\\$[\\d,]+/')
            if currency_elements.count() > 0:
                print(f"  ✅ Found {currency_elements.count()} currency formatted values")
            else:
                print("  ❌ No currency formatted values found")
            
            # Check for percentage formatting
            percentage_elements = page.locator('text=/\\d+%/')
            if percentage_elements.count() > 0:
                print(f"  ✅ Found {percentage_elements.count()} percentage formatted values")
            else:
                print("  ❌ No percentage formatted values found")
            
            # Check for date formatting
            date_elements = page.locator('text=/\\w{3}\\s+\\d{1,2},\\s+\\d{4}/')
            if date_elements.count() > 0:
                print(f"  ✅ Found {date_elements.count()} date formatted values")
            else:
                print("  ❌ No date formatted values found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/customer_segmentation_api_integration.png")
            print("✅ Screenshot saved as customer_segmentation_api_integration.png")
            
            print("\n🎉 Customer Segmentation API integration test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during UI test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_customer_segmentation_api_integration()
    if success:
        print("\n✅ Customer Segmentation API integration test passed!")
    else:
        print("\n❌ Customer Segmentation API integration test failed.")

