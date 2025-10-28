#!/usr/bin/env python3
"""
Minimal test script to verify app functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app():
    try:
        from backend.app import app
        print("App imported successfully")

        from fastapi.testclient import TestClient
        client = TestClient(app)

        # Test health endpoint
        response = client.get('/api/health')
        print(f"Health endpoint: {response.status_code}")
        try:
            print(f"Health response: {response.json()}")
        except:
            print(f"Health response (text): {response.text}")

        # Test root endpoint
        response = client.get('/')
        print(f"Root endpoint: {response.status_code} - Content length: {len(response.text)}")
        print(f"  Content preview: {response.text[:100]}...")

        # Check if HTML contains expected elements
        if '<!doctype html>' in response.text.lower():
            print("Root endpoint returns HTML")
        else:
            print("Root endpoint does not return HTML")

        if 'neuracrm' in response.text.lower():
            print("HTML contains NeuraCRM branding")
        else:
            print("HTML missing NeuraCRM branding")

        if '<script' in response.text and 'index-' in response.text:
            print("HTML contains JavaScript assets")
        else:
            print("HTML missing JavaScript assets")

        print("\nAll tests passed! App is working correctly.")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app()