import { useState, useEffect } from 'react';
import { 
  Mail, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Send, 
  BarChart3, 
  // Calendar,
  // Users,
  Target,
  FileText,
  // Settings,
  CheckCircle,
  // AlertCircle,
  Clock,
  Play,
  Pause,
  // Square
} from 'lucide-react';
import {
  getEmailTemplates,
  createEmailTemplate,
  updateEmailTemplate,
  deleteEmailTemplate,
  previewTemplate,
  createSampleTemplates,
  getEmailCampaigns,
  createEmailCampaign,
  sendCampaign,
  getEmailLogs,
  getEmailAnalytics,
  // getTemplateVariables,
  // formatTemplateVariable,
  type EmailTemplate,
  type EmailCampaign,
  type EmailLog,
  type EmailAnalytics,
  type TemplatePreview
} from '../services/emailAutomation';
import { fetchLeads } from '../services/leads';
import { fetchContacts } from '../services/contacts';

export default function EmailAutomationPage() {
  // State management
  const [activeTab, setActiveTab] = useState<'templates' | 'campaigns' | 'analytics'>('templates');
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [campaigns, setCampaigns] = useState<EmailCampaign[]>([]);
  const [logs, setLogs] = useState<EmailLog[]>([]);
  const [analytics, setAnalytics] = useState<EmailAnalytics | null>(null);
  const [leads, setLeads] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // Auto-clear toast after 3 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // Template management
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    subject: '',
    body: '',
    category: ''
  });

  // Campaign management
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [campaignForm, setCampaignForm] = useState({
    name: '',
    template_id: 0,
    target_type: 'leads',
    target_ids: [] as number[],
    scheduled_at: ''
  });

  // Preview
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewData, setPreviewData] = useState<TemplatePreview | null>(null);
  const [previewRecipient, setPreviewRecipient] = useState({
    type: 'lead',
    id: 0
  });

  // Load data
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [templatesData, campaignsData, logsData, analyticsData, leadsData, contactsData] = await Promise.all([
        getEmailTemplates(),
        getEmailCampaigns(),
        getEmailLogs(),
        getEmailAnalytics(),
        fetchLeads(),
        fetchContacts()
      ]);
      
      setTemplates(templatesData);
      setCampaigns(campaignsData);
      setLogs(logsData);
      setAnalytics(analyticsData);
      setLeads(leadsData);
      setContacts(contactsData);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Template functions
  const handleCreateTemplate = async () => {
    try {
      await createEmailTemplate(templateForm);
      setShowTemplateModal(false);
      setTemplateForm({ name: '', subject: '', body: '', category: '' });
      loadData();
      setToast('Template created successfully!');
    } catch (err) {
      setToast('Failed to create template');
    }
  };

  const handleUpdateTemplate = async () => {
    if (!editingTemplate) return;
    try {
      await updateEmailTemplate(editingTemplate.id, templateForm);
      setShowTemplateModal(false);
      setEditingTemplate(null);
      setTemplateForm({ name: '', subject: '', body: '', category: '' });
      loadData();
      setToast('Template updated successfully!');
    } catch (err) {
      setToast('Failed to update template');
    }
  };

  const handleDeleteTemplate = async (id: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    try {
      await deleteEmailTemplate(id);
      loadData();
      setToast('Template deleted successfully!');
    } catch (err) {
      setToast('Failed to delete template');
    }
  };

  const handleEditTemplate = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setTemplateForm({
      name: template.name,
      subject: template.subject,
      body: template.body,
      category: template.category || ''
    });
    setShowTemplateModal(true);
  };

  const handlePreviewTemplate = async (template: EmailTemplate) => {
    if (previewRecipient.id === 0) {
      setToast('Please select a recipient for preview');
      return;
    }
    try {
      const preview = await previewTemplate(template.id, previewRecipient.type, previewRecipient.id);
      setPreviewData(preview);
      setShowPreviewModal(true);
    } catch (err) {
      setToast('Failed to preview template');
    }
  };

  const handleCreateSampleTemplates = async () => {
    try {
      await createSampleTemplates();
      loadData();
      setToast('Sample templates created successfully!');
    } catch (err) {
      setToast('Failed to create sample templates');
    }
  };

  // Campaign functions
  const handleCreateCampaign = async () => {
    try {
      await createEmailCampaign(campaignForm);
      setShowCampaignModal(false);
      setCampaignForm({ name: '', template_id: 0, target_type: 'leads', target_ids: [], scheduled_at: '' });
      loadData();
      setToast('Campaign created successfully!');
    } catch (err) {
      setToast('Failed to create campaign');
    }
  };

  const handleSendCampaign = async (campaignId: number) => {
    if (!confirm('Are you sure you want to send this campaign?')) return;
    try {
      const result = await sendCampaign(campaignId);
      loadData();
      setToast(`Campaign sent! ${result.sent_count} emails delivered.`);
    } catch (err) {
      setToast('Failed to send campaign');
    }
  };

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700';
      case 'scheduled': return 'bg-blue-100 text-blue-700';
      case 'sending': return 'bg-yellow-100 text-yellow-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'paused': return 'bg-orange-100 text-orange-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft': return <FileText className="w-4 h-4" />;
      case 'scheduled': return <Clock className="w-4 h-4" />;
      case 'sending': return <Play className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'paused': return <Pause className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  if (loading) return <div className="p-8 text-lg">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50">
          {toast}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">Email Automation</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage templates, campaigns, and automation</p>
        </div>
        <button
          onClick={handleCreateSampleTemplates}
          className="px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg hover:from-purple-600 hover:to-indigo-600 transition"
        >
          <Plus className="w-4 h-4 inline mr-2" />
          Create Sample Templates
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 mb-6">
        <button
          onClick={() => setActiveTab('templates')}
          className={`flex items-center px-4 py-2 rounded-md transition ${
            activeTab === 'templates' 
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          Templates
        </button>
        <button
          onClick={() => setActiveTab('campaigns')}
          className={`flex items-center px-4 py-2 rounded-md transition ${
            activeTab === 'campaigns' 
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Send className="w-4 h-4 mr-2" />
          Campaigns
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center px-4 py-2 rounded-md transition ${
            activeTab === 'analytics' 
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow' 
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Analytics
        </button>
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Email Templates</h2>
            <button
              onClick={() => setShowTemplateModal(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              <Plus className="w-4 h-4 inline mr-2" />
              Create Template
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <div key={template.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{template.name}</h3>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handlePreviewTemplate(template)}
                      className="p-1 text-gray-400 hover:text-blue-500"
                      title="Preview"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleEditTemplate(template)}
                      className="p-1 text-gray-400 hover:text-green-500"
                      title="Edit"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteTemplate(template.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{template.subject}</p>
                
                {template.category && (
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full mb-2">
                    {template.category}
                  </span>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Variables: {template.validation.total_variables}</span>
                  <span className={template.validation.valid ? 'text-green-500' : 'text-red-500'}>
                    {template.validation.valid ? 'Valid' : 'Invalid'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Email Campaigns</h2>
            <button
              onClick={() => setShowCampaignModal(true)}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
            >
              <Plus className="w-4 h-4 inline mr-2" />
              Create Campaign
            </button>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Template</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {campaigns.map((campaign) => (
                  <tr key={campaign.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{campaign.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {templates.find(t => t.id === campaign.template_id)?.name || 'Unknown'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {campaign.target_type} ({JSON.parse(campaign.target_ids).length})
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                        {getStatusIcon(campaign.status)}
                        <span className="ml-1">{campaign.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => handleSendCampaign(campaign.id)}
                          className="text-green-600 hover:text-green-900 mr-3"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Email Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center">
                <Mail className="w-8 h-8 text-blue-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Total Sent</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">{analytics.total_sent}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center">
                <Eye className="w-8 h-8 text-green-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Opened</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">{analytics.total_opened}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center">
                <Target className="w-8 h-8 text-purple-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Clicked</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">{analytics.total_clicked}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center">
                <BarChart3 className="w-8 h-8 text-orange-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Open Rate</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">{analytics.open_rate}%</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium">Recent Email Logs</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recipient</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {logs.slice(0, 10).map((log) => (
                    <tr key={log.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">{log.recipient_name}</div>
                        <div className="text-sm text-gray-500">{log.recipient_email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 dark:text-white">{log.subject}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          log.status === 'sent' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                        }`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(log.sent_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">
              {editingTemplate ? 'Edit Template' : 'Create Template'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm({...templateForm, name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select
                  value={templateForm.category}
                  onChange={(e) => setTemplateForm({...templateForm, category: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Category</option>
                  <option value="welcome">Welcome</option>
                  <option value="follow_up">Follow-up</option>
                  <option value="reminder">Reminder</option>
                  <option value="notification">Notification</option>
                  <option value="deal_update">Deal Update</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Subject</label>
                <input
                  type="text"
                  value={templateForm.subject}
                  onChange={(e) => setTemplateForm({...templateForm, subject: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Welcome to {{contact.company}}, {{contact.name}}!"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Body (HTML)</label>
                <textarea
                  value={templateForm.body}
                  onChange={(e) => setTemplateForm({...templateForm, body: e.target.value})}
                  rows={10}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="<div>Hello {{contact.name}}!</div>"
                />
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                <h4 className="font-medium mb-2">Available Variables:</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;contact.name&#125;&#125;</code> - Contact Name</div>
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;contact.email&#125;&#125;</code> - Contact Email</div>
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;contact.company&#125;&#125;</code> - Company</div>
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;lead.title&#125;&#125;</code> - Lead Title</div>
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;deal.value&#125;&#125;</code> - Deal Value</div>
                  <div><code className="bg-gray-200 px-1 rounded">&#123;&#123;user.name&#125;&#125;</code> - User Name</div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowTemplateModal(false);
                  setEditingTemplate(null);
                  setTemplateForm({ name: '', subject: '', body: '', category: '' });
                }}
                className="px-4 py-2 text-gray-600 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={editingTemplate ? handleUpdateTemplate : handleCreateTemplate}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                {editingTemplate ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Campaign Modal */}
      {showCampaignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl">
            <h2 className="text-xl font-semibold mb-4">Create Campaign</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Campaign Name</label>
                <input
                  type="text"
                  value={campaignForm.name}
                  onChange={(e) => setCampaignForm({...campaignForm, name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Template</label>
                <select
                  value={campaignForm.template_id}
                  onChange={(e) => setCampaignForm({...campaignForm, template_id: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={0}>Select Template</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>{template.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Target Type</label>
                <select
                  value={campaignForm.target_type}
                  onChange={(e) => setCampaignForm({...campaignForm, target_type: e.target.value, target_ids: []})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="leads">Leads</option>
                  <option value="contacts">Contacts</option>
                  <option value="deals">Deals</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Target Recipients</label>
                <select
                  multiple
                  value={campaignForm.target_ids.map(String)}
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                    setCampaignForm({...campaignForm, target_ids: selected});
                  }}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  size={5}
                >
                  {campaignForm.target_type === 'leads' && leads.map((lead) => (
                    <option key={lead.id} value={lead.id}>
                      {lead.title} - {lead.contact?.name || 'Unknown'}
                    </option>
                  ))}
                  {campaignForm.target_type === 'contacts' && contacts.map((contact) => (
                    <option key={contact.id} value={contact.id}>
                      {contact.name} - {contact.company || 'No Company'}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowCampaignModal(false);
                  setCampaignForm({ name: '', template_id: 0, target_type: 'leads', target_ids: [], scheduled_at: '' });
                }}
                className="px-4 py-2 text-gray-600 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCampaign}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Create Campaign
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreviewModal && previewData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Template Preview</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Preview Recipient</label>
              <div className="flex space-x-2">
                <select
                  value={previewRecipient.type}
                  onChange={(e) => setPreviewRecipient({...previewRecipient, type: e.target.value, id: 0})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value="lead">Lead</option>
                  <option value="contact">Contact</option>
                  <option value="deal">Deal</option>
                </select>
                <select
                  value={previewRecipient.id}
                  onChange={(e) => setPreviewRecipient({...previewRecipient, id: parseInt(e.target.value)})}
                  className="px-3 py-2 border rounded-lg"
                >
                  <option value={0}>Select Recipient</option>
                  {previewRecipient.type === 'lead' && leads.map((lead) => (
                    <option key={lead.id} value={lead.id}>
                      {lead.title} - {lead.contact?.name || 'Unknown'}
                    </option>
                  ))}
                  {previewRecipient.type === 'contact' && contacts.map((contact) => (
                    <option key={contact.id} value={contact.id}>
                      {contact.name} - {contact.company || 'No Company'}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-4">
              <h3 className="font-medium mb-2">Subject:</h3>
              <p className="text-gray-900 dark:text-white">{previewData.subject}</p>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Body:</h3>
              <div 
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: previewData.body }}
              />
            </div>
            
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowPreviewModal(false)}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 