import React, { useState, useEffect } from 'react';
import {
  Plus,
  Play,
  Pause,
  Edit,
  Trash2,
  Users,
  Target,
  TrendingUp,
  Clock,
  Mail,
  Phone,
  CheckSquare,
  Calendar,
  Filter,
  Search,
  Eye,
  Settings
} from 'lucide-react';
import AnimatedModal from '../components/AnimatedModal';

interface Campaign {
  id: number;
  campaign_name: string;
  campaign_description?: string;
  campaign_type: string;
  target_segment?: string;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  total_leads: number;
  active_leads: number;
  converted_leads: number;
  conversion_rate: number;
  created_at: string;
  updated_at: string;
  created_by: number;
}

interface NurturingStep {
  id: number;
  campaign_id: number;
  step_name: string;
  step_type: string;
  step_order: number;
  delay_days: number;
  delay_hours: number;
  step_data: any;
  trigger_conditions?: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface CampaignEnrollment {
  id: number;
  lead_id: number;
  campaign_id: number;
  enrollment_reason?: string;
  current_step: number;
  status: string;
  enrolled_at: string;
  last_activity?: string;
  completed_at?: string;
}

const LeadNurturing: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'campaigns' | 'steps' | 'enrollments'>('campaigns');
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [steps, setSteps] = useState<NurturingStep[]>([]);
  const [enrollments, setEnrollments] = useState<CampaignEnrollment[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateCampaign, setShowCreateCampaign] = useState(false);
  const [showCreateStep, setShowCreateStep] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [newCampaign, setNewCampaign] = useState({
    campaign_name: '',
    campaign_description: '',
    campaign_type: 'drip',
    target_segment: '',
    is_active: true,
    start_date: '',
    end_date: ''
  });
  const [newStep, setNewStep] = useState({
    step_name: '',
    step_type: 'email',
    step_order: 1,
    delay_days: 0,
    delay_hours: 0,
    step_data: {},
    trigger_conditions: {},
    is_active: true
  });
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('No authentication token found, skipping API calls');
      return;
    }

    if (activeTab === 'campaigns') {
      fetchCampaigns();
    } else if (activeTab === 'steps' && selectedCampaign) {
      fetchCampaignSteps(selectedCampaign.id);
    } else if (activeTab === 'enrollments' && selectedCampaign) {
      fetchCampaignEnrollments(selectedCampaign.id);
    }
  }, [activeTab, selectedCampaign]);

  const fetchCampaigns = async () => {
    try {
      const response = await fetch('/api/lead-nurturing-campaigns', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        setCampaigns(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch campaigns:', data.error);
        setCampaigns([]);
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      setCampaigns([]);
    }
  };

  const fetchCampaignSteps = async (campaignId: number) => {
    try {
      const response = await fetch(`/api/lead-nurturing-campaigns/${campaignId}/steps`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        setSteps(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch steps:', data.error);
        setSteps([]);
      }
    } catch (error) {
      console.error('Error fetching steps:', error);
      setSteps([]);
    }
  };

  const fetchCampaignEnrollments = async (campaignId: number) => {
    try {
      const response = await fetch(`/api/lead-nurturing-campaigns/${campaignId}/enrollments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        setEnrollments(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch enrollments:', data.error);
        setEnrollments([]);
      }
    } catch (error) {
      console.error('Error fetching enrollments:', error);
      setEnrollments([]);
    }
  };

  const createCampaign = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No authentication token found - please log in first');
      alert('Please log in first to create campaigns');
      return;
    }

    try {
      // Prepare campaign data, converting empty strings to null for optional datetime fields
      const campaignData = {
        ...newCampaign,
        start_date: newCampaign.start_date && newCampaign.start_date.trim() !== '' ? newCampaign.start_date : null,
        end_date: newCampaign.end_date && newCampaign.end_date.trim() !== '' ? newCampaign.end_date : null,
        target_segment: newCampaign.target_segment && newCampaign.target_segment.trim() !== '' ? newCampaign.target_segment : null
      };

      const response = await fetch('/api/lead-nurturing-campaigns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(campaignData)
      });
      
      const data = await response.json();
      if (response.ok) {
        fetchCampaigns();
        setShowCreateCampaign(false);
        setNewCampaign({
          campaign_name: '',
          campaign_description: '',
          campaign_type: 'drip',
          target_segment: '',
          is_active: true,
          start_date: '',
          end_date: ''
        });
        setSuccessMessage('Campaign created successfully!');
        setShowSuccessModal(true);
      } else {
        console.error('Failed to create campaign:', data.error);
        setSuccessMessage(`Failed to create campaign: ${data.error}`);
        setShowSuccessModal(true);
      }
    } catch (error) {
      console.error('Error creating campaign:', error);
      setSuccessMessage('Error creating campaign');
      setShowSuccessModal(true);
    }
  };

  const createStep = async () => {
    if (!selectedCampaign) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No authentication token found - please log in first');
      alert('Please log in first to create steps');
      return;
    }

    try {
      const response = await fetch(`/api/lead-nurturing-campaigns/${selectedCampaign.id}/steps`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newStep)
      });
      
      const data = await response.json();
      if (response.ok) {
        fetchCampaignSteps(selectedCampaign.id);
        setShowCreateStep(false);
        setNewStep({
          step_name: '',
          step_type: 'email',
          step_order: 1,
          delay_days: 0,
          delay_hours: 0,
          step_data: {},
          trigger_conditions: {},
          is_active: true
        });
        setSuccessMessage('Step created successfully!');
        setShowSuccessModal(true);
      } else {
        console.error('Failed to create step:', data.error);
        setSuccessMessage(`Failed to create step: ${data.error}`);
        setShowSuccessModal(true);
      }
    } catch (error) {
      console.error('Error creating step:', error);
      setSuccessMessage('Error creating step');
      setShowSuccessModal(true);
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'call': return <Phone className="w-4 h-4" />;
      case 'task': return <CheckSquare className="w-4 h-4" />;
      case 'wait': return <Clock className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'completed': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'converted': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Lead Nurturing Campaigns
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Create and manage automated lead nurturing campaigns to improve conversion rates
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('campaigns')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'campaigns'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Campaigns
            </button>
            <button
              onClick={() => setActiveTab('steps')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'steps'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : !selectedCampaign 
                    ? 'border-transparent text-gray-400 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Campaign Steps
            </button>
            <button
              onClick={() => setActiveTab('enrollments')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'enrollments'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : !selectedCampaign 
                    ? 'border-transparent text-gray-400 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              Enrollments
            </button>
          </nav>
        </div>
      </div>

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search campaigns..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
              </div>
              <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white">
                <option value="all">All Types</option>
                <option value="drip">Drip Campaigns</option>
                <option value="behavioral">Behavioral</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
            <button
              onClick={() => setShowCreateCampaign(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Create Campaign</span>
            </button>
          </div>

          {/* Campaigns Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign) => (
              <div
                key={campaign.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedCampaign(campaign)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {campaign.campaign_name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {campaign.campaign_type.charAt(0).toUpperCase() + campaign.campaign_type.slice(1)} Campaign
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedCampaign(campaign);
                        setActiveTab('steps');
                      }}
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                    <button
                      className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedCampaign(campaign);
                        setActiveTab('enrollments');
                      }}
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {campaign.campaign_description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {campaign.campaign_description}
                  </p>
                )}

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {campaign.total_leads}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Total Leads</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {campaign.conversion_rate}%
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Conversion Rate</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    campaign.is_active 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                  }`}>
                    {campaign.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(campaign.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {campaigns.length === 0 && (
            <div className="text-center py-12">
              <Target className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No campaigns</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Get started by creating your first lead nurturing campaign.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateCampaign(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Campaign
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Steps Tab */}
      {activeTab === 'steps' && (
        <div>
          {!selectedCampaign ? (
            <div className="text-center py-12">
              <Target className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Select a Campaign</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Please select a campaign from the Campaigns tab to view and manage its steps.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setActiveTab('campaigns')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Go to Campaigns
                </button>
              </div>
            </div>
          ) : (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Steps for "{selectedCampaign.campaign_name}"
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Manage the sequence of actions in your campaign
              </p>
            </div>
            <button
              onClick={() => setShowCreateStep(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Step</span>
            </button>
          </div>

          <div className="space-y-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full">
                      <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                        {step.step_order}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStepIcon(step.step_type)}
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {step.step_name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {step.delay_days > 0 && `${step.delay_days}d `}
                      {step.delay_hours > 0 && `${step.delay_hours}h`}
                      {step.delay_days === 0 && step.delay_hours === 0 && 'Immediate'}
                    </span>
                    <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {steps.length === 0 && (
            <div className="text-center py-12">
              <Target className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No steps</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Add steps to create your nurturing sequence.
              </p>
            </div>
          )}
        </div>
          )}
        </div>
      )}

      {/* Enrollments Tab */}
      {activeTab === 'enrollments' && (
        <div>
          {!selectedCampaign ? (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Select a Campaign</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Please select a campaign from the Campaigns tab to view its enrollments.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setActiveTab('campaigns')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Go to Campaigns
                </button>
              </div>
            </div>
          ) : (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Enrollments for "{selectedCampaign.campaign_name}"
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                View and manage lead enrollments in this campaign
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Lead ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Current Step
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Enrolled
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Last Activity
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {enrollments.map((enrollment) => (
                  <tr key={enrollment.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      #{enrollment.lead_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      Step {enrollment.current_step}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(enrollment.status)}`}>
                        {enrollment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {new Date(enrollment.enrolled_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {enrollment.last_activity ? new Date(enrollment.last_activity).toLocaleDateString() : 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {enrollments.length === 0 && (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No enrollments</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                No leads have been enrolled in this campaign yet.
              </p>
            </div>
          )}
        </div>
          )}
        </div>
      )}

      {/* Create Campaign Modal */}
      <AnimatedModal
        open={showCreateCampaign}
        onClose={() => setShowCreateCampaign(false)}
        title="Create Lead Nurturing Campaign"
        animationType="scale"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Campaign Name
            </label>
            <input
              type="text"
              value={newCampaign.campaign_name}
              onChange={(e) => setNewCampaign({...newCampaign, campaign_name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Enter campaign name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={newCampaign.campaign_description}
              onChange={(e) => setNewCampaign({...newCampaign, campaign_description: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              rows={3}
              placeholder="Enter campaign description"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Campaign Type
              </label>
              <select
                value={newCampaign.campaign_type}
                onChange={(e) => setNewCampaign({...newCampaign, campaign_type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="drip">Drip Campaign</option>
                <option value="behavioral">Behavioral</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Target Segment
              </label>
              <input
                type="text"
                value={newCampaign.target_segment}
                onChange={(e) => setNewCampaign({...newCampaign, target_segment: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                placeholder="e.g., High-value leads"
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={newCampaign.is_active}
              onChange={(e) => setNewCampaign({...newCampaign, is_active: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Active campaign
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setShowCreateCampaign(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={createCampaign}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Campaign
            </button>
          </div>
        </div>
      </AnimatedModal>

      {/* Create Step Modal */}
      <AnimatedModal
        open={showCreateStep}
        onClose={() => setShowCreateStep(false)}
        title="Add Campaign Step"
        animationType="scale"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Step Name
            </label>
            <input
              type="text"
              value={newStep.step_name}
              onChange={(e) => setNewStep({...newStep, step_name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Enter step name"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Step Type
              </label>
              <select
                value={newStep.step_type}
                onChange={(e) => setNewStep({...newStep, step_type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="email">Email</option>
                <option value="call">Call</option>
                <option value="task">Task</option>
                <option value="wait">Wait</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Step Order
              </label>
              <input
                type="number"
                value={newStep.step_order}
                onChange={(e) => setNewStep({...newStep, step_order: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                min="1"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Delay (Days)
              </label>
              <input
                type="number"
                value={newStep.delay_days}
                onChange={(e) => setNewStep({...newStep, delay_days: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Delay (Hours)
              </label>
              <input
                type="number"
                value={newStep.delay_hours}
                onChange={(e) => setNewStep({...newStep, delay_hours: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                min="0"
                max="23"
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="step_active"
              checked={newStep.is_active}
              onChange={(e) => setNewStep({...newStep, is_active: e.target.checked})}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="step_active" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Active step
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={() => setShowCreateStep(false)}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={createStep}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Step
            </button>
          </div>
        </div>
      </AnimatedModal>

      {/* Success/Error Modal */}
      <AnimatedModal
        open={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title={successMessage.includes('Failed') || successMessage.includes('Error') ? 'Error' : 'Success'}
        animationType="scale"
        size="sm"
      >
        <div className="text-center space-y-4">
          <div className={`mx-auto flex items-center justify-center h-16 w-16 rounded-full ${
            successMessage.includes('Failed') || successMessage.includes('Error') 
              ? 'bg-red-100 dark:bg-red-900' 
              : 'bg-green-100 dark:bg-green-900'
          }`}>
            {successMessage.includes('Failed') || successMessage.includes('Error') ? (
              <Target className="h-8 w-8 text-red-600 dark:text-red-400" />
            ) : (
              <TrendingUp className="h-8 w-8 text-green-600 dark:text-green-400" />
            )}
          </div>
          <p className="text-lg text-gray-900 dark:text-white">
            {successMessage}
          </p>
          <button
            onClick={() => setShowSuccessModal(false)}
            className={`w-full px-4 py-2 text-white rounded-lg transition-colors duration-200 ${
              successMessage.includes('Failed') || successMessage.includes('Error')
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            Close
          </button>
        </div>
      </AnimatedModal>
    </div>
  );
};

export default LeadNurturing;
