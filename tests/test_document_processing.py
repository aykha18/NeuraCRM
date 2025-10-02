#!/usr/bin/env python3
"""
Test script for Document Processing functionality
"""
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/documents"

def create_test_txt_file():
    """Create a test text file for upload"""
    test_content = """
    NeuraCRM Document Processing Test

    This is a sample document for testing the AI-powered document processing capabilities of NeuraCRM.

    Key Features:
    - AI-powered summarization
    - Entity extraction
    - Sentiment analysis
    - Document categorization
    - Full-text search

    The system supports multiple file formats including PDF, DOCX, and TXT files.

    Contact Information:
    - Email: support@neuracrm.com
    - Phone: +1-555-0123
    - Address: 123 AI Street, Tech City, TC 12345

    This document demonstrates the advanced capabilities of our document processing pipeline.
    """

    test_file_path = "test_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)

    return test_file_path

def test_document_upload():
    """Test document upload"""
    print("Testing Document Upload...")
    try:
        # Create test file
        test_file_path = create_test_txt_file()

        with open(test_file_path, 'rb') as f:
            files = {'file': (os.path.basename(test_file_path), f, 'text/plain')}
            response = requests.post(f"{BASE_URL}{API_PREFIX}/upload", files=files)

        # Clean up test file
        os.remove(test_file_path)

        if response.status_code == 200:
            data = response.json()
            print("✅ Document uploaded successfully")
            print(f"   Document ID: {data.get('id')}")
            print(f"   Filename: {data.get('filename')}")
            print(f"   File Type: {data.get('file_type')}")
            print(f"   File Size: {data.get('file_size')} bytes")
            return data.get('id')
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return None

def test_document_listing():
    """Test document listing"""
    print("\nTesting Document Listing...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/documents")

        if response.status_code == 200:
            data = response.json()
            print("✅ Documents listed successfully")
            print(f"   Total documents: {len(data)}")
            if data:
                print(f"   Latest document: {data[0].get('filename')}")
            return True
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return False

def test_document_analysis(doc_id):
    """Test document analysis"""
    print(f"\nTesting Document Analysis for {doc_id}...")
    try:
        response = requests.post(f"{BASE_URL}{API_PREFIX}/documents/{doc_id}/analyze")

        if response.status_code == 200:
            data = response.json()
            print("✅ Document analyzed successfully")
            print(f"   Summary: {data.get('summary', '')[:100]}...")
            print(f"   Key Points: {len(data.get('key_points', []))}")
            print(f"   Entities: {len(data.get('entities', []))}")
            print(f"   Categories: {data.get('categories', [])}")
            print(f"   Sentiment: {data.get('sentiment', {}).get('label', 'unknown')}")
            return True
        else:
            print(f"❌ Document analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document analysis error: {e}")
        return False

def test_document_search():
    """Test document search"""
    print("\nTesting Document Search...")
    try:
        search_queries = ["NeuraCRM", "AI-powered", "contact"]

        for query in search_queries:
            response = requests.get(f"{BASE_URL}{API_PREFIX}/search?q={query}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search for '{query}' successful - found {len(data)} results")
            else:
                print(f"❌ Search for '{query}' failed: {response.status_code}")
                return False

        return True
    except Exception as e:
        print(f"❌ Document search error: {e}")
        return False

def test_document_download(doc_id, filename):
    """Test document download"""
    print(f"\nTesting Document Download for {doc_id}...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/documents/{doc_id}/download")

        if response.status_code == 200:
            print("✅ Document downloaded successfully")
            print(f"   Content length: {len(response.content)} bytes")

            # Save downloaded file for verification
            download_path = f"downloaded_{filename}"
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"   Saved as: {download_path}")

            # Clean up
            os.remove(download_path)
            return True
        else:
            print(f"❌ Document download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document download error: {e}")
        return False

def test_document_stats():
    """Test document statistics"""
    print("\nTesting Document Statistics...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stats")

        if response.status_code == 200:
            data = response.json()
            print("✅ Document statistics retrieved successfully")
            print(f"   Total documents: {data.get('total_documents', 0)}")
            print(f"   Total size: {data.get('total_size_mb', 0):.2f} MB")
            print(f"   By type: {data.get('by_type', {})}")
            print(f"   Processing status: {data.get('processing_status', {})}")
            return True
        else:
            print(f"❌ Document statistics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document statistics error: {e}")
        return False

def main():
    """Run all document processing tests"""
    print("🚀 Starting Document Processing Functionality Tests")
    print("=" * 60)

    # Test document listing (should work even with no documents)
    listing_ok = test_document_listing()

    # Test document upload
    doc_id = test_document_upload()

    if not doc_id:
        print("\n❌ Document upload failed. Cannot continue with analysis tests.")
        return

    # Get document details for download test
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/documents/{doc_id}")
        if response.status_code == 200:
            doc_data = response.json()
            filename = doc_data.get('filename')
        else:
            filename = "test_document.txt"
    except:
        filename = "test_document.txt"

    # Test document analysis
    analysis_ok = test_document_analysis(doc_id)

    # Test document download
    download_ok = test_document_download(doc_id, filename)

    # Test document search
    search_ok = test_document_search()

    # Test document statistics
    stats_ok = test_document_stats()

    print("\n" + "=" * 60)
    print("🏁 Document Processing Testing Complete")
    print("\nTest Results Summary:")
    print(f"✅ Document Listing: {'PASS' if listing_ok else 'FAIL'}")
    print(f"✅ Document Upload: {'PASS' if doc_id else 'FAIL'}")
    print(f"✅ Document Analysis: {'PASS' if analysis_ok else 'FAIL'}")
    print(f"✅ Document Download: {'PASS' if download_ok else 'FAIL'}")
    print(f"✅ Document Search: {'PASS' if search_ok else 'FAIL'}")
    print(f"✅ Document Statistics: {'PASS' if stats_ok else 'FAIL'}")

if __name__ == "__main__":
    main()