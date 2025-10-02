#!/usr/bin/env python3
"""
Test script for RAG setup and basic functionality
Tests vector database connection, document ingestion, and Q&A
"""

import os
import asyncio
import tempfile
from pathlib import Path

# Set up environment variables for testing
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-openai-key-here')
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY', 'your-pinecone-key-here')

from api.services.rag_service import rag_service

async def test_rag_setup():
    """Test basic RAG functionality"""
    print("🧪 Testing RAG Setup...")

    try:
        # Test 1: Service initialization
        print("1. Testing service initialization...")
        print(f"   Index name: {rag_service.index_name}")
        print(f"   Dimension: {rag_service.dimension}")
        print("   ✅ Service initialized successfully")

        # Test 2: Create sample knowledge base content
        print("\n2. Creating sample knowledge base content...")

        sample_content = """
# NeuraCRM Support Guide

## Getting Started
Welcome to NeuraCRM! Our AI-powered CRM helps you manage leads, deals, and customer interactions efficiently.

## Lead Management
- Create leads from website forms, email campaigns, or manual entry
- AI-powered lead scoring helps prioritize your best prospects
- Convert leads to deals when they're sales-ready

## Deal Pipeline
- Use our Kanban-style deal pipeline to track progress
- Set up automated reminders and follow-ups
- Get AI insights on deal velocity and conversion rates

## Customer Support
- Create support tickets for customer issues
- Use our knowledge base for instant answers
- AI-powered ticket routing and prioritization

## Reporting & Analytics
- Real-time dashboards with key metrics
- Predictive analytics for sales forecasting
- Customer segmentation and churn prediction

## Contact Information
- Support Email: support@neuracrm.com
- Sales Inquiries: sales@neuracrm.com
- Emergency Support: +1-800-NEURA-CRM
"""

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_content)
            temp_file = f.name

        # Test document ingestion
        print("3. Testing document ingestion...")
        metadata = {
            "document_id": "sample_support_guide",
            "title": "NeuraCRM Support Guide",
            "category": "documentation",
            "type": "markdown",
            "author": "NeuraCRM Team",
            "tags": ["support", "getting-started", "features"],
            "description": "Comprehensive guide for NeuraCRM users"
        }

        result = await rag_service.ingest_document(temp_file, metadata, None)
        print(f"   ✅ Document ingested: {result}")

        # Clean up
        os.unlink(temp_file)

        # Test 4: Search functionality
        print("\n4. Testing search functionality...")
        test_queries = [
            "How do I create a lead?",
            "What is the deal pipeline?",
            "How do I contact support?",
            "What are the key features?"
        ]

        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = await rag_service.search_knowledge(query, top_k=3)
            if results:
                print(f"   Found {len(results)} relevant chunks")
                for i, result in enumerate(results[:2]):  # Show top 2
                    print(".3f")
            else:
                print("   No results found")

        # Test 5: Q&A functionality
        print("\n5. Testing Q&A functionality...")
        qa_query = "How do I get started with NeuraCRM?"
        print(f"\n   Q&A Query: '{qa_query}'")

        relevant_chunks = await rag_service.search_knowledge(qa_query, top_k=3)
        if relevant_chunks:
            answer_result = await rag_service.generate_answer(qa_query, relevant_chunks)
            print("   Answer generated successfully"            print(f"   Citations: {len(answer_result.get('citations', []))}")
        else:
            print("   No relevant chunks found for Q&A")

        print("\n🎉 RAG setup test completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Set up Pinecone API key in environment variables")
        print("2. Set up OpenAI API key in environment variables")
        print("3. Ingest your actual knowledge base documents")
        print("4. Test with real customer queries")
        print("5. Integrate with your frontend application")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API keys are set correctly")
        print("2. Ensure Pinecone index is accessible")
        print("3. Verify OpenAI API has sufficient credits")
        print("4. Check network connectivity")

if __name__ == "__main__":
    asyncio.run(test_rag_setup())