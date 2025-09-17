import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiRequest } from '../utils/api';
import AnimatedModal from '../components/AnimatedModal';
import { 
  Users, 
  Plus, 
  Eye, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  UserCheck,
  BarChart3,
  X,
  Calendar,
  CheckSquare,
  UserPlus
} from 'lucide-react';

interface CustomerAccount {
  id: number;
  deal_id: number;
  account_name: string;
  contact_id: number;
  account_type: string;
  onboarding_status: string;
  success_manager_id: number;
  created_at: string;
  updated_at?: string;
  health_score?: number;
  engagement_level?: string;
  renewal_probability?: number;
}

interface SuccessMetrics {
  account_id: number;
  health_score: number;
  engagement_level: string;
  last_activity: string;
  renewal_probability: number;
  satisfaction_score?: number;
  metrics: {
    total_interactions: number;
    response_time_avg: string;
    feature_adoption: number;
    support_tickets: number;
    last_renewal: string;
    next_renewal: string;
  };
}

export default function CustomerAccounts() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState<CustomerAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<CustomerAccount | null>(null);
  const [successMetrics, setSuccessMetrics] = useState<SuccessMetrics | null>(null);
  const [showOnboardingModal, setShowOnboardingModal] = useState(false);
  const [onboardingResult, setOnboardingResult] = useState<any>(null);
  const [showMetrics, setShowMetrics] = useState(false);

  useEffect(() => {
    fetchCustomerAccounts();
  }, []);

  const fetchCustomerAccounts = async () => {
    try {
      setLoading(true);
      const data = await apiRequest<CustomerAccount[]>('/api/customer-accounts');
      // Ensure data is an array
      if (Array.isArray(data)) {
        setAccounts(data);
      } else {
        console.error('API returned non-array data:', data);
        setAccounts([]);
        setError('Invalid data format received from server');
      }
    } catch (err) {
      setError('Failed to load customer accounts');
      console.error('Error fetching customer accounts:', err);
      setAccounts([]); // Ensure accounts is always an array
    } finally {
      setLoading(false);
    }
  };

  const fetchSuccessMetrics = async (accountId: number) => {
    try {
      const data = await apiRequest<SuccessMetrics>(`/api/customer-accounts/${accountId}/success-metrics`);
      setSuccessMetrics(data);
      setShowMetrics(true);
    } catch (err) {
      console.error('Error fetching success metrics:', err);
    }
  };

  const startOnboarding = async (accountId: number) => {
    try {
      setLoading(true);
      const data = await apiRequest(`/api/customer-accounts/${accountId}/onboarding/start`, 'POST');
      setOnboardingResult(data);
      setShowOnboardingModal(true);
      fetchCustomerAccounts(); // Refresh the list
    } catch (err) {
      console.error('Error starting onboarding:', err);
      setError('Failed to start onboarding');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'pending':
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Users className="w-6 h-6" />
            Customer Accounts
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage customer accounts and track success metrics
          </p>
        </div>
      </div>

      {/* Customer Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {Array.isArray(accounts) && accounts.map((account) => (
          <div key={account.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {account.account_name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Deal ID: {account.deal_id}
                </p>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(account.onboarding_status)}`}>
                {account.onboarding_status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(account.onboarding_status)}
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  Onboarding: {account.onboarding_status}
                </span>
              </div>

              {account.health_score && (
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Health Score: <span className={`font-medium ${getHealthScoreColor(account.health_score)}`}>
                      {account.health_score}%
                    </span>
                  </span>
                </div>
              )}

              {account.renewal_probability && (
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Renewal: <span className="font-medium text-green-600">
                      {account.renewal_probability}%
                    </span>
                  </span>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => fetchSuccessMetrics(account.id)}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                >
                  <Eye className="w-4 h-4" />
                  Metrics
                </button>
                
                {account.onboarding_status === 'pending' && (
                  <button
                    onClick={() => startOnboarding(account.id)}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                  >
                    <UserCheck className="w-4 h-4" />
                    Start Onboarding
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Success Metrics Modal */}
      {showMetrics && successMetrics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Customer Success Metrics
              </h2>
              <button
                onClick={() => setShowMetrics(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {successMetrics.health_score}%
                </div>
                <div className="text-sm text-blue-600">Health Score</div>
              </div>
              
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {successMetrics.renewal_probability}%
                </div>
                <div className="text-sm text-green-600">Renewal Probability</div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Key Metrics</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Total Interactions:</span>
                    <span className="ml-2 font-medium">{successMetrics.metrics.total_interactions}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Avg Response Time:</span>
                    <span className="ml-2 font-medium">{successMetrics.metrics.response_time_avg}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Feature Adoption:</span>
                    <span className="ml-2 font-medium">{successMetrics.metrics.feature_adoption}%</span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Support Tickets:</span>
                    <span className="ml-2 font-medium">{successMetrics.metrics.support_tickets}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Engagement</h3>
                <div className="text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Level:</span>
                  <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                    successMetrics.engagement_level === 'high' ? 'bg-green-100 text-green-800' :
                    successMetrics.engagement_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {successMetrics.engagement_level}
                  </span>
                </div>
                <div className="text-sm mt-1">
                  <span className="text-gray-600 dark:text-gray-400">Last Activity:</span>
                  <span className="ml-2 font-medium">
                    {new Date(successMetrics.last_activity).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Onboarding Success Modal */}
      <AnimatedModal
        open={showOnboardingModal}
        onClose={() => setShowOnboardingModal(false)}
        title="Onboarding Started Successfully!"
        animationType="scale"
        size="lg"
      >
        {onboardingResult && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 dark:bg-green-900 mb-4">
                <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Onboarding Process Initiated
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {onboardingResult.tasks?.length || 0} onboarding tasks have been created and assigned.
              </p>
            </div>

            {onboardingResult.tasks && onboardingResult.tasks.length > 0 && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                  <CheckSquare className="w-5 h-5 mr-2" />
                  Onboarding Tasks Created
                </h4>
                <div className="space-y-3">
                  {onboardingResult.tasks.map((task: any, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 dark:bg-blue-900">
                          <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                            {index + 1}
                          </span>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {task.title}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {task.description}
                        </p>
                        <div className="mt-2 flex items-center text-xs text-gray-500 dark:text-gray-400">
                          <Calendar className="w-3 h-3 mr-1" />
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          task.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                          task.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                          'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        }`}>
                          {task.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <UserPlus className="h-5 w-5 text-blue-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      What happens next?
                    </h3>
                    <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                      <ul className="list-disc list-inside space-y-1">
                        <li>Tasks have been assigned to the success manager</li>
                        <li>Customer will receive welcome email with next steps</li>
                        <li>Onboarding progress will be tracked automatically</li>
                        <li>You can monitor progress in the Customer Accounts section</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button
                onClick={() => setShowOnboardingModal(false)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Got it!
              </button>
            </div>
          </div>
        )}
      </AnimatedModal>
    </div>
  );
}
