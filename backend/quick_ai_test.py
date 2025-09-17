#!/usr/bin/env python3
"""
Quick AI Integration Test
Fast validation of core AI functionality
"""
import asyncio
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """Run quick AI integration test"""
    print("🚀 Quick AI Integration Test")
    print("=" * 40)
    
    try:
        # Test 1: OpenAI Provider
        print("1. Testing OpenAI Provider...")
        from ai.providers.openai_provider import OpenAIProvider
        from ai.providers.base import AIModel, AIMessage
        
        provider = OpenAIProvider(model=AIModel.GPT_4O_MINI)
        
        messages = [
            AIMessage(role="system", content="You are a helpful assistant."),
            AIMessage(role="user", content="Say 'AI integration test successful!'")
        ]
        
        response = await provider.chat_completion(messages=messages)
        
        if response.content and "successful" in response.content.lower():
            print("   ✅ OpenAI Provider: PASS")
        else:
            print("   ❌ OpenAI Provider: FAIL")
            return False
        
        # Test 2: Entity Extraction
        print("2. Testing Entity Extraction...")
        test_text = "John Smith from ACME Corp is interested in our enterprise software."
        schema = {
            "contact_name": "string",
            "company": "string",
            "interest": "string"
        }
        
        extracted = await provider.extract_entities(test_text, schema)
        
        if extracted.get("contact_name") == "John Smith" and extracted.get("company") == "ACME Corp":
            print("   ✅ Entity Extraction: PASS")
        else:
            print("   ❌ Entity Extraction: FAIL")
            return False
        
        # Test 3: Email Generation
        print("3. Testing Email Generation...")
        template = "Hi {{contact.name}}, thank you for your interest in {{product}}."
        context = {
            "contact": {"name": "John Smith"},
            "product": "Enterprise Software"
        }
        
        email = await provider.generate_email(template, context)
        
        if "John Smith" in email and "Enterprise Software" in email:
            print("   ✅ Email Generation: PASS")
        else:
            print("   ❌ Email Generation: FAIL")
            return False
        
        # Test 4: Sentiment Analysis
        print("4. Testing Sentiment Analysis...")
        sentiment = await provider.analyze_sentiment("I'm very interested in your product!")
        
        if sentiment.get("sentiment") == "positive":
            print("   ✅ Sentiment Analysis: PASS")
        else:
            print("   ❌ Sentiment Analysis: FAIL")
            return False
        
        print("\n🎉 ALL QUICK TESTS PASSED!")
        print("✅ AI integration is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ QUICK TEST FAILED: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if OPENAI_API_KEY is set in .env file")
        print("2. Verify OpenAI API key is valid")
        print("3. Check internet connection")
        print("4. Ensure all dependencies are installed")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
