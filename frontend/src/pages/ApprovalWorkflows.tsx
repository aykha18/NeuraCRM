import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Users, 
  Settings, 
  Plus, 
  Filter,
  Search,
  Eye,
  Check,
  X,
  UserCheck,
  AlertCircle,
  Calendar,
  FileText,
  DollarSign,
  Target,
  TrendingUp
} from 'lucide-react';
import AnimatedModal from '../components/AnimatedModal';

interface ApprovalWorkflow {
  id: number;
  workflow_name: string;
  workflow_description?: string;
  entity_type: string;
  trigger_conditions: any;
  approval_steps: any[];
  is_active: boolean;
  auto_approve_conditions?: any;
  created_at: string;
  created_by: number;
}

interface ApprovalRequest {
  id: number;
  entity_type: string;
  entity_id: number;
  request_reason: string;
  priority: string;
  status: string;
  current_step: number;
  total_steps: number;
  requested_at: string;
  requester_name?: string;
  due_date?: string;
  completion_notes?: string;
}

interface ApprovalStep {
  id: number;
  step_number: number;
  approver_id: number;
  approver_name: string;
  status: string;
  comments?: string;
  approved_at?: string;
  due_date?: string;
}

const ApprovalWorkflows: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workflows' | 'requests' | 'my-pending' | 'settings'>('workflows');
  const [workflows, setWorkflows] = useState<ApprovalWorkflow[]>([]);
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [approvalSteps, setApprovalSteps] = useState<ApprovalStep[]>([]);
  const [showCreateWorkflow, setShowCreateWorkflow] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject' | 'delegate'>('approve');
  const [approvalComments, setApprovalComments] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Create Workflow Modal State
  const [newWorkflow, setNewWorkflow] = useState({
    workflow_name: '',
    workflow_description: '',
    entity_type: 'deal',
    trigger_conditions: {},
    approval_steps: [],
    is_active: true
  });

  const tabs = [
    { id: 'workflows', name: 'Workflows', icon: <Settings className="w-5 h-5" /> },
    { id: 'requests', name: 'All Requests', icon: <FileText className="w-5 h-5" /> },
    { id: 'my-pending', name: 'My Pending', icon: <Clock className="w-5 h-5" /> },
    { id: 'settings', name: 'Settings', icon: <Settings className="w-5 h-5" /> }
  ];

  useEffect(() => {
    // Only fetch data if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('No authentication token found, skipping API calls');
      return;
    }

    if (activeTab === 'workflows') {
      fetchWorkflows();
    } else if (activeTab === 'requests') {
      fetchRequests();
    } else if (activeTab === 'my-pending') {
      fetchPendingApprovals();
    }
  }, [activeTab, filterStatus, filterEntityType]);

  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/approval-workflows', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setWorkflows(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch workflows:', data.error);
        if (response.status === 401) {
          console.error('Authentication failed - please log in again');
          // Optionally redirect to login
        }
        setWorkflows([]);
      }
    } catch (error) {
      console.error('Error fetching workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRequests = async () => {
    setLoading(true);
    try {
      let url = '/api/approval-requests';
      const params = new URLSearchParams();
      
      if (filterStatus !== 'all') {
        params.append('status', filterStatus);
      }
      if (filterEntityType !== 'all') {
        params.append('entity_type', filterEntityType);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setRequests(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch requests:', data.error);
        setRequests([]);
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingApprovals = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/approval-requests/my-pending', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setPendingApprovals(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch pending approvals:', data.error);
        setPendingApprovals([]);
      }
    } catch (error) {
      console.error('Error fetching pending approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchApprovalSteps = async (requestId: number) => {
    try {
      const response = await fetch(`/api/approval-requests/${requestId}/steps`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setApprovalSteps(data);
      } else {
        console.error('Failed to fetch approval steps:', data.error);
      }
    } catch (error) {
      console.error('Error fetching approval steps:', error);
    }
  };

  const createSampleWorkflows = async () => {
    // Check authentication first
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No authentication token found - please log in first');
      alert('Please log in first to create sample workflows');
      return;
    }

    try {
      const response = await fetch('/api/approval-workflows/create-samples', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      if (response.ok) {
        fetchWorkflows();
        if (data.already_exists) {
          setSuccessMessage(`Sample workflows already exist: ${data.workflows.map((w: any) => w.name).join(', ')}`);
        } else {
          setSuccessMessage(`Successfully created ${data.workflows.length} sample workflows!`);
        }
        setShowSuccessModal(true);
      } else {
        alert(`Failed to create sample workflows: ${data.error}`);
      }
    } catch (error) {
      console.error('Error creating sample workflows:', error);
      alert('Error creating sample workflows');
    }
  };

  const createWorkflow = async () => {
    // Check authentication first
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No authentication token found - please log in first');
      alert('Please log in first to create workflows');
      return;
    }

    try {
      const response = await fetch('/api/approval-workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newWorkflow)
      });
      
      const data = await response.json();
      if (response.ok) {
        setShowCreateWorkflow(false);
        setNewWorkflow({
          workflow_name: '',
          workflow_description: '',
          entity_type: 'deal',
          trigger_conditions: {},
          approval_steps: [],
          is_active: true
        });
        fetchWorkflows();
        setSuccessMessage('Workflow created successfully!');
        setShowSuccessModal(true);
      } else {
        alert(`Failed to create workflow: ${data.error}`);
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      alert('Error creating workflow');
    }
  };

  const handleApprovalAction = async (requestId: number, action: 'approve' | 'reject' | 'delegate') => {
    try {
      const response = await fetch(`/api/approval-requests/${requestId}/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          action,
          comments: approvalComments
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        setShowApprovalModal(false);
        setApprovalComments('');
        fetchPendingApprovals();
        fetchRequests();
        setSuccessMessage(`Request ${action}d successfully`);
        setShowSuccessModal(true);
      } else {
        alert(`Failed to ${action} request: ${data.error}`);
      }
    } catch (error) {
      console.error(`Error ${action}ing request:`, error);
      alert(`Error ${action}ing request`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'cancelled': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getEntityIcon = (entityType: string) => {
    switch (entityType) {
      case 'deal': return <DollarSign className="w-4 h-4" />;
      case 'task': return <CheckCircle className="w-4 h-4" />;
      case 'expense': return <TrendingUp className="w-4 h-4" />;
      case 'lead_qualification': return <Target className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Approval Workflows
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage approval processes for deals, tasks, and other business operations
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.icon}
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Filters */}
        {(activeTab === 'requests' || activeTab === 'my-pending') && (
          <div className="mb-6 flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <select
                value={filterEntityType}
                onChange={(e) => setFilterEntityType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Types</option>
                <option value="deal">Deals</option>
                <option value="task">Tasks</option>
                <option value="expense">Expenses</option>
                <option value="lead_qualification">Lead Qualification</option>
              </select>
            </div>
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Workflows Tab */}
            {activeTab === 'workflows' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Approval Workflows
                  </h2>
                  <div className="flex space-x-3">
                    <button
                      onClick={createSampleWorkflows}
                      className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Create Samples</span>
                    </button>
                    <button
                      onClick={() => setShowCreateWorkflow(true)}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Create Workflow</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {workflows && Array.isArray(workflows) ? workflows.map((workflow) => (
                    <div key={workflow.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          {getEntityIcon(workflow.entity_type)}
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {workflow.workflow_name}
                          </h3>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          workflow.is_active 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                        }`}>
                          {workflow.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      
                      {workflow.workflow_description && (
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                          {workflow.workflow_description}
                        </p>
                      )}
                      
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex justify-between">
                          <span>Entity Type:</span>
                          <span className="capitalize">{workflow.entity_type.replace('_', ' ')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Steps:</span>
                          <span>{workflow.approval_steps.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Created:</span>
                          <span>{formatDate(workflow.created_at)}</span>
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
                      No workflows found
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Requests Tab */}
            {activeTab === 'requests' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  All Approval Requests
                </h2>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Request
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Priority
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Progress
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Requested
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        {requests && Array.isArray(requests) ? requests.map((request) => (
                          <tr key={request.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div>
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                  {request.request_reason}
                                </div>
                                <div className="text-sm text-gray-500 dark:text-gray-400">
                                  ID: {request.id}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center space-x-2">
                                {getEntityIcon(request.entity_type)}
                                <span className="text-sm text-gray-900 dark:text-white capitalize">
                                  {request.entity_type.replace('_', ' ')}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(request.priority)}`}>
                                {request.priority}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(request.status)}`}>
                                {request.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center space-x-2">
                                <div className="w-16 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                                  <div 
                                    className="bg-blue-600 h-2 rounded-full" 
                                    style={{ width: `${(request.current_step / request.total_steps) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                  {request.current_step}/{request.total_steps}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {formatDate(request.requested_at)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <button
                                onClick={() => {
                                  setSelectedRequest(request);
                                  fetchApprovalSteps(request.id);
                                }}
                                className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        )) : (
                          <tr>
                            <td colSpan={7} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                              No requests found
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* My Pending Tab */}
            {activeTab === 'my-pending' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  My Pending Approvals
                </h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {pendingApprovals && Array.isArray(pendingApprovals) ? pendingApprovals.map((request) => (
                    <div key={request.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          {getEntityIcon(request.entity_type)}
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {request.request_reason}
                          </h3>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(request.priority)}`}>
                          {request.priority}
                        </span>
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                        <div className="flex justify-between">
                          <span>Type:</span>
                          <span className="capitalize">{request.entity_type.replace('_', ' ')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Requested by:</span>
                          <span>{request.requester_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Requested:</span>
                          <span>{formatDate(request.requested_at)}</span>
                        </div>
                        {request.due_date && (
                          <div className="flex justify-between">
                            <span>Due:</span>
                            <span className={new Date(request.due_date) < new Date() ? 'text-red-600' : ''}>
                              {formatDate(request.due_date)}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${(request.current_step / request.total_steps) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {request.current_step}/{request.total_steps}
                          </span>
                        </div>
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setApprovalAction('approve');
                              setShowApprovalModal(true);
                            }}
                            className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                          >
                            <Check className="w-3 h-3" />
                            <span>Approve</span>
                          </button>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setApprovalAction('reject');
                              setShowApprovalModal(true);
                            }}
                            className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                          >
                            <X className="w-3 h-3" />
                            <span>Reject</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
                      No pending approvals found
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Approval Settings
                </h2>
                
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <p className="text-gray-600 dark:text-gray-400">
                    Approval workflow settings and configuration options will be available here.
                  </p>
                </div>
              </div>
            )}
          </>
        )}

        {/* Create Workflow Modal */}
        {showCreateWorkflow && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Create New Approval Workflow
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Workflow Name
                  </label>
                  <input
                    type="text"
                    value={newWorkflow.workflow_name}
                    onChange={(e) => setNewWorkflow({...newWorkflow, workflow_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Enter workflow name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newWorkflow.workflow_description}
                    onChange={(e) => setNewWorkflow({...newWorkflow, workflow_description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Enter workflow description"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Entity Type
                  </label>
                  <select
                    value={newWorkflow.entity_type}
                    onChange={(e) => setNewWorkflow({...newWorkflow, entity_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="deal">Deal</option>
                    <option value="task">Task</option>
                    <option value="expense">Expense</option>
                    <option value="lead_qualification">Lead Qualification</option>
                  </select>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={newWorkflow.is_active}
                    onChange={(e) => setNewWorkflow({...newWorkflow, is_active: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    Active
                  </label>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowCreateWorkflow(false);
                    setNewWorkflow({
                      workflow_name: '',
                      workflow_description: '',
                      entity_type: 'deal',
                      trigger_conditions: {},
                      approval_steps: [],
                      is_active: true
                    });
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={createWorkflow}
                  disabled={!newWorkflow.workflow_name.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Create Workflow
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Approval Modal */}
        {showApprovalModal && selectedRequest && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                {approvalAction === 'approve' ? 'Approve Request' : 'Reject Request'}
              </h3>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Request: {selectedRequest.request_reason}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Type: {selectedRequest.entity_type.replace('_', ' ')}
                </p>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Comments (optional)
                </label>
                <textarea
                  value={approvalComments}
                  onChange={(e) => setApprovalComments(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Add comments for this approval..."
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowApprovalModal(false);
                    setApprovalComments('');
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleApprovalAction(selectedRequest.id, approvalAction)}
                  className={`px-4 py-2 text-white rounded-md transition-colors ${
                    approvalAction === 'approve'
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {approvalAction === 'approve' ? 'Approve' : 'Reject'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Success Modal */}
      <AnimatedModal
        open={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title="Success"
        animationType="scale"
        size="sm"
      >
        <div className="text-center space-y-4">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 dark:bg-green-900">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-lg text-gray-900 dark:text-white">
            {successMessage}
          </p>
          <button
            onClick={() => setShowSuccessModal(false)}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
          >
            OK
          </button>
        </div>
      </AnimatedModal>
    </div>
  );
};

export default ApprovalWorkflows;
