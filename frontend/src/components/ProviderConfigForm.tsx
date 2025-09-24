import React, { useState } from 'react';
import { 
  X, 
  Save, 
  TestTube, 
  Eye, 
  EyeOff,
  ChevronDown,
  ChevronRight,
  Info,
  AlertCircle
} from 'lucide-react';

interface ProviderConfigFormProps {
  providerForm: any;
  setProviderForm: (form: any) => void;
  onSave: () => void;
  onTest: () => void;
  onClose: () => void;
  isEditing: boolean;
}

const ProviderConfigForm: React.FC<ProviderConfigFormProps> = ({
  providerForm,
  setProviderForm,
  onSave,
  onTest,
  onClose,
  isEditing
}) => {
  const [activeTab, setActiveTab] = useState('basic');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['basic']));
  const [showPassword, setShowPassword] = useState(false);

  const tabs = [
    { id: 'basic', name: 'Basic', icon: '📋' },
    { id: 'advanced', name: 'Advanced', icon: '⚙️' },
    { id: 'dids', name: 'DIDs/DDIs', icon: '📞' },
    { id: 'caller-id', name: 'Inbound Caller ID Reformatting', icon: '🔄' },
    { id: 'outbound-caller-id', name: 'Outbound Caller ID', icon: '📤' },
    { id: 'sip-headers', name: 'SIP Headers', icon: '📋' }
  ];

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const handleInputChange = (field: string, value: any) => {
    setProviderForm({
      ...providerForm,
      [field]: value
    });
  };

  const renderBasicTab = () => (
    <div className="space-y-6">
      {/* Provider Details */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Provider Details
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Provider Type *
            </label>
            <select
              value={providerForm.provider_type}
              onChange={(e) => handleInputChange('provider_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="asterisk">Asterisk</option>
              <option value="freepbx">FreePBX</option>
              <option value="3cx">3CX</option>
              <option value="twilio">Twilio</option>
              <option value="yeastar">Yeastar</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Display Name *
            </label>
            <input
              type="text"
              value={providerForm.display_name}
              onChange={(e) => handleInputChange('display_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="My PBX Provider"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={providerForm.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Provider description..."
            />
          </div>
        </div>
      </div>

      {/* Basic Connection Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Basic Connection Settings
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hostname/IP *
            </label>
            <input
              type="text"
              value={providerForm.host}
              onChange={(e) => handleInputChange('host', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="192.168.1.100 or pbx.example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Port
            </label>
            <input
              type="number"
              value={providerForm.port}
              onChange={(e) => handleInputChange('port', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="5060"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username *
            </label>
            <input
              type="text"
              value={providerForm.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="SIP username"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Authentication Name
            </label>
            <input
              type="text"
              value={providerForm.authentication_name}
              onChange={(e) => handleInputChange('authentication_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Auth name (if different from username)"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password *
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={providerForm.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="SIP password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transport
            </label>
            <select
              value={providerForm.transport}
              onChange={(e) => handleInputChange('transport', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="UDP">UDP</option>
              <option value="TCP">TCP</option>
              <option value="TLS">TLS</option>
              <option value="DNS-NAPTR">DNS-NAPTR</option>
            </select>
          </div>
        </div>
      </div>

      {/* Trunk Configuration */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Trunk Configuration
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Trunk Type
            </label>
            <select
              value={providerForm.trunk_type}
              onChange={(e) => handleInputChange('trunk_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="register">Register Trunk</option>
              <option value="peer">Peer Trunk</option>
              <option value="user">User Trunk</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Register Interval (seconds)
            </label>
            <input
              type="number"
              value={providerForm.register_interval}
              onChange={(e) => handleInputChange('register_interval', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="3600"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Register Timeout (seconds)
            </label>
            <input
              type="number"
              value={providerForm.register_timeout}
              onChange={(e) => handleInputChange('register_timeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="20"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Retries
            </label>
            <input
              type="number"
              value={providerForm.max_retries}
              onChange={(e) => handleInputChange('max_retries', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="5"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderAdvancedTab = () => (
    <div className="space-y-6">
      {/* Advanced Connection Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Advanced Connection Settings
          </h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="enable_outbound_proxy"
              checked={providerForm.enable_outbound_proxy}
              onChange={(e) => handleInputChange('enable_outbound_proxy', e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="enable_outbound_proxy" className="text-sm font-medium text-gray-700">
              Enable Outbound Proxy
            </label>
          </div>
          {providerForm.enable_outbound_proxy && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Outbound Proxy Host
                </label>
                <input
                  type="text"
                  value={providerForm.outbound_proxy_host}
                  onChange={(e) => handleInputChange('outbound_proxy_host', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Outbound Proxy Port
                </label>
                <input
                  type="number"
                  value={providerForm.outbound_proxy_port}
                  onChange={(e) => handleInputChange('outbound_proxy_port', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="enable_nat_traversal"
              checked={providerForm.enable_nat_traversal}
              onChange={(e) => handleInputChange('enable_nat_traversal', e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="enable_nat_traversal" className="text-sm font-medium text-gray-700">
              Enable NAT Traversal
            </label>
          </div>
          {providerForm.enable_nat_traversal && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  NAT Type
                </label>
                <select
                  value={providerForm.nat_type}
                  onChange={(e) => handleInputChange('nat_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="auto">Auto</option>
                  <option value="force_rport">Force RPort</option>
                  <option value="comedia">Comedia</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Local Network (CIDR)
                </label>
                <input
                  type="text"
                  value={providerForm.local_network}
                  onChange={(e) => handleInputChange('local_network', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="192.168.1.0/24"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* SIP Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            SIP Settings
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              SIP Context
            </label>
            <input
              type="text"
              value={providerForm.sip_context}
              onChange={(e) => handleInputChange('sip_context', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Caller ID Field
            </label>
            <input
              type="text"
              value={providerForm.caller_id_field}
              onChange={(e) => handleInputChange('caller_id_field', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="CallerIDNum"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dialplan Context
            </label>
            <input
              type="text"
              value={providerForm.dialplan_context}
              onChange={(e) => handleInputChange('dialplan_context', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="from-internal"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From Domain
            </label>
            <input
              type="text"
              value={providerForm.from_domain}
              onChange={(e) => handleInputChange('from_domain', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sip.domain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To Domain
            </label>
            <input
              type="text"
              value={providerForm.to_domain}
              onChange={(e) => handleInputChange('to_domain', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sip.domain.com"
            />
          </div>
        </div>
      </div>

      {/* Codec Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Codec Settings
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Codec Negotiation
            </label>
            <select
              value={providerForm.codec_negotiation}
              onChange={(e) => handleInputChange('codec_negotiation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="negotiate">Negotiate</option>
              <option value="force">Force</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              DTMF Mode
            </label>
            <select
              value={providerForm.dtmf_mode}
              onChange={(e) => handleInputChange('dtmf_mode', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="rfc2833">RFC 2833</option>
              <option value="inband">Inband</option>
              <option value="sip_info">SIP INFO</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Codecs (JSON Array)
            </label>
            <textarea
              value={providerForm.preferred_codecs}
              onChange={(e) => handleInputChange('preferred_codecs', e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder='["ulaw", "alaw", "g729"]'
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderDIDsTab = () => (
    <div className="space-y-6">
      {/* DID/DDI Configuration */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            DID/DDI Configuration
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              DID Numbers (JSON Array)
            </label>
            <textarea
              value={providerForm.did_numbers}
              onChange={(e) => handleInputChange('did_numbers', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder='["+1234567890", "+0987654321"]'
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              DID Pattern
            </label>
            <input
              type="text"
              value={providerForm.did_pattern}
              onChange={(e) => handleInputChange('did_pattern', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="^\+1(\d{10})$"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Strip Digits
            </label>
            <input
              type="number"
              value={providerForm.did_strip_digits}
              onChange={(e) => handleInputChange('did_strip_digits', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderCallerIDTab = () => (
    <div className="space-y-6">
      {/* Caller ID Reformatting */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Inbound Caller ID Reformatting
          </h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="inbound_caller_id_reformatting"
              checked={providerForm.inbound_caller_id_reformatting}
              onChange={(e) => handleInputChange('inbound_caller_id_reformatting', e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="inbound_caller_id_reformatting" className="text-sm font-medium text-gray-700">
              Enable Inbound Caller ID Reformatting
            </label>
          </div>
          {providerForm.inbound_caller_id_reformatting && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Caller ID Prefix
                </label>
                <input
                  type="text"
                  value={providerForm.caller_id_prefix}
                  onChange={(e) => handleInputChange('caller_id_prefix', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="+1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Caller ID Suffix
                </label>
                <input
                  type="text"
                  value={providerForm.caller_id_suffix}
                  onChange={(e) => handleInputChange('caller_id_suffix', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Replacement Rules (JSON Array)
                </label>
                <textarea
                  value={providerForm.caller_id_replacement_rules}
                  onChange={(e) => handleInputChange('caller_id_replacement_rules', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder='[{"pattern": "^\\+1(\\d{10})$", "replacement": "+1$1"}]'
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderOutboundCallerIDTab = () => (
    <div className="space-y-6">
      {/* Outbound Caller ID */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Outbound Caller ID
          </h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="outbound_caller_id_reformatting"
              checked={providerForm.outbound_caller_id_reformatting}
              onChange={(e) => handleInputChange('outbound_caller_id_reformatting', e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="outbound_caller_id_reformatting" className="text-sm font-medium text-gray-700">
              Enable Outbound Caller ID Reformatting
            </label>
          </div>
          <div className="bg-blue-50 p-3 rounded-md">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-blue-500 mr-2 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium">Outbound Caller ID Settings</p>
                <p className="mt-1">Configure how caller ID appears for outbound calls from this trunk.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSIPHeadersTab = () => (
    <div className="space-y-6">
      {/* SIP Headers */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Info className="w-5 h-5 mr-2" />
            SIP Headers
          </h3>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              P-Asserted-Identity
            </label>
            <input
              type="text"
              value={providerForm.p_asserted_identity}
              onChange={(e) => handleInputChange('p_asserted_identity', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sip:user@domain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Remote-Party-ID
            </label>
            <input
              type="text"
              value={providerForm.remote_party_id}
              onChange={(e) => handleInputChange('remote_party_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sip:user@domain.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Custom SIP Headers (JSON Object)
            </label>
            <textarea
              value={providerForm.custom_sip_headers}
              onChange={(e) => handleInputChange('custom_sip_headers', e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder='{"X-Custom-Header": "value", "X-Another-Header": "another-value"}'
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'basic':
        return renderBasicTab();
      case 'advanced':
        return renderAdvancedTab();
      case 'dids':
        return renderDIDsTab();
      case 'caller-id':
        return renderCallerIDTab();
      case 'outbound-caller-id':
        return renderOutboundCallerIDTab();
      case 'sip-headers':
        return renderSIPHeadersTab();
      default:
        return renderBasicTab();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Edit PBX Provider' : 'Add PBX Provider'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {renderTabContent()}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <div className="flex items-center space-x-4">
            <button
              onClick={onTest}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <TestTube className="w-4 h-4 mr-2" />
              Test Connection
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              onClick={onSave}
              className="flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Save className="w-4 h-4 mr-2" />
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProviderConfigForm;
