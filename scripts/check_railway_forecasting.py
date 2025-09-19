#!/usr/bin/env python3
"""
Check Railway Forecasting Data
=============================

This script checks if forecasting data exists in the Railway database.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def check_forecasting_data():
    """Check forecasting data in Railway database"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Check forecasting_models table
        cursor.execute("SELECT COUNT(*) FROM forecasting_models WHERE organization_id = 1")
        models_count = cursor.fetchone()[0]
        print(f"📊 Forecasting models count for org 1: {models_count}")
        
        if models_count > 0:
            cursor.execute("""
                SELECT id, name, model_type, model_algorithm, is_active, last_trained, created_at 
                FROM forecasting_models 
                WHERE organization_id = 1 
                ORDER BY created_at DESC
            """)
            models = cursor.fetchall()
            
            print("\n📋 Forecasting Models:")
            for model in models:
                print(f"  - ID: {model[0]}, Name: {model[1]}, Type: {model[2]}")
                print(f"    Algorithm: {model[3]}, Active: {model[4]}, Trained: {model[5]}")
        else:
            print("❌ No forecasting models found for organization 1")
        
        # Check forecast_results table
        cursor.execute("SELECT COUNT(*) FROM forecast_results WHERE organization_id = 1")
        results_count = cursor.fetchone()[0]
        print(f"\n📈 Forecast results count for org 1: {results_count}")
        
        if results_count > 0:
            # Check what columns exist in forecast_results table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'forecast_results'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"📋 Available columns in forecast_results: {columns}")
            
            # Use available columns for the query
            cursor.execute("""
                SELECT id, model_id, forecast_type, forecast_period, forecasted_value, accuracy_score, generated_at 
                FROM forecast_results 
                WHERE organization_id = 1 
                ORDER BY generated_at DESC 
                LIMIT 5
            """)
            results = cursor.fetchall()
            
            print("\n📊 Recent Forecast Results:")
            for result in results:
                print(f"  - ID: {result[0]}, Model: {result[1]}, Type: {result[2]}")
                print(f"    Period: {result[3]}, Value: ${result[4]:,.2f}, Accuracy: {result[5]}")
        
        # Check forecasting_analytics table
        cursor.execute("SELECT COUNT(*) FROM forecasting_analytics WHERE organization_id = 1")
        analytics_count = cursor.fetchone()[0]
        print(f"\n📊 Forecasting analytics count for org 1: {analytics_count}")
        
        # Check if we have deals data to create forecasts from
        cursor.execute("SELECT COUNT(*) FROM deals WHERE organization_id = 1")
        deals_count = cursor.fetchone()[0]
        print(f"\n💼 Deals count for org 1: {deals_count}")
        
        cursor.close()
        conn.close()
        
        if models_count == 0:
            print("\n💡 Recommendation: Run the forecasting seeding script:")
            print("   python scripts/seed_forecasting_data.py")
        
        return models_count > 0
        
    except Exception as e:
        print(f"❌ Error checking forecasting data: {e}")
        return False

if __name__ == "__main__":
    check_forecasting_data()