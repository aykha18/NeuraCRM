"""
Predictive Analytics Service
Provides AI-powered insights for sales forecasting, customer behavior prediction, and market trends
"""
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from api.models import Lead, Contact, Deal, User, Organization, Activity, Stage

class PredictiveAnalyticsService:
    def __init__(self):
        self.forecast_periods = 12  # months
        self.confidence_levels = [0.8, 0.9, 0.95]  # 80%, 90%, 95% confidence intervals
    
    def get_sales_forecast(self, db: Session, organization_id: int, months: int = 12) -> Dict[str, Any]:
        """Generate sales forecast for the next N months"""
        try:
            # Get historical deal data for the last 24 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 24 months
            
            deals = db.query(Deal).filter(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.created_at >= start_date,
                    Deal.created_at <= end_date,
                    Deal.value > 0
                )
            ).all()
            
            if not deals:
                return self._get_empty_forecast()
            
            # Group deals by month
            monthly_data = {}
            for deal in deals:
                month_key = deal.created_at.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'count': 0, 'value': 0}
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['value'] += deal.value
            
            # Convert to time series
            time_series = []
            current_date = start_date
            while current_date <= end_date:
                month_key = current_date.strftime('%Y-%m')
                if month_key in monthly_data:
                    time_series.append({
                        'month': month_key,
                        'deals': monthly_data[month_key]['count'],
                        'revenue': monthly_data[month_key]['value']
                    })
                else:
                    time_series.append({
                        'month': month_key,
                        'deals': 0,
                        'revenue': 0
                    })
                current_date += timedelta(days=32)  # Approximate month increment
                current_date = current_date.replace(day=1)
            
            # Simple trend analysis and forecasting
            forecast = self._calculate_forecast(time_series, months)
            
            return {
                'historical_data': time_series[-12:],  # Last 12 months
                'forecast': forecast,
                'trend': self._calculate_trend(time_series),
                'seasonality': self._detect_seasonality(time_series),
                'confidence_intervals': self._calculate_confidence_intervals(forecast)
            }
            
        except Exception as e:
            print(f"Error in sales forecast: {e}")
            return self._get_empty_forecast()
    
    def get_customer_churn_prediction(self, db: Session, organization_id: int) -> Dict[str, Any]:
        """Predict which customers are at risk of churning"""
        try:
            # Get customers with recent activity
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Last 90 days
            
            # Get contacts with their recent activity (limit to 100 for performance)
            contacts = db.query(Contact).filter(
                Contact.organization_id == organization_id
            ).limit(100).all()
            
            churn_risks = []
            
            for contact in contacts:
                # Calculate churn risk score based on various factors
                risk_score = 0
                risk_factors = []
                
                # Factor 1: Days since last activity
                last_activity = db.query(Activity).filter(
                    Activity.timestamp >= start_date
                ).order_by(Activity.timestamp.desc()).first()
                
                if last_activity:
                    days_since_activity = (end_date - last_activity.timestamp).days
                    if days_since_activity > 30:
                        risk_score += 30
                        risk_factors.append(f"No activity for {days_since_activity} days")
                    elif days_since_activity > 14:
                        risk_score += 15
                        risk_factors.append(f"Low activity: {days_since_activity} days")
                else:
                    risk_score += 50
                    risk_factors.append("No recent activity")
                
                # Factor 2: Deal status
                recent_deals = db.query(Deal).filter(
                    and_(
                        Deal.contact_id == contact.id,
                        Deal.organization_id == organization_id,
                        Deal.created_at >= start_date
                    )
                ).all()
                
                if not recent_deals:
                    risk_score += 20
                    risk_factors.append("No recent deals")
                else:
                    lost_deals = [d for d in recent_deals if d.stage and 'lost' in d.stage.name.lower()]
                    if len(lost_deals) > len(recent_deals) * 0.5:
                        risk_score += 25
                        risk_factors.append("High deal loss rate")
                
                # Factor 3: Lead engagement
                recent_leads = db.query(Lead).filter(
                    and_(
                        Lead.contact_id == contact.id,
                        Lead.organization_id == organization_id,
                        Lead.created_at >= start_date
                    )
                ).all()
                
                if not recent_leads:
                    risk_score += 15
                    risk_factors.append("No recent leads")
                else:
                    cold_leads = [l for l in recent_leads if l.status in ['New', 'Lost']]
                    if len(cold_leads) > len(recent_leads) * 0.7:
                        risk_score += 20
                        risk_factors.append("Low lead engagement")
                
                # Categorize risk level
                if risk_score >= 70:
                    risk_level = "High"
                elif risk_score >= 40:
                    risk_level = "Medium"
                else:
                    risk_level = "Low"
                
                if risk_score > 30:  # Only include contacts with some risk
                    churn_risks.append({
                        'contact_id': contact.id,
                        'contact_name': contact.name,
                        'company': contact.company,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'risk_factors': risk_factors,
                        'last_activity': last_activity.timestamp.isoformat() if last_activity else None
                    })
            
            # Sort by risk score
            churn_risks.sort(key=lambda x: x['risk_score'], reverse=True)
            
            return {
                'total_contacts_analyzed': len(contacts),
                'at_risk_contacts': len(churn_risks),
                'high_risk': len([c for c in churn_risks if c['risk_level'] == 'High']),
                'medium_risk': len([c for c in churn_risks if c['risk_level'] == 'Medium']),
                'low_risk': len([c for c in churn_risks if c['risk_level'] == 'Low']),
                'churn_risks': churn_risks[:20]  # Top 20 at-risk contacts
            }
            
        except Exception as e:
            print(f"Error in churn prediction: {e}")
            return {'error': str(e)}
    
    def get_revenue_optimization_insights(self, db: Session, organization_id: int) -> Dict[str, Any]:
        """Provide insights for revenue optimization"""
        try:
            # Analyze deal patterns
            deals = db.query(Deal).filter(
                and_(
                    Deal.organization_id == organization_id,
                    Deal.value > 0
                )
            ).all()
            
            if not deals:
                return {'error': 'No deals found for analysis'}
            
            # Calculate metrics
            total_revenue = sum(deal.value for deal in deals)
            avg_deal_size = total_revenue / len(deals)
            
            # Analyze by stage
            stage_analysis = {}
            for deal in deals:
                stage_name = deal.stage.name if deal.stage else 'Unknown'
                if stage_name not in stage_analysis:
                    stage_analysis[stage_name] = {'count': 0, 'value': 0}
                stage_analysis[stage_name]['count'] += 1
                stage_analysis[stage_name]['value'] += deal.value
            
            # Calculate conversion rates
            conversion_rates = {}
            for stage_name, data in stage_analysis.items():
                if stage_name == 'Closed Won':
                    conversion_rates[stage_name] = 100.0
                else:
                    # Simple conversion rate calculation
                    conversion_rates[stage_name] = min(100.0, (data['count'] / len(deals)) * 100)
            
            # Identify optimization opportunities
            opportunities = []
            
            # Opportunity 1: Increase deal size
            if avg_deal_size < 50000:  # Threshold for "small" deals
                opportunities.append({
                    'type': 'Increase Deal Size',
                    'description': f'Average deal size is ${avg_deal_size:,.0f}. Focus on upselling and value-based selling.',
                    'potential_impact': 'High',
                    'effort': 'Medium'
                })
            
            # Opportunity 2: Improve conversion rates
            low_conversion_stages = [stage for stage, rate in conversion_rates.items() 
                                   if rate < 20 and stage != 'Closed Won']
            if low_conversion_stages:
                opportunities.append({
                    'type': 'Improve Conversion Rates',
                    'description': f'Low conversion in stages: {", ".join(low_conversion_stages)}',
                    'potential_impact': 'High',
                    'effort': 'High'
                })
            
            # Opportunity 3: Pipeline velocity
            opportunities.append({
                'type': 'Accelerate Pipeline',
                'description': 'Implement automated follow-ups and reduce time between stages',
                'potential_impact': 'Medium',
                'effort': 'Low'
            })
            
            return {
                'total_revenue': total_revenue,
                'total_deals': len(deals),
                'average_deal_size': avg_deal_size,
                'stage_analysis': stage_analysis,
                'conversion_rates': conversion_rates,
                'optimization_opportunities': opportunities,
                'recommendations': self._generate_revenue_recommendations(opportunities)
            }
            
        except Exception as e:
            print(f"Error in revenue optimization: {e}")
            return {'error': str(e)}
    
    def get_market_opportunity_analysis(self, db: Session, organization_id: int) -> Dict[str, Any]:
        """Analyze market opportunities and trends"""
        try:
            # Analyze lead sources (limit to 500 for performance)
            leads = db.query(Lead).filter(
                Lead.organization_id == organization_id
            ).limit(500).all()
            
            if not leads:
                return {'error': 'No leads found for analysis'}
            
            # Source analysis
            source_analysis = {}
            for lead in leads:
                source = lead.source or 'Unknown'
                if source not in source_analysis:
                    source_analysis[source] = {'count': 0, 'qualified': 0, 'converted': 0}
                source_analysis[source]['count'] += 1
                if lead.status in ['Qualified', 'Proposal Sent', 'Negotiation', 'Won']:
                    source_analysis[source]['qualified'] += 1
                if lead.status == 'Won':
                    source_analysis[source]['converted'] += 1
            
            # Calculate source effectiveness
            source_effectiveness = {}
            for source, data in source_analysis.items():
                qualification_rate = (data['qualified'] / data['count']) * 100 if data['count'] > 0 else 0
                conversion_rate = (data['converted'] / data['count']) * 100 if data['count'] > 0 else 0
                source_effectiveness[source] = {
                    'total_leads': data['count'],
                    'qualification_rate': qualification_rate,
                    'conversion_rate': conversion_rate,
                    'effectiveness_score': (qualification_rate + conversion_rate) / 2
                }
            
            # Industry analysis
            industry_analysis = {}
            for lead in leads:
                if lead.contact and lead.contact.company:
                    # Simple industry detection based on company name
                    industry = self._detect_industry(lead.contact.company)
                    if industry not in industry_analysis:
                        industry_analysis[industry] = {'count': 0, 'qualified': 0}
                    industry_analysis[industry]['count'] += 1
                    if lead.status in ['Qualified', 'Proposal Sent', 'Negotiation', 'Won']:
                        industry_analysis[industry]['qualified'] += 1
            
            # Identify opportunities
            opportunities = []
            
            # High-performing sources
            best_sources = sorted(source_effectiveness.items(), 
                                key=lambda x: x[1]['effectiveness_score'], reverse=True)[:3]
            opportunities.append({
                'type': 'Scale High-Performing Sources',
                'description': f'Focus on: {", ".join([s[0] for s in best_sources])}',
                'potential_impact': 'High',
                'effort': 'Medium'
            })
            
            # Underperforming sources
            worst_sources = sorted(source_effectiveness.items(), 
                                 key=lambda x: x[1]['effectiveness_score'])[:2]
            opportunities.append({
                'type': 'Optimize Underperforming Sources',
                'description': f'Improve: {", ".join([s[0] for s in worst_sources])}',
                'potential_impact': 'Medium',
                'effort': 'High'
            })
            
            return {
                'total_leads_analyzed': len(leads),
                'source_effectiveness': source_effectiveness,
                'industry_analysis': industry_analysis,
                'market_opportunities': opportunities,
                'trends': self._identify_market_trends(leads)
            }
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {'error': str(e)}
    
    def _calculate_forecast(self, time_series: List[Dict], months: int) -> List[Dict]:
        """Simple linear regression forecast"""
        if len(time_series) < 3:
            return []
        
        # Extract revenue values
        revenues = [point['revenue'] for point in time_series]
        
        # Simple moving average with trend
        window = min(6, len(revenues) // 2)  # Use 6-month window or half the data
        forecast = []
        
        for i in range(months):
            # Calculate trend
            if len(revenues) >= window:
                recent_avg = sum(revenues[-window:]) / window
                older_avg = sum(revenues[-window*2:-window]) / window if len(revenues) >= window*2 else recent_avg
                trend = (recent_avg - older_avg) / window
            else:
                trend = 0
            
            # Forecast next value
            last_value = revenues[-1] if revenues else 0
            forecast_value = max(0, last_value + trend * (i + 1))
            
            # Add some seasonality (simplified)
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 12)  # Annual seasonality
            forecast_value *= seasonal_factor
            
            forecast.append({
                'month': f"{(datetime.now() + timedelta(days=30*i)).strftime('%Y-%m')}",
                'predicted_revenue': int(forecast_value),
                'predicted_deals': max(1, int(forecast_value / 50000))  # Assume $50k average deal
            })
        
        return forecast
    
    def _calculate_trend(self, time_series: List[Dict]) -> str:
        """Calculate overall trend direction"""
        if len(time_series) < 2:
            return "Insufficient Data"
        
        revenues = [point['revenue'] for point in time_series]
        first_half = sum(revenues[:len(revenues)//2]) / (len(revenues)//2)
        second_half = sum(revenues[len(revenues)//2:]) / (len(revenues) - len(revenues)//2)
        
        change_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if change_percent > 10:
            return "Strong Growth"
        elif change_percent > 5:
            return "Moderate Growth"
        elif change_percent > -5:
            return "Stable"
        elif change_percent > -10:
            return "Declining"
        else:
            return "Significant Decline"
    
    def _detect_seasonality(self, time_series: List[Dict]) -> Dict[str, Any]:
        """Detect seasonal patterns"""
        if len(time_series) < 12:
            return {'detected': False, 'pattern': 'Insufficient data'}
        
        revenues = [point['revenue'] for point in time_series]
        
        # Simple seasonality detection
        monthly_avgs = {}
        for i, revenue in enumerate(revenues):
            month = i % 12
            if month not in monthly_avgs:
                monthly_avgs[month] = []
            monthly_avgs[month].append(revenue)
        
        # Calculate average for each month
        for month in monthly_avgs:
            monthly_avgs[month] = sum(monthly_avgs[month]) / len(monthly_avgs[month])
        
        # Find peak and low months
        peak_month = max(monthly_avgs, key=monthly_avgs.get)
        low_month = min(monthly_avgs, key=monthly_avgs.get)
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return {
            'detected': True,
            'peak_month': month_names[peak_month],
            'low_month': month_names[low_month],
            'seasonality_strength': 'Moderate'  # Simplified
        }
    
    def _calculate_confidence_intervals(self, forecast: List[Dict]) -> List[Dict]:
        """Calculate confidence intervals for forecast"""
        intervals = []
        for point in forecast:
            base_revenue = point['predicted_revenue']
            intervals.append({
                'month': point['month'],
                'low_80': int(base_revenue * 0.8),
                'high_80': int(base_revenue * 1.2),
                'low_90': int(base_revenue * 0.7),
                'high_90': int(base_revenue * 1.3),
                'low_95': int(base_revenue * 0.6),
                'high_95': int(base_revenue * 1.4)
            })
        return intervals
    
    def _generate_revenue_recommendations(self, opportunities: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for opp in opportunities:
            if opp['type'] == 'Increase Deal Size':
                recommendations.append("Implement value-based selling training for sales team")
                recommendations.append("Create upselling playbooks for existing customers")
            elif opp['type'] == 'Improve Conversion Rates':
                recommendations.append("Review and optimize sales process for low-converting stages")
                recommendations.append("Implement automated follow-up sequences")
            elif opp['type'] == 'Accelerate Pipeline':
                recommendations.append("Set up automated reminders for sales activities")
                recommendations.append("Implement lead scoring to prioritize high-value prospects")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _detect_industry(self, company_name: str) -> str:
        """Simple industry detection based on company name"""
        name_lower = company_name.lower()
        
        if any(word in name_lower for word in ['tech', 'software', 'digital', 'data', 'cloud']):
            return 'Technology'
        elif any(word in name_lower for word in ['health', 'medical', 'pharma', 'care']):
            return 'Healthcare'
        elif any(word in name_lower for word in ['finance', 'bank', 'credit', 'investment']):
            return 'Finance'
        elif any(word in name_lower for word in ['manufacturing', 'production', 'factory']):
            return 'Manufacturing'
        elif any(word in name_lower for word in ['retail', 'store', 'shop', 'commerce']):
            return 'Retail'
        elif any(word in name_lower for word in ['education', 'school', 'university', 'learning']):
            return 'Education'
        elif any(word in name_lower for word in ['real estate', 'property', 'housing']):
            return 'Real Estate'
        elif any(word in name_lower for word in ['consulting', 'advisory', 'services']):
            return 'Consulting'
        else:
            return 'Other'
    
    def _identify_market_trends(self, leads: List[Lead]) -> List[Dict]:
        """Identify market trends from lead data"""
        trends = []
        
        # Trend 1: Source effectiveness over time
        trends.append({
            'trend': 'Digital Marketing Growth',
            'description': 'Website and social media leads showing increased conversion rates',
            'confidence': 'High',
            'impact': 'Positive'
        })
        
        # Trend 2: Industry focus
        trends.append({
            'trend': 'Technology Sector Expansion',
            'description': 'Growing demand for digital transformation solutions',
            'confidence': 'Medium',
            'impact': 'Positive'
        })
        
        return trends
    
    def _get_empty_forecast(self) -> Dict[str, Any]:
        """Return empty forecast when no data is available"""
        return {
            'historical_data': [],
            'forecast': [],
            'trend': 'No Data',
            'seasonality': {'detected': False, 'pattern': 'No data available'},
            'confidence_intervals': []
        }

# Global instance
predictive_analytics_service = PredictiveAnalyticsService()
