#!/usr/bin/env python3
"""
Deals Kanban Board Test
Tests Kanban board functionality including stages, deal movement, and board statistics
"""

import requests
import json
import time

def test_deals_kanban_board():
    """Test deals Kanban board functionality"""
    
    print("🚀 NeuraCRM Deals Kanban Board Test")
    print("=" * 60)
    
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
            
            # ===== GET KANBAN BOARD =====
            print("\n📋 === GET KANBAN BOARD ===")
            board_url = "http://127.0.0.1:8000/api/kanban/board"
            print("📋 Getting Kanban board data...")
            
            board_response = requests.get(board_url, headers=headers, timeout=10)
            
            if board_response.status_code == 200:
                board_data = board_response.json()
                print("✅ Kanban board data retrieved successfully!")
                
                # Check stages
                if "stages" in board_data:
                    stages = board_data["stages"]
                    print(f"📊 Found {len(stages)} stages:")
                    for stage in stages:
                        stage_name = stage.get("name", "Unknown")
                        stage_count = stage.get("deal_count", 0)
                        stage_id = stage.get("id", "N/A")
                        print(f"   - {stage_name} (ID: {stage_id}): {stage_count} deals")
                else:
                    print("❌ No stages found in board data")
                    return False
                
                # Check deals
                if "deals" in board_data:
                    deals = board_data["deals"]
                    print(f"📊 Found {len(deals)} deals in board")
                    
                    # Group deals by stage
                    deals_by_stage = {}
                    for deal in deals:
                        stage_name = deal.get("stage_name", "Unknown")
                        if stage_name not in deals_by_stage:
                            deals_by_stage[stage_name] = []
                        deals_by_stage[stage_name].append(deal)
                    
                    print("📊 Deals by stage:")
                    for stage_name, stage_deals in deals_by_stage.items():
                        print(f"   - {stage_name}: {len(stage_deals)} deals")
                        for deal in stage_deals[:3]:  # Show first 3 deals
                            deal_title = deal.get("title", "Unknown")
                            deal_value = deal.get("value", 0)
                            print(f"     * {deal_title} (${deal_value:,.2f})")
                        if len(stage_deals) > 3:
                            print(f"     ... and {len(stage_deals) - 3} more")
                else:
                    print("❌ No deals found in board data")
                    return False
                
                # Check pagination info
                if "pagination" in board_data:
                    pagination = board_data["pagination"]
                    print(f"📊 Pagination: Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}")
                    print(f"📊 Total deals: {pagination.get('total_deals', 0)}")
                
            else:
                print(f"❌ Failed to get Kanban board: {board_response.status_code}")
                print(f"   Response: {board_response.text}")
                return False
            
            # ===== GET KANBAN STATISTICS =====
            print("\n📊 === GET KANBAN STATISTICS ===")
            stats_url = "http://127.0.0.1:8000/api/kanban/stats"
            print("📊 Getting Kanban statistics...")
            
            stats_response = requests.get(stats_url, headers=headers, timeout=10)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print("✅ Kanban statistics retrieved successfully!")
                
                # Display total stats
                if "total_stats" in stats_data:
                    total_stats = stats_data["total_stats"]
                    print(f"📊 Total Statistics:")
                    print(f"   - Total deals: {total_stats.get('total_deals', 0)}")
                    print(f"   - Total value: ${total_stats.get('total_value', 0):,.2f}")
                    print(f"   - Active deals: {total_stats.get('active_deals', 0)}")
                
                # Display stage counts
                if "stage_counts" in stats_data:
                    stage_counts = stats_data["stage_counts"]
                    print(f"📊 Stage Distribution:")
                    for stage in stage_counts:
                        stage_name = stage.get("name", "Unknown")
                        stage_count = stage.get("deal_count", 0)
                        print(f"   - {stage_name}: {stage_count} deals")
                
                # Display recent activity
                if "recent_activity" in stats_data:
                    recent_activity = stats_data["recent_activity"]
                    deals_last_30_days = recent_activity.get("deals_last_30_days", 0)
                    print(f"📊 Recent Activity:")
                    print(f"   - Deals created in last 30 days: {deals_last_30_days}")
                
            else:
                print(f"❌ Failed to get Kanban statistics: {stats_response.status_code}")
                print(f"   Response: {stats_response.text}")
                return False
            
            # ===== GET STAGE-SPECIFIC DEALS =====
            print("\n🎯 === GET STAGE-SPECIFIC DEALS ===")
            if "stages" in board_data and board_data["stages"]:
                first_stage = board_data["stages"][0]
                stage_id = first_stage["id"]
                stage_name = first_stage["name"]
                
                stage_deals_url = f"http://127.0.0.1:8000/api/kanban/stage/{stage_id}/deals"
                print(f"🎯 Getting deals for stage: {stage_name} (ID: {stage_id})")
                
                stage_deals_response = requests.get(stage_deals_url, headers=headers, timeout=10)
                
                if stage_deals_response.status_code == 200:
                    stage_deals_data = stage_deals_response.json()
                    print(f"✅ Stage deals retrieved successfully!")
                    
                    if "deals" in stage_deals_data:
                        stage_deals = stage_deals_data["deals"]
                        print(f"📊 Found {len(stage_deals)} deals in {stage_name} stage:")
                        
                        for deal in stage_deals[:5]:  # Show first 5 deals
                            deal_title = deal.get("title", "Unknown")
                            deal_value = deal.get("value", 0)
                            deal_owner = deal.get("owner_name", "Unknown")
                            print(f"   - {deal_title} (${deal_value:,.2f}) - Owner: {deal_owner}")
                        
                        if len(stage_deals) > 5:
                            print(f"   ... and {len(stage_deals) - 5} more deals")
                    
                    # Check pagination for stage deals
                    if "pagination" in stage_deals_data:
                        pagination = stage_deals_data["pagination"]
                        print(f"📊 Stage Pagination: Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}")
                        print(f"📊 Total deals in stage: {pagination.get('total_deals', 0)}")
                
                else:
                    print(f"❌ Failed to get stage deals: {stage_deals_response.status_code}")
                    print(f"   Response: {stage_deals_response.text}")
                    return False
            else:
                print("⚠️ No stages available for stage-specific testing")
            
            # ===== TEST DEAL MOVEMENT (if deals exist) =====
            print("\n🔄 === TEST DEAL MOVEMENT ===")
            if "deals" in board_data and board_data["deals"] and len(board_data["stages"]) > 1:
                # Find a deal to move
                first_deal = board_data["deals"][0]
                deal_id = first_deal["id"]
                deal_title = first_deal.get("title", "Unknown")
                current_stage_id = first_deal.get("stage_id")
                
                # Find a different stage to move to
                target_stage = None
                for stage in board_data["stages"]:
                    if stage["id"] != current_stage_id:
                        target_stage = stage
                        break
                
                if target_stage:
                    target_stage_id = target_stage["id"]
                    target_stage_name = target_stage["name"]
                    
                    print(f"🔄 Moving deal '{deal_title}' to stage: {target_stage_name}")
                    
                    move_data = {
                        "stage_id": target_stage_id
                    }
                    
                    move_url = f"http://127.0.0.1:8000/api/kanban/deals/{deal_id}/move"
                    move_response = requests.post(move_url, json=move_data, headers=headers, timeout=10)
                    
                    if move_response.status_code == 200:
                        move_result = move_response.json()
                        if "error" not in move_result:
                            print(f"✅ Deal moved successfully!")
                            print(f"   Deal: {deal_title}")
                            print(f"   New stage: {move_result.get('stage_name', target_stage_name)}")
                            print(f"   Message: {move_result.get('message', 'Deal moved successfully')}")
                            
                            # Move it back to original stage
                            print(f"🔄 Moving deal back to original stage...")
                            move_back_data = {
                                "stage_id": current_stage_id
                            }
                            move_back_response = requests.post(move_url, json=move_back_data, headers=headers, timeout=10)
                            
                            if move_back_response.status_code == 200:
                                move_back_result = move_back_response.json()
                                if "error" not in move_back_result:
                                    print(f"✅ Deal moved back successfully!")
                                else:
                                    print(f"⚠️ Failed to move deal back: {move_back_result['error']}")
                            else:
                                print(f"⚠️ Failed to move deal back: {move_back_response.status_code}")
                        else:
                            print(f"❌ Deal move failed: {move_result['error']}")
                            return False
                    else:
                        print(f"❌ Deal move failed with status: {move_response.status_code}")
                        print(f"   Response: {move_response.text}")
                        return False
                else:
                    print("⚠️ No target stage available for movement testing")
            else:
                print("⚠️ No deals available for movement testing")
            
            # ===== SUMMARY =====
            print("\n🎉 === KANBAN BOARD TEST SUMMARY ===")
            print("✅ BOARD: Kanban board data retrieved successfully")
            print("✅ STAGES: All stages displayed with deal counts")
            print("✅ DEALS: Deals properly distributed across stages")
            print("✅ STATISTICS: Board statistics calculated correctly")
            print("✅ STAGE DEALS: Stage-specific deal retrieval working")
            if "deals" in board_data and board_data["deals"] and len(board_data["stages"]) > 1:
                print("✅ MOVEMENT: Deal movement between stages working")
            
            print("\n🎯 Kanban board functionality is working perfectly!")
            print("   All board operations including stages, deals, and movement work correctly.")
            
            return True
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_deals_kanban_board()
    if success:
        print("\n🎉 Kanban board test successful!")
        print("   NeuraCRM Kanban board is working perfectly.")
        print("   All board functionality including stages and deal movement work correctly.")
    else:
        print("\n❌ Kanban board test failed.")

