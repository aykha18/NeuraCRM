import { apiRequest } from '../utils/api';

export interface PBXProvider {
  id: number;
  name: string;
  provider_type: string;
  display_name: string;
  host: string;
  port: number;
  username?: string;
  password?: string;
  is_active: boolean;
  is_primary: boolean;
  recording_enabled: boolean;
  transcription_enabled: boolean;
  created_at: string;
  last_sync: string;
}

export interface Call {
  id: number;
  unique_id: string;
  caller_id: string;
  caller_name: string;
  called_number: string;
  called_name: string;
  direction: string;
  call_type: string;
  status: string;
  start_time: string;
  answer_time?: string;
  end_time?: string;
  duration?: number;
  talk_time?: number;
  hold_time?: number;
  wait_time?: number;
  quality_score?: number;
  recording_url?: string;
  transcription_text?: string;
  disposition?: string;
  notes?: string;
  cost?: number;
  cost_currency?: string;
  agent_id?: number;
  queue_id?: number;
  contact_id?: number;
  lead_id?: number;
  deal_id?: number;
  created_at: string;
}

export interface CallQueue {
  id: number;
  name: string;
  description?: string;
  queue_number: string;
  strategy: string;
  timeout: number;
  retry: number;
  wrapup_time: number;
  max_wait_time: number;
  music_on_hold: string;
  announce_frequency: number;
  announce_position: boolean;
  announce_hold_time: boolean;
  max_calls_per_agent: number;
  join_empty: boolean;
  leave_when_empty: boolean;
  priority: number;
  skill_based_routing: boolean;
  required_skills?: string[];
  is_active: boolean;
  current_calls: number;
  current_agents: number;
  total_calls: number;
  answered_calls: number;
  abandoned_calls: number;
  avg_wait_time: number;
  avg_talk_time: number;
  service_level: number;
  created_at: string;
}

export interface DashboardData {
  active_calls: number;
  queued_calls: number;
  available_agents: number;
  busy_agents: number;
  offline_agents: number;
  current_queue_status: Array<{
    id: number;
    name: string;
    queue_number: string;
    current_calls: number;
    current_agents: number;
    wait_time: number;
  }>;
  recent_calls: Array<{
    id: number;
    caller_id: string;
    called_number: string;
    direction: string;
    status: string;
    start_time: string;
    duration: number;
    agent_id: number;
  }>;
  agent_status: Array<{
    id: number;
    name: string;
    email: string;
    status: string;
    active_calls: number;
    queues: string[];
  }>;
  queue_metrics: Array<{
    id: number;
    name: string;
    calls_today: number;
    answered_today: number;
    answer_rate: number;
    avg_wait_time: number;
    service_level: number;
  }>;
  hourly_stats: Record<string, number>;
  daily_stats: Record<string, number>;
  alerts: Array<{
    type: string;
    message: string;
  }>;
}

export const telephonyService = {
  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    return apiRequest<DashboardData>('/api/telephony/dashboard');
  },

  // PBX Providers
  async getProviders(): Promise<PBXProvider[]> {
    return apiRequest<PBXProvider[]>('/api/telephony/providers');
  },

  async createProvider(providerData: Partial<PBXProvider>): Promise<PBXProvider> {
    return apiRequest<PBXProvider>('/api/telephony/providers', 'POST', providerData);
  },

  async getProvider(providerId: number): Promise<PBXProvider> {
    return apiRequest<PBXProvider>(`/api/telephony/providers/${providerId}`);
  },

  async updateProvider(providerId: number, providerData: Partial<PBXProvider>): Promise<PBXProvider> {
    return apiRequest<PBXProvider>(`/api/telephony/providers/${providerId}`, 'PUT', providerData);
  },

  async deleteProvider(providerId: number): Promise<{ message: string }> {
    return apiRequest<{ message: string }>(`/api/telephony/providers/${providerId}`, 'DELETE');
  },

  async testProviderConnection(providerId: number): Promise<{ success: boolean; message: string; response_time?: number; error?: string }> {
    return apiRequest<{ success: boolean; message: string; response_time?: number; error?: string }>(`/api/telephony/providers/${providerId}/test`, 'POST');
  },

  // Calls
  async getCalls(params?: {
    provider_id?: number;
    agent_id?: number;
    status?: string;
    direction?: string;
    limit?: number;
    offset?: number;
  }): Promise<Call[]> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const endpoint = `/api/telephony/calls${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiRequest<Call[]>(endpoint);
  },

  async getCall(callId: number): Promise<Call> {
    return apiRequest<Call>(`/api/telephony/calls/${callId}`);
  },

  async updateCall(callId: number, callData: Partial<Call>): Promise<any> {
    return apiRequest(`/api/telephony/calls/${callId}`, 'PUT', callData);
  },

  async holdCall(callId: number, holdData: { hold: boolean; reason?: string }): Promise<any> {
    return apiRequest(`/api/telephony/calls/${callId}/hold`, 'POST', holdData);
  },

  async transferCall(callId: number, transferData: {
    target_extension: string;
    target_type: string;
    transfer_type?: string;
    notes?: string;
  }): Promise<any> {
    return apiRequest(`/api/telephony/calls/${callId}/transfer`, 'POST', transferData);
  },

  // Call Queues
  async getQueues(providerId?: number): Promise<CallQueue[]> {
    const endpoint = providerId ? `/api/telephony/queues?provider_id=${providerId}` : '/api/telephony/queues';
    return apiRequest<CallQueue[]>(endpoint);
  },

  async createQueue(queueData: Partial<CallQueue>): Promise<CallQueue> {
    return apiRequest<CallQueue>('/api/telephony/queues', 'POST', queueData);
  },

  // Queue Members (Agents)
  async getQueueMembers(queueId?: number): Promise<any[]> {
    const endpoint = queueId ? `/api/telephony/queues/${queueId}/members` : '/api/telephony/queue-members';
    return apiRequest<any[]>(endpoint);
  },

  async addQueueMember(queueId: number, memberData: any): Promise<any> {
    return apiRequest(`/api/telephony/queues/${queueId}/members`, 'POST', memberData);
  },

  async updateQueueMember(queueId: number, memberId: number, memberData: any): Promise<any> {
    return apiRequest(`/api/telephony/queues/${queueId}/members/${memberId}`, 'PUT', memberData);
  },

  async removeQueueMember(queueId: number, memberId: number): Promise<any> {
    return apiRequest(`/api/telephony/queues/${queueId}/members/${memberId}`, 'DELETE');
  },

  // Extensions
  async getExtensions(providerId?: number): Promise<any[]> {
    const endpoint = providerId ? `/api/telephony/providers/${providerId}/extensions` : '/api/telephony/extensions';
    return apiRequest<any[]>(endpoint);
  },

  async createExtension(extensionData: any): Promise<any> {
    return apiRequest('/api/telephony/extensions', 'POST', extensionData);
  },

  // Analytics
  async getAnalytics(params?: {
    start_date?: string;
    end_date?: string;
    queue_id?: number;
    agent_id?: number;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const endpoint = `/api/telephony/analytics${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiRequest(endpoint);
  }
};

export default telephonyService;
