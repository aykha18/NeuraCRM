#!/usr/bin/env python3
"""
Seed Local Forecasting Data
===========================

Creates realistic forecasting models and data for the local database.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from api.db import get_session_local
from api.models import (
    User, Organization, ForecastingModel, ForecastResult, ForecastingAnalytics
)
from datetime import datetime, timedelta
import random
import json
import math

def seed_local_forecasting():
    """Create realistic forecasting data for the local organization"""
    
    # Get database session
    db_session = get_session_local()()
    
    try:
        print("🚀 Seeding Local Forecasting Data...")
        print("=" * 50)
        
        # Find the organization (should be ID 18 for local)
        org = db_session.query(Organization).filter(Organization.id == 18).first()
        if not org:
            print("❌ Organization 18 not found. Please run essential demo data first.")
            return False
        
        print(f"✓ Found organization: {org.name}")
        
        # Check if we have the necessary data
        deals_count = db_session.query(Deal).filter(Deal.organization_id == 18).count()
        print(f"💼 Found {deals_count} deals")
        
        if deals_count == 0:
            print("❌ Not enough data to create forecasting models")
            return False
        
        # Clear existing forecasting data for organization 18
        db_session.query(ForecastResult).filter(
            ForecastResult.organization_id == 18
        ).delete(synchronize_session=False)
        
        db_session.query(ForecastingAnalytics).filter(
            ForecastingAnalytics.organization_id == 18
        ).delete(synchronize_session=False)
        
        db_session.query(ForecastingModel).filter(
            ForecastingModel.organization_id == 18
        ).delete(synchronize_session=False)
        
        print("🧹 Cleared existing forecasting data")
        
        # Create forecasting models
        models_data = [
            {
                "name": "Revenue Forecasting Model",
                "description": "Predicts monthly revenue based on historical deal data",
                "model_type": "revenue",
                "data_source": "deals",
                "model_algorithm": "ARIMA",
                "training_data_period": "12_months",
                "forecast_horizon": "6_months"
            },
            {
                "name": "Pipeline Growth Model",
                "description": "Forecasts pipeline growth and conversion rates",
                "model_type": "pipeline",
                "data_source": "deals",
                "model_algorithm": "Prophet",
                "training_data_period": "6_months",
                "forecast_horizon": "3_months"
            },
            {
                "name": "Customer Acquisition Model",
                "description": "Predicts new customer acquisition rates",
                "model_type": "customer_growth",
                "data_source": "contacts",
                "model_algorithm": "Linear_Regression",
                "training_data_period": "12_months",
                "forecast_horizon": "12_months"
            },
            {
                "name": "Churn Prediction Model",
                "description": "Identifies customers at risk of churning",
                "model_type": "churn",
                "data_source": "deals",
                "model_algorithm": "Exponential_Smoothing",
                "training_data_period": "6_months",
                "forecast_horizon": "3_months"
            },
            {
                "name": "Seasonal Sales Model",
                "description": "Accounts for seasonal variations in sales performance",
                "model_type": "revenue",
                "data_source": "deals",
                "model_algorithm": "Prophet",
                "training_data_period": "24_months",
                "forecast_horizon": "12_months"
            }
        ]
        
        # Insert forecasting models
        model_objects = []
        for model_data in models_data:
            model = ForecastingModel(
                organization_id=18,
                name=model_data["name"],
                description=model_data["description"],
                model_type=model_data["model_type"],
                data_source=model_data["data_source"],
                model_algorithm=model_data["model_algorithm"],
                model_parameters={"confidence": 0.85, "seasonality": True},
                training_data_period=model_data["training_data_period"],
                forecast_horizon=model_data["forecast_horizon"],
                accuracy_metrics={"mape": 0.15, "rmse": 12500, "r_squared": 0.82},
                is_active=True,
                last_trained=datetime.now(),
                created_by=23,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_session.add(model)
            model_objects.append(model)
        
        db_session.commit()
        print(f"✓ Created {len(models_data)} forecasting models")
        
        # Generate forecast results for each model
        for model in model_objects:
            print(f"\n🔄 Generating forecasts for: {model.name}")
            
            # Find the model data
            model_data = None
            for data in models_data:
                if data["name"] == model.name:
                    model_data = data
                    break
            
            if not model_data:
                continue
            
            # Generate historical data points
            historical_months = 12 if "12_months" in model_data["training_data_period"] else 6
            forecast_months = 6 if "6_months" in model_data["forecast_horizon"] else 3
            
            # Base values for different model types
            if model_data["model_type"] == "revenue":
                base_value = random.randint(80000, 150000)
                growth_rate = 0.08
            elif model_data["model_type"] == "pipeline":
                base_value = random.randint(50, 120)
                growth_rate = 0.12
            elif model_data["model_type"] == "customer_growth":
                base_value = random.randint(20, 50)
                growth_rate = 0.15
            elif model_data["model_type"] == "churn":
                base_value = random.randint(5, 15)
                growth_rate = -0.05
            else:
                base_value = random.randint(100000, 200000)
                growth_rate = 0.10
            
            # Generate historical and forecast data
            for month_offset in range(historical_months + forecast_months):
                forecast_date = datetime.now() - timedelta(days=30 * (historical_months - month_offset))
                
                # Apply growth and seasonality
                seasonal_factor = 1 + 0.3 * math.sin(2 * math.pi * forecast_date.month / 12)
                trend_factor = (1 + growth_rate) ** (month_offset - historical_months)
                value = base_value * seasonal_factor * trend_factor * (1 + random.uniform(-0.1, 0.1))
                
                # Determine if this is historical or forecast
                is_forecast = month_offset >= historical_months
                actual_value = value if not is_forecast else None
                
                # Calculate confidence interval
                confidence_lower = value * (1 - random.uniform(0.1, 0.2))
                confidence_upper = value * (1 + random.uniform(0.1, 0.2))
                
                # Determine forecast type and period
                if month_offset < historical_months:
                    forecast_type = "historical"
                    forecast_period = "monthly"
                else:
                    forecast_type = "prediction"
                    forecast_period = "monthly"
                
                # Calculate accuracy score for historical data
                accuracy_score = random.uniform(0.75, 0.95) if not is_forecast else None
                
                result = ForecastResult(
                    model_id=model.id,
                    organization_id=18,
                    forecast_type=forecast_type,
                    forecast_period=forecast_period,
                    forecast_date=forecast_date,
                    forecasted_value=value,
                    confidence_interval_lower=confidence_lower,
                    confidence_interval_upper=confidence_upper,
                    actual_value=actual_value,
                    accuracy_score=accuracy_score,
                    trend_direction="increasing" if growth_rate > 0 else "decreasing",
                    seasonality_factor=seasonal_factor,
                    anomaly_detected=random.choice([True, False]) if is_forecast else False,
                    forecast_quality_score=random.uniform(0.8, 0.95),
                    insights={
                        "key_findings": f"Model shows {growth_rate*100:.1f}% growth trend",
                        "seasonality": "Strong seasonal patterns detected"
                    },
                    recommendations=[
                        "Monitor key performance indicators",
                        "Adjust strategy based on seasonal trends",
                        "Focus on high-growth periods"
                    ],
                    generated_at=datetime.now()
                )
                db_session.add(result)
            
            print(f"  ✓ Generated {historical_months + forecast_months} data points")
        
        # Create forecasting analytics
        for model in model_objects:
            analytics = ForecastingAnalytics(
                organization_id=18,
                analytics_type="monthly",
                period_start=datetime.now() - timedelta(days=30),
                period_end=datetime.now(),
                total_forecasts=random.randint(50, 100),
                accurate_forecasts=random.randint(40, 90),
                accuracy_rate=random.uniform(0.75, 0.95),
                avg_forecast_error=random.uniform(0.05, 0.15),
                best_performing_model="ARIMA",
                worst_performing_model="Exponential_Smoothing",
                trend_analysis={"trend": "positive", "growth_rate": "8.5%"},
                seasonality_analysis={"seasonal_patterns": "detected", "peak_months": ["Dec", "Mar", "Jun"]},
                anomaly_detection={"anomalies_detected": 3, "high_confidence": True},
                performance_insights={"overall_performance": "excellent", "recommendations": "continue current strategy"},
                improvement_recommendations=["Increase data frequency", "Add external variables", "Improve model validation"],
                generated_at=datetime.now()
            )
            db_session.add(analytics)
        
        db_session.commit()
        
        print("=" * 50)
        print("✅ Local forecasting data seeding completed!")
        print("\nYou can now:")
        print("1. Refresh the Advanced Forecasting page")
        print("2. View forecasting models, results, and analytics")
        print("3. See realistic forecasting data with trends and seasonality")
        
        return True
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error seeding forecasting data: {e}")
        return False
    finally:
        db_session.close()

if __name__ == "__main__":
    from api.models import Deal
    seed_local_forecasting()
