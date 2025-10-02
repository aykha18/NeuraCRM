#!/usr/bin/env python3
"""
Simple test for sentiment analysis functionality
"""
import requests
import json

def test_sentiment_analysis():
    """Test sentiment analysis endpoints"""

    base_url = "http://localhost:8000"

    # Test endpoints
    endpoints = [
        "/api/sentiment-analysis/overview",
        "/api/sentiment-analysis/support-tickets",
        "/api/sentiment-analysis/chat-messages",
        "/api/sentiment-analysis/activities"
    ]

    print("Testing Sentiment Analysis Endpoints")
    print("=" * 50)

    # First, authenticate
    print("\nAuthenticating...")
    auth_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "nodeit@node.com",
        "password": "NodeIT2024!"
    })

    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        token = auth_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("Authentication successful")
    else:
        print("Authentication failed")
        print(f"Response: {auth_response.text}")
        return

    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers)

            if response.status_code == 200:
                data = response.json()
                print(f"  Status: SUCCESS (200)")
                print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Array response'}")

                # Check for specific data
                if endpoint == "/api/sentiment-analysis/overview":
                    if "overall_score" in data and "overall_label" in data:
                        print(f"  Overall sentiment: {data.get('overall_label', 'N/A')} ({data.get('overall_score', 0):.2f})")
                    else:
                        print("  WARNING: Missing expected overview data")

                elif endpoint == "/api/sentiment-analysis/support-tickets":
                    if "tickets" in data:
                        print(f"  Found {len(data['tickets'])} ticket sentiments")
                    else:
                        print("  WARNING: Missing tickets data")

                elif endpoint == "/api/sentiment-analysis/chat-messages":
                    if "messages" in data:
                        print(f"  Found {len(data['messages'])} chat message sentiments")
                    else:
                        print("  WARNING: Missing messages data")

                elif endpoint == "/api/sentiment-analysis/activities":
                    if "activities" in data:
                        print(f"  Found {len(data['activities'])} activity sentiments")
                    else:
                        print("  WARNING: Missing activities data")

            else:
                print(f"  Status: FAILED ({response.status_code})")
                print(f"  Response: {response.text[:200]}...")

        except Exception as e:
            print(f"  ERROR: {str(e)}")

    print("\n" + "=" * 50)
    print("Sentiment Analysis Test Complete")

if __name__ == "__main__":
    test_sentiment_analysis()