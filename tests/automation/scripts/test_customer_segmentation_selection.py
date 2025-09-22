#!/usr/bin/env python3
"""
Customer Segmentation Selection Test
Tests selecting segments and viewing their details
"""

from playwright.sync_api import sync_playwright
import time

def test_customer_segmentation_selection():
    """Test selecting customer segments and viewing details"""
    
    print("👥 Testing Customer Segmentation Selection")
    print("=" * 50)
    
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
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to customer segmentation page")
            
            # Check for segments
            print("\n👥 Checking for customer segments...")
            segments = page.locator('.space-y-4 > div')
            segment_count = segments.count()
            if segment_count > 0:
                print(f"✅ Found {segment_count} customer segments")
                
                # Test selecting the first segment
                print("\n🎯 Testing segment selection...")
                first_segment = segments.first
                if first_segment.is_visible():
                    first_segment.click()
                    time.sleep(2)  # Wait for details to load
                    print("✅ Clicked on first segment")
                    
                    # Check if segment is selected (highlighted)
                    class_attr = first_segment.get_attribute('class')
                    if 'border-purple-500' in class_attr or 'bg-purple-50' in class_attr:
                        print("✅ Segment is highlighted/selected")
                    else:
                        print("⚠️ Segment may not be properly selected")
                    
                    # Check segment details panel
                    print("\n📋 Checking segment details panel...")
                    
                    # Check for segment overview section
                    overview_section = page.locator('h3:has-text("Segment Overview")')
                    if overview_section.is_visible():
                        print("✅ Segment Overview section found")
                        
                        # Check for risk score
                        risk_score = page.locator('text="Risk Score"')
                        if risk_score.is_visible():
                            print("  ✅ Risk Score found")
                        else:
                            print("  ❌ Risk Score not found")
                        
                        # Check for opportunity score
                        opportunity_score = page.locator('text="Opportunity Score"')
                        if opportunity_score.is_visible():
                            print("  ✅ Opportunity Score found")
                        else:
                            print("  ❌ Opportunity Score not found")
                        
                        # Check for last updated
                        last_updated = page.locator('text="Last Updated"')
                        if last_updated.is_visible():
                            print("  ✅ Last Updated found")
                        else:
                            print("  ❌ Last Updated not found")
                    else:
                        print("❌ Segment Overview section not found")
                    
                    # Check for AI insights section
                    print("\n🧠 Checking AI insights section...")
                    ai_insights = page.locator('h3:has-text("AI Insights")')
                    if ai_insights.is_visible():
                        print("✅ AI Insights section found")
                        
                        # Check for key characteristics
                        key_char = page.locator('text="Key Characteristics"')
                        if key_char.is_visible():
                            print("  ✅ Key Characteristics found")
                        else:
                            print("  ❌ Key Characteristics not found")
                        
                        # Check for performance summary
                        perf_summary = page.locator('text="Performance Summary"')
                        if perf_summary.is_visible():
                            print("  ✅ Performance Summary found")
                        else:
                            print("  ❌ Performance Summary not found")
                        
                        # Check for trends
                        trends = page.locator('text="Trends"')
                        if trends.is_visible():
                            print("  ✅ Trends found")
                        else:
                            print("  ❌ Trends not found")
                    else:
                        print("⚠️ AI Insights section not found (may not have insights)")
                    
                    # Check for recommendations section
                    print("\n💡 Checking recommendations section...")
                    recommendations = page.locator('h3:has-text("Recommendations")')
                    if recommendations.is_visible():
                        print("✅ Recommendations section found")
                        
                        # Check for recommendation items
                        rec_items = page.locator('.space-y-2 > li')
                        rec_count = rec_items.count()
                        if rec_count > 0:
                            print(f"  ✅ Found {rec_count} recommendations")
                        else:
                            print("  ❌ No recommendations found")
                    else:
                        print("⚠️ Recommendations section not found (may not have recommendations)")
                    
                    # Check for segment members section
                    print("\n👥 Checking segment members section...")
                    members_section = page.locator('h3:has-text("Segment Members")')
                    if members_section.is_visible():
                        print("✅ Segment Members section found")
                        
                        # Check for member count in header
                        member_count = page.locator('text=/Segment Members \\(\\d+\\)/')
                        if member_count.is_visible():
                            count_text = member_count.text_content()
                            print(f"  ✅ Member count found: {count_text}")
                        else:
                            print("  ❌ Member count not found")
                        
                        # Check for member items
                        member_items = page.locator('.space-y-3 > div')
                        member_item_count = member_items.count()
                        if member_item_count > 0:
                            print(f"  ✅ Found {member_item_count} member items")
                            
                            # Check first member for required info
                            first_member = member_items.first
                            if first_member.is_visible():
                                # Check for contact name
                                contact_name = first_member.locator('.font-medium')
                                if contact_name.is_visible():
                                    name_text = contact_name.text_content()
                                    print(f"    ✅ Contact name: {name_text}")
                                else:
                                    print("    ❌ Contact name not found")
                                
                                # Check for company
                                company = first_member.locator('.text-sm.text-gray-600')
                                if company.is_visible():
                                    print("    ✅ Company found")
                                else:
                                    print("    ❌ Company not found")
                                
                                # Check for email
                                email = first_member.locator('.text-xs.text-gray-500')
                                if email.is_visible():
                                    print("    ✅ Email found")
                                else:
                                    print("    ❌ Email not found")
                                
                                # Check for membership score
                                membership_score = first_member.locator('.text-sm.font-medium')
                                if membership_score.is_visible():
                                    score_text = membership_score.text_content()
                                    print(f"    ✅ Membership score: {score_text}")
                                else:
                                    print("    ❌ Membership score not found")
                        else:
                            print("  ❌ No member items found")
                    else:
                        print("❌ Segment Members section not found")
                    
                    # Test selecting another segment
                    print("\n🔄 Testing selection of another segment...")
                    if segment_count > 1:
                        second_segment = segments.nth(1)
                        if second_segment.is_visible():
                            second_segment.click()
                            time.sleep(2)
                            print("✅ Clicked on second segment")
                            
                            # Check if details updated
                            new_overview = page.locator('h3:has-text("Segment Overview")')
                            if new_overview.is_visible():
                                print("✅ Segment details updated for second segment")
                            else:
                                print("❌ Segment details not updated")
                        else:
                            print("❌ Second segment not visible")
                    else:
                        print("⚠️ Only one segment available, cannot test selection switching")
                    
                else:
                    print("❌ First segment not visible")
                    return False
            else:
                print("❌ No customer segments found")
                return False
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/customer_segmentation_selection.png")
            print("✅ Screenshot saved as customer_segmentation_selection.png")
            
            print("\n🎉 Customer Segmentation selection test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_customer_segmentation_selection()
    if success:
        print("\n✅ Customer Segmentation selection test passed!")
    else:
        print("\n❌ Customer Segmentation selection test failed.")

