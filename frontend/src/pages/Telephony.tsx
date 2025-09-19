import React, { useState, useEffect } from 'react';
import { 
  Phone, 
  Users, 
  Activity, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Headphones,
  Mic,
  MicOff,
  PhoneCall,
  PhoneIncoming,
  PhoneOutgoing,
  Pause,
  Play,
  Square,
  Settings,
  BarChart3,
  User,
  Calendar,
  Filter
} from 'lucide-react';
import { telephonyService } from '../services/telephony';

interface DashboardData {
  active_calls: number;
  queued_calls: number;
  available_agents: number;
  busy_agents: number;
  offline_agents: number;
  current_queue_status: Array<{
    id: number;
    name: string;
    queue_number: string;
    current_calls: number;
    current_agents: number;
    wait_time: number;
  }>;
  recent_calls: Array<{
    id: number;
    caller_id: string;
    called_number: string;
    direction: string;
    status: string;
    start_time: string;
    duration: number;
    agent_id: number;
  }>;
  agent_status: Array<{
    id: number;
    name: string;
    email: string;
    status: string;
    active_calls: number;
    queues: string[];
  }>;
  queue_metrics: Array<{
    id: number;
    name: string;
    calls_today: number;
    answered_today: number;
    answer_rate: number;
    avg_wait_time: number;
    service_level: number;
  }>;
  hourly_stats: Record<string, number>;
  daily_stats: Record<string, number>;
  alerts: Array<{
    type: string;
    message: string;
  }>;
}

const Telephony: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'calls' | 'agents' | 'queues' | 'settings'>('dashboard');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await telephonyService.getDashboard();
      setDashboardData(data);
      setError(null);
    } catch (err) {
      setError('Failed to load telephony dashboard');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'busy':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'offline':
        return <XCircle className="w-4 h-4 text-gray-400" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'text-green-600 bg-green-50';
      case 'busy':
        return 'text-red-600 bg-red-50';
      case 'offline':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'inbound':
        return <PhoneIncoming className="w-4 h-4 text-green-500" />;
      case 'outbound':
        return <PhoneOutgoing className="w-4 h-4 text-blue-500" />;
      default:
        return <PhoneCall className="w-4 h-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Phone className="w-8 h-8 text-blue-600" />
            Call Center
          </h1>
          <p className="text-gray-600 mt-1">Manage your call center operations</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Activity className="w-4 h-4" />
            Refresh
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'calls', label: 'Calls', icon: PhoneCall },
            { id: 'agents', label: 'Agents', icon: Users },
            { id: 'queues', label: 'Queues', icon: Headphones },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && dashboardData && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Calls</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.active_calls}</p>
                </div>
                <Phone className="w-8 h-8 text-green-600" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Queued Calls</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.queued_calls}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Available Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.available_agents}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Busy Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.busy_agents}</p>
                </div>
                <Users className="w-8 h-8 text-red-600" />
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Offline Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.offline_agents}</p>
                </div>
                <Users className="w-8 h-8 text-gray-400" />
              </div>
            </div>
          </div>

          {/* Alerts */}
          {dashboardData.alerts.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts</h3>
                <div className="space-y-3">
                  {dashboardData.alerts.map((alert, index) => (
                    <div 
                      key={index}
                      className={`p-4 rounded-lg flex items-center gap-3 ${
                        alert.type === 'error' 
                          ? 'bg-red-50 border border-red-200' 
                          : 'bg-yellow-50 border border-yellow-200'
                      }`}
                    >
                      <AlertTriangle className={`w-5 h-5 ${
                        alert.type === 'error' ? 'text-red-500' : 'text-yellow-500'
                      }`} />
                      <p className={`${
                        alert.type === 'error' ? 'text-red-700' : 'text-yellow-700'
                      }`}>
                        {alert.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recent Calls */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Calls</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Caller</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Direction</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {dashboardData.recent_calls.map((call) => (
                      <tr key={call.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            {getDirectionIcon(call.direction)}
                            <span className="text-sm font-medium text-gray-900">{call.caller_id}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-500 capitalize">{call.direction}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(call.status)}`}>
                            {call.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {call.duration ? `${Math.floor(call.duration / 60)}:${(call.duration % 60).toString().padStart(2, '0')}` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(call.start_time).toLocaleTimeString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Agent Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData.agent_status.map((agent) => (
                  <div key={agent.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(agent.status)}
                        <span className="font-medium text-gray-900">{agent.name}</span>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                        {agent.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">{agent.email}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Active calls: {agent.active_calls}</span>
                      <span className="text-gray-600">Queues: {agent.queues.length}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Other tabs placeholder */}
      {activeTab !== 'dashboard' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-gray-400 mb-4">
            {activeTab === 'calls' && <PhoneCall className="w-16 h-16 mx-auto" />}
            {activeTab === 'agents' && <Users className="w-16 h-16 mx-auto" />}
            {activeTab === 'queues' && <Headphones className="w-16 h-16 mx-auto" />}
            {activeTab === 'settings' && <Settings className="w-16 h-16 mx-auto" />}
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {activeTab === 'calls' && 'Call Management'}
            {activeTab === 'agents' && 'Agent Management'}
            {activeTab === 'queues' && 'Queue Management'}
            {activeTab === 'settings' && 'Telephony Settings'}
          </h3>
          <p className="text-gray-500">
            This section is coming soon. Check back later for advanced call center features.
          </p>
        </div>
      )}
    </div>
  );
};

export default Telephony;
