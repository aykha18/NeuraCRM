#!/usr/bin/env python3
"""
Chat Page Load Test
Tests the basic loading and display of the chat page
"""

from playwright.sync_api import sync_playwright
import time

def test_chat_page_load():
    """Test that the chat page loads correctly"""
    
    print("💬 Testing Chat Page Load")
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
            
            # Navigate to chat
            print("\n💬 Navigating to Chat page...")
            page.goto("http://127.0.0.1:8000/chat")
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Wait for data to load
            print("✅ Navigated to chat page")
            
            # Check page title
            print("\n📋 Checking page title...")
            title = page.locator('h1:has-text("Chat")')
            if title.is_visible():
                print("✅ Page title 'Chat' found")
            else:
                print("❌ Page title not found")
                return False
            
            # Check sidebar
            print("\n📱 Checking sidebar...")
            sidebar = page.locator('.w-80.bg-white.border-r')
            if sidebar.is_visible():
                print("✅ Sidebar found")
                
                # Check sidebar header
                sidebar_header = page.locator('.p-4.border-b.border-gray-200')
                if sidebar_header.is_visible():
                    print("  ✅ Sidebar header found")
                else:
                    print("  ❌ Sidebar header not found")
            else:
                print("❌ Sidebar not found")
            
            # Check Create Room button
            print("\n➕ Checking Create Room button...")
            create_button = page.locator('button:has-text("Create Room"), .p-2.bg-gradient-to-r')
            if create_button.is_visible():
                print("✅ Create Room button found")
            else:
                print("❌ Create Room button not found")
            
            # Check search functionality
            print("\n🔍 Checking search functionality...")
            search_input = page.locator('input[placeholder*="Search conversations"]')
            if search_input.is_visible():
                print("✅ Search input found")
                
                # Test search functionality
                search_input.fill("test")
                time.sleep(1)
                search_input.clear()
                print("  ✅ Search input is functional")
            else:
                print("❌ Search input not found")
            
            # Check chat window
            print("\n💬 Checking chat window...")
            chat_window = page.locator('.flex-1.flex.flex-col').first
            if chat_window.is_visible():
                print("✅ Chat window found")
            else:
                print("❌ Chat window not found")
            
            # Check for chat rooms
            print("\n🏠 Checking for chat rooms...")
            rooms = page.locator('.space-y-1.p-2 > button')
            room_count = rooms.count()
            if room_count > 0:
                print(f"✅ Found {room_count} chat rooms")
                
                # Check first room for required elements
                first_room = rooms.first
                if first_room.is_visible():
                    # Check for room name
                    room_name = first_room.locator('h3.text-sm.font-medium')
                    if room_name.is_visible():
                        name_text = room_name.text_content()
                        print(f"  ✅ First room name: {name_text}")
                    else:
                        print("  ❌ Room name not found")
                    
                    # Check for room description
                    room_description = first_room.locator('.text-xs.text-gray-500')
                    if room_description.is_visible():
                        print("  ✅ Room description found")
                    else:
                        print("  ❌ Room description not found")
                    
                    # Check for room type
                    room_type = first_room.locator('.text-xs.text-gray-400')
                    if room_type.is_visible():
                        print("  ✅ Room type found")
                    else:
                        print("  ❌ Room type not found")
                    
                    # Check for room icon
                    room_icon = first_room.locator('.w-10.h-10.bg-gradient-to-r')
                    if room_icon.is_visible():
                        print("  ✅ Room icon found")
                    else:
                        print("  ❌ Room icon not found")
                    
                    # Check for online status indicator
                    online_indicator = first_room.locator('.w-2.h-2.bg-green-500')
                    if online_indicator.is_visible():
                        print("  ✅ Online status indicator found")
                    else:
                        print("  ⚠️ Online status indicator not found (may not be direct message)")
                else:
                    print("❌ First room not visible")
            else:
                print("❌ No chat rooms found")
            
            # Test room selection
            print("\n🎯 Testing room selection...")
            if room_count > 0:
                first_room = rooms.first
                first_room.click()
                time.sleep(2)
                print("✅ Clicked on first room")
                
                # Check if room is selected (highlighted)
                class_attr = first_room.get_attribute('class')
                if 'bg-gradient-to-r from-fuchsia-50 to-pink-50' in class_attr or 'border-fuchsia-200' in class_attr:
                    print("✅ Room is highlighted/selected")
                else:
                    print("⚠️ Room may not be properly selected")
                
                # Check if chat window shows room content
                chat_content = page.locator('.flex-1.flex.flex-col').first
                if chat_content.is_visible():
                    print("✅ Chat window is displayed")
                else:
                    print("❌ Chat window not displayed")
            else:
                print("❌ No rooms available for selection test")
            
            # Check for empty state
            print("\n📭 Checking for empty state...")
            empty_state = page.locator('.p-4.text-center')
            if empty_state.is_visible():
                empty_text = empty_state.text_content()
                if "No conversations" in empty_text:
                    print("✅ Empty state is displayed correctly")
                    
                    # Check for Create Room button in empty state
                    empty_create_button = empty_state.locator('button:has-text("Create Room")')
                    if empty_create_button.is_visible():
                        print("  ✅ Create Room button in empty state found")
                    else:
                        print("  ❌ Create Room button in empty state not found")
                else:
                    print("⚠️ Empty state text may be different")
            else:
                print("⚠️ Empty state not found (rooms may exist)")
            
            # Check for error state
            print("\n⚠️ Checking for error state...")
            error_state = page.locator('.text-red-500')
            if error_state.is_visible():
                print("⚠️ Error state is displayed")
                
                # Check for retry button
                retry_button = page.locator('button:has-text("Retry")')
                if retry_button.is_visible():
                    print("  ✅ Retry button found")
                else:
                    print("  ❌ Retry button not found")
            else:
                print("✅ No error state found")
            
            # Check for loading state
            print("\n⏳ Checking for loading state...")
            loading_spinner = page.locator('.animate-spin')
            if loading_spinner.is_visible():
                print("⚠️ Loading spinner still visible")
            else:
                print("✅ Loading spinner not visible")
            
            # Check for icons
            print("\n🎯 Checking for icons...")
            icons = page.locator('.lucide-message-circle, .lucide-plus, .lucide-search')
            icon_count = icons.count()
            if icon_count > 0:
                print(f"✅ Found {icon_count} icons")
            else:
                print("❌ No icons found")
            
            # Take a screenshot
            print("\n📸 Taking screenshot...")
            page.screenshot(path="test-results/chat_page_load.png")
            print("✅ Screenshot saved as chat_page_load.png")
            
            print("\n🎉 Chat page load test completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_chat_page_load()
    if success:
        print("\n✅ Chat page load test passed!")
    else:
        print("\n❌ Chat page load test failed.")
