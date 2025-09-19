#!/usr/bin/env python3
"""
Seed Railway Forecasting Data
=============================

Creates realistic forecasting models and data for organization ID 1 in Railway.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime, timedelta
import random

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def seed_forecasting_data():
    """Create realistic forecasting data for Railway organization 1"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Check if we have the necessary data
        cursor.execute("SELECT COUNT(*) FROM deals WHERE organization_id = 1")
        deals_count = cursor.fetchone()[0]
        print(f"💼 Found {deals_count} deals for organization 1")
        
        if deals_count == 0:
            print("❌ Not enough data to create forecasting models")
            return False
        
        # Clear existing forecasting data for organization 1
        cursor.execute("DELETE FROM forecast_results WHERE organization_id = 1")
        cursor.execute("DELETE FROM forecasting_analytics WHERE organization_id = 1")
        cursor.execute("DELETE FROM forecasting_models WHERE organization_id = 1")
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
        model_ids = []
        for i, model_data in enumerate(models_data, 1):
            cursor.execute("""
                INSERT INTO forecasting_models (
                    organization_id, name, description, model_type, data_source,
                    model_algorithm, model_parameters, training_data_period,
                    forecast_horizon, accuracy_metrics, is_active, last_trained,
                    created_by, created_at, updated_at
                ) VALUES (
                    1, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, %s, 16, %s, %s
                ) RETURNING id
            """, (
                model_data["name"],
                model_data["description"],
                model_data["model_type"],
                model_data["data_source"],
                model_data["model_algorithm"],
                json.dumps({"confidence": 0.85, "seasonality": True}),
                model_data["training_data_period"],
                model_data["forecast_horizon"],
                json.dumps({"mape": 0.15, "rmse": 12500, "r_squared": 0.82}),
                datetime.now(),
                datetime.now(),
                datetime.now()
            ))
            
            model_id = cursor.fetchone()[0]
            model_ids.append(model_id)
            print(f"✓ Created model: {model_data['name']} (ID: {model_id})")
        
        # Generate forecast results for each model
        for model_id, model_data in zip(model_ids, models_data):
            print(f"\n🔄 Generating forecasts for: {model_data['name']}")
            
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
                
                cursor.execute("""
                    INSERT INTO forecast_results (
                        model_id, organization_id, forecast_type, forecast_period,
                        forecast_date, forecasted_value, confidence_interval_lower,
                        confidence_interval_upper, actual_value, accuracy_score,
                        trend_direction, seasonality_factor, anomaly_detected,
                        forecast_quality_score, insights, recommendations,
                        generated_at
                    ) VALUES (
                        %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    model_id,
                    forecast_type,
                    forecast_period,
                    forecast_date,
                    value,
                    confidence_lower,
                    confidence_upper,
                    actual_value,
                    accuracy_score,
                    "increasing" if growth_rate > 0 else "decreasing",
                    seasonal_factor,
                    random.choice([True, False]) if is_forecast else False,
                    random.uniform(0.8, 0.95),
                    json.dumps({
                        "key_findings": f"Model shows {growth_rate*100:.1f}% growth trend",
                        "seasonality": "Strong seasonal patterns detected"
                    }),
                    json.dumps([
                        "Monitor key performance indicators",
                        "Adjust strategy based on seasonal trends",
                        "Focus on high-growth periods"
                    ]),
                    datetime.now()
                ))
            
            print(f"  ✓ Generated {historical_months + forecast_months} data points")
        
        # Create forecasting analytics
        for model_id in model_ids:
            cursor.execute("""
                INSERT INTO forecasting_analytics (
                    organization_id, analytics_type, period_start, period_end,
                    total_forecasts, accurate_forecasts, accuracy_rate,
                    avg_forecast_error, best_performing_model, worst_performing_model,
                    trend_analysis, seasonality_analysis, anomaly_detection,
                    performance_insights, improvement_recommendations, generated_at
                ) VALUES (
                    1, 'monthly', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                datetime.now() - timedelta(days=30),
                datetime.now(),
                random.randint(50, 100),
                random.randint(40, 90),
                random.uniform(0.75, 0.95),
                random.uniform(0.05, 0.15),
                "ARIMA",
                "Exponential_Smoothing",
                json.dumps({"trend": "positive", "growth_rate": "8.5%"}),
                json.dumps({"seasonal_patterns": "detected", "peak_months": ["Dec", "Mar", "Jun"]}),
                json.dumps({"anomalies_detected": 3, "high_confidence": True}),
                json.dumps({"overall_performance": "excellent", "recommendations": "continue current strategy"}),
                json.dumps(["Increase data frequency", "Add external variables", "Improve model validation"]),
                datetime.now()
            ))
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Forecasting data seeding completed successfully!")
        print("\nYou can now:")
        print("1. Login with: nodeit@node.com / NodeIT2024!")
        print("2. Access the AI Features page to see Advanced Forecasting")
        print("3. View forecasting models, results, and analytics")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding forecasting data: {e}")
        return False

if __name__ == "__main__":
    import math
    seed_forecasting_data()
