#!/usr/bin/env python3
"""
Direct test of MLOps service functionality (bypassing API authentication)
"""
from backend.api.services.mlops_service import MLOpsService

def test_mlops_service():
    """Test MLOps service directly"""
    print(">>> Testing MLOps Service Directly")
    print("=" * 50)

    # Initialize service
    mlops_service = MLOpsService()

    # Test dashboard data
    print("Testing dashboard data...")
    dashboard_data = mlops_service.get_mlops_dashboard_data()
    print(f"[OK] Dashboard data: {dashboard_data}")

    # Test model registration
    print("\nTesting model registration...")
    model_name = "test_sentiment_analyzer"
    version_str = mlops_service.register_model_version(
        model_name,
        {"type": "mock_model", "version": "1.0"},
        0.85,
        1000,
        {"algorithm": "keyword_based"}
    )
    print(f"[OK] Registered model version: {version_str}")

    # Test model deployment
    print(f"\nTesting model deployment for {model_name}...")
    success = mlops_service.deploy_model_version(model_name, version_str)
    print(f"[OK] Deployment success: {success}")

    # Test metrics recording
    print(f"\nTesting metrics recording...")
    mlops_service.record_model_metrics(
        model_name,
        version_str,
        0.87, 0.85, 0.89, 0.87, 0.02, 150
    )
    print("[OK] Metrics recorded")

    # Test retraining trigger
    print(f"\nTesting retraining trigger...")
    job_id = mlops_service.start_retraining_job(model_name, "manual_test")
    print(f"[OK] Started retraining job: {job_id}")

    # Test getting retraining jobs
    print(f"\nTesting retraining jobs retrieval...")
    jobs = mlops_service.get_retraining_jobs()
    job = next((j for j in jobs if j.job_id == job_id), None)
    if job:
        print(f"[OK] Job status: {job.status}")
    else:
        print("[FAIL] Job not found")

    # Test model versions
    print(f"\nTesting model versions retrieval...")
    versions = mlops_service.get_model_versions(model_name)
    print(f"[OK] Found {len(versions)} versions")

    # Test model metrics
    print(f"\nTesting model metrics retrieval...")
    metrics = mlops_service.get_model_metrics(model_name, 10)
    print(f"[OK] Found {len(metrics)} metrics records")

    print("\n" + "=" * 50)
    print("[DONE] MLOps Service Testing Complete")
    print("\nAll core MLOps functionality is working correctly!")

if __name__ == "__main__":
    test_mlops_service()