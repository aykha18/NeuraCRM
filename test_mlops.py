#!/usr/bin/env python3
"""
Test script for MLOps functionality
"""
import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/mlops"
def authenticate():
    """Authenticate and get access token"""
    global AUTH_TOKEN
    try:
        # Try to login with test credentials
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }

        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get("access_token")
            print("[OK] Authentication successful")
            return True
        else:
            # Try to register a test user first
            register_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpass123",
                "organization_id": 1
            }

            register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
            if register_response.status_code == 200:
                # Now try to login
                login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    AUTH_TOKEN = data.get("access_token")
                    print("[OK] User registered and authenticated successfully")
                    return True

            print(f"[FAIL] Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Authentication error: {e}")
        return False

def get_auth_headers():
    """Get authorization headers"""
    if AUTH_TOKEN:
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    return {}

AUTH_TOKEN = None

def test_mlops_dashboard():
    """Test MLOps dashboard endpoint"""
    print("Testing MLOps Dashboard...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/dashboard", headers=get_auth_headers())
        if response.status_code == 200:
            data = response.json()
            print("[OK] Dashboard loaded successfully")
            print(f"   Total models: {data.get('total_models', 0)}")
            print(f"   Active models: {data.get('active_models', 0)}")
            print(f"   Retraining jobs: {data.get('retraining_jobs', 0)}")
            return True
        else:
            print(f"[FAIL] Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Dashboard error: {e}")
        return False

def test_model_registration():
    """Test model registration"""
    print("\nTesting Model Registration...")
    try:
        # Mock model data
        model_data = {
            "model_name": "test_sentiment_analyzer",
            "model_object": {"type": "mock_model", "version": "1.0"},
            "accuracy_score": 0.85,
            "training_data_size": 1000,
            "metadata": {"algorithm": "keyword_based", "features": ["text_length", "sentiment_words"]}
        }

        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/models/register",
            json=model_data,
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("[OK] Model registered successfully")
            print(f"   Model ID: {data.get('model_id')}")
            print(f"   Version: {data.get('version')}")
            return data.get('model_id')
        else:
            print(f"[FAIL] Model registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Model registration error: {e}")
        return None

def test_model_deployment(model_id):
    """Test model deployment"""
    print(f"\nTesting Model Deployment for {model_id}...")
    try:
        # Deploy version 1.0 (the version we registered)
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/models/{model_id}/deploy/1.0",
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("[OK] Model deployed successfully")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"[FAIL] Model deployment failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Model deployment error: {e}")
        return False

def test_metrics_recording(model_id):
    """Test metrics recording"""
    print(f"\nTesting Metrics Recording for {model_id}...")
    try:
        metrics_data = {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
            "predictions_count": 150,
            "avg_response_time": 45.2,
            "drift_score": 0.02
        }

        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/metrics/{model_id}/record",
            json=metrics_data,
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("[OK] Metrics recorded successfully")
            print(f"   Recorded at: {data.get('recorded_at')}")
            return True
        else:
            print(f"[FAIL] Metrics recording failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Metrics recording error: {e}")
        return False

def test_retraining_trigger(model_id):
    """Test retraining trigger"""
    print(f"\nTesting Retraining Trigger for {model_id}...")
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/retraining/{model_id}/start",
            json={"trigger_reason": "manual_test"},
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("[OK] Retraining job started successfully")
            print(f"   Job ID: {data.get('job_id')}")
            return data.get('job_id')
        else:
            print(f"[FAIL] Retraining trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Retraining trigger error: {e}")
        return None

def test_retraining_status(job_id):
    """Test retraining status check"""
    print(f"\nTesting Retraining Status for job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/retraining/job/{job_id}", headers=get_auth_headers())

        if response.status_code == 200:
            data = response.json()
            print("[OK] Retraining status retrieved successfully")
            print(f"   Status: {data.get('status')}")
            print(f"   Progress: {data.get('progress')}%")
            return True
        else:
            print(f"[FAIL] Retraining status failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Retraining status error: {e}")
        return False

def main():
    """Run all MLOps tests"""
    print(">>> Starting MLOps Functionality Tests")
    print("=" * 50)

    # Authenticate first
    if not authenticate():
        print("\n[FAIL] Authentication failed. Cannot continue with tests.")
        return

    # Test dashboard
    dashboard_ok = test_mlops_dashboard()

    if not dashboard_ok:
        print("\n[FAIL] Dashboard test failed. Please ensure the server is running.")
        return

    # Test model registration
    model_id = test_model_registration()

    if not model_id:
        print("\n[FAIL] Model registration failed. Cannot continue with other tests.")
        return

    # Test model deployment
    deployment_ok = test_model_deployment(model_id)

    # Test metrics recording
    metrics_ok = test_metrics_recording(model_id)

    # Test retraining trigger
    job_id = test_retraining_trigger(model_id)

    if job_id:
        # Wait a moment for job to start
        time.sleep(1)
        # Test retraining status
        status_ok = test_retraining_status(job_id)

    print("\n" + "=" * 50)
    print("[DONE] MLOps Testing Complete")
    print("\nTest Results Summary:")
    print(f"[OK] Dashboard: {'PASS' if dashboard_ok else 'FAIL'}")
    print(f"[OK] Model Registration: {'PASS' if model_id else 'FAIL'}")
    print(f"[OK] Model Deployment: {'PASS' if deployment_ok else 'FAIL'}")
    print(f"[OK] Metrics Recording: {'PASS' if metrics_ok else 'FAIL'}")
    print(f"[OK] Retraining Trigger: {'PASS' if job_id else 'FAIL'}")

if __name__ == "__main__":
    main()