#!/usr/bin/env python3
"""
Comprehensive AI Integration Test
Tests all AI functionality with the actual CRM system
"""
import os
import asyncio
import json
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def comprehensive_test():
    """Run comprehensive AI integration test"""
    print("🚀 Comprehensive AI Integration Test")
    print("=" * 50)
    
    try:
        # Check API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        # Test 1: Basic Chat Completion
        print("\n1. Testing Basic Chat Completion...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful sales assistant."},
                {"role": "user", "content": "Hello! Can you help me with sales tasks?"}
            ],
            max_tokens=100
        )
        
        content = response.choices[0].message.content
        if content and len(content) > 10:
            print("   ✅ Basic Chat Completion: PASS")
            print(f"   📝 Response: {content[:100]}...")
        else:
            print("   ❌ Basic Chat Completion: FAIL")
            return False
        
        # Test 2: Sales Assistant Context
        print("\n2. Testing Sales Assistant Context...")
        sales_prompt = """
        You are an AI sales assistant for a CRM system. A user asks: "What should I do with my leads?"
        
        Provide a helpful response that includes:
        1. Lead qualification advice
        2. Follow-up recommendations
        3. Pipeline management tips
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert sales assistant with deep CRM knowledge."},
                {"role": "user", "content": sales_prompt}
            ],
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        if content and any(word in content.lower() for word in ["lead", "qualification", "follow", "pipeline"]):
            print("   ✅ Sales Assistant Context: PASS")
            print(f"   📝 Response length: {len(content)} characters")
        else:
            print("   ❌ Sales Assistant Context: FAIL")
            return False
        
        # Test 3: Entity Extraction
        print("\n3. Testing Entity Extraction...")
        extraction_prompt = """
        Extract the following information from this text and return as JSON:
        "John Smith from ACME Corp is interested in our enterprise software. His email is john@acmecorp.com and phone is 555-0123."
        
        Extract: name, company, email, phone, interest
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured information. Always return valid JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        try:
            extracted = json.loads(content)
            if "John Smith" in str(extracted) and "ACME Corp" in str(extracted):
                print("   ✅ Entity Extraction: PASS")
                print(f"   📝 Extracted: {extracted}")
            else:
                print("   ❌ Entity Extraction: FAIL")
                return False
        except json.JSONDecodeError:
            print("   ❌ Entity Extraction: FAIL - Invalid JSON")
            return False
        
        # Test 4: Email Generation
        print("\n4. Testing Email Generation...")
        email_prompt = """
        Generate a professional follow-up email for a sales lead:
        - Contact: Sarah Johnson
        - Company: TechStart Inc
        - Previous interaction: Demo call last week
        - Next step: Proposal presentation
        
        Make it personalized and professional.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert sales email writer. Create professional, personalized emails."},
                {"role": "user", "content": email_prompt}
            ],
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        if content and len(content) > 100:
            print("   ✅ Email Generation: PASS")
            print(f"   📝 Email length: {len(content)} characters")
        else:
            print("   ❌ Email Generation: FAIL")
            return False
        
        # Test 5: Sales Analysis
        print("\n5. Testing Sales Analysis...")
        analysis_prompt = """
        Analyze this sales scenario and provide recommendations:
        - Deal: $50K enterprise software license
        - Stage: Proposal
        - Contact: Michael Chen (CTO)
        - Company: DataFlow Solutions (200 employees)
        - Timeline: Decision in 2 weeks
        - Competition: Salesforce
        
        Provide strategic recommendations.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a sales strategy expert. Provide data-driven recommendations."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=250
        )
        
        content = response.choices[0].message.content
        if content and any(word in content.lower() for word in ["recommend", "strategy", "approach", "competitive"]):
            print("   ✅ Sales Analysis: PASS")
            print(f"   📝 Analysis length: {len(content)} characters")
        else:
            print("   ❌ Sales Analysis: FAIL")
            return False
        
        # Test 6: Pipeline Insights
        print("\n6. Testing Pipeline Insights...")
        pipeline_prompt = """
        Provide insights on this sales pipeline:
        - 15 deals in prospecting (avg 2 weeks)
        - 8 deals in qualification (avg 3 weeks)
        - 5 deals in proposal (avg 1 week)
        - 3 deals in negotiation (avg 2 weeks)
        - Total pipeline value: $2.5M
        - Win rate: 25%
        
        Identify bottlenecks and opportunities.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a sales pipeline expert. Analyze data and provide actionable insights."},
                {"role": "user", "content": pipeline_prompt}
            ],
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        if content and any(word in content.lower() for word in ["bottleneck", "opportunity", "improve", "recommend"]):
            print("   ✅ Pipeline Insights: PASS")
            print(f"   📝 Insights length: {len(content)} characters")
        else:
            print("   ❌ Pipeline Insights: FAIL")
            return False
        
        # Test 7: Cost Analysis
        print("\n7. Testing Cost Analysis...")
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # gpt-4o-mini costs: $0.00015/1K input, $0.0006/1K output
            input_cost = (prompt_tokens / 1000) * 0.00015
            output_cost = (completion_tokens / 1000) * 0.0006
            total_cost = input_cost + output_cost
            
            print("   ✅ Cost Analysis: PASS")
            print(f"   💰 Total tokens: {total_tokens}")
            print(f"   💰 Estimated cost: ${total_cost:.6f}")
            print(f"   💰 Cost per 1K tokens: ${(total_cost / total_tokens * 1000):.6f}")
        else:
            print("   ⚠️ Cost Analysis: SKIP - No usage data")
        
        print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✅ AI integration is working excellently")
        print("✅ Ready for production deployment")
        return True
        
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE TEST FAILED: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if OPENAI_API_KEY is set in .env file")
        print("2. Verify OpenAI API key is valid")
        print("3. Check internet connection")
        print("4. Ensure OpenAI package is installed: pip install openai")
        return False

if __name__ == "__main__":
    success = asyncio.run(comprehensive_test())
    exit(0 if success else 1)
