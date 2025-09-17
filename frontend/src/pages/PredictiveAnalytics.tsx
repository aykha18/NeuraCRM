import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Target, 
  AlertTriangle, 
  CheckCircle,
  BarChart3,
  PieChart,
  LineChart,
  Calendar,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Brain,
  Lightbulb
} from 'lucide-react';
import { 
  predictiveAnalyticsService,
  formatCurrency,
  formatNumber,
  formatPercentage,
  getRiskColor,
  getImpactColor,
  getEffortColor,
  type DashboardInsights,
  type SalesForecast,
  type ChurnPrediction,
  type RevenueOptimization,
  type MarketAnalysis
} from '../services/predictiveAnalytics';

// Fallback data for when API fails
const getFallbackInsights = (): DashboardInsights => ({
  key_metrics: {
    forecasted_revenue_6m: 1250000,
    at_risk_customers: 23,
    high_risk_customers: 8,
    avg_deal_size: 45000,
    total_opportunities: 156
  },
  sales_forecast: {
    historical_data: [
      { month: '2024-01', deals: 12, revenue: 480000 },
      { month: '2024-02', deals: 15, revenue: 600000 },
      { month: '2024-03', deals: 18, revenue: 720000 },
      { month: '2024-04', deals: 14, revenue: 560000 },
      { month: '2024-05', deals: 16, revenue: 640000 },
      { month: '2024-06', deals: 20, revenue: 800000 }
    ],
    forecast: [
      { month: '2024-07', predicted_revenue: 850000, predicted_deals: 21 },
      { month: '2024-08', predicted_revenue: 920000, predicted_deals: 23 },
      { month: '2024-09', predicted_revenue: 880000, predicted_deals: 22 },
      { month: '2024-10', predicted_revenue: 950000, predicted_deals: 24 },
      { month: '2024-11', predicted_revenue: 1000000, predicted_deals: 25 },
      { month: '2024-12', predicted_revenue: 1100000, predicted_deals: 27 }
    ],
    trend: 'upward',
    seasonality: {
      detected: true,
      pattern: 'Q4 peak',
      peak_month: 'December',
      low_month: 'January'
    },
    confidence_intervals: [
      { month: '2024-07', low_80: 680000, high_80: 1020000, low_90: 595000, high_90: 1105000, low_95: 510000, high_95: 1190000 },
      { month: '2024-08', low_80: 736000, high_80: 1104000, low_90: 644000, high_90: 1196000, low_95: 552000, high_95: 1288000 },
      { month: '2024-09', low_80: 704000, high_80: 1056000, low_90: 616000, high_90: 1144000, low_95: 528000, high_95: 1232000 },
      { month: '2024-10', low_80: 760000, high_80: 1140000, low_90: 665000, high_90: 1235000, low_95: 570000, high_95: 1330000 },
      { month: '2024-11', low_80: 800000, high_80: 1200000, low_90: 700000, high_90: 1300000, low_95: 600000, high_95: 1400000 },
      { month: '2024-12', low_80: 880000, high_80: 1320000, low_90: 770000, high_90: 1430000, low_95: 660000, high_95: 1540000 }
    ]
  },
  churn_prediction: {
    total_contacts_analyzed: 1000,
    at_risk_contacts: 23,
    high_risk: 8,
    medium_risk: 10,
    low_risk: 5,
    churn_risks: [
      {
        contact_id: 1,
        contact_name: 'John Smith',
        company: 'TechCorp Inc',
        risk_score: 85,
        risk_level: 'High',
        risk_factors: ['No activity in 60+ days', 'Low engagement score'],
        last_activity: '2024-04-15'
      },
      {
        contact_id: 2,
        contact_name: 'Sarah Johnson',
        company: 'InnovateLabs',
        risk_score: 72,
        risk_level: 'High',
        risk_factors: ['Declining interaction frequency', 'Support ticket escalation'],
        last_activity: '2024-05-02'
      }
    ]
  },
  revenue_optimization: {
    total_revenue: 4200000,
    total_deals: 95,
    average_deal_size: 44210,
    stage_analysis: {
      'Prospecting': { count: 25, value: 750000 },
      'Qualified': { count: 18, value: 810000 },
      'Proposal': { count: 12, value: 720000 },
      'Negotiation': { count: 8, value: 560000 },
      'Closed Won': { count: 32, value: 1360000 }
    },
    conversion_rates: {
      'Prospecting to Qualified': 72,
      'Qualified to Proposal': 67,
      'Proposal to Negotiation': 67,
      'Negotiation to Closed Won': 75
    },
    optimization_opportunities: [
      {
        type: 'Lead Qualification',
        description: 'Improve lead scoring to focus on high-value prospects',
        potential_impact: 'High',
        effort: 'Medium'
      },
      {
        type: 'Follow-up Automation',
        description: 'Implement automated follow-up sequences',
        potential_impact: 'Medium',
        effort: 'Low'
      }
    ],
    recommendations: [
      'Focus on high-value prospects in the qualification stage',
      'Implement automated follow-up sequences for better conversion',
      'Provide additional training for negotiation stage improvements'
    ]
  },
  market_opportunities: {
    total_leads_analyzed: 5000,
    source_effectiveness: {
      'Website': { total_leads: 1500, qualification_rate: 65, conversion_rate: 12, effectiveness_score: 85 },
      'Referral': { total_leads: 800, qualification_rate: 85, conversion_rate: 25, effectiveness_score: 95 },
      'Social Media': { total_leads: 1200, qualification_rate: 45, conversion_rate: 8, effectiveness_score: 60 },
      'Email Campaign': { total_leads: 1000, qualification_rate: 55, conversion_rate: 10, effectiveness_score: 70 },
      'Trade Show': { total_leads: 500, qualification_rate: 75, conversion_rate: 18, effectiveness_score: 88 }
    },
    industry_analysis: {
      'Technology': { count: 1200, qualified: 780 },
      'Healthcare': { count: 800, qualified: 520 },
      'Finance': { count: 600, qualified: 390 },
      'Manufacturing': { count: 400, qualified: 260 },
      'Retail': { count: 300, qualified: 195 }
    },
    market_opportunities: [
      {
        type: 'Industry Expansion',
        description: 'Expand into the healthcare sector with specialized solutions',
        potential_impact: 'High',
        effort: 'High'
      },
      {
        type: 'Referral Program',
        description: 'Launch a formal referral program to increase high-quality leads',
        potential_impact: 'High',
        effort: 'Medium'
      }
    ],
    trends: [
      {
        trend: 'AI Integration Demand',
        description: 'Growing demand for AI-powered business solutions',
        confidence: 'High',
        impact: 'Positive'
      },
      {
        trend: 'Remote Work Solutions',
        description: 'Increased need for remote collaboration tools',
        confidence: 'Medium',
        impact: 'Positive'
      }
    ]
  }
});

export default function PredictiveAnalytics() {
  const [insights, setInsights] = useState<DashboardInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'forecast' | 'churn' | 'revenue' | 'market'>('overview');

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    setLoading(true);
    setError(null);
    
    // Add a shorter timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.log('API call timed out, using fallback data');
      setInsights(getFallbackInsights());
      setLoading(false);
    }, 3000); // 3 second timeout
    
    try {
      console.log('Attempting to load predictive analytics data...');
      const data = await predictiveAnalyticsService.getDashboardInsights();
      clearTimeout(timeoutId);
      console.log('Successfully loaded predictive analytics data:', data);
      setInsights(data);
    } catch (err) {
      clearTimeout(timeoutId);
      console.error('Error loading insights:', err);
      console.log('Using fallback data due to API error');
      // Provide fallback data instead of showing error
      setInsights(getFallbackInsights());
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const { key_metrics, sales_forecast, churn_prediction, revenue_optimization, market_opportunities } = insights;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Brain className="w-6 h-6 text-purple-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Predictive Analytics</h1>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
            AI-Powered
          </span>
        </div>
        <p className="text-gray-600">
          Forecast sales trends, identify opportunities, and predict customer behavior using AI algorithms
        </p>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 text-sm">
            <strong>Demo Mode:</strong> Showing sample predictive analytics data. In production, this would be powered by real-time AI analysis of your CRM data.
          </p>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">
              <strong>API Error:</strong> {error}. Showing demo data instead.
            </p>
          </div>
        )}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">6M Forecasted Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(key_metrics.forecasted_revenue_6m)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">At-Risk Customers</p>
              <p className="text-2xl font-bold text-gray-900">{key_metrics.at_risk_customers}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Risk</p>
              <p className="text-2xl font-bold text-gray-900">{key_metrics.high_risk_customers}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Users className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Deal Size</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(key_metrics.avg_deal_size)}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Opportunities</p>
              <p className="text-2xl font-bold text-gray-900">{key_metrics.total_opportunities}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-8">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'forecast', label: 'Sales Forecast', icon: LineChart },
            { id: 'churn', label: 'Churn Prediction', icon: Users },
            { id: 'revenue', label: 'Revenue Optimization', icon: DollarSign },
            { id: 'market', label: 'Market Opportunities', icon: Target }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === id
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && <OverviewTab insights={insights} />}
        {activeTab === 'forecast' && <ForecastTab forecast={sales_forecast} />}
        {activeTab === 'churn' && <ChurnTab churn={churn_prediction} />}
        {activeTab === 'revenue' && <RevenueTab revenue={revenue_optimization} />}
        {activeTab === 'market' && <MarketTab market={market_opportunities} />}
      </div>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ insights }: { insights: DashboardInsights }) {
  const { sales_forecast, churn_prediction, revenue_optimization, market_opportunities } = insights;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Sales Trend */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-600" />
          Sales Trend
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Current Trend</span>
            <span className={`font-medium ${
              sales_forecast.trend.includes('Growth') ? 'text-green-600' : 
              sales_forecast.trend.includes('Decline') ? 'text-red-600' : 'text-gray-600'
            }`}>
              {sales_forecast.trend}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Seasonality</span>
            <span className="text-sm text-gray-900">
              {sales_forecast.seasonality.detected ? 
                `Peak: ${sales_forecast.seasonality.peak_month}` : 
                'No pattern detected'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Churn Risk Summary */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          Churn Risk Summary
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Analyzed</span>
            <span className="font-medium">{churn_prediction.total_contacts_analyzed}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">At Risk</span>
            <span className="font-medium text-red-600">{churn_prediction.at_risk_contacts}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">High Risk</span>
            <span className="font-medium text-red-600">{churn_prediction.high_risk}</span>
          </div>
        </div>
      </div>

      {/* Revenue Insights */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-blue-600" />
          Revenue Insights
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Revenue</span>
            <span className="font-medium">{formatCurrency(revenue_optimization.total_revenue)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Deals</span>
            <span className="font-medium">{revenue_optimization.total_deals}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Avg Deal Size</span>
            <span className="font-medium">{formatCurrency(revenue_optimization.average_deal_size)}</span>
          </div>
        </div>
      </div>

      {/* Market Opportunities */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-purple-600" />
          Market Opportunities
        </h3>
        <div className="space-y-2">
          {(market_opportunities.market_opportunities || []).slice(0, 3).map((opp, index) => (
            <div key={index} className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-700">{opp.type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Forecast Tab Component
function ForecastTab({ forecast }: { forecast: SalesForecast }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Sales Forecast (Next 6 Months)</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Month</th>
                <th className="text-right py-3 px-4">Predicted Revenue</th>
                <th className="text-right py-3 px-4">Predicted Deals</th>
                <th className="text-right py-3 px-4">Confidence (80%)</th>
              </tr>
            </thead>
            <tbody>
              {forecast.forecast.map((item, index) => (
                <tr key={index} className="border-b">
                  <td className="py-3 px-4">{item.month}</td>
                  <td className="text-right py-3 px-4 font-medium">{formatCurrency(item.predicted_revenue)}</td>
                  <td className="text-right py-3 px-4">{item.predicted_deals}</td>
                  <td className="text-right py-3 px-4 text-sm text-gray-600">
                    {formatCurrency(forecast.confidence_intervals[index]?.low_80 || 0)} - {formatCurrency(forecast.confidence_intervals[index]?.high_80 || 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Churn Tab Component
function ChurnTab({ churn }: { churn: ChurnPrediction }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Customer Churn Risk Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{churn.high_risk}</div>
            <div className="text-sm text-gray-600">High Risk</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{churn.medium_risk}</div>
            <div className="text-sm text-gray-600">Medium Risk</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{churn.low_risk}</div>
            <div className="text-sm text-gray-600">Low Risk</div>
          </div>
        </div>
        
        <div className="space-y-3">
          {(churn.churn_risks || []).slice(0, 10).map((risk, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">{risk.contact_name}</div>
                <div className="text-sm text-gray-600">{risk.company}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {(risk.risk_factors || []).slice(0, 2).join(', ')}
                </div>
              </div>
              <div className="text-right">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(risk.risk_level)}`}>
                  {risk.risk_level} Risk
                </div>
                <div className="text-sm text-gray-600 mt-1">Score: {risk.risk_score}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Revenue Tab Component
function RevenueTab({ revenue }: { revenue: RevenueOptimization }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Revenue Optimization Opportunities</h3>
        <div className="space-y-4">
          {revenue.optimization_opportunities.map((opp, index) => (
            <div key={index} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium">{opp.type}</h4>
                <div className="flex gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${getImpactColor(opp.potential_impact)} bg-opacity-20`}>
                    {opp.potential_impact} Impact
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${getEffortColor(opp.effort)} bg-opacity-20`}>
                    {opp.effort} Effort
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{opp.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
        <div className="space-y-2">
          {revenue.recommendations.map((rec, index) => (
            <div key={index} className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">{rec}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Market Tab Component
function MarketTab({ market }: { market: MarketAnalysis }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Source Effectiveness</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Source</th>
                <th className="text-right py-3 px-4">Total Leads</th>
                <th className="text-right py-3 px-4">Qualification Rate</th>
                <th className="text-right py-3 px-4">Conversion Rate</th>
                <th className="text-right py-3 px-4">Effectiveness Score</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(market.source_effectiveness).map(([source, data]) => (
                <tr key={source} className="border-b">
                  <td className="py-3 px-4 font-medium">{source}</td>
                  <td className="text-right py-3 px-4">{data.total_leads}</td>
                  <td className="text-right py-3 px-4">{formatPercentage(data.qualification_rate)}</td>
                  <td className="text-right py-3 px-4">{formatPercentage(data.conversion_rate)}</td>
                  <td className="text-right py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      data.effectiveness_score > 50 ? 'bg-green-100 text-green-800' :
                      data.effectiveness_score > 30 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {formatPercentage(data.effectiveness_score)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Market Opportunities</h3>
        <div className="space-y-4">
          {market.market_opportunities.map((opp, index) => (
            <div key={index} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium">{opp.type}</h4>
                <div className="flex gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${getImpactColor(opp.potential_impact)} bg-opacity-20`}>
                    {opp.potential_impact} Impact
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${getEffortColor(opp.effort)} bg-opacity-20`}>
                    {opp.effort} Effort
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{opp.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
