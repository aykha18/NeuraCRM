import React, { useState, useEffect } from 'react';
import { apiRequest } from '../utils/api';
import { PlusIcon, PencilIcon, TrashIcon, PlayIcon } from '@heroicons/react/24/outline';

interface LeadAssignmentRule {
  id: number;
  rule_name: string;
  rule_description?: string;
  criteria: Record<string, any>;
  assignment_type: 'user' | 'round_robin' | 'team';
  assigned_user_id?: number;
  assigned_team_id?: number;
  priority: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: number;
}

interface User {
  id: number;
  name: string;
  email: string;
}

const LeadAssignmentRules: React.FC = () => {
  const [rules, setRules] = useState<LeadAssignmentRule[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRule, setEditingRule] = useState<LeadAssignmentRule | null>(null);
  const [formData, setFormData] = useState({
    rule_name: '',
    rule_description: '',
    criteria: {
      source: '',
      priority: '',
      location: '',
      industry: ''
    },
    assignment_type: 'user' as 'user' | 'round_robin' | 'team',
    assigned_user_id: 0,
    priority: 1,
    is_active: true
  });

  useEffect(() => {
    fetchRules();
    fetchUsers();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await apiRequest<LeadAssignmentRule[]>('/api/lead-assignment-rules', 'GET');
      setRules(response);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching rules:', error);
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await apiRequest<User[]>('/api/users', 'GET');
      setUsers(response);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        assigned_user_id: formData.assignment_type === 'user' ? formData.assigned_user_id : undefined,
        assigned_team_id: formData.assignment_type === 'team' ? formData.assigned_user_id : undefined
      };

      if (editingRule) {
        await apiRequest(`/api/lead-assignment-rules/${editingRule.id}`, 'PUT', payload);
      } else {
        await apiRequest('/api/lead-assignment-rules', 'POST', payload);
      }

      setShowCreateForm(false);
      setEditingRule(null);
      resetForm();
      fetchRules();
    } catch (error) {
      console.error('Error saving rule:', error);
      alert('Error saving rule. Please try again.');
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    
    try {
      await apiRequest(`/api/lead-assignment-rules/${ruleId}`, 'DELETE');
      fetchRules();
    } catch (error) {
      console.error('Error deleting rule:', error);
      alert('Error deleting rule. Please try again.');
    }
  };

  const handleEditRule = (rule: LeadAssignmentRule) => {
    setEditingRule(rule);
    setFormData({
      rule_name: rule.rule_name,
      rule_description: rule.rule_description || '',
      criteria: {
        source: rule.criteria?.source || '',
        priority: rule.criteria?.priority || '',
        location: rule.criteria?.location || '',
        industry: rule.criteria?.industry || ''
      },
      assignment_type: rule.assignment_type,
      assigned_user_id: rule.assigned_user_id || 0,
      priority: rule.priority,
      is_active: rule.is_active
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setFormData({
      rule_name: '',
      rule_description: '',
      criteria: {
        source: '',
        priority: '',
        location: '',
        industry: ''
      },
      assignment_type: 'user',
      assigned_user_id: 0,
      priority: 1,
      is_active: true
    });
  };

  const handleCriteriaChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      criteria: {
        ...prev.criteria,
        [key]: value
      }
    }));
  };

  const getAssignmentDisplay = (rule: LeadAssignmentRule) => {
    switch (rule.assignment_type) {
      case 'user':
        const user = users.find(u => u.id === rule.assigned_user_id);
        return user ? user.name : `User ID: ${rule.assigned_user_id}`;
      case 'round_robin':
        return 'Round Robin';
      case 'team':
        return `Team ID: ${rule.assigned_team_id}`;
      default:
        return 'Unknown';
    }
  };

  const getCriteriaDisplay = (criteria: Record<string, any>) => {
    return Object.entries(criteria)
      .filter(([_, value]) => value && value !== '')
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ') || 'No criteria';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Lead Assignment Rules</h1>
          <p className="text-gray-600 mt-2">Automatically assign leads based on predefined criteria</p>
        </div>
        <button
          onClick={() => {
            setEditingRule(null);
            resetForm();
            setShowCreateForm(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          Create Rule
        </button>
      </div>

      {/* Create/Edit Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingRule ? 'Edit Rule' : 'Create New Rule'}
            </h2>
            
            <form onSubmit={handleCreateRule} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rule Name *
                  </label>
                  <input
                    type="text"
                    value={formData.rule_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, rule_name: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority *
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.priority}
                    onChange={(e) => setFormData(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Lower numbers = higher priority</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.rule_description}
                  onChange={(e) => setFormData(prev => ({ ...prev, rule_description: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>

              {/* Criteria Section */}
              <div className="border-t pt-4">
                <h3 className="text-lg font-medium mb-3">Assignment Criteria</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Lead Source
                    </label>
                    <select
                      value={formData.criteria.source}
                      onChange={(e) => handleCriteriaChange('source', e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Any</option>
                      <option value="website">Website</option>
                      <option value="referral">Referral</option>
                      <option value="email">Email</option>
                      <option value="phone">Phone</option>
                      <option value="social">Social Media</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Priority Level
                    </label>
                    <select
                      value={formData.criteria.priority}
                      onChange={(e) => handleCriteriaChange('priority', e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Any</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location
                    </label>
                    <input
                      type="text"
                      value={formData.criteria.location}
                      onChange={(e) => handleCriteriaChange('location', e.target.value)}
                      placeholder="e.g., Dubai, UAE"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Industry
                    </label>
                    <input
                      type="text"
                      value={formData.criteria.industry}
                      onChange={(e) => handleCriteriaChange('industry', e.target.value)}
                      placeholder="e.g., Technology, Healthcare"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Assignment Type */}
              <div className="border-t pt-4">
                <h3 className="text-lg font-medium mb-3">Assignment Method</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assignment Type *
                  </label>
                  <select
                    value={formData.assignment_type}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      assignment_type: e.target.value as 'user' | 'round_robin' | 'team',
                      assigned_user_id: e.target.value === 'round_robin' ? 0 : prev.assigned_user_id
                    }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="user">Assign to Specific User</option>
                    <option value="round_robin">Round Robin Distribution</option>
                    <option value="team">Assign to Team</option>
                  </select>
                </div>

                {formData.assignment_type === 'user' && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Assign to User *
                    </label>
                    <select
                      value={formData.assigned_user_id}
                      onChange={(e) => setFormData(prev => ({ ...prev, assigned_user_id: parseInt(e.target.value) }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value={0}>Select User</option>
                      {users.map(user => (
                        <option key={user.id} value={user.id}>
                          {user.name} ({user.email})
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Active (Rule will be applied to new leads)
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setEditingRule(null);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingRule ? 'Update Rule' : 'Create Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Rules List */}
      <div className="bg-white rounded-lg shadow">
        {rules.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📋</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No assignment rules yet</h3>
            <p className="text-gray-600 mb-4">Create your first rule to automatically assign leads</p>
            <button
              onClick={() => {
                setEditingRule(null);
                resetForm();
                setShowCreateForm(true);
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Create Your First Rule
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rule
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Criteria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assignment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {rule.rule_name}
                        </div>
                        {rule.rule_description && (
                          <div className="text-sm text-gray-500">
                            {rule.rule_description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {getCriteriaDisplay(rule.criteria)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {getAssignmentDisplay(rule)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {rule.assignment_type.replace('_', ' ')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Priority {rule.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        rule.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEditRule(rule)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">How Lead Assignment Rules Work</h3>
        <div className="text-blue-800 space-y-2">
          <p>• Rules are processed in priority order (1 = highest priority)</p>
          <p>• When a new lead is created, the system checks all active rules</p>
          <p>• The first rule whose criteria match the lead will assign it</p>
          <p>• Use specific criteria (source, priority, location) to target the right leads</p>
          <p>• Round-robin assignment distributes leads evenly among available users</p>
        </div>
      </div>
    </div>
  );
};

export default LeadAssignmentRules;
