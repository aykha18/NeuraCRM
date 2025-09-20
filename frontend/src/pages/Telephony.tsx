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
  Filter,
  Search,
  Plus,
  Edit,
  Trash2,
  RefreshCw,
  Download,
  Upload,
  Eye,
  MoreHorizontal,
  Zap,
  Target,
  Timer,
  Volume2,
  VolumeX,
  MessageSquare,
  Star,
  AlertCircle,
  CheckCircle2,
  X,
  ChevronDown,
  ChevronUp
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

const TelephonyEnhanced: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [calls, setCalls] = useState<any[]>([]);
  const [queues, setQueues] = useState<any[]>([]);
  const [queueMembers, setQueueMembers] = useState<any[]>([]);
  const [providers, setProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'calls' | 'agents' | 'queues' | 'settings'>('dashboard');
  
  // Filters and search
  const [callFilters, setCallFilters] = useState({
    status: '',
    direction: '',
    dateRange: '',
    search: ''
  });
  const [agentFilters, setAgentFilters] = useState({
    status: '',
    queue: '',
    search: ''
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [dashboard, callsData, queuesData, membersData, providersData] = await Promise.all([
        telephonyService.getDashboard(),
        telephonyService.getCalls({ limit: 100 }),
        telephonyService.getQueues(),
        telephonyService.getQueueMembers(),
        telephonyService.getProviders()
      ]);
      
      setDashboardData(dashboard);
      setCalls(callsData);
      setQueues(queuesData);
      setQueueMembers(membersData);
      setProviders(providersData);
      setError(null);
    } catch (err) {
      setError('Failed to load telephony data');
      console.error('Error fetching telephony data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available':
      case 'logged_in':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'busy':
      case 'answered':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'offline':
      case 'logged_out':
        return <XCircle className="w-4 h-4 text-gray-400" />;
      case 'ringing':
        return <PhoneCall className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available':
      case 'logged_in':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'busy':
      case 'answered':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'offline':
      case 'logged_out':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      case 'ringing':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getDirectionIcon = (direction: string) => {
    switch (direction.toLowerCase()) {
      case 'inbound':
        return <PhoneIncoming className="w-4 h-4 text-green-500" />;
      case 'outbound':
        return <PhoneOutgoing className="w-4 h-4 text-blue-500" />;
      case 'internal':
        return <Phone className="w-4 h-4 text-purple-500" />;
      default:
        return <PhoneCall className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDuration = (seconds: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredCalls = calls.filter(call => {
    if (callFilters.status && call.status !== callFilters.status) return false;
    if (callFilters.direction && call.direction !== callFilters.direction) return false;
    if (callFilters.search) {
      const search = callFilters.search.toLowerCase();
      return (
        call.caller_id?.toLowerCase().includes(search) ||
        call.called_number?.toLowerCase().includes(search) ||
        call.caller_name?.toLowerCase().includes(search) ||
        call.called_name?.toLowerCase().includes(search)
      );
    }
    return true;
  });

  const filteredAgents = queueMembers.filter(member => {
    if (agentFilters.status && member.status !== agentFilters.status) return false;
    if (agentFilters.search) {
      const search = agentFilters.search.toLowerCase();
      return (
        member.member_name?.toLowerCase().includes(search) ||
        member.user?.name?.toLowerCase().includes(search) ||
        member.user?.email?.toLowerCase().includes(search)
      );
    }
    return true;
  });

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
            onClick={fetchAllData}
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
            onClick={fetchAllData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
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
          {dashboardData.alerts && dashboardData.alerts.length > 0 && (
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
          {dashboardData.recent_calls && dashboardData.recent_calls.length > 0 && (
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
                      {dashboardData.recent_calls.slice(0, 10).map((call) => (
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
                            {formatDuration(call.duration)}
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
          )}
        </div>
      )}

      {/* Calls Tab */}
      {activeTab === 'calls' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={callFilters.status}
                  onChange={(e) => setCallFilters({...callFilters, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  <option value="ringing">Ringing</option>
                  <option value="answered">Answered</option>
                  <option value="completed">Completed</option>
                  <option value="busy">Busy</option>
                  <option value="no-answer">No Answer</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Direction</label>
                <select
                  value={callFilters.direction}
                  onChange={(e) => setCallFilters({...callFilters, direction: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Directions</option>
                  <option value="inbound">Inbound</option>
                  <option value="outbound">Outbound</option>
                  <option value="internal">Internal</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search calls..."
                    value={callFilters.search}
                    onChange={(e) => setCallFilters({...callFilters, search: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setCallFilters({ status: '', direction: '', dateRange: '', search: '' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>

          {/* Calls Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">All Calls ({filteredCalls.length})</h3>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Caller</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Called</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Direction</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredCalls.map((call) => (
                      <tr key={call.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            {getDirectionIcon(call.direction)}
                            <div>
                              <div className="text-sm font-medium text-gray-900">{call.caller_id}</div>
                              {call.caller_name && (
                                <div className="text-sm text-gray-500">{call.caller_name}</div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{call.called_number}</div>
                          {call.called_name && (
                            <div className="text-sm text-gray-500">{call.called_name}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-500 capitalize">{call.direction}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(call.status)}`}>
                            {getStatusIcon(call.status)}
                            <span className="ml-1">{call.status}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDuration(call.duration)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(call.start_time).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {call.agent_id ? `Agent ${call.agent_id}` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center gap-2">
                            <button className="text-blue-600 hover:text-blue-900">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="text-green-600 hover:text-green-900">
                              <Phone className="w-4 h-4" />
                            </button>
                            <button className="text-gray-600 hover:text-gray-900">
                              <MoreHorizontal className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={agentFilters.status}
                  onChange={(e) => setAgentFilters({...agentFilters, status: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  <option value="logged_in">Available</option>
                  <option value="logged_out">Offline</option>
                  <option value="paused">Paused</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Queue</label>
                <select
                  value={agentFilters.queue}
                  onChange={(e) => setAgentFilters({...agentFilters, queue: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Queues</option>
                  {queues.map(queue => (
                    <option key={queue.id} value={queue.id}>{queue.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search agents..."
                    value={agentFilters.search}
                    onChange={(e) => setAgentFilters({...agentFilters, search: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Agents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((member) => (
              <div key={member.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(member.status)}
                    <div>
                      <h3 className="font-semibold text-gray-900">{member.member_name || member.user?.name || 'Unknown'}</h3>
                      <p className="text-sm text-gray-500">{member.user?.email || 'No email'}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(member.status)}`}>
                    {member.status}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Extension:</span>
                    <span className="font-medium">{member.extension_number || '-'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Queue:</span>
                    <span className="font-medium">{member.queue?.name || '-'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Penalty:</span>
                    <span className="font-medium">{member.penalty || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Calls:</span>
                    <span className="font-medium">{member.total_calls || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Answer Rate:</span>
                    <span className="font-medium">
                      {member.total_calls > 0 
                        ? `${Math.round((member.answered_calls / member.total_calls) * 100)}%`
                        : '0%'
                      }
                    </span>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm">
                    <Phone className="w-4 h-4 inline mr-1" />
                    Call
                  </button>
                  <button className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Queues Tab */}
      {activeTab === 'queues' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Call Queues</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Queue
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {queues.map((queue) => (
              <div key={queue.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{queue.name}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    queue.is_active ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
                  }`}>
                    {queue.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Queue Number:</span>
                    <span className="font-medium">{queue.queue_number}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Strategy:</span>
                    <span className="font-medium">{queue.strategy}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current Calls:</span>
                    <span className="font-medium">{queue.current_calls || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Available Agents:</span>
                    <span className="font-medium">{queue.current_agents || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Calls:</span>
                    <span className="font-medium">{queue.total_calls || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Answer Rate:</span>
                    <span className="font-medium">
                      {queue.total_calls > 0 
                        ? `${Math.round((queue.answered_calls / queue.total_calls) * 100)}%`
                        : '0%'
                      }
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Avg Wait Time:</span>
                    <span className="font-medium">{queue.avg_wait_time || 0}s</span>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm">
                    <Users className="w-4 h-4 inline mr-1" />
                    Manage
                  </button>
                  <button className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Telephony Settings</h2>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Provider
            </button>
          </div>

          {/* PBX Providers */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">PBX Providers</h3>
              <div className="space-y-4">
                {providers.map((provider) => (
                  <div key={provider.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${
                          provider.is_active ? 'bg-green-500' : 'bg-red-500'
                        }`}></div>
                        <div>
                          <h4 className="font-semibold text-gray-900">{provider.display_name}</h4>
                          <p className="text-sm text-gray-500">{provider.provider_type} - {provider.host}:{provider.port}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          provider.is_primary ? 'text-blue-600 bg-blue-50' : 'text-gray-600 bg-gray-50'
                        }`}>
                          {provider.is_primary ? 'Primary' : 'Secondary'}
                        </span>
                        <button className="text-blue-600 hover:text-blue-900">
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Recording:</span>
                        <span className={`ml-2 ${provider.recording_enabled ? 'text-green-600' : 'text-red-600'}`}>
                          {provider.recording_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Transcription:</span>
                        <span className={`ml-2 ${provider.transcription_enabled ? 'text-green-600' : 'text-red-600'}`}>
                          {provider.transcription_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Last Sync:</span>
                        <span className="ml-2">{new Date(provider.last_sync).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Created:</span>
                        <span className="ml-2">{new Date(provider.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* System Settings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Auto Call Recording</h4>
                    <p className="text-sm text-gray-500">Automatically record all calls</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition translate-x-6" />
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Call Transcription</h4>
                    <p className="text-sm text-gray-500">Automatically transcribe call recordings</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition translate-x-1" />
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Real-time Analytics</h4>
                    <p className="text-sm text-gray-500">Enable real-time call center analytics</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition translate-x-6" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TelephonyEnhanced;
