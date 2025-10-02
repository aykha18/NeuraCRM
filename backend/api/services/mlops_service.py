#!/usr/bin/env python3
"""
MLOps Service for AI Model Lifecycle Management
Handles model versioning, monitoring, retraining, and deployment
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import pickle
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

@dataclass
class ModelVersion:
    """Model version information"""
    model_name: str
    version: str
    created_at: datetime
    accuracy_score: float
    training_data_size: int
    model_path: str
    metadata: Dict[str, Any]
    is_active: bool = False
    deployment_date: Optional[datetime] = None

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    model_name: str
    version: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    data_drift_score: float
    prediction_count: int

@dataclass
class RetrainingJob:
    """Automated retraining job information"""
    job_id: str
    model_name: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    trigger_reason: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    old_version: Optional[str] = None
    new_version: Optional[str] = None
    metrics_before: Optional[Dict[str, float]] = None
    metrics_after: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None

class MLOpsService:
    """MLOps service for managing AI model lifecycle"""

    def __init__(self):
        self.models_dir = Path("backend/models")
        self.models_dir.mkdir(exist_ok=True)
        self.versions_file = self.models_dir / "model_versions.json"
        self.metrics_file = self.models_dir / "model_metrics.json"
        self.jobs_file = self.models_dir / "retraining_jobs.json"

        # Load existing data
        self.model_versions = self._load_model_versions()
        self.model_metrics = self._load_model_metrics()
        self.retraining_jobs = self._load_retraining_jobs()

    def _load_model_versions(self) -> Dict[str, List[ModelVersion]]:
        """Load model versions from storage"""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r') as f:
                    data = json.load(f)
                    versions = {}
                    for model_name, version_list in data.items():
                        versions[model_name] = [
                            ModelVersion(**v) for v in version_list
                        ]
                    return versions
            except Exception as e:
                logger.error(f"Error loading model versions: {e}")
        return {}

    def _save_model_versions(self):
        """Save model versions to storage"""
        try:
            data = {}
            for model_name, versions in self.model_versions.items():
                data[model_name] = [asdict(v) for v in versions]

            with open(self.versions_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving model versions: {e}")

    def _load_model_metrics(self) -> Dict[str, List[ModelMetrics]]:
        """Load model metrics from storage"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    metrics = {}
                    for model_name, metrics_list in data.items():
                        metrics[model_name] = [
                            ModelMetrics(**m) for m in metrics_list
                        ]
                    return metrics
            except Exception as e:
                logger.error(f"Error loading model metrics: {e}")
        return {}

    def _save_model_metrics(self):
        """Save model metrics to storage"""
        try:
            data = {}
            for model_name, metrics in self.model_metrics.items():
                data[model_name] = [asdict(m) for m in metrics]

            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving model metrics: {e}")

    def _load_retraining_jobs(self) -> Dict[str, RetrainingJob]:
        """Load retraining jobs from storage"""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    data = json.load(f)
                    jobs = {}
                    for job_id, job_data in data.items():
                        jobs[job_id] = RetrainingJob(**job_data)
                    return jobs
            except Exception as e:
                logger.error(f"Error loading retraining jobs: {e}")
        return {}

    def _save_retraining_jobs(self):
        """Save retraining jobs to storage"""
        try:
            data = {}
            for job_id, job in self.retraining_jobs.items():
                data[job_id] = asdict(job)

            with open(self.jobs_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving retraining jobs: {e}")

    def register_model_version(self, model_name: str, model_object: Any,
                             accuracy_score: float, training_data_size: int,
                             metadata: Dict[str, Any] = None) -> str:
        """Register a new model version"""
        try:
            # Generate version hash
            model_hash = hashlib.md5(pickle.dumps(model_object)).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version = f"{timestamp}_{model_hash}"

            # Save model file
            model_path = self.models_dir / f"{model_name}_{version}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model_object, f)

            # Create version record
            model_version = ModelVersion(
                model_name=model_name,
                version=version,
                created_at=datetime.now(),
                accuracy_score=accuracy_score,
                training_data_size=training_data_size,
                model_path=str(model_path),
                metadata=metadata or {}
            )

            # Add to versions
            if model_name not in self.model_versions:
                self.model_versions[model_name] = []
            self.model_versions[model_name].append(model_version)

            # Save to disk
            self._save_model_versions()

            logger.info(f"Registered new model version: {model_name} v{version}")
            return version

        except Exception as e:
            logger.error(f"Error registering model version: {e}")
            raise

    def deploy_model_version(self, model_name: str, version: str) -> bool:
        """Deploy a specific model version"""
        try:
            if model_name not in self.model_versions:
                raise ValueError(f"Model {model_name} not found")

            # Find the version
            version_obj = None
            for v in self.model_versions[model_name]:
                if v.version == version:
                    version_obj = v
                    break

            if not version_obj:
                raise ValueError(f"Version {version} not found for model {model_name}")

            # Deactivate current active version
            for v in self.model_versions[model_name]:
                v.is_active = False

            # Activate new version
            version_obj.is_active = True
            version_obj.deployment_date = datetime.now()

            # Save changes
            self._save_model_versions()

            logger.info(f"Deployed model {model_name} version {version}")
            return True

        except Exception as e:
            logger.error(f"Error deploying model version: {e}")
            return False

    def get_active_model_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get the currently active model version"""
        if model_name not in self.model_versions:
            return None

        for version in self.model_versions[model_name]:
            if version.is_active:
                return version
        return None

    def load_model(self, model_name: str, version: str = None) -> Optional[Any]:
        """Load a model from storage"""
        try:
            if version is None:
                # Load active version
                active_version = self.get_active_model_version(model_name)
                if not active_version:
                    return None
                version = active_version.version
                model_path = active_version.model_path
            else:
                # Find specific version
                if model_name not in self.model_versions:
                    return None
                version_obj = None
                for v in self.model_versions[model_name]:
                    if v.version == version:
                        version_obj = v
                        break
                if not version_obj:
                    return None
                model_path = version_obj.model_path

            # Load model
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            return model

        except Exception as e:
            logger.error(f"Error loading model {model_name} v{version}: {e}")
            return None

    def record_model_metrics(self, model_name: str, version: str,
                           accuracy: float, precision: float, recall: float,
                           f1_score: float, data_drift_score: float,
                           prediction_count: int):
        """Record model performance metrics"""
        try:
            metrics = ModelMetrics(
                model_name=model_name,
                version=version,
                timestamp=datetime.now(),
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                data_drift_score=data_drift_score,
                prediction_count=prediction_count
            )

            if model_name not in self.model_metrics:
                self.model_metrics[model_name] = []
            self.model_metrics[model_name].append(metrics)

            # Keep only last 1000 metrics per model
            if len(self.model_metrics[model_name]) > 1000:
                self.model_metrics[model_name] = self.model_metrics[model_name][-1000:]

            self._save_model_metrics()

            logger.info(f"Recorded metrics for {model_name} v{version}")

        except Exception as e:
            logger.error(f"Error recording model metrics: {e}")

    def check_retraining_needed(self, model_name: str, threshold: float = 0.05) -> bool:
        """Check if model needs retraining based on performance degradation"""
        try:
            if model_name not in self.model_metrics:
                return False

            metrics = self.model_metrics[model_name]
            if len(metrics) < 10:  # Need minimum data points
                return False

            # Check recent performance vs historical average
            recent_metrics = metrics[-10:]  # Last 10 measurements
            historical_metrics = metrics[:-10] if len(metrics) > 10 else metrics

            recent_avg_accuracy = sum(m.accuracy for m in recent_metrics) / len(recent_metrics)
            historical_avg_accuracy = sum(m.accuracy for m in historical_metrics) / len(historical_metrics)

            # Check for significant degradation
            if historical_avg_accuracy - recent_avg_accuracy > threshold:
                logger.warning(f"Model {model_name} performance degraded: {historical_avg_accuracy:.3f} -> {recent_avg_accuracy:.3f}")
                return True

            # Check data drift
            recent_avg_drift = sum(m.data_drift_score for m in recent_metrics) / len(recent_metrics)
            if recent_avg_drift > 0.1:  # Significant drift threshold
                logger.warning(f"Model {model_name} data drift detected: {recent_avg_drift:.3f}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking retraining need: {e}")
            return False

    def start_retraining_job(self, model_name: str, trigger_reason: str) -> str:
        """Start a retraining job"""
        try:
            job_id = f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Get current active version
            active_version = self.get_active_model_version(model_name)
            old_version = active_version.version if active_version else None

            # Get current metrics
            metrics_before = None
            if model_name in self.model_metrics and self.model_metrics[model_name]:
                latest_metrics = self.model_metrics[model_name][-1]
                metrics_before = {
                    'accuracy': latest_metrics.accuracy,
                    'precision': latest_metrics.precision,
                    'recall': latest_metrics.recall,
                    'f1_score': latest_metrics.f1_score,
                    'data_drift_score': latest_metrics.data_drift_score
                }

            job = RetrainingJob(
                job_id=job_id,
                model_name=model_name,
                status='pending',
                created_at=datetime.now(),
                trigger_reason=trigger_reason,
                old_version=old_version,
                metrics_before=metrics_before
            )

            self.retraining_jobs[job_id] = job
            self._save_retraining_jobs()

            logger.info(f"Started retraining job {job_id} for {model_name}")
            return job_id

        except Exception as e:
            logger.error(f"Error starting retraining job: {e}")
            raise

    def update_retraining_job(self, job_id: str, status: str,
                            new_version: str = None, error_message: str = None):
        """Update retraining job status"""
        try:
            if job_id not in self.retraining_jobs:
                raise ValueError(f"Job {job_id} not found")

            job = self.retraining_jobs[job_id]
            job.status = status

            if status == 'running' and not job.started_at:
                job.started_at = datetime.now()
            elif status in ['completed', 'failed']:
                job.completed_at = datetime.now()
                if new_version:
                    job.new_version = new_version
                if error_message:
                    job.error_message = error_message

                # Record metrics after if completed
                if status == 'completed' and job.model_name in self.model_metrics:
                    latest_metrics = self.model_metrics[job.model_name][-1]
                    job.metrics_after = {
                        'accuracy': latest_metrics.accuracy,
                        'precision': latest_metrics.precision,
                        'recall': latest_metrics.recall,
                        'f1_score': latest_metrics.f1_score,
                        'data_drift_score': latest_metrics.data_drift_score
                    }

            self._save_retraining_jobs()

            logger.info(f"Updated retraining job {job_id} status to {status}")

        except Exception as e:
            logger.error(f"Error updating retraining job: {e}")

    def get_model_versions(self, model_name: str) -> List[ModelVersion]:
        """Get all versions of a model"""
        return self.model_versions.get(model_name, [])

    def get_model_metrics(self, model_name: str, limit: int = 100) -> List[ModelMetrics]:
        """Get metrics for a model"""
        metrics = self.model_metrics.get(model_name, [])
        return metrics[-limit:] if limit > 0 else metrics

    def get_retraining_jobs(self, model_name: str = None, status: str = None) -> List[RetrainingJob]:
        """Get retraining jobs with optional filters"""
        jobs = list(self.retraining_jobs.values())

        if model_name:
            jobs = [j for j in jobs if j.model_name == model_name]

        if status:
            jobs = [j for j in jobs if j.status == status]

        return sorted(jobs, key=lambda x: x.created_at, reverse=True)

    def rollback_model(self, model_name: str, target_version: str) -> bool:
        """Rollback to a previous model version"""
        try:
            return self.deploy_model_version(model_name, target_version)
        except Exception as e:
            logger.error(f"Error rolling back model {model_name} to {target_version}: {e}")
            return False

    def cleanup_old_versions(self, model_name: str, keep_versions: int = 5):
        """Clean up old model versions, keeping only the most recent ones"""
        try:
            if model_name not in self.model_versions:
                return

            versions = sorted(self.model_versions[model_name],
                            key=lambda x: x.created_at, reverse=True)

            # Keep active version + specified number of recent versions
            active_version = None
            recent_versions = []

            for v in versions:
                if v.is_active:
                    active_version = v
                else:
                    recent_versions.append(v)

            # Determine which versions to keep
            keep_list = []
            if active_version:
                keep_list.append(active_version)
            keep_list.extend(recent_versions[:keep_versions])

            # Remove old versions
            versions_to_remove = [v for v in versions if v not in keep_list]

            for v in versions_to_remove:
                try:
                    # Remove model file
                    if os.path.exists(v.model_path):
                        os.remove(v.model_path)
                    # Remove from list
                    self.model_versions[model_name].remove(v)
                except Exception as e:
                    logger.error(f"Error removing old version {v.version}: {e}")

            # Save updated versions
            self._save_model_versions()

            logger.info(f"Cleaned up {len(versions_to_remove)} old versions for {model_name}")

        except Exception as e:
            logger.error(f"Error cleaning up old versions: {e}")

    def get_mlops_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive MLOps dashboard data"""
        try:
            dashboard_data = {
                'models': {},
                'recent_jobs': [],
                'system_health': {
                    'total_models': len(self.model_versions),
                    'active_models': sum(1 for versions in self.model_versions.values()
                                       for v in versions if v.is_active),
                    'total_versions': sum(len(versions) for versions in self.model_versions.values()),
                    'pending_jobs': len([j for j in self.retraining_jobs.values() if j.status == 'pending']),
                    'running_jobs': len([j for j in self.retraining_jobs.values() if j.status == 'running'])
                }
            }

            # Model details
            for model_name, versions in self.model_versions.items():
                active_version = None
                latest_metrics = None

                for v in versions:
                    if v.is_active:
                        active_version = v

                if model_name in self.model_metrics and self.model_metrics[model_name]:
                    latest_metrics = self.model_metrics[model_name][-1]

                dashboard_data['models'][model_name] = {
                    'active_version': active_version.version if active_version else None,
                    'total_versions': len(versions),
                    'latest_accuracy': latest_metrics.accuracy if latest_metrics else None,
                    'latest_data_drift': latest_metrics.data_drift_score if latest_metrics else None,
                    'last_updated': active_version.deployment_date.isoformat() if active_version and active_version.deployment_date else None,
                    'needs_retraining': self.check_retraining_needed(model_name)
                }

            # Recent jobs
            all_jobs = list(self.retraining_jobs.values())
            recent_jobs = sorted(all_jobs, key=lambda x: x.created_at, reverse=True)[:10]
            dashboard_data['recent_jobs'] = [asdict(job) for job in recent_jobs]

            return dashboard_data

        except Exception as e:
            logger.error(f"Error getting MLOps dashboard data: {e}")
            return {'error': str(e)}