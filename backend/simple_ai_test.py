#!/usr/bin/env python3
"""
Simple AI Integration Test
Basic validation of OpenAI API functionality
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def simple_test():
    """Run simple AI integration test"""
    print("🚀 Simple AI Integration Test")
    print("=" * 40)
    
    try:
        # Check API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        # Test 1: Basic chat completion
        print("1. Testing Basic Chat Completion...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'AI integration test successful!'"}
            ],
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        if content and "successful" in content.lower():
            print("   ✅ Basic Chat Completion: PASS")
        else:
            print("   ❌ Basic Chat Completion: FAIL")
            return False
        
        # Test 2: Function calling
        print("2. Testing Function Calling...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the weather like?"}
            ],
            functions=[
                {
                    "name": "get_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state"
                            }
                        },
                        "required": ["location"]
                    }
                }
            ],
            function_call="auto",
            max_tokens=100
        )
        
        if response.choices[0].message.function_call:
            print("   ✅ Function Calling: PASS")
        else:
            print("   ❌ Function Calling: FAIL")
            return False
        
        # Test 3: JSON mode
        print("3. Testing JSON Mode...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON."},
                {"role": "user", "content": "Extract the name and company from: 'John Smith from ACME Corp'"}
            ],
            response_format={"type": "json_object"},
            max_tokens=100
        )
        
        content = response.choices[0].message.content
        if content and "John Smith" in content and "ACME Corp" in content:
            print("   ✅ JSON Mode: PASS")
        else:
            print("   ❌ JSON Mode: FAIL")
            return False
        
        print("\n🎉 ALL SIMPLE TESTS PASSED!")
        print("✅ OpenAI API integration is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ SIMPLE TEST FAILED: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if OPENAI_API_KEY is set in .env file")
        print("2. Verify OpenAI API key is valid")
        print("3. Check internet connection")
        print("4. Ensure OpenAI package is installed: pip install openai")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_test())
    exit(0 if success else 1)
