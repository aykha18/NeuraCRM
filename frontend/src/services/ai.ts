import { apiRequest } from '../utils/api';

export interface AIChatRequest {
  message: string;
  user_id: number;
}

export interface AIChatResponse {
  response: string;
}

export interface ChatMessage {
  id: string;
  message: string;
  response: string;
  timestamp: Date;
  isUser: boolean;
}

export const sendAIMessage = async (request: AIChatRequest): Promise<AIChatResponse> => {
  try {
    return await apiRequest<AIChatResponse>('/api/ai/assistant', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  } catch (error: any) {
    console.error('AI API Error:', error);
    if (error.message.includes('timeout')) {
      throw new Error('Request timed out. Please try again.');
    }
    throw new Error('Failed to get AI response. Please try again.');
  }
};

// Mock function for getting CRM context (will be enhanced later)
export const getCRMContext = async (_userId: number) => {
  // TODO: Fetch real CRM data (deals, contacts, etc.) for context
  return {
    deals: [],
    contacts: [],
    leads: [],
    activities: []
  };
}; 