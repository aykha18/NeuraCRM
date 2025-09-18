import React, { useState, useEffect } from 'react';
import { TrendingUp, MessageSquare, Ticket, Activity, BarChart3, Users, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { apiRequest } from '../utils/api';

interface SentimentData {
  overall_score: number;
  overall_label: string;
  support_tickets: {
    count: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  chat_messages: {
    count: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  activities: {
    count: number;
    positive: number;
    negative: number;
    neutral: number;
  };
}

interface TicketSentiment {
  ticket_id: number;
  ticket_number: string;
  title: string;
  description: string;
  sentiment_score: number;
  sentiment_label: string;
  status: string;
  created_at: string;
}

interface ChatSentiment {
  message_id: number;
  room_id: number;
  room_name: string;
  content: string;
  sentiment_score: number;
  sentiment_label: string;
  sender_id: number;
  created_at: string;
}

interface ActivitySentiment {
  activity_id: number;
  type: string;
  message: string;
  sentiment_score: number;
  sentiment_label: string;
  user_id: number;
  deal_id?: number;
  created_at: string;
}

const SentimentAnalysis: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'tickets' | 'chats' | 'activities'>('overview');
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [ticketSentiments, setTicketSentiments] = useState<TicketSentiment[]>([]);
  const [chatSentiments, setChatSentiments] = useState<ChatSentiment[]>([]);
  const [activitySentiments, setActivitySentiments] = useState<ActivitySentiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSentimentData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch overview data
      const overviewResponse = await apiRequest<any>('/api/sentiment-analysis/overview', {
        method: 'GET',
      });
      
      // Check if response contains an error
      if (overviewResponse.error) {
        throw new Error(overviewResponse.error);
      }
      
      setSentimentData(overviewResponse as SentimentData);

      // Fetch detailed data based on active tab
      if (activeTab === 'tickets') {
        const ticketsResponse = await apiRequest<{tickets: TicketSentiment[]}>('/api/sentiment-analysis/support-tickets', {
          method: 'GET',
        });
        setTicketSentiments(ticketsResponse.tickets || []);
      } else if (activeTab === 'chats') {
        const chatsResponse = await apiRequest<{messages: ChatSentiment[]}>('/api/sentiment-analysis/chat-messages', {
          method: 'GET',
        });
        setChatSentiments(chatsResponse.messages || []);
      } else if (activeTab === 'activities') {
        const activitiesResponse = await apiRequest<{activities: ActivitySentiment[]}>('/api/sentiment-analysis/activities', {
          method: 'GET',
        });
        setActivitySentiments(activitiesResponse.activities || []);
      }
    } catch (err) {
      console.error('Error fetching sentiment data:', err);
      setError('Failed to fetch sentiment analysis data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentimentData();
  }, [activeTab]);

  const getSentimentColor = (label: string) => {
    switch (label) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getSentimentEmoji = (label: string) => {
    switch (label) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '😐';
    }
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case 'positive': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'negative': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'neutral': return <AlertTriangle className="w-5 h-5 text-gray-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-500" />;
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

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Chart data for overview
  const chartData = sentimentData ? [
    {
      category: 'Support Tickets',
      positive: sentimentData.support_tickets?.positive || 0,
      negative: sentimentData.support_tickets?.negative || 0,
      neutral: sentimentData.support_tickets?.neutral || 0,
    },
    {
      category: 'Chat Messages',
      positive: sentimentData.chat_messages?.positive || 0,
      negative: sentimentData.chat_messages?.negative || 0,
      neutral: sentimentData.chat_messages?.neutral || 0,
    },
    {
      category: 'Activities',
      positive: sentimentData.activities?.positive || 0,
      negative: sentimentData.activities?.negative || 0,
      neutral: sentimentData.activities?.neutral || 0,
    },
  ] : [];

  const pieData = sentimentData ? [
    { name: 'Positive', value: (sentimentData.support_tickets?.positive || 0) + (sentimentData.chat_messages?.positive || 0) + (sentimentData.activities?.positive || 0), color: '#10b981' },
    { name: 'Negative', value: (sentimentData.support_tickets?.negative || 0) + (sentimentData.chat_messages?.negative || 0) + (sentimentData.activities?.negative || 0), color: '#ef4444' },
    { name: 'Neutral', value: (sentimentData.support_tickets?.neutral || 0) + (sentimentData.chat_messages?.neutral || 0) + (sentimentData.activities?.neutral || 0), color: '#6b7280' },
  ] : [];

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center mb-2">
          <TrendingUp className="w-8 h-8 text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Sentiment Analysis</h1>
        </div>
        <p className="text-gray-600">Analyze customer sentiment across support tickets, chats, and activities</p>
      </div>

      {/* Overall Sentiment Score */}
      {sentimentData && (
        <div className="mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Sentiment</h3>
                <div className="flex items-center">
                  <span className="text-4xl font-bold mr-3">{getSentimentEmoji(sentimentData.overall_label)}</span>
                  <div>
                    <div className="text-2xl font-bold" style={{ color: getSentimentColor(sentimentData.overall_label) }}>
                      {sentimentData.overall_label.toUpperCase()}
                    </div>
                    <div className="text-sm text-gray-600">
                      Score: {sentimentData.overall_score.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600 mb-1">Total Interactions</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(sentimentData.support_tickets?.count || 0) + (sentimentData.chat_messages?.count || 0) + (sentimentData.activities?.count || 0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
              { id: 'tickets', label: 'Support Tickets', icon: <Ticket className="w-4 h-4" /> },
              { id: 'chats', label: 'Chat Messages', icon: <MessageSquare className="w-4 h-4" /> },
              { id: 'activities', label: 'Activities', icon: <Activity className="w-4 h-4" /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                <span className="ml-2">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && sentimentData && (
        <div className="space-y-6">
          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bar Chart */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="positive" stackId="a" fill="#10b981" name="Positive" />
                  <Bar dataKey="neutral" stackId="a" fill="#6b7280" name="Neutral" />
                  <Bar dataKey="negative" stackId="a" fill="#ef4444" name="Negative" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Sentiment Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <Ticket className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">Support Tickets</h4>
                  <div className="text-sm text-gray-600">
                    {sentimentData.support_tickets?.positive || 0} positive, {sentimentData.support_tickets?.negative || 0} negative, {sentimentData.support_tickets?.neutral || 0} neutral
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <MessageSquare className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">Chat Messages</h4>
                  <div className="text-sm text-gray-600">
                    {sentimentData.chat_messages?.positive || 0} positive, {sentimentData.chat_messages?.negative || 0} negative, {sentimentData.chat_messages?.neutral || 0} neutral
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <Activity className="w-8 h-8 text-purple-600 mr-3" />
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">Activities</h4>
                  <div className="text-sm text-gray-600">
                    {sentimentData.activities?.positive || 0} positive, {sentimentData.activities?.negative || 0} negative, {sentimentData.activities?.neutral || 0} neutral
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Support Tickets Tab */}
      {activeTab === 'tickets' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Support Ticket Sentiment Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">Detailed sentiment analysis for support tickets</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticket</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ticketSentiments.map((ticket) => (
                  <tr key={ticket.ticket_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{ticket.ticket_number}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        <div className="font-medium">{ticket.title}</div>
                        <div className="text-gray-500 text-xs mt-1">
                          {truncateText(ticket.description, 80)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getSentimentIcon(ticket.sentiment_label)}
                        <span className="ml-2 text-sm font-medium" style={{ color: getSentimentColor(ticket.sentiment_label) }}>
                          {ticket.sentiment_label}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          ({ticket.sentiment_score.toFixed(2)})
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        ticket.status === 'open' ? 'bg-green-100 text-green-800' :
                        ticket.status === 'closed' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {ticket.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(ticket.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Chat Messages Tab */}
      {activeTab === 'chats' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Chat Message Sentiment Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">Detailed sentiment analysis for chat messages</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Room</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {chatSentiments.map((message) => (
                  <tr key={message.message_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {message.room_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        {truncateText(message.content, 100)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getSentimentIcon(message.sentiment_label)}
                        <span className="ml-2 text-sm font-medium" style={{ color: getSentimentColor(message.sentiment_label) }}>
                          {message.sentiment_label}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          ({message.sentiment_score.toFixed(2)})
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(message.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Activities Tab */}
      {activeTab === 'activities' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Activity Sentiment Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">Detailed sentiment analysis for activities</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activitySentiments.map((activity) => (
                  <tr key={activity.activity_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {activity.type}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        {truncateText(activity.message, 100)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getSentimentIcon(activity.sentiment_label)}
                        <span className="ml-2 text-sm font-medium" style={{ color: getSentimentColor(activity.sentiment_label) }}>
                          {activity.sentiment_label}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          ({activity.sentiment_score.toFixed(2)})
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(activity.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SentimentAnalysis;
