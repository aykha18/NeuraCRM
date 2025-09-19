#!/usr/bin/env python3
"""
Script to seed forecasting data for user ID 23 and organization ID 18
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from api.db import get_db, get_engine, get_session_local
    from api.models import User, Organization, ForecastingModel, ForecastResult, ForecastingAnalytics
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    sys.exit(1)

def seed_forecasting_data():
    """Seed forecasting data for the organization"""
    try:
        print("Getting session local...")
        SessionLocal = get_session_local()
        if not SessionLocal:
            print("❌ SessionLocal is None")
            return False
            
        print("Creating database session...")
        db_session = SessionLocal()
        
        # Verify user and organization exist
        user = db_session.query(User).filter(User.id == 23).first()
        if not user:
            print("❌ User ID 23 not found")
            return False
            
        org = db_session.query(Organization).filter(Organization.id == 18).first()
        if not org:
            print("❌ Organization ID 18 not found")
            return False
            
        print(f"✅ Found user: {user.name} ({user.email})")
        print(f"✅ Found organization: {org.name}")
        
        # Create forecasting models
        forecasting_models = [
            {
                "name": "Revenue Forecasting Model",
                "description": "Predicts monthly revenue based on historical deal data",
                "model_type": "revenue",
                "data_source": "deals",
                "model_algorithm": "Prophet",
                "training_data_period": "12_months",
                "forecast_horizon": "6_months"
            },
            {
                "name": "Customer Growth Model",
                "description": "Forecasts customer acquisition rates",
                "model_type": "customer_growth",
                "data_source": "contacts",
                "model_algorithm": "ARIMA",
                "training_data_period": "12_months",
                "forecast_horizon": "3_months"
            },
            {
                "name": "Pipeline Forecasting Model",
                "description": "Predicts pipeline value and conversion rates",
                "model_type": "pipeline",
                "data_source": "deals",
                "model_algorithm": "Linear_Regression",
                "training_data_period": "6_months",
                "forecast_horizon": "3_months"
            },
            {
                "name": "Churn Prediction Model",
                "description": "Forecasts customer churn rates",
                "model_type": "churn",
                "data_source": "contacts",
                "model_algorithm": "Exponential_Smoothing",
                "training_data_period": "24_months",
                "forecast_horizon": "12_months"
            },
            {
                "name": "Quarterly Sales Forecast",
                "description": "Quarterly revenue forecasting with seasonal adjustments",
                "model_type": "revenue",
                "data_source": "deals",
                "model_algorithm": "Prophet",
                "training_data_period": "24_months",
                "forecast_horizon": "12_months"
            }
        ]
        
        created_models = []
        
        for model_data in forecasting_models:
            # Check if model already exists
            existing_model = db_session.query(ForecastingModel).filter(
                ForecastingModel.name == model_data["name"],
                ForecastingModel.organization_id == 18
            ).first()
            
            if existing_model:
                print(f"⚠️  Model '{model_data['name']}' already exists, skipping...")
                created_models.append(existing_model)
                continue
            
            # Create new model
            model = ForecastingModel(
                name=model_data["name"],
                description=model_data["description"],
                model_type=model_data["model_type"],
                data_source=model_data["data_source"],
                model_algorithm=model_data["model_algorithm"],
                training_data_period=model_data["training_data_period"],
                forecast_horizon=model_data["forecast_horizon"],
                organization_id=18,
                created_by=23,
                model_parameters={
                    "alpha": 0.3,
                    "beta": 0.1,
                    "gamma": 0.05,
                    "seasonality": True,
                    "holidays": True
                },
                accuracy_metrics={
                    "overall_accuracy": round(random.uniform(0.75, 0.95), 3),
                    "mae": round(random.uniform(1000, 5000), 2),
                    "rmse": round(random.uniform(1500, 6000), 2),
                    "mape": round(random.uniform(5, 15), 2)
                },
                is_active=True,
                last_trained=datetime.utcnow() - timedelta(days=random.randint(1, 7))
            )
            
            db_session.add(model)
            db_session.flush()  # Get the ID
            created_models.append(model)
            print(f"✅ Created model: {model_data['name']}")
        
        db_session.commit()
        print(f"✅ Created {len(created_models)} forecasting models")
        
        # Generate forecast results for each model
        for model in created_models:
            generate_forecast_results(model, db_session)
        
        # Create forecasting analytics
        create_forecasting_analytics(db_session)
        
        db_session.commit()
        print("✅ Forecasting data seeded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding forecasting data: {e}")
        db_session.rollback()
        return False
    finally:
        if 'db_session' in locals():
            db_session.close()

def generate_forecast_results(model, db_session):
    """Generate forecast results for a model"""
    try:
        # Get forecast horizon in months
        horizon_map = {
            "1_month": 1,
            "3_months": 3,
            "6_months": 6,
            "12_months": 12
        }
        horizon_months = horizon_map.get(model.forecast_horizon, 3)
        
        # Generate forecasts for the past 6 months (historical)
        base_date = datetime.utcnow() - timedelta(days=180)
        
        for i in range(horizon_months):
            forecast_date = base_date + timedelta(days=30 * i)
            
            # Generate realistic forecast values based on model type
            if model.model_type == "revenue":
                base_value = random.uniform(50000, 200000)
                trend_factor = 1 + (i * 0.05)  # 5% growth per month
            elif model.model_type == "customer_growth":
                base_value = random.uniform(20, 100)
                trend_factor = 1 + (i * 0.03)  # 3% growth per month
            elif model.model_type == "pipeline":
                base_value = random.uniform(100000, 500000)
                trend_factor = 1 + (i * 0.04)  # 4% growth per month
            else:  # churn
                base_value = random.uniform(0.05, 0.25)  # 5-25% churn rate
                trend_factor = 1 - (i * 0.01)  # Slight decrease in churn
            
            forecasted_value = base_value * trend_factor
            
            # Add some actual values for historical forecasts
            actual_value = None
            if forecast_date < datetime.utcnow():
                # Simulate actual values with some variance
                variance = random.uniform(0.85, 1.15)
                actual_value = forecasted_value * variance
            
            # Calculate accuracy score if we have actual value
            accuracy_score = None
            if actual_value:
                error_rate = abs(actual_value - forecasted_value) / actual_value
                accuracy_score = max(0, 1 - error_rate)
            
            # Generate confidence intervals
            confidence_range = forecasted_value * 0.15  # 15% confidence range
            
            # Determine trend direction
            if i == 0:
                trend_direction = "stable"
            else:
                if forecasted_value > base_value * (1 + (i-1) * 0.05):
                    trend_direction = "increasing"
                elif forecasted_value < base_value * (1 + (i-1) * 0.05):
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
            
            # Generate insights and recommendations
            insights = {
                "trend": f"Model shows {trend_direction} trend",
                "confidence": "High confidence based on historical data",
                "seasonality": "Seasonal patterns detected" if i % 12 in [0, 6] else "No strong seasonality",
                "volatility": "Low volatility" if random.random() > 0.3 else "Moderate volatility"
            }
            
            recommendations = [
                "Monitor actual results vs forecasts",
                "Retrain model monthly for better accuracy",
                "Consider external factors in planning"
            ]
            
            if model.model_type == "revenue":
                recommendations.append("Focus on high-value deal conversion")
            elif model.model_type == "customer_growth":
                recommendations.append("Optimize lead generation channels")
            elif model.model_type == "pipeline":
                recommendations.append("Improve sales process efficiency")
            else:  # churn
                recommendations.append("Implement customer retention strategies")
            
            # Create forecast result
            forecast = ForecastResult(
                model_id=model.id,
                organization_id=18,
                forecast_type=model.model_type,
                forecast_period=f"Month {i+1}",
                forecast_date=forecast_date,
                forecasted_value=round(forecasted_value, 2),
                confidence_interval_lower=round(max(0, forecasted_value - confidence_range), 2),
                confidence_interval_upper=round(forecasted_value + confidence_range, 2),
                actual_value=round(actual_value, 2) if actual_value else None,
                accuracy_score=round(accuracy_score, 3) if accuracy_score else None,
                trend_direction=trend_direction,
                seasonality_factor=round(1 + 0.1 * (i % 12) / 12, 3),
                anomaly_detected=random.random() < 0.1,  # 10% chance of anomaly
                forecast_quality_score=round(random.uniform(0.7, 0.95), 3),
                insights=insights,
                recommendations=recommendations,
                generated_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            db_session.add(forecast)
        
        print(f"✅ Generated {horizon_months} forecasts for model: {model.name}")
        
    except Exception as e:
        print(f"❌ Error generating forecasts for model {model.name}: {e}")

def create_forecasting_analytics(db_session):
    """Create forecasting analytics"""
    try:
        # Check if analytics already exist
        existing_analytics = db_session.query(ForecastingAnalytics).filter(
            ForecastingAnalytics.organization_id == 18
        ).first()
        
        if existing_analytics:
            print("⚠️  Forecasting analytics already exist, skipping...")
            return
        
        # Create analytics for the past 6 months
        for i in range(6):
            period_start = datetime.utcnow() - timedelta(days=30 * (i + 1))
            period_end = datetime.utcnow() - timedelta(days=30 * i)
            
            analytics = ForecastingAnalytics(
                organization_id=18,
                analytics_type="model_performance",
                period_start=period_start,
                period_end=period_end,
                total_forecasts=random.randint(20, 50),
                accurate_forecasts=random.randint(15, 45),
                accuracy_rate=round(random.uniform(0.75, 0.95), 3),
                avg_forecast_error=round(random.uniform(1000, 5000), 2),
                best_performing_model="Revenue Forecasting Model",
                worst_performing_model="Churn Prediction Model",
                trend_analysis={
                    "overall_trend": "increasing",
                    "growth_rate": round(random.uniform(0.05, 0.15), 3),
                    "volatility": "low",
                    "seasonality_detected": True
                },
                seasonality_analysis={
                    "monthly_pattern": [1.1, 0.9, 1.2, 1.0, 1.1, 0.8, 0.7, 0.9, 1.3, 1.0, 0.9, 1.2],
                    "quarterly_pattern": [1.05, 0.95, 1.15, 0.85],
                    "peak_months": ["March", "September"],
                    "low_months": ["July", "December"]
                },
                anomaly_detection={
                    "anomalies_detected": random.randint(0, 3),
                    "anomaly_types": ["spike", "drop", "pattern_change"],
                    "confidence_threshold": 0.95
                },
                performance_insights={
                    "key_findings": [
                        "Revenue forecasts show strong upward trend",
                        "Customer growth is accelerating",
                        "Pipeline forecasting accuracy improved",
                        "Churn prediction needs retraining"
                    ],
                    "recommendations": [
                        "Focus on high-value customer acquisition",
                        "Improve sales process efficiency",
                        "Implement customer retention programs",
                        "Retrain churn prediction model"
                    ]
                },
                improvement_recommendations={
                    "model_updates": [
                        "Increase Prophet model training data",
                        "Add external economic indicators",
                        "Implement ensemble methods",
                        "Improve feature engineering"
                    ],
                    "process_improvements": [
                        "Automate forecast generation",
                        "Implement real-time monitoring",
                        "Add forecast confidence scoring",
                        "Create forecast validation workflows"
                    ]
                },
                generated_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            db_session.add(analytics)
        
        print("✅ Created forecasting analytics")
        
    except Exception as e:
        print(f"❌ Error creating forecasting analytics: {e}")

if __name__ == "__main__":
    print("🚀 Seeding forecasting data...")
    success = seed_forecasting_data()
    
    if success:
        print("✅ Forecasting data seeded successfully!")
    else:
        print("❌ Failed to seed forecasting data")
        sys.exit(1)
