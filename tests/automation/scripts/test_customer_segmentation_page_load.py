#!/usr/bin/env python3
"""
Customer Segmentation Page Load Test
Tests the basic loading and display of the customer segmentation page
"""

from playwright.sync_api import sync_playwright
import time

def test_customer_segmentation_page_load():
    """Test that the customer segmentation page loads correctly"""
    
    print("👥 Testing Customer Segmentation Page Load")
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
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("AI Customer Segmentation")')
            if title.is_visible():
                print("✅ Page title 'AI Customer Segmentation' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check page description
            print("\n📝 Checking page description...")
            description = page.locator('.text-gray-600:has-text("Automatically segment customers")')
            if description.is_visible():
                print("✅ Page description found")
            else:
                print("❌ Page description not found")
            
            # Check AI insights banner
            print("\n🧠 Checking AI insights banner...")
            ai_banner = page.locator('.bg-gradient-to-r.from-purple-50.to-pink-50')
            if ai_banner.is_visible():
                print("✅ AI insights banner found")
                
                # Check for AI-powered segmentation text
                ai_text = page.locator('text="AI-Powered Segmentation"')
                if ai_text.is_visible():
                    print("  ✅ AI-Powered Segmentation text found")
                else:
                    print("  ❌ AI-Powered Segmentation text not found")
            else:
                print("❌ AI insights banner not found")
            
            # Check segments list section
            print("\n📊 Checking segments list section...")
            segments_section = page.locator('.bg-white.rounded-xl.shadow-lg.border').first
            if segments_section.is_visible():
                print("✅ Segments list section found")
                
                # Check for segments heading
                segments_heading = page.locator('h2:has-text("Customer Segments")')
                if segments_heading.is_visible():
                    print("  ✅ Customer Segments heading found")
                else:
                    print("  ❌ Customer Segments heading not found")
                
                # Check for segment count
                segment_count = page.locator('.text-sm.text-gray-500')
                if segment_count.is_visible():
                    count_text = segment_count.text_content()
                    print(f"  ✅ Segment count found: {count_text}")
                else:
                    print("  ❌ Segment count not found")
            else:
                print("❌ Segments list section not found")
            
            # Check segment details panel
            print("\n📋 Checking segment details panel...")
            details_panel = page.locator('.lg\\:col-span-1')
            if details_panel.is_visible():
                print("✅ Segment details panel found")
                
                # Check for default message
                default_message = page.locator('text="Select a segment to view details"')
                if default_message.is_visible():
                    print("  ✅ Default 'Select a segment' message found")
                else:
                    print("  ❌ Default message not found")
            else:
                print("❌ Segment details panel not found")
            
            # Check for segments
            print("\n👥 Checking for customer segments...")
            segments = page.locator('.space-y-4 > div')
            segment_count = segments.count()
            if segment_count > 0:
                print(f"✅ Found {segment_count} customer segments")
                
                # Check first segment for required elements
                first_segment = segments.first
                if first_segment.is_visible():
                    # Check for segment name
                    segment_name = first_segment.locator('h3.font-semibold')
                    if segment_name.is_visible():
                        name_text = segment_name.text_content()
                        print(f"  ✅ First segment name: {name_text}")
                    else:
                        print("  ❌ Segment name not found")
                    
                    # Check for segment description
                    segment_desc = first_segment.locator('.text-sm.text-gray-600')
                    if segment_desc.is_visible():
                        print("  ✅ Segment description found")
                    else:
                        print("  ❌ Segment description not found")
                    
                    # Check for segment type badge
                    segment_type = first_segment.locator('.px-2.py-1.rounded-full')
                    if segment_type.is_visible():
                        type_text = segment_type.text_content()
                        print(f"  ✅ Segment type badge: {type_text}")
                    else:
                        print("  ❌ Segment type badge not found")
                    
                    # Check for segment statistics
                    stats = first_segment.locator('.grid.grid-cols-4.gap-4')
                    if stats.is_visible():
                        print("  ✅ Segment statistics found")
                        
                        # Check for specific stats
                        stat_items = first_segment.locator('.text-center')
                        stat_count = stat_items.count()
                        if stat_count >= 4:
                            print(f"    ✅ Found {stat_count} statistic items")
                        else:
                            print(f"    ❌ Expected at least 4 stats, found {stat_count}")
                    else:
                        print("  ❌ Segment statistics not found")
                    
                    # Check for refresh button
                    refresh_button = first_segment.locator('button')
                    if refresh_button.is_visible():
                        print("  ✅ Refresh button found")
                    else:
                        print("  ❌ Refresh button not found")
            else:
                print("❌ No customer segments found")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-users, .lucide-users2, .lucide-brain, .lucide-zap, .lucide-eye')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/customer_segmentation_page_load.png")
            print("✅ Screenshot saved as customer_segmentation_page_load.png")
            
            print("\n🎉 Customer Segmentation page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_customer_segmentation_page_load()
    if success:
        print("\n✅ Customer Segmentation page load test passed!")
    else:
        print("\n❌ Customer Segmentation page load test failed.")
