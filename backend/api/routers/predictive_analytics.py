"""
Predictive Analytics Router
Provides AI-powered insights and forecasting endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from backend.api.db import get_db
from backend.api.dependencies import get_current_user
from backend.api.models import User
from backend.api.predictive_analytics import predictive_analytics_service

router = APIRouter(prefix="/api/predictive-analytics", tags=["Predictive Analytics"])

@router.get("/sales-forecast")
def get_sales_forecast(
    months: int = Query(12, description="Number of months to forecast"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get sales forecast for the next N months
    """
    try:
        forecast_data = predictive_analytics_service.get_sales_forecast(
            db=db, 
            organization_id=current_user.organization_id, 
            months=months
        )
        return {
            "success": True,
            "data": forecast_data,
            "generated_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales forecast: {str(e)}")

@router.get("/churn-prediction")
def get_churn_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict which customers are at risk of churning
    """
    try:
        churn_data = predictive_analytics_service.get_customer_churn_prediction(
            db=db,
            organization_id=current_user.organization_id
        )
        return {
            "success": True,
            "data": churn_data,
            "generated_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate churn prediction: {str(e)}")

@router.get("/revenue-optimization")
def get_revenue_optimization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get insights for revenue optimization
    """
    try:
        optimization_data = predictive_analytics_service.get_revenue_optimization_insights(
            db=db,
            organization_id=current_user.organization_id
        )
        return {
            "success": True,
            "data": optimization_data,
            "generated_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate revenue optimization insights: {str(e)}")

@router.get("/market-opportunities")
def get_market_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze market opportunities and trends
    """
    try:
        market_data = predictive_analytics_service.get_market_opportunity_analysis(
            db=db,
            organization_id=current_user.organization_id
        )
        return {
            "success": True,
            "data": market_data,
            "generated_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze market opportunities: {str(e)}")

@router.get("/dashboard-insights")
def get_dashboard_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive predictive analytics insights for dashboard
    """
    try:
        # Get all analytics data
        sales_forecast = predictive_analytics_service.get_sales_forecast(
            db=db, 
            organization_id=current_user.organization_id, 
            months=6
        )
        
        churn_prediction = predictive_analytics_service.get_customer_churn_prediction(
            db=db,
            organization_id=current_user.organization_id
        )
        
        revenue_optimization = predictive_analytics_service.get_revenue_optimization_insights(
            db=db,
            organization_id=current_user.organization_id
        )
        
        market_opportunities = predictive_analytics_service.get_market_opportunity_analysis(
            db=db,
            organization_id=current_user.organization_id
        )
        
        # Calculate key metrics
        key_metrics = {
            "forecasted_revenue_6m": sum(point.get('predicted_revenue', 0) for point in sales_forecast.get('forecast', [])),
            "at_risk_customers": churn_prediction.get('at_risk_contacts', 0),
            "high_risk_customers": churn_prediction.get('high_risk', 0),
            "avg_deal_size": revenue_optimization.get('average_deal_size', 0),
            "total_opportunities": len(market_opportunities.get('market_opportunities', []))
        }
        
        return {
            "success": True,
            "data": {
                "key_metrics": key_metrics,
                "sales_forecast": sales_forecast,
                "churn_prediction": churn_prediction,
                "revenue_optimization": revenue_optimization,
                "market_opportunities": market_opportunities
            },
            "generated_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard insights: {str(e)}")

@router.get("/health-check")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for predictive analytics service
    """
    return {
        "status": "healthy",
        "service": "predictive-analytics",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
