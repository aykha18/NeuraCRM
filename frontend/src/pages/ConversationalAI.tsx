import React, { useState, useEffect } from 'react';
import { Phone, Mic, Users, BarChart3, Play, Pause, Square, Plus, Settings, Trash2 } from 'lucide-react';

interface Voice {
  voice_id: string;
  name: string;
  language: string;
  gender?: string;
  accent?: string;
}

interface Agent {
  agent_id: string;
  name: string;
  voice_id: string;
  language: string;
  scenario: string;
  status: string;
  created_at: string;
  config: any;
}

interface Call {
  call_id: string;
  agent_id: string;
  to_number: string;
  from_number?: string;
  status: string;
  scenario: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  recording_url?: string;
  transcript?: string;
  cost?: number;
  created_at: string;
}

interface Analytics {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  total_duration: number;
  average_duration: number;
  total_cost: number;
  success_rate: number;
  scenario_breakdown: Record<string, number>;
}

const ConversationalAI: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'agents' | 'calls' | 'analytics'>('agents');
  const [voices, setVoices] = useState<Voice[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [calls, setCalls] = useState<Call[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCreateAgent, setShowCreateAgent] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  // Load data on component mount
  useEffect(() => {
    loadVoices();
    loadAgents();
    loadCalls();
    loadAnalytics();
  }, []);

  const loadVoices = async () => {
    try {
      const response = await fetch('/conversational-ai/voices');
      const data = await response.json();
      setVoices(data.voices || []);
    } catch (error) {
      console.error('Error loading voices:', error);
    }
  };

  const loadAgents = async () => {
    try {
      const response = await fetch('/conversational-ai/agents');
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const loadCalls = async () => {
    try {
      const response = await fetch('/conversational-ai/calls');
      const data = await response.json();
      setCalls(data.calls || []);
    } catch (error) {
      console.error('Error loading calls:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch('/conversational-ai/analytics');
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const createDemoAgents = async () => {
    setLoading(true);
    try {
      const response = await fetch('/conversational-ai/demo/create-agents', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.message) {
        setToast(data.message);
        setTimeout(() => setToast(null), 2000);
        loadAgents(); // Reload agents
      }
    } catch (error) {
      console.error('Error creating demo agents:', error);
      setToast('Error creating demo agents');
      setTimeout(() => setToast(null), 2000);
    } finally {
      setLoading(false);
    }
  };

  const createCall = async (agentId: string, toNumber: string) => {
    setLoading(true);
    try {
      const response = await fetch('/conversational-ai/calls', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          to_number: toNumber,
          scenario: 'SALES_OUTBOUND', // Use enum value
          call_metadata: {
            demo: true,
            created_by: 'frontend'
          },
          lead_id: null,
          contact_id: null,
          user_id: null
        })
      });
      const data = await response.json();
      if (data.call_id) {
        setToast(`Call created successfully! Call ID: ${data.call_id}`);
        setTimeout(() => setToast(null), 3000);
        loadCalls(); // Reload calls
      }
    } catch (error) {
      console.error('Error creating call:', error);
      setToast('Error creating call');
      setTimeout(() => setToast(null), 2000);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Conversational AI</h1>
          <p className="text-gray-600">Manage AI voice agents, calls, and analytics</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={createDemoAgents}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Create Demo Agents
          </button>
          <button
            onClick={() => setShowCreateAgent(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <Settings className="h-4 w-4" />
            Create Custom Agent
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { id: 'agents', label: 'AI Agents', icon: Users },
                { id: 'calls', label: 'Call History', icon: Phone },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Agents Tab */}
            {activeTab === 'agents' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">AI Agents</h3>
                  <span className="text-sm text-gray-500">{agents.length} agents</span>
                </div>
                
                {agents.length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 mb-4">No AI agents created yet</p>
                    <button
                      onClick={createDemoAgents}
                      disabled={loading}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      Create Demo Agents
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {agents.map((agent) => (
                      <div key={agent.agent_id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-gray-900">{agent.name}</h4>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            agent.status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {agent.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Scenario: {agent.scenario.replace('_', ' ')}</p>
                        <p className="text-sm text-gray-600 mb-4">Voice: {agent.voice_id}</p>
                        
                        <div className="flex gap-2">
                          <button
                            onClick={() => createCall(agent.agent_id, '+971524566488')}
                            disabled={loading}
                            className="flex-1 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
                          >
                            Test Call
                          </button>
                          <button className="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-300">
                            <Settings className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Calls Tab */}
            {activeTab === 'calls' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Call History</h3>
                  <span className="text-sm text-gray-500">{calls.length} calls</span>
                </div>
                
                {calls.length === 0 ? (
                  <div className="text-center py-8">
                    <Phone className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No calls made yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Call ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            To Number
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Duration
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Cost
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Created
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {calls.map((call) => (
                          <tr key={call.call_id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                              {call.call_id.slice(0, 8)}...
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {call.to_number}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                call.status === 'completed' 
                                  ? 'bg-green-100 text-green-800'
                                  : call.status === 'failed'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {call.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {call.duration ? formatDuration(call.duration) : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {call.cost ? `$${call.cost.toFixed(4)}` : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(call.created_at)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Call Analytics</h3>
                
                {analytics ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{analytics.total_calls}</div>
                      <div className="text-sm text-blue-600">Total Calls</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{analytics.success_rate.toFixed(1)}%</div>
                      <div className="text-sm text-green-600">Success Rate</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {formatDuration(Math.round(analytics.average_duration))}
                      </div>
                      <div className="text-sm text-purple-600">Avg Duration</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">${analytics.total_cost.toFixed(2)}</div>
                      <div className="text-sm text-orange-600">Total Cost</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No analytics data available</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-green-600 text-white px-6 py-3 rounded-xl shadow-lg z-50 animate-fade-in">
          {toast}
        </div>
      )}
    </div>
  );
};

export default ConversationalAI;
