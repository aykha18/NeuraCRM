import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Calendar, 
  Target, 
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Plus,
  Eye,
  Settings
} from 'lucide-react';
import { apiRequest } from '../utils/api';

interface ForecastingModel {
  id: number;
  name: string;
  description: string;
  model_type: string;
  data_source: string;
  model_algorithm: string;
  training_data_period: string;
  forecast_horizon: string;
  accuracy_metrics: {
    overall_accuracy: number;
    mae: number;
    rmse: number;
    mape: number;
  };
  is_active: boolean;
  last_trained: string;
  created_at: string;
}

interface ForecastResult {
  id: number;
  model_id: number;
  forecast_type: string;
  forecast_period: string;
  forecast_date: string;
  forecasted_value: number;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  actual_value?: number;
  accuracy_score?: number;
  trend_direction: string;
  seasonality_factor: number;
  anomaly_detected: boolean;
  forecast_quality_score: number;
  insights: {
    trend: string;
    confidence: string;
    seasonality?: string;
    volatility?: string;
  };
  recommendations: string[];
}

interface DashboardInsights {
  summary: {
    total_models: number;
    active_forecasts: number;
    average_accuracy: number;
    last_updated: string;
  };
  models: Array<{
    id: number;
    name: string;
    type: string;
    algorithm: string;
    last_trained: string;
    accuracy: number;
  }>;
  recent_forecasts: Array<{
    id: number;
    model_name: string;
    forecast_type: string;
    forecasted_value: number;
    forecast_date: string;
    accuracy_score: number;
    trend_direction: string;
  }>;
  trend_analysis: {
    trend: string;
    confidence: string;
    average_accuracy: number;
    insights: string[];
    trend_distribution: {
      increasing: number;
      decreasing: number;
      stable: number;
    };
  };
}

const AdvancedForecasting: React.FC = () => {
  const [models, setModels] = useState<ForecastingModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<ForecastingModel | null>(null);
  const [modelForecasts, setModelForecasts] = useState<ForecastResult[]>([]);
  const [dashboardInsights, setDashboardInsights] = useState<DashboardInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardInsights();
    fetchModels();
  }, []);

  const fetchDashboardInsights = async () => {
    try {
      const response = await apiRequest('/api/forecasting/dashboard-insights');
      setDashboardInsights(response as DashboardInsights);
    } catch (err) {
      console.error('Error fetching dashboard insights:', err);
      setError('Failed to fetch dashboard insights');
    }
  };

  const fetchModels = async () => {
    try {
      const response = await apiRequest('/api/forecasting-models');
      setModels(response as ForecastingModel[]);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError('Failed to fetch forecasting models');
    } finally {
      setLoading(false);
    }
  };

  const fetchModelForecasts = async (modelId: number) => {
    try {
      const response = await apiRequest(`/api/forecasting-models/${modelId}/forecasts`);
      setModelForecasts(response as ForecastResult[]);
    } catch (err) {
      console.error('Error fetching model forecasts:', err);
      setError('Failed to fetch model forecasts');
    }
  };

  const retrainModel = async (modelId: number) => {
    try {
      await apiRequest(`/api/forecasting-models/${modelId}/retrain`, 'POST');
      // Refresh data
      fetchDashboardInsights();
      fetchModels();
      if (selectedModel) {
        fetchModelForecasts(selectedModel.id);
      }
    } catch (err) {
      console.error('Error retraining model:', err);
      setError('Failed to retrain model');
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'decreasing':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <BarChart3 className="w-4 h-4 text-blue-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600 bg-green-100';
      case 'decreasing':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-blue-600 bg-blue-100';
    }
  };

  const formatValue = (value: number, type: string) => {
    if (type === 'revenue' || type === 'pipeline') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value);
    } else if (type === 'customer_growth') {
      return Math.round(value).toString();
    } else if (type === 'churn') {
      return `${(value * 100).toFixed(1)}%`;
    }
    return value.toFixed(2);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Forecasting</h1>
          <p className="text-gray-600 mt-1">
            AI-powered time-series forecasting for revenue, pipeline, and customer growth
          </p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          New Model
        </button>
      </div>

      {/* Dashboard Insights */}
      {dashboardInsights && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Models</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardInsights.summary.total_models}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Forecasts</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardInsights.summary.active_forecasts}</p>
              </div>
              <Target className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(dashboardInsights.summary.average_accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Updated</p>
                <p className="text-sm text-gray-900">
                  {formatDate(dashboardInsights.summary.last_updated)}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>
      )}

      {/* Trend Analysis */}
      {dashboardInsights?.trend_analysis && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Trend Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getTrendColor(dashboardInsights.trend_analysis.trend)}`}>
                {getTrendIcon(dashboardInsights.trend_analysis.trend)}
                <span className="ml-2 capitalize">{dashboardInsights.trend_analysis.trend}</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">Overall Trend</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {(dashboardInsights.trend_analysis.average_accuracy * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Average Accuracy</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 capitalize">
                {dashboardInsights.trend_analysis.confidence}
              </p>
              <p className="text-sm text-gray-600">Confidence Level</p>
            </div>
          </div>
          
          {dashboardInsights.trend_analysis.insights.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Key Insights</h4>
              <ul className="space-y-1">
                {dashboardInsights.trend_analysis.insights.map((insight, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {models.map((model) => (
          <div key={model.id} className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{model.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{model.description}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setSelectedModel(model);
                    fetchModelForecasts(model.id);
                  }}
                  className="p-2 text-gray-400 hover:text-blue-600"
                  title="View Forecasts"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => retrainModel(model.id)}
                  className="p-2 text-gray-400 hover:text-green-600"
                  title="Retrain Model"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Algorithm</p>
                <p className="text-sm font-medium text-gray-900">{model.model_algorithm}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Horizon</p>
                <p className="text-sm font-medium text-gray-900">{model.forecast_horizon}</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <p className="text-xs text-gray-500">Accuracy</p>
                  <p className="text-sm font-semibold text-green-600">
                    {(model.accuracy_metrics.overall_accuracy * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-500">Last Trained</p>
                  <p className="text-sm text-gray-900">
                    {formatDate(model.last_trained)}
                  </p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                model.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {model.is_active ? 'Active' : 'Inactive'}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Model Forecasts */}
      {selectedModel && modelForecasts.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Forecasts for {selectedModel.name}
            </h3>
            <button
              onClick={() => setSelectedModel(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Forecast Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Forecasted Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence Interval
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quality Score
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {modelForecasts.map((forecast) => (
                  <tr key={forecast.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {forecast.forecast_period}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(forecast.forecast_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatValue(forecast.forecasted_value, selectedModel.model_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatValue(forecast.confidence_interval_lower, selectedModel.model_type)} - {formatValue(forecast.confidence_interval_upper, selectedModel.model_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTrendColor(forecast.trend_direction)}`}>
                        {getTrendIcon(forecast.trend_direction)}
                        <span className="ml-1 capitalize">{forecast.trend_direction}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(forecast.forecast_quality_score * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Forecast Insights */}
          {modelForecasts.length > 0 && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Insights</h4>
                <div className="space-y-2">
                  {Object.entries(modelForecasts[0].insights).map(([key, value]) => (
                    <div key={key} className="text-sm text-gray-600">
                      <span className="font-medium capitalize">{key}:</span> {value}
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h4>
                <ul className="space-y-1">
                  {modelForecasts[0].recommendations.map((recommendation, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedForecasting;
