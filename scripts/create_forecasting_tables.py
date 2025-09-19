#!/usr/bin/env python3
"""
Script to create forecasting tables in the database
"""

import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from api.db import get_engine
    from api.models import ForecastingModel, ForecastResult, ForecastingAnalytics
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    sys.exit(1)

def create_forecasting_tables():
    """Create forecasting tables in the database"""
    try:
        engine = get_engine()
        
        # Create forecasting tables
        ForecastingModel.metadata.create_all(bind=engine)
        ForecastResult.metadata.create_all(bind=engine)
        ForecastingAnalytics.metadata.create_all(bind=engine)
        
        print("✅ Forecasting tables created/verified successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating forecasting tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating forecasting tables...")
    success = create_forecasting_tables()
    
    if success:
        print("✅ All forecasting tables created successfully!")
    else:
        print("❌ Failed to create forecasting tables")
        sys.exit(1)
