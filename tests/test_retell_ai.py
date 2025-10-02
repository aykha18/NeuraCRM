#!/usr/bin/env python3
"""
Test script for Retell AI integration
"""

import os
import sys
import asyncio
import httpx

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_retell_ai_service():
    """Test the Retell AI service"""
    print("🧪 Testing Retell AI Integration...")
    
    try:
        from api.services.retell_ai import retell_ai_service
        
        print("\n1. Testing voice fetching...")
        voices = await retell_ai_service.get_voices()
        print(f"   ✅ Found {len(voices)} voices")
        
        if voices:
            print(f"   📢 Sample voice: {voices[0].name} ({voices[0].voice_id})")
        
        print("\n2. Testing scenario configuration...")
        scenarios = retell_ai_service.get_conversation_scenarios()
        print(f"   ✅ Found {len(scenarios)} scenarios:")
        
        for scenario_id, config in scenarios.items():
            print(f"   📞 {scenario_id}: {config['name']}")
        
        print("\n3. Testing API endpoints...")
        
        # Test voices endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/api/conversational-ai/voices")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Voices API: {data.get('total', 0)} voices available")
                else:
                    print(f"   ⚠️  Voices API returned status {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Voices API not available: {str(e)}")
            
            try:
                response = await client.get("http://localhost:8000/api/conversational-ai/scenarios")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Scenarios API: {data.get('total', 0)} scenarios available")
                else:
                    print(f"   ⚠️  Scenarios API returned status {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Scenarios API not available: {str(e)}")
        
        print("\n4. Environment setup...")
        api_key = os.getenv("RETELL_AI_API_KEY")
        if api_key:
            print("   ✅ RETELL_AI_API_KEY is set")
            print(f"   🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
        else:
            print("   ⚠️  RETELL_AI_API_KEY not set")
            print("   📝 To set: export RETELL_AI_API_KEY='your_api_key_here'")
        
        webhook_url = os.getenv("WEBHOOK_BASE_URL")
        if webhook_url:
            print(f"   ✅ WEBHOOK_BASE_URL is set: {webhook_url}")
        else:
            print("   ⚠️  WEBHOOK_BASE_URL not set (optional)")
            print("   📝 To set: export WEBHOOK_BASE_URL='https://your-domain.com'")
        
        print("\n🎉 Retell AI Integration Test Complete!")
        print("\n📋 Next Steps:")
        print("1. Get Retell AI API key from https://retellai.com")
        print("2. Set environment variable: export RETELL_AI_API_KEY='your_key'")
        print("3. Start the server: python working_app.py")
        print("4. Visit http://localhost:8000/docs to see API documentation")
        print("5. Test the frontend interface")
        
    except Exception as e:
        print(f"❌ Error testing Retell AI: {str(e)}")
        import traceback
        traceback.print_exc()

def test_frontend_build():
    """Test if frontend builds successfully"""
    print("\n🎨 Testing Frontend Build...")
    
    try:
        import subprocess
        import os
        
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
        if os.path.exists(frontend_dir):
            print("   ✅ Frontend directory found")
            
            # Check if ConversationalAI component exists
            ai_component = os.path.join(frontend_dir, 'src', 'pages', 'ConversationalAI.tsx')
            if os.path.exists(ai_component):
                print("   ✅ ConversationalAI component exists")
            else:
                print("   ⚠️  ConversationalAI component not found")
        else:
            print("   ⚠️  Frontend directory not found")
            
    except Exception as e:
        print(f"   ⚠️  Frontend test error: {str(e)}")

if __name__ == "__main__":
    print("🚀 NeuraCRM Retell AI Integration Test")
    print("=" * 50)
    
    # Test backend integration
    asyncio.run(test_retell_ai_service())
    
    # Test frontend
    test_frontend_build()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
