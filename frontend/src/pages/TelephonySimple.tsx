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
  Settings,
  Plus,
  Edit,
  Trash2,
  X
} from 'lucide-react';
import { telephonyService } from '../services/telephony';
import ProviderConfigForm from '../components/ProviderConfigForm';

const TelephonySimple: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [calls, setCalls] = useState<any[]>([]);
  const [queues, setQueues] = useState<any[]>([]);
  const [providers, setProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'calls' | 'agents' | 'queues' | 'settings'>('dashboard');
  
  // Provider management state
  const [showProviderModal, setShowProviderModal] = useState(false);
  const [editingProvider, setEditingProvider] = useState<any>(null);
  const [providerForm, setProviderForm] = useState({
    // Basic Information
    name: '',
    provider_type: 'asterisk',
    display_name: '',
    description: '',
    
    // Basic Connection Settings
    host: '',
    port: 5060,
    username: '',
    password: '',
    authentication_name: '',
    
    // Advanced Connection Settings
    enable_outbound_proxy: false,
    outbound_proxy_host: '',
    outbound_proxy_port: 5060,
    transport: 'UDP',
    enable_nat_traversal: false,
    nat_type: 'auto',
    local_network: '',
    
    // Trunk Configuration
    trunk_type: 'register',
    register_interval: 3600,
    register_timeout: 20,
    max_retries: 5,
    
    // SIP Settings
    sip_context: 'default',
    caller_id_field: 'CallerIDNum',
    dialplan_context: 'from-internal',
    from_domain: '',
    to_domain: '',
    
    // DID/DDI Configuration
    did_numbers: '',
    did_pattern: '',
    did_strip_digits: 0,
    
    // Caller ID Reformatting
    inbound_caller_id_reformatting: false,
    outbound_caller_id_reformatting: false,
    caller_id_prefix: '',
    caller_id_suffix: '',
    caller_id_replacement_rules: '',
    
    // SIP Headers
    custom_sip_headers: '',
    p_asserted_identity: '',
    remote_party_id: '',
    
    // Codec Settings
    preferred_codecs: '',
    codec_negotiation: 'negotiate',
    dtmf_mode: 'rfc2833',
    
    // Quality of Service (QoS)
    enable_qos: false,
    dscp_value: 46,
    bandwidth_limit: '',
    
    // Security Settings
    enable_srtp: false,
    srtp_mode: 'optional',
    enable_tls: false,
    tls_cert_path: '',
    tls_key_path: '',
    tls_ca_path: '',
    
    // Advanced Settings
    recording_enabled: true,
    recording_path: '/var/spool/asterisk/monitor',
    transcription_enabled: false,
    cdr_enabled: true,
    cdr_path: '/var/log/asterisk/cdr-csv',
    call_forwarding_enabled: true,
    call_waiting_enabled: true,
    three_way_calling_enabled: true,
    
    // Monitoring and Analytics
    enable_call_monitoring: true,
    enable_call_recording: false,
    recording_format: 'wav',
    recording_quality: 'high',
    
    // Webhook Settings
    webhook_url: '',
    webhook_secret: '',
    webhook_events: '',
    
    // API Integration
    api_endpoint: '',
    api_key: '',
    api_secret: '',
    api_version: 'v1',
    
    // Status Settings
    is_primary: false,
    auto_assign_calls: true,
    failover_enabled: false,
    failover_provider_id: '',
    is_active: true
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [dashboardRes, callsRes, queuesRes, providersRes] = await Promise.all([
        telephonyService.getDashboard(),
        telephonyService.getCalls(),
        telephonyService.getQueues(),
        telephonyService.getProviders()
      ]);
      
      setDashboardData(dashboardRes);
      setCalls(callsRes);
      setQueues(queuesRes);
      setProviders(providersRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProvider = async () => {
    try {
      if (editingProvider) {
        await telephonyService.updateProvider(editingProvider.id, providerForm);
      } else {
        await telephonyService.createProvider(providerForm);
      }
      
      setShowProviderModal(false);
      setEditingProvider(null);
      setProviderForm({
        name: '',
        provider_type: 'asterisk',
        display_name: '',
        description: '',
        host: '',
        port: 5060,
        username: '',
        password: '',
        authentication_name: '',
        enable_outbound_proxy: false,
        outbound_proxy_host: '',
        outbound_proxy_port: 5060,
        transport: 'UDP',
        enable_nat_traversal: false,
        nat_type: 'auto',
        local_network: '',
        trunk_type: 'register',
        register_interval: 3600,
        register_timeout: 20,
        max_retries: 5,
        sip_context: 'default',
        caller_id_field: 'CallerIDNum',
        dialplan_context: 'from-internal',
        from_domain: '',
        to_domain: '',
        did_numbers: '',
        did_pattern: '',
        did_strip_digits: 0,
        inbound_caller_id_reformatting: false,
        outbound_caller_id_reformatting: false,
        caller_id_prefix: '',
        caller_id_suffix: '',
        caller_id_replacement_rules: '',
        custom_sip_headers: '',
        p_asserted_identity: '',
        remote_party_id: '',
        preferred_codecs: '',
        codec_negotiation: 'negotiate',
        dtmf_mode: 'rfc2833',
        enable_qos: false,
        dscp_value: 46,
        bandwidth_limit: '',
        enable_srtp: false,
        srtp_mode: 'optional',
        enable_tls: false,
        tls_cert_path: '',
        tls_key_path: '',
        tls_ca_path: '',
        recording_enabled: true,
        recording_path: '/var/spool/asterisk/monitor',
        transcription_enabled: false,
        cdr_enabled: true,
        cdr_path: '/var/log/asterisk/cdr-csv',
        call_forwarding_enabled: true,
        call_waiting_enabled: true,
        three_way_calling_enabled: true,
        enable_call_monitoring: true,
        enable_call_recording: false,
        recording_format: 'wav',
        recording_quality: 'high',
        webhook_url: '',
        webhook_secret: '',
        webhook_events: '',
        api_endpoint: '',
        api_key: '',
        api_secret: '',
        api_version: 'v1',
        is_primary: false,
        auto_assign_calls: true,
        failover_enabled: false,
        failover_provider_id: '',
        is_active: true
      });
      
      await fetchAllData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save provider');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Telephony</h1>
          <p className="text-gray-600">Manage your PBX providers and call center</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              setEditingProvider(null);
              setShowProviderModal(true);
            }}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Provider
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'dashboard', name: 'Dashboard', icon: Activity },
            { id: 'calls', name: 'Calls', icon: Phone },
            { id: 'agents', name: 'Agents', icon: Users },
            { id: 'queues', name: 'Queues', icon: Headphones },
            { id: 'settings', name: 'Settings', icon: Settings }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow">
        {activeTab === 'dashboard' && (
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">Call Center Dashboard</h2>
            {dashboardData && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Phone className="w-8 h-8 text-blue-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-blue-600">Active Calls</p>
                      <p className="text-2xl font-bold text-blue-900">{dashboardData.active_calls}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Users className="w-8 h-8 text-green-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-green-600">Available Agents</p>
                      <p className="text-2xl font-bold text-green-900">{dashboardData.available_agents}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Clock className="w-8 h-8 text-yellow-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-yellow-600">Queued Calls</p>
                      <p className="text-2xl font-bold text-yellow-900">{dashboardData.queued_calls}</p>
                    </div>
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <TrendingUp className="w-8 h-8 text-purple-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-purple-600">Service Level</p>
                      <p className="text-2xl font-bold text-purple-900">{dashboardData.service_level}%</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">PBX Providers</h2>
              <button
                onClick={() => {
                  setEditingProvider(null);
                  setShowProviderModal(true);
                }}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Provider
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {providers.map((provider) => (
                <div key={provider.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{provider.display_name}</h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setEditingProvider(provider);
                          setProviderForm({
                            ...providerForm,
                            ...provider
                          });
                          setShowProviderModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-800">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{provider.provider_type}</p>
                  <p className="text-sm text-gray-500">{provider.host}:{provider.port}</p>
                  <div className="flex items-center mt-2">
                    {provider.is_active ? (
                      <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-500 mr-1" />
                    )}
                    <span className={`text-sm ${provider.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {provider.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Provider Modal */}
      {showProviderModal && (
        <ProviderConfigForm
          providerForm={providerForm}
          setProviderForm={setProviderForm}
          onSave={handleSaveProvider}
          onTest={() => {
            alert('Test connection functionality will be implemented');
          }}
          onClose={() => setShowProviderModal(false)}
          isEditing={!!editingProvider}
        />
      )}
    </div>
  );
};

export default TelephonySimple;
