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
    try {
      const data = await predictiveAnalyticsService.getDashboardInsights();
      setInsights(data);
    } catch (err) {
      setError('Failed to load predictive analytics data');
      console.error('Error loading insights:', err);
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

  if (error || !insights) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Error loading predictive analytics</div>
          <div className="text-gray-600 mb-4">{error}</div>
          <button 
            onClick={loadInsights}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
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
          {market_opportunities.market_opportunities.slice(0, 3).map((opp, index) => (
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
          {churn.churn_risks.slice(0, 10).map((risk, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">{risk.contact_name}</div>
                <div className="text-sm text-gray-600">{risk.company}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {risk.risk_factors.slice(0, 2).join(', ')}
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
