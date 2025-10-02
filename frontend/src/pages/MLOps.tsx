import { useState, useEffect } from 'react';
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Settings,
  RefreshCw,
  Activity,
  Zap,
  Clock,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

// Type definitions
interface Model {
  id: string;
  name: string;
  version: string;
  status: string;
  accuracy: number;
  last_trained: string;
  last_deployed: string;
  training_data_size: number;
  model_type: string;
  performance_trend: string;
}

interface RetrainingJob {
  id: string;
  model_name: string;
  status: string;
  progress: number;
  started_at: string | null;
  estimated_completion: string;
  trigger_reason: string;
  current_accuracy: number;
  target_accuracy: number;
}

interface Metrics {
  system_health: string;
  total_predictions_today: number;
  average_response_time: number;
  error_rate: number;
  model_drift_detected: boolean;
  data_quality_score: number;
}

interface MLOpsData {
  dashboard: {
    total_models: number;
    active_models: number;
    retraining_jobs: number;
    average_accuracy: number;
    models_needing_retraining: number;
    recent_deployments: number;
  };
  models: Model[];
  retraining_jobs: RetrainingJob[];
  metrics: Metrics;
}

// Fallback data for when API fails
const getFallbackMLOpsData = (): MLOpsData => ({
  dashboard: {
    total_models: 5,
    active_models: 4,
    retraining_jobs: 2,
    average_accuracy: 87.5,
    models_needing_retraining: 1,
    recent_deployments: 3
  },
  models: [
    {
      id: 'sentiment_analyzer',
      name: 'Sentiment Analyzer',
      version: '2.1.0',
      status: 'active',
      accuracy: 0.92,
      last_trained: '2024-10-01T10:00:00Z',
      last_deployed: '2024-10-01T11:00:00Z',
      training_data_size: 15000,
      model_type: 'keyword_based',
      performance_trend: 'stable'
    },
    {
      id: 'lead_scorer',
      name: 'Lead Scoring Model',
      version: '1.8.3',
      status: 'active',
      accuracy: 0.85,
      last_trained: '2024-09-28T14:30:00Z',
      last_deployed: '2024-09-28T15:45:00Z',
      training_data_size: 8500,
      model_type: 'gradient_boosting',
      performance_trend: 'improving'
    },
    {
      id: 'forecasting_model',
      name: 'Sales Forecasting',
      version: '3.2.1',
      status: 'active',
      accuracy: 0.88,
      last_trained: '2024-09-25T09:15:00Z',
      last_deployed: '2024-09-25T10:30:00Z',
      training_data_size: 12000,
      model_type: 'time_series',
      performance_trend: 'stable'
    },
    {
      id: 'customer_segmentation',
      name: 'Customer Segmentation',
      version: '1.5.2',
      status: 'needs_retraining',
      accuracy: 0.78,
      last_trained: '2024-09-15T16:20:00Z',
      last_deployed: '2024-09-15T17:00:00Z',
      training_data_size: 6800,
      model_type: 'clustering',
      performance_trend: 'declining'
    },
    {
      id: 'churn_predictor',
      name: 'Churn Predictor',
      version: '2.0.1',
      status: 'active',
      accuracy: 0.91,
      last_trained: '2024-09-30T08:00:00Z',
      last_deployed: '2024-09-30T09:15:00Z',
      training_data_size: 9500,
      model_type: 'neural_network',
      performance_trend: 'improving'
    }
  ],
  retraining_jobs: [
    {
      id: 'job_001',
      model_name: 'customer_segmentation',
      status: 'running',
      progress: 65,
      started_at: '2024-10-02T12:00:00Z',
      estimated_completion: '2024-10-02T14:30:00Z',
      trigger_reason: 'performance_degradation',
      current_accuracy: 0.78,
      target_accuracy: 0.85
    },
    {
      id: 'job_002',
      model_name: 'lead_scorer',
      status: 'scheduled',
      progress: 0,
      started_at: null,
      estimated_completion: '2024-10-03T10:00:00Z',
      trigger_reason: 'scheduled_maintenance',
      current_accuracy: 0.85,
      target_accuracy: 0.87
    }
  ],
  metrics: {
    system_health: 'healthy',
    total_predictions_today: 15420,
    average_response_time: 45,
    error_rate: 0.02,
    model_drift_detected: false,
    data_quality_score: 94
  }
});

export default function MLOps() {
  const [mlopsData, setMLOpsData] = useState<MLOpsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadMLOpsData();
  }, []);

  const loadMLOpsData = async () => {
    setLoading(true);
    setError(null);

    // Add timeout for API call
    const timeoutId = setTimeout(() => {
      console.log('MLOps API call timed out, using fallback data');
      setMLOpsData(getFallbackMLOpsData());
      setLoading(false);
    }, 3000);

    try {
      // TODO: Implement actual API call
      // const data = await mlopsService.getDashboard();
      clearTimeout(timeoutId);
      setMLOpsData(getFallbackMLOpsData());
    } catch (err) {
      clearTimeout(timeoutId);
      console.error('Error loading MLOps data:', err);
      setMLOpsData(getFallbackMLOpsData());
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

  if (!mlopsData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const { dashboard, models, retraining_jobs, metrics } = mlopsData;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Brain className="w-6 h-6 text-purple-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">MLOps Dashboard</h1>
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
            Model Lifecycle Management
          </span>
        </div>
        <p className="text-gray-600">
          Monitor, manage, and optimize your AI models with automated retraining and performance tracking
        </p>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm">
            <strong>Demo Mode:</strong> Showing sample MLOps data. In production, this would connect to your actual model registry and monitoring systems.
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Models</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.total_models}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Models</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.active_models}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Retraining Jobs</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.retraining_jobs}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <RefreshCw className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.average_accuracy}%</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Needs Retraining</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.models_needing_retraining}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent Deployments</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.recent_deployments}</p>
            </div>
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Zap className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-8">
        <nav className="flex space-x-8">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'models', label: 'Models', icon: Brain },
            { id: 'retraining', label: 'Retraining', icon: RefreshCw },
            { id: 'monitoring', label: 'Monitoring', icon: Activity }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
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
        {activeTab === 'dashboard' && <DashboardTab data={mlopsData} />}
        {activeTab === 'models' && <ModelsTab models={models} />}
        {activeTab === 'retraining' && <RetrainingTab jobs={retraining_jobs} />}
        {activeTab === 'monitoring' && <MonitoringTab metrics={metrics} />}
      </div>
    </div>
  );
}

// Dashboard Tab Component
function DashboardTab({ data }: { data: MLOpsData }) {
  const { dashboard, models, retraining_jobs, metrics } = data;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* System Health */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-green-600" />
          System Health
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Overall Status</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              metrics.system_health === 'healthy' ? 'bg-green-100 text-green-800' :
              metrics.system_health === 'warning' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {metrics.system_health.toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Predictions Today</span>
            <span className="font-medium">{metrics.total_predictions_today.toLocaleString()}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Avg Response Time</span>
            <span className="font-medium">{metrics.average_response_time}ms</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Error Rate</span>
            <span className="font-medium">{(metrics.error_rate * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>

      {/* Model Performance Overview */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Model Performance
        </h3>
        <div className="space-y-3">
          {models.slice(0, 4).map((model, index) => (
            <div key={index} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{model.name}</div>
                <div className="text-xs text-gray-500">v{model.version}</div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{(model.accuracy * 100).toFixed(1)}%</span>
                <div className={`w-2 h-2 rounded-full ${
                  model.performance_trend === 'improving' ? 'bg-green-500' :
                  model.performance_trend === 'declining' ? 'bg-red-500' :
                  'bg-gray-500'
                }`} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Retraining Jobs */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <RefreshCw className="w-5 h-5 text-orange-600" />
          Active Retraining Jobs
        </h3>
        <div className="space-y-3">
          {retraining_jobs.filter(job => job.status === 'running').map((job, index) => (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">{job.model_name}</span>
                <span className="text-xs text-gray-500">{job.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
              <div className="text-xs text-gray-500">
                {job.trigger_reason.replace('_', ' ')}
              </div>
            </div>
          ))}
          {retraining_jobs.filter(job => job.status === 'running').length === 0 && (
            <p className="text-sm text-gray-500">No active retraining jobs</p>
          )}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          Recent Alerts
        </h3>
        <div className="space-y-3">
          {models.filter(model => model.status === 'needs_retraining').map((model, index) => (
            <div key={index} className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">{model.name}</div>
                <div className="text-xs text-gray-600">Performance degradation detected</div>
              </div>
            </div>
          ))}
          {metrics.model_drift_detected && (
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">Data Drift Detected</div>
                <div className="text-xs text-gray-600">Model inputs have changed significantly</div>
              </div>
            </div>
          )}
          {models.filter(model => model.status === 'needs_retraining').length === 0 && !metrics.model_drift_detected && (
            <p className="text-sm text-gray-500">No active alerts</p>
          )}
        </div>
      </div>
    </div>
  );
}

// Models Tab Component
function ModelsTab({ models }: { models: Model[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'needs_retraining': return 'bg-red-100 text-red-800';
      case 'training': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <ArrowUpRight className="w-4 h-4 text-green-600" />;
      case 'declining': return <ArrowDownRight className="w-4 h-4 text-red-600" />;
      default: return <div className="w-4 h-4 rounded-full bg-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Model Registry</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4">Model Name</th>
                <th className="text-left py-3 px-4">Version</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-right py-3 px-4">Accuracy</th>
                <th className="text-left py-3 px-4">Type</th>
                <th className="text-left py-3 px-4">Last Trained</th>
                <th className="text-center py-3 px-4">Trend</th>
                <th className="text-center py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model, index) => (
                <tr key={index} className="border-b">
                  <td className="py-3 px-4">
                    <div className="font-medium">{model.name}</div>
                    <div className="text-sm text-gray-500">{model.id}</div>
                  </td>
                  <td className="py-3 px-4">{model.version}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(model.status)}`}>
                      {model.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="text-right py-3 px-4 font-medium">
                    {(model.accuracy * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-4">{model.model_type.replace('_', ' ')}</td>
                  <td className="py-3 px-4 text-sm">
                    {new Date(model.last_trained).toLocaleDateString()}
                  </td>
                  <td className="text-center py-3 px-4">
                    {getTrendIcon(model.performance_trend)}
                  </td>
                  <td className="text-center py-3 px-4">
                    <div className="flex gap-1 justify-center">
                      <button className="p-1 text-blue-600 hover:bg-blue-50 rounded">
                        <Settings className="w-4 h-4" />
                      </button>
                      {model.status === 'needs_retraining' && (
                        <button className="p-1 text-green-600 hover:bg-green-50 rounded">
                          <RefreshCw className="w-4 h-4" />
                        </button>
                      )}
                    </div>
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

// Retraining Tab Component
function RetrainingTab({ jobs }: { jobs: RetrainingJob[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'scheduled': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'scheduled': return <Clock className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Pause className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Retraining Jobs</h3>
        <div className="space-y-4">
          {jobs.map((job, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-medium">{job.model_name}</h4>
                  <p className="text-sm text-gray-600">Job ID: {job.id}</p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(job.status)}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                    {job.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                <div>
                  <div className="text-sm text-gray-600">Trigger Reason</div>
                  <div className="font-medium">{job.trigger_reason.replace('_', ' ')}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Current Accuracy</div>
                  <div className="font-medium">{(job.current_accuracy * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Target Accuracy</div>
                  <div className="font-medium">{(job.target_accuracy * 100).toFixed(1)}%</div>
                </div>
              </div>

              {job.status === 'running' && (
                <div className="mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Progress</span>
                    <span className="text-sm font-medium">{job.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>
                  {job.started_at ? `Started: ${new Date(job.started_at).toLocaleString()}` : 'Not started'}
                </span>
                <span>
                  {job.estimated_completion ? `Est. completion: ${new Date(job.estimated_completion).toLocaleString()}` : ''}
                </span>
              </div>
            </div>
          ))}

          {jobs.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <RefreshCw className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No retraining jobs found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Monitoring Tab Component
function MonitoringTab({ metrics }: { metrics: Metrics }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Performance Metrics */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Predictions</span>
              <span className="font-medium">{metrics.total_predictions_today.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Response Time</span>
              <span className="font-medium">{metrics.average_response_time}ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Error Rate</span>
              <span className={`font-medium ${(metrics.error_rate * 100) > 1 ? 'text-red-600' : 'text-green-600'}`}>
                {(metrics.error_rate * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Data Quality Score</span>
              <span className={`font-medium ${metrics.data_quality_score > 90 ? 'text-green-600' : 'text-yellow-600'}`}>
                {metrics.data_quality_score}%
              </span>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Overall Status</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                metrics.system_health === 'healthy' ? 'bg-green-100 text-green-800' :
                metrics.system_health === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {metrics.system_health.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Model Drift</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                metrics.model_drift_detected ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
              }`}>
                {metrics.model_drift_detected ? 'DETECTED' : 'NORMAL'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Active Models</span>
              <span className="font-medium text-green-600">4/5</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Failed Deployments</span>
              <span className="font-medium text-green-600">0</span>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">Model deployed</div>
                <div className="text-xs text-gray-600">Sentiment Analyzer v2.1.0 - 2 hours ago</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <RefreshCw className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">Retraining started</div>
                <div className="text-xs text-gray-600">Customer Segmentation - 4 hours ago</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">Performance alert</div>
                <div className="text-xs text-gray-600">Lead Scorer accuracy dropped - 6 hours ago</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Play className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium">Scheduled retraining</div>
                <div className="text-xs text-gray-600">Churn Predictor - scheduled for tomorrow</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="flex items-center justify-center gap-2 p-3 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors">
            <RefreshCw className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-700">Run Health Check</span>
          </button>
          <button className="flex items-center justify-center gap-2 p-3 border border-green-200 rounded-lg hover:bg-green-50 transition-colors">
            <Play className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-700">Start Retraining</span>
          </button>
          <button className="flex items-center justify-center gap-2 p-3 border border-purple-200 rounded-lg hover:bg-purple-50 transition-colors">
            <Brain className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-700">Deploy Model</span>
          </button>
          <button className="flex items-center justify-center gap-2 p-3 border border-orange-200 rounded-lg hover:bg-orange-50 transition-colors">
            <Settings className="w-4 h-4 text-orange-600" />
            <span className="text-sm font-medium text-orange-700">Configure Alerts</span>
          </button>
        </div>
      </div>
    </div>
  );
}