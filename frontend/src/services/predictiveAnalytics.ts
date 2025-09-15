import { apiRequest } from '../utils/api';

// Predictive Analytics Service
// API calls for AI-powered insights and forecasting

export interface SalesForecast {
  historical_data: Array<{
    month: string;
    deals: number;
    revenue: number;
  }>;
  forecast: Array<{
    month: string;
    predicted_revenue: number;
    predicted_deals: number;
  }>;
  trend: string;
  seasonality: {
    detected: boolean;
    pattern: string;
    peak_month?: string;
    low_month?: string;
  };
  confidence_intervals: Array<{
    month: string;
    low_80: number;
    high_80: number;
    low_90: number;
    high_90: number;
    low_95: number;
    high_95: number;
  }>;
}

export interface ChurnRisk {
  contact_id: number;
  contact_name: string;
  company: string;
  risk_score: number;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_factors: string[];
  last_activity?: string;
}

export interface ChurnPrediction {
  total_contacts_analyzed: number;
  at_risk_contacts: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  churn_risks: ChurnRisk[];
}

export interface RevenueOptimization {
  total_revenue: number;
  total_deals: number;
  average_deal_size: number;
  stage_analysis: Record<string, { count: number; value: number }>;
  conversion_rates: Record<string, number>;
  optimization_opportunities: Array<{
    type: string;
    description: string;
    potential_impact: string;
    effort: string;
  }>;
  recommendations: string[];
}

export interface MarketOpportunity {
  type: string;
  description: string;
  potential_impact: string;
  effort: string;
}

export interface MarketAnalysis {
  total_leads_analyzed: number;
  source_effectiveness: Record<string, {
    total_leads: number;
    qualification_rate: number;
    conversion_rate: number;
    effectiveness_score: number;
  }>;
  industry_analysis: Record<string, { count: number; qualified: number }>;
  market_opportunities: MarketOpportunity[];
  trends: Array<{
    trend: string;
    description: string;
    confidence: string;
    impact: string;
  }>;
}

export interface DashboardInsights {
  key_metrics: {
    forecasted_revenue_6m: number;
    at_risk_customers: number;
    high_risk_customers: number;
    avg_deal_size: number;
    total_opportunities: number;
  };
  sales_forecast: SalesForecast;
  churn_prediction: ChurnPrediction;
  revenue_optimization: RevenueOptimization;
  market_opportunities: MarketAnalysis;
}

// API calls
export const predictiveAnalyticsService = {
  // Get sales forecast
  async getSalesForecast(months: number = 12): Promise<SalesForecast> {
    const response = await apiRequest<{ success: boolean; data: SalesForecast }>(
      `/api/predictive-analytics/sales-forecast?months=${months}`,
      'GET'
    );
    return response.data;
  },

  // Get churn prediction
  async getChurnPrediction(): Promise<ChurnPrediction> {
    const response = await apiRequest<{ success: boolean; data: ChurnPrediction }>(
      '/api/predictive-analytics/churn-prediction',
      'GET'
    );
    return response.data;
  },

  // Get revenue optimization insights
  async getRevenueOptimization(): Promise<RevenueOptimization> {
    const response = await apiRequest<{ success: boolean; data: RevenueOptimization }>(
      '/api/predictive-analytics/revenue-optimization',
      'GET'
    );
    return response.data;
  },

  // Get market opportunities
  async getMarketOpportunities(): Promise<MarketAnalysis> {
    const response = await apiRequest<{ success: boolean; data: MarketAnalysis }>(
      '/api/predictive-analytics/market-opportunities',
      'GET'
    );
    return response.data;
  },

  // Get comprehensive dashboard insights
  async getDashboardInsights(): Promise<DashboardInsights> {
    const response = await apiRequest<{ success: boolean; data: DashboardInsights }>(
      '/api/predictive-analytics/dashboard-insights',
      'GET'
    );
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    return apiRequest('/api/predictive-analytics/health-check', 'GET');
  }
};

// Helper functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

export const getRiskColor = (riskLevel: string): string => {
  switch (riskLevel) {
    case 'High': return 'text-red-600 bg-red-100';
    case 'Medium': return 'text-yellow-600 bg-yellow-100';
    case 'Low': return 'text-green-600 bg-green-100';
    default: return 'text-gray-600 bg-gray-100';
  }
};

export const getImpactColor = (impact: string): string => {
  switch (impact) {
    case 'High': return 'text-red-600';
    case 'Medium': return 'text-yellow-600';
    case 'Low': return 'text-green-600';
    default: return 'text-gray-600';
  }
};

export const getEffortColor = (effort: string): string => {
  switch (effort) {
    case 'High': return 'text-red-600';
    case 'Medium': return 'text-yellow-600';
    case 'Low': return 'text-green-600';
    default: return 'text-gray-600';
  }
};
