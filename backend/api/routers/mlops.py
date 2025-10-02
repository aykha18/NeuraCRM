#!/usr/bin/env python3
"""
MLOps API Router
Provides endpoints for model lifecycle management, monitoring, and automated retraining
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..db import get_db
from ..models import User
from ..services.mlops_service import MLOpsService
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize MLOps service
mlops_service = MLOpsService()
@router.post("/models/register")
def register_model_version(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Register a new model version"""
    try:
        model_name = request_data["model_name"]
        model_object = request_data["model_object"]
        accuracy_score = request_data["accuracy_score"]
        training_data_size = request_data["training_data_size"]
        metadata = request_data.get("metadata")

        version = mlops_service.register_model_version(
            model_name, model_object, accuracy_score, training_data_size, metadata
        )
        return {
            "message": f"Successfully registered {model_name} version {version.version}",
            "model_id": model_name,
            "version": version.version,
            "created_at": version.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error registering model version: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register model version: {str(e)}")

@router.post("/metrics/{model_name}/record")
def record_model_metrics_endpoint(
    model_name: str,
    metrics_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Record performance metrics for a model"""
    try:
        mlops_service.record_model_metrics(
            model_name,
            metrics_data.get("version", "latest"),
            metrics_data["accuracy"],
            metrics_data["precision"],
            metrics_data["recall"],
            metrics_data["f1_score"],
            metrics_data.get("data_drift_score", 0.0),
            metrics_data["predictions_count"]
        )
        return {"message": f"Recorded metrics for {model_name}"}
    except Exception as e:
        logger.error(f"Error recording model metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record metrics: {str(e)}")

@router.get("/retraining/job/{job_id}")
def get_retraining_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a specific retraining job"""
    try:
        job = mlops_service.get_retraining_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Retraining job not found")

        return {
            "job_id": job.job_id,
            "model_name": job.model_name,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "progress": getattr(job, 'progress', 0),
            "trigger_reason": job.trigger_reason,
            "error_message": job.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting retraining job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/dashboard")
def get_mlops_dashboard(current_user: User = Depends(get_current_user)):
    """Get MLOps dashboard data"""
    try:
        dashboard_data = mlops_service.get_mlops_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting MLOps dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.get("/models/{model_name}/versions")
def get_model_versions(model_name: str, current_user: User = Depends(get_current_user)):
    """Get all versions of a specific model"""
    try:
        versions = mlops_service.get_model_versions(model_name)
        return {
            "model_name": model_name,
            "versions": [
                {
                    "version": v.version,
                    "created_at": v.created_at.isoformat(),
                    "accuracy_score": v.accuracy_score,
                    "training_data_size": v.training_data_size,
                    "is_active": v.is_active,
                    "deployment_date": v.deployment_date.isoformat() if v.deployment_date else None,
                    "metadata": v.metadata
                }
                for v in versions
            ]
        }
    except Exception as e:
        logger.error(f"Error getting model versions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model versions: {str(e)}")

@router.post("/models/{model_name}/deploy/{version}")
def deploy_model_version(model_name: str, version: str, current_user: User = Depends(get_current_user)):
    """Deploy a specific model version"""
    try:
        success = mlops_service.deploy_model_version(model_name, version)
        if success:
            return {"message": f"Successfully deployed {model_name} version {version}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to deploy model version")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deploying model version: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy model version: {str(e)}")

@router.post("/models/{model_name}/rollback/{version}")
def rollback_model(model_name: str, version: str, current_user: User = Depends(get_current_user)):
    """Rollback to a previous model version"""
    try:
        success = mlops_service.rollback_model(model_name, version)
        if success:
            return {"message": f"Successfully rolled back {model_name} to version {version}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to rollback model")
    except Exception as e:
        logger.error(f"Error rolling back model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rollback model: {str(e)}")

@router.get("/models/{model_name}/metrics")
def get_model_metrics(model_name: str, limit: int = 100, current_user: User = Depends(get_current_user)):
    """Get performance metrics for a model"""
    try:
        metrics = mlops_service.get_model_metrics(model_name, limit)
        return {
            "model_name": model_name,
            "metrics": [
                {
                    "version": m.version,
                    "timestamp": m.timestamp.isoformat(),
                    "accuracy": m.accuracy,
                    "precision": m.precision,
                    "recall": m.recall,
                    "f1_score": m.f1_score,
                    "data_drift_score": m.data_drift_score,
                    "prediction_count": m.prediction_count
                }
                for m in metrics
            ]
        }
    except Exception as e:
        logger.error(f"Error getting model metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model metrics: {str(e)}")

@router.get("/models/{model_name}/health")
def check_model_health(model_name: str, current_user: User = Depends(get_current_user)):
    """Check if a model needs retraining"""
    try:
        needs_retraining = mlops_service.check_retraining_needed(model_name)
        active_version = mlops_service.get_active_model_version(model_name)

        return {
            "model_name": model_name,
            "needs_retraining": needs_retraining,
            "active_version": active_version.version if active_version else None,
            "last_checked": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking model health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check model health: {str(e)}")

@router.post("/retraining/{model_name}/start")
def start_retraining_job(model_name: str, trigger_reason: str = "manual", current_user: User = Depends(get_current_user)):
    """Start a retraining job for a model"""
    try:
        job_id = mlops_service.start_retraining_job(model_name, trigger_reason)
        return {
            "message": f"Started retraining job for {model_name}",
            "job_id": job_id
        }
    except Exception as e:
        logger.error(f"Error starting retraining job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start retraining job: {str(e)}")

@router.get("/retraining/jobs")
def get_retraining_jobs(model_name: Optional[str] = None, status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Get retraining jobs with optional filters"""
    try:
        jobs = mlops_service.get_retraining_jobs(model_name, status)
        return {
            "jobs": [
                {
                    "job_id": job.job_id,
                    "model_name": job.model_name,
                    "status": job.status,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "trigger_reason": job.trigger_reason,
                    "old_version": job.old_version,
                    "new_version": job.new_version,
                    "metrics_before": job.metrics_before,
                    "metrics_after": job.metrics_after,
                    "error_message": job.error_message
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting retraining jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get retraining jobs: {str(e)}")

@router.post("/retraining/{job_id}/update")
def update_retraining_job(
    job_id: str,
    status: str,
    new_version: Optional[str] = None,
    error_message: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update retraining job status"""
    try:
        mlops_service.update_retraining_job(job_id, status, new_version, error_message)
        return {"message": f"Updated retraining job {job_id} status to {status}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating retraining job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update retraining job: {str(e)}")

@router.post("/models/{model_name}/cleanup")
def cleanup_old_versions(model_name: str, keep_versions: int = 5, current_user: User = Depends(get_current_user)):
    """Clean up old model versions"""
    try:
        mlops_service.cleanup_old_versions(model_name, keep_versions)
        return {"message": f"Cleaned up old versions for {model_name}, keeping {keep_versions} recent versions"}
    except Exception as e:
        logger.error(f"Error cleaning up old versions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup old versions: {str(e)}")

@router.post("/automated-retraining/check")
def check_all_models_for_retraining(current_user: User = Depends(get_current_user)):
    """Check all models for retraining needs and start jobs if necessary"""
    try:
        results = []
        for model_name in mlops_service.model_versions.keys():
            needs_retraining = mlops_service.check_retraining_needed(model_name)
            if needs_retraining:
                job_id = mlops_service.start_retraining_job(model_name, "automated_check")
                results.append({
                    "model_name": model_name,
                    "needs_retraining": True,
                    "job_id": job_id
                })
            else:
                results.append({
                    "model_name": model_name,
                    "needs_retraining": False
                })

        return {
            "message": "Completed automated retraining check",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in automated retraining check: {e}")
        raise HTTPException(status_code=500, detail=f"Failed automated retraining check: {str(e)}")

@router.post("/metrics/record")
def record_model_metrics(
    model_name: str,
    version: str,
    accuracy: float,
    precision: float,
    recall: float,
    f1_score: float,
    data_drift_score: float,
    prediction_count: int,
    current_user: User = Depends(get_current_user)
):
    """Record model performance metrics"""
    try:
        mlops_service.record_model_metrics(
            model_name, version, accuracy, precision, recall,
            f1_score, data_drift_score, prediction_count
        )
        return {"message": f"Recorded metrics for {model_name} v{version}"}
    except Exception as e:
        logger.error(f"Error recording model metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record metrics: {str(e)}")

@router.get("/models")
def list_all_models(current_user: User = Depends(get_current_user)):
    """List all registered models"""
    try:
        models = []
        for model_name, versions in mlops_service.model_versions.items():
            active_version = None
            for v in versions:
                if v.is_active:
                    active_version = v
                    break

            models.append({
                "name": model_name,
                "active_version": active_version.version if active_version else None,
                "total_versions": len(versions),
                "created_at": min(v.created_at for v in versions).isoformat(),
                "last_updated": max(v.created_at for v in versions).isoformat()
            })

        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")