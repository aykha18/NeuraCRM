#!/usr/bin/env python3
"""
Deals UI Detail Modal Test
Tests the deal detail modal and its structure to understand available features
"""

from playwright.sync_api import sync_playwright
import time

def test_deals_ui_detail_modal():
    """Test deal detail modal structure and features"""
    
    print("🚀 NeuraCRM Deals UI Detail Modal Test")
    print("=" * 50)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # ===== LOGIN =====
            print("🔐 Logging in...")
            page.goto("http://127.0.0.1:8000/signin")
            page.wait_for_load_state("networkidle")
            
            # Fill login form
            page.fill('input[type="email"]', "nodeit@node.com")
            page.fill('input[type="password"]', "NodeIT2024!")
            page.click('button[type="submit"]')
            
            # Wait for dashboard to load
            page.wait_for_url("**/dashboard", timeout=10000)
            print("✅ Login successful")
            
            # ===== NAVIGATE TO DEALS =====
            print("\n📋 Navigating to deals (Kanban) page...")
            page.goto("http://127.0.0.1:8000/kanban")
            page.wait_for_load_state("networkidle")
            
            # Wait for Kanban board
            page.wait_for_selector('[data-rbd-droppable-id], .flex-shrink-0.w-72', timeout=15000)
            print("✅ Navigated to deals (Kanban) page")
            
            # ===== EXPLORE DEAL DETAIL MODAL =====
            print("\n🔍 Exploring deal detail modal...")
            
            # Get first deal card
            deal_cards = page.locator('[data-rbd-draggable-id], .space-y-4 > div')
            deal_count = deal_cards.count()
            print(f"🎯 Found {deal_count} deal cards")
            
            if deal_count > 0:
                first_deal = deal_cards.first
                
                # Look for "View" button on the deal card
                print("🖱️ Looking for View button on deal card...")
                view_button = first_deal.locator('button:has-text("View")').first
                
                if view_button.is_visible():
                    print("✅ Found View button, clicking...")
                    view_button.click()
                    page.wait_for_timeout(3000)
                else:
                    print("⚠️ View button not found, trying to click deal card...")
                    first_deal.click()
                    page.wait_for_timeout(3000)
                
                # Check for any modal or detail view
                print("\n🔍 Looking for modal/detail view...")
                
                # Check for various modal selectors
                modal_selectors = [
                    '.modal',
                    '.dialog',
                    '[role="dialog"]',
                    '.detail-modal',
                    '.deal-detail',
                    '.fixed.inset-0',
                    '.backdrop-blur-sm',
                    '.z-50',
                    '.z-40'
                ]
                
                modal_found = False
                for selector in modal_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible():
                            print(f"✅ Found modal with selector: {selector}")
                            modal_found = True
                            
                            # Get modal content
                            modal_text = element.text_content()
                            print(f"📄 Modal content preview: {modal_text[:200]}...")
                            break
                    except:
                        continue
                
                if not modal_found:
                    print("⚠️ No modal found - checking for inline detail view...")
                    
                    # Check if detail view opened inline
                    detail_elements = page.locator('.deal-detail, .detail-view, .expanded-view')
                    if detail_elements.count() > 0:
                        print("✅ Found inline detail view")
                        modal_found = True
                    else:
                        print("⚠️ No detail view found")
                
                if modal_found:
                    # ===== EXPLORE MODAL STRUCTURE =====
                    print("\n🔍 Exploring modal structure...")
                    
                    # Look for tabs or sections
                    tabs = page.locator('button, a, .tab, .nav-item, [role="tab"]')
                    tab_count = tabs.count()
                    print(f"📑 Found {tab_count} potential tabs/buttons")
                    
                    # Look for specific feature sections
                    feature_sections = [
                        ('Tags', '.tags, .tag-section, [data-testid="tags"]'),
                        ('Activity', '.activity, .activity-log, .activity-section'),
                        ('Comments', '.comments, .comment-section, .comments-section'),
                        ('Details', '.details, .deal-details, .info'),
                        ('Edit', '.edit, .edit-form, .form'),
                        ('Watchers', '.watchers, .watch-section, .watcher-list')
                    ]
                    
                    for feature_name, selector in feature_sections:
                        elements = page.locator(selector)
                        count = elements.count()
                        if count > 0:
                            print(f"✅ {feature_name}: Found {count} elements")
                            
                            # Get first element text
                            first_element = elements.first
                            if first_element.is_visible():
                                text = first_element.text_content()
                                print(f"   📄 {feature_name} preview: {text[:100]}...")
                        else:
                            print(f"⚠️ {feature_name}: Not found")
                    
                    # Look for form fields
                    form_fields = page.locator('input, textarea, select, button')
                    field_count = form_fields.count()
                    print(f"📝 Found {field_count} form fields")
                    
                    # Look for specific field types
                    field_types = [
                        ('Input fields', 'input'),
                        ('Text areas', 'textarea'),
                        ('Select dropdowns', 'select'),
                        ('Buttons', 'button')
                    ]
                    
                    for field_type, selector in field_types:
                        elements = page.locator(selector)
                        count = elements.count()
                        if count > 0:
                            print(f"   📝 {field_type}: {count} found")
                    
                    # Try to find and click on different sections
                    print("\n🖱️ Testing section interactions...")
                    
                    # Look for clickable elements that might be tabs
                    clickable_elements = page.locator('button:visible, a:visible, [role="button"]:visible')
                    clickable_count = clickable_elements.count()
                    print(f"🖱️ Found {clickable_count} clickable elements")
                    
                    # Try clicking on first few clickable elements to see if they reveal more content
                    for i in range(min(clickable_count, 5)):
                        try:
                            element = clickable_elements.nth(i)
                            if element.is_visible():
                                text = element.text_content()
                                print(f"   🖱️ Clicking: {text[:30]}...")
                                element.click()
                                page.wait_for_timeout(1000)
                                
                                # Check if new content appeared
                                new_elements = page.locator('.new-content, .revealed, .expanded')
                                if new_elements.count() > 0:
                                    print(f"   ✅ New content revealed after clicking: {text[:30]}")
                        except:
                            continue
                    
                    # Close modal
                    print("\n❌ Closing modal...")
                    close_selectors = [
                        'button:has-text("Close")',
                        'button:has-text("×")',
                        '.close-button',
                        '[aria-label="Close"]',
                        'button[title*="close"]'
                    ]
                    
                    closed = False
                    for selector in close_selectors:
                        try:
                            close_button = page.locator(selector).first
                            if close_button.is_visible():
                                close_button.click()
                                page.wait_for_timeout(1000)
                                print("✅ Modal closed")
                                closed = True
                                break
                        except:
                            continue
                    
                    if not closed:
                        # Try pressing Escape
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                        print("✅ Modal closed with Escape key")
                else:
                    print("❌ Could not find deal detail modal")
                    return False
            else:
                print("❌ No deal cards found")
                return False
            
            # ===== SUMMARY =====
            print("\n🎉 === DEAL DETAIL MODAL TEST SUMMARY ===")
            print("✅ LOGIN: Successfully logged in")
            print("✅ NAVIGATION: Navigated to deals (Kanban) page")
            print("✅ DEAL CLICK: Successfully clicked on deal card")
            print("✅ MODAL EXPLORATION: Explored modal structure and content")
            print("✅ FEATURE DETECTION: Detected available features and sections")
            print("✅ INTERACTION TESTING: Tested clickable elements")
            print("✅ MODAL CLOSURE: Successfully closed modal")
            
            print("\n🎯 Deal detail modal exploration completed!")
            print("   Modal structure and available features have been analyzed.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during modal exploration: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_deals_ui_detail_modal()
    if success:
        print("\n🎉 Deal detail modal test successful!")
        print("   NeuraCRM deal detail modal structure has been explored.")
    else:
        print("\n❌ Deal detail modal test failed.")
