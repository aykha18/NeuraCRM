import React, { useState, useEffect } from 'react';
import { 
  Ticket, 
  MessageSquare, 
  BookOpen, 
  BarChart3, 
  Plus, 
  Search, 
  Filter, 
  Clock, 
  User, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  Star,
  TrendingUp,
  Users,
  MessageCircle,
  FileText,
  Calendar,
  Tag,
  Eye,
  Edit,
  Trash2,
  Send,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  Settings,
  Bell,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import AnimatedModal from '../components/AnimatedModal';
import { apiRequest } from '../utils/api';

interface SupportTicket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent' | 'critical';
  status: 'open' | 'in_progress' | 'pending_customer' | 'resolved' | 'closed' | 'cancelled';
  category: string;
  subcategory?: string;
  customer_name: string;
  customer_email: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  sla_deadline?: string;
  first_response_at?: string;
  resolution_deadline?: string;
  escalated: boolean;
  escalated_at?: string;
  satisfaction_rating?: number;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  closed_at?: string;
  comments?: SupportComment[];
}

interface SupportComment {
  id: number;
  author_name: string;
  author_email: string;
  author_type: 'agent' | 'customer' | 'system';
  content: string;
  is_internal: boolean;
  comment_type: string;
  created_at: string;
}

interface KnowledgeBaseArticle {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  category: string;
  subcategory?: string;
  tags: string[];
  status: 'draft' | 'published' | 'archived';
  visibility: 'public' | 'internal' | 'customer_only';
  featured: boolean;
  view_count: number;
  helpful_count: number;
  not_helpful_count: number;
  author_name?: string;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

interface SupportAnalytics {
  ticket_metrics: {
    total_tickets: number;
    open_tickets: number;
    resolved_tickets: number;
    closed_tickets: number;
    resolution_rate: number;
  };
  response_metrics: {
    avg_first_response_time: number;
    avg_resolution_time: number;
    sla_breach_count: number;
    sla_compliance_rate: number;
  };
  satisfaction_metrics: {
    avg_satisfaction_rating: number;
    nps_score: number;
    survey_count: number;
  };
  breakdown: {
    tickets_by_category: Record<string, number>;
    tickets_by_priority: Record<string, number>;
  };
}

const CustomerSupport: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tickets' | 'knowledge' | 'analytics' | 'surveys'>('tickets');
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [filteredTickets, setFilteredTickets] = useState<SupportTicket[]>([]);
  const [knowledgeArticles, setKnowledgeArticles] = useState<KnowledgeBaseArticle[]>([]);
  const [analytics, setAnalytics] = useState<SupportAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  // Modals
  const [showCreateTicketModal, setShowCreateTicketModal] = useState(false);
  const [showTicketDetailsModal, setShowTicketDetailsModal] = useState(false);
  const [showCreateArticleModal, setShowCreateArticleModal] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [agents, setAgents] = useState<any[]>([]);
  const [assignmentForm, setAssignmentForm] = useState({
    assigned_to_id: '',
    reason: '',
    type: 'manual'
  });
  const [escalationForm, setEscalationForm] = useState({
    reason: '',
    escalated_to_id: ''
  });
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Forms
  const [ticketForm, setTicketForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: 'general',
    subcategory: '',
    customer_name: '',
    customer_email: '',
    assigned_to_id: ''
  });

  const [articleForm, setArticleForm] = useState({
    title: '',
    content: '',
    summary: '',
    category: 'general',
    subcategory: '',
    tags: [] as string[],
    status: 'draft',
    visibility: 'public',
    featured: false,
    meta_description: ''
  });

  const [commentForm, setCommentForm] = useState({
    content: '',
    is_internal: false
  });

  useEffect(() => {
    fetchTickets();
    fetchKnowledgeArticles();
    fetchAnalytics();
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await apiRequest('/api/support/agents') as any;
      if (response && !response.error) {
        setAgents(response);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const assignTicket = async () => {
    if (!selectedTicket) return;
    
    try {
      const response = await apiRequest(`/api/support/tickets/${selectedTicket.id}/assign`, {
        method: 'PATCH',
        body: JSON.stringify(assignmentForm)
      }) as any;
      
      if (response && !response.error) {
        setShowAssignmentModal(false);
        setAssignmentForm({ assigned_to_id: '', reason: '', type: 'manual' });
        fetchTickets(); // Refresh tickets
        setShowSuccessModal(true);
        setSuccessMessage('Ticket assigned successfully');
      } else {
        setShowErrorModal(true);
        setErrorMessage(response?.error || 'Failed to assign ticket');
      }
    } catch (error) {
      setShowErrorModal(true);
      setErrorMessage('Failed to assign ticket');
    }
  };

  const autoAssignTicket = async (ticketId: number) => {
    try {
      const response = await apiRequest(`/api/support/tickets/${ticketId}/auto-assign`, {
        method: 'POST'
      }) as any;
      
      if (response && !response.error) {
        fetchTickets(); // Refresh tickets
        setShowSuccessModal(true);
        setSuccessMessage('Ticket auto-assigned successfully');
      } else {
        setShowErrorModal(true);
        setErrorMessage(response?.error || 'Failed to auto-assign ticket');
      }
    } catch (error) {
      setShowErrorModal(true);
      setErrorMessage('Failed to auto-assign ticket');
    }
  };

  const escalateTicket = async () => {
    if (!selectedTicket) return;
    
    try {
      const response = await apiRequest(`/api/support/tickets/${selectedTicket.id}/escalate`, {
        method: 'POST',
        body: JSON.stringify(escalationForm)
      }) as any;
      
      if (response && !response.error) {
        setShowEscalationModal(false);
        setEscalationForm({ reason: '', escalated_to_id: '' });
        fetchTickets(); // Refresh tickets
        setShowSuccessModal(true);
        setSuccessMessage('Ticket escalated successfully');
      } else {
        setShowErrorModal(true);
        setErrorMessage(response?.error || 'Failed to escalate ticket');
      }
    } catch (error) {
      setShowErrorModal(true);
      setErrorMessage('Failed to escalate ticket');
    }
  };

  useEffect(() => {
    filterTickets();
  }, [tickets, statusFilter, priorityFilter, categoryFilter, searchTerm]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/support/tickets') as SupportTicket[];
      if (Array.isArray(data)) {
        setTickets(data);
      }
    } catch (err) {
      console.error('Error fetching tickets:', err);
      setError('Failed to fetch support tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchKnowledgeArticles = async () => {
    try {
      const data = await apiRequest('/api/support/knowledge-base') as KnowledgeBaseArticle[];
      if (Array.isArray(data)) {
        setKnowledgeArticles(data);
      }
    } catch (err) {
      console.error('Error fetching knowledge articles:', err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const data = await apiRequest('/api/support/analytics/dashboard') as SupportAnalytics;
      setAnalytics(data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };

  const filterTickets = () => {
    let filtered = tickets;

    if (statusFilter) {
      filtered = filtered.filter(ticket => ticket.status === statusFilter);
    }
    if (priorityFilter) {
      filtered = filtered.filter(ticket => ticket.priority === priorityFilter);
    }
    if (categoryFilter) {
      filtered = filtered.filter(ticket => ticket.category === categoryFilter);
    }
    if (searchTerm) {
      filtered = filtered.filter(ticket =>
        ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.ticket_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredTickets(filtered);
  };

  const createTicket = async () => {
    try {
      setLoading(true);
      const response = await apiRequest('/api/support/tickets', {
        method: 'POST',
        body: JSON.stringify(ticketForm)
      });

      setError(null);
      setSuccessMessage('Support ticket created successfully!');
      setShowSuccessModal(true);
      setShowCreateTicketModal(false);
      setTicketForm({
        title: '',
        description: '',
        priority: 'medium',
        category: 'general',
        subcategory: '',
        customer_name: '',
        customer_email: '',
        assigned_to_id: ''
      });
      fetchTickets();
    } catch (err) {
      console.error('Error creating ticket:', err);
      setError('Failed to create support ticket');
    } finally {
      setLoading(false);
    }
  };

  const createArticle = async () => {
    try {
      setLoading(true);
      const response = await apiRequest('/api/support/knowledge-base', {
        method: 'POST',
        body: JSON.stringify(articleForm)
      });

      setError(null);
      setSuccessMessage('Knowledge base article created successfully!');
      setShowSuccessModal(true);
      setShowCreateArticleModal(false);
      setArticleForm({
        title: '',
        content: '',
        summary: '',
        category: 'general',
        subcategory: '',
        tags: [],
        status: 'draft',
        visibility: 'public',
        featured: false,
        meta_description: ''
      });
      fetchKnowledgeArticles();
    } catch (err) {
      console.error('Error creating article:', err);
      setError('Failed to create knowledge base article');
    } finally {
      setLoading(false);
    }
  };

  const addComment = async (ticketId: number) => {
    try {
      setLoading(true);
      const response = await apiRequest(`/api/support/tickets/${ticketId}/comments`, {
        method: 'POST',
        body: JSON.stringify(commentForm)
      });

      setError(null);
      setSuccessMessage('Comment added successfully!');
      setShowSuccessModal(true);
      setCommentForm({ content: '', is_internal: false });
      fetchTickets();
    } catch (err) {
      console.error('Error adding comment:', err);
      setError('Failed to add comment');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      case 'urgent': return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900';
      case 'high': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
      case 'medium': return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900';
      case 'low': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900';
      case 'in_progress': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
      case 'pending_customer': return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900';
      case 'resolved': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      case 'closed': return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
      case 'cancelled': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
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

  const renderTicketsTab = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Support Tickets</h2>
          <p className="text-gray-600 dark:text-gray-400">Manage customer support requests</p>
        </div>
        <button
          data-testid="cs-create-ticket"
          onClick={() => setShowCreateTicketModal(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Create Ticket</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="pending_customer">Pending Customer</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Priority
            </label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Category
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Categories</option>
              <option value="technical">Technical</option>
              <option value="billing">Billing</option>
              <option value="feature_request">Feature Request</option>
              <option value="bug_report">Bug Report</option>
              <option value="general">General</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tickets List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700" data-testid="cs-ticket-list">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600 dark:text-gray-400">Loading tickets...</p>
          </div>
        ) : filteredTickets.length === 0 ? (
          <div className="p-8 text-center">
            <Ticket className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No tickets found</h3>
            <p className="text-gray-600 dark:text-gray-400">Create your first support ticket to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Ticket
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {ticket.ticket_number}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 truncate max-w-xs">
                          {ticket.title}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {ticket.customer_name}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {ticket.customer_email}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(ticket.status)}`}>
                        {ticket.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {ticket.assigned_to_name || 'Unassigned'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(ticket.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSelectedTicket(ticket);
                            setShowTicketDetailsModal(true);
                          }}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          View
                        </button>
                        {!ticket.assigned_to_id && (
                          <button
                            onClick={() => {
                              setSelectedTicket(ticket);
                              setShowAssignmentModal(true);
                            }}
                            className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                          >
                            Assign
                          </button>
                        )}
                        <button
                          onClick={() => autoAssignTicket(ticket.id)}
                          className="text-purple-600 hover:text-purple-900 dark:text-purple-400 dark:hover:text-purple-300"
                        >
                          Auto
                        </button>
                        <button
                          onClick={() => {
                            setSelectedTicket(ticket);
                            setShowEscalationModal(true);
                          }}
                          className="text-orange-600 hover:text-orange-900 dark:text-orange-400 dark:hover:text-orange-300"
                        >
                          Escalate
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
    </div>
  );

  const renderKnowledgeTab = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Knowledge Base</h2>
          <p className="text-gray-600 dark:text-gray-400">Manage help articles and documentation</p>
        </div>
        <button
          onClick={() => setShowCreateArticleModal(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Create Article</span>
        </button>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {knowledgeArticles.map((article) => (
          <div key={article.id} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {article.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {article.summary}
                </p>
              </div>
              {article.featured && (
                <Star className="w-5 h-5 text-yellow-500 flex-shrink-0 ml-2" />
              )}
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                {article.category}
              </span>
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <Eye className="w-4 h-4 mr-1" />
                  {article.view_count}
                </span>
                <span className="flex items-center">
                  <ThumbsUp className="w-4 h-4 mr-1" />
                  {article.helpful_count}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className={`text-xs px-2 py-1 rounded-full ${
                article.status === 'published' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              }`}>
                {article.status}
              </span>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Support Analytics</h2>
        <p className="text-gray-600 dark:text-gray-400">Track support performance and metrics</p>
      </div>

      {analytics ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <Ticket className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tickets</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analytics.ticket_metrics.total_tickets}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Resolution Rate</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analytics.ticket_metrics.resolution_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analytics.response_metrics.avg_first_response_time.toFixed(1)}h
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <Star className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Satisfaction</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {analytics.satisfaction_metrics.avg_satisfaction_rating.toFixed(1)}/5
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tickets by Category</h3>
              <div className="space-y-3">
                {Object.entries(analytics.breakdown.tickets_by_category).map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                      {category.replace('_', ' ')}
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tickets by Priority</h3>
              <div className="space-y-3">
                {Object.entries(analytics.breakdown.tickets_by_priority).map(([priority, count]) => (
                  <div key={priority} className="flex items-center justify-between">
                    <span className={`text-sm px-2 py-1 rounded-full ${getPriorityColor(priority)}`}>
                      {priority}
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-8">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Customer Support</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage tickets, knowledge base, and support analytics
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'tickets', label: 'Tickets', icon: Ticket },
                { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
                { id: 'surveys', label: 'Surveys', icon: MessageSquare }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        {activeTab === 'tickets' && renderTicketsTab()}
        {activeTab === 'knowledge' && renderKnowledgeTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
        {activeTab === 'surveys' && (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Surveys</h3>
            <p className="text-gray-600 dark:text-gray-400">Customer satisfaction surveys coming soon.</p>
          </div>
        )}

        {/* Create Ticket Modal */}
        <AnimatedModal
          open={showCreateTicketModal}
          onClose={() => setShowCreateTicketModal(false)}
          title="Create Support Ticket"
          animationType="scale"
          size="lg"
        >
          <div className="space-y-4" data-testid="cs-ticket-modal">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Title
              </label>
              <input
                data-testid="cs-title"
                type="text"
                value={ticketForm.title}
                onChange={(e) => setTicketForm({ ...ticketForm, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Brief description of the issue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                data-testid="cs-description"
                value={ticketForm.description}
                onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Detailed description of the issue"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority
                </label>
                <select
                  data-testid="cs-priority"
                  value={ticketForm.priority}
                  onChange={(e) => setTicketForm({ ...ticketForm, priority: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category
                </label>
                <select
                  data-testid="cs-category"
                  value={ticketForm.category}
                  onChange={(e) => setTicketForm({ ...ticketForm, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="technical">Technical</option>
                  <option value="billing">Billing</option>
                  <option value="feature_request">Feature Request</option>
                  <option value="bug_report">Bug Report</option>
                  <option value="general">General</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Customer Name
                </label>
              <input
                data-testid="cs-customer-name"
                  type="text"
                  value={ticketForm.customer_name}
                  onChange={(e) => setTicketForm({ ...ticketForm, customer_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Customer name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Customer Email
                </label>
              <input
                data-testid="cs-customer-email"
                  type="email"
                  value={ticketForm.customer_email}
                  onChange={(e) => setTicketForm({ ...ticketForm, customer_email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="customer@example.com"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={() => setShowCreateTicketModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createTicket}
                disabled={loading || !ticketForm.title || !ticketForm.description || !ticketForm.customer_name || !ticketForm.customer_email}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {loading ? 'Creating...' : 'Create Ticket'}
              </button>
            </div>
          </div>
        </AnimatedModal>

        {/* Create Article Modal */}
        <AnimatedModal
          open={showCreateArticleModal}
          onClose={() => setShowCreateArticleModal(false)}
          title="Create Knowledge Base Article"
          animationType="scale"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Title
              </label>
              <input
                type="text"
                value={articleForm.title}
                onChange={(e) => setArticleForm({ ...articleForm, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Article title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Summary
              </label>
              <textarea
                value={articleForm.summary}
                onChange={(e) => setArticleForm({ ...articleForm, summary: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Brief summary of the article"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Content
              </label>
              <textarea
                value={articleForm.content}
                onChange={(e) => setArticleForm({ ...articleForm, content: e.target.value })}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Article content (markdown supported)"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category
                </label>
                <select
                  value={articleForm.category}
                  onChange={(e) => setArticleForm({ ...articleForm, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="getting_started">Getting Started</option>
                  <option value="troubleshooting">Troubleshooting</option>
                  <option value="billing">Billing</option>
                  <option value="features">Features</option>
                  <option value="general">General</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={articleForm.status}
                  onChange={(e) => setArticleForm({ ...articleForm, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="featured"
                checked={articleForm.featured}
                onChange={(e) => setArticleForm({ ...articleForm, featured: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="featured" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Featured article
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={() => setShowCreateArticleModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createArticle}
                disabled={loading || !articleForm.title || !articleForm.content}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {loading ? 'Creating...' : 'Create Article'}
              </button>
            </div>
          </div>
        </AnimatedModal>

        {/* Assignment Modal */}
        <AnimatedModal
          open={showAssignmentModal}
          onClose={() => setShowAssignmentModal(false)}
          title="Assign Ticket"
          animationType="scale"
          size="md"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Assign to Agent
              </label>
              <select
                value={assignmentForm.assigned_to_id}
                onChange={(e) => setAssignmentForm({ ...assignmentForm, assigned_to_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select an agent</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.role}) - {agent.workload} tickets
                    {agent.skills.length > 0 && ` - Skills: ${agent.skills.map((s: any) => s.name).join(', ')}`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Assignment Reason
              </label>
              <textarea
                value={assignmentForm.reason}
                onChange={(e) => setAssignmentForm({ ...assignmentForm, reason: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Why is this ticket being assigned to this agent?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Assignment Type
              </label>
              <select
                value={assignmentForm.type}
                onChange={(e) => setAssignmentForm({ ...assignmentForm, type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="manual">Manual Assignment</option>
                <option value="skills_based">Skills-Based</option>
                <option value="escalation">Escalation</option>
              </select>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowAssignmentModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={assignTicket}
                disabled={!assignmentForm.assigned_to_id || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Assigning...' : 'Assign Ticket'}
              </button>
            </div>
          </div>
        </AnimatedModal>

        {/* Escalation Modal */}
        <AnimatedModal
          open={showEscalationModal}
          onClose={() => setShowEscalationModal(false)}
          title="Escalate Ticket"
          animationType="scale"
          size="md"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Escalation Reason *
              </label>
              <textarea
                value={escalationForm.reason}
                onChange={(e) => setEscalationForm({ ...escalationForm, reason: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Why is this ticket being escalated?"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Escalate to Agent (Optional)
              </label>
              <select
                value={escalationForm.escalated_to_id}
                onChange={(e) => setEscalationForm({ ...escalationForm, escalated_to_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Auto-assign to senior agent</option>
                {agents.filter(agent => agent.role === 'manager' || agent.role === 'admin').map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.role}) - {agent.workload} tickets
                  </option>
                ))}
              </select>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowEscalationModal(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={escalateTicket}
                disabled={!escalationForm.reason || loading}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Escalating...' : 'Escalate Ticket'}
              </button>
            </div>
          </div>
        </AnimatedModal>

        {/* Success Modal */}
        <AnimatedModal
          open={showSuccessModal}
          onClose={() => setShowSuccessModal(false)}
          title="Success!"
          animationType="scale"
          size="sm"
        >
          <div className="text-center">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">{successMessage}</p>
          </div>
        </AnimatedModal>

        {/* Error Modal */}
        <AnimatedModal
          open={showErrorModal}
          onClose={() => setShowErrorModal(false)}
          title="Error"
          animationType="scale"
          size="sm"
        >
          <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">{errorMessage}</p>
          </div>
        </AnimatedModal>
      </div>
    </div>
  );
};

export default CustomerSupport;
