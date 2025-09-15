import { apiRequest } from '../utils/api';

// Email Automation Service
// API calls for email templates, campaigns, and automation

export interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  category?: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  validation: {
    valid: boolean;
    available_variables: string[];
    missing_variables: string[];
    total_variables: number;
  };
}

export interface EmailCampaign {
  id: number;
  name: string;
  template_id: number;
  subject_override?: string;
  body_override?: string;
  target_type: string;
  target_ids: string;
  scheduled_at?: string;
  sent_at?: string;
  status: string;
  created_by?: number;
  created_at: string;
  template?: EmailTemplate;
}

export interface EmailLog {
  id: number;
  campaign_id: number;
  recipient_type?: string;
  recipient_id?: number;
  recipient_email: string;
  recipient_name?: string;
  subject: string;
  body: string;
  sent_at: string;
  status: string;
  opened_at?: string;
  clicked_at?: string;
  error_message?: string;
}

export interface EmailAnalytics {
  total_sent: number;
  total_opened: number;
  total_clicked: number;
  open_rate: number;
  click_rate: number;
}

export interface TemplatePreview {
  subject: string;
  body: string;
  context: Record<string, any>;
}

// Template API calls
export async function getEmailTemplates(category?: string, activeOnly: boolean = true): Promise<EmailTemplate[]> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  params.append('active_only', activeOnly.toString());
  
  return apiRequest<EmailTemplate[]>(`/api/email/templates?${params}`, 'GET');
}

export async function createEmailTemplate(data: {
  name: string;
  subject: string;
  body: string;
  category?: string;
}): Promise<EmailTemplate> {
  return apiRequest<EmailTemplate>('/api/email/templates', 'POST', data);
}

export async function updateEmailTemplate(id: number, data: Partial<{
  name: string;
  subject: string;
  body: string;
  category: string;
  is_active: boolean;
}>): Promise<EmailTemplate> {
  return apiRequest<EmailTemplate>(`/api/email/templates/${id}`, 'PUT', data);
}

export async function deleteEmailTemplate(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/email/templates/${id}`, 'DELETE');
}

export async function previewTemplate(templateId: number, recipientType: string, recipientId: number): Promise<TemplatePreview> {
  return apiRequest<TemplatePreview>('/api/email/templates/preview', 'POST', {
    template_id: templateId,
    recipient_type: recipientType,
    recipient_id: recipientId
  });
}

export async function createSampleTemplates(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/api/email/templates/sample', 'POST');
}

// Campaign API calls
export async function getEmailCampaigns(status?: string): Promise<EmailCampaign[]> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  
  return apiRequest<EmailCampaign[]>(`/api/email/campaigns?${params}`, 'GET');
}

export async function createEmailCampaign(data: {
  name: string;
  template_id: number;
  subject_override?: string;
  body_override?: string;
  target_type: string;
  target_ids: number[];
  scheduled_at?: string;
}): Promise<EmailCampaign> {
  return apiRequest<EmailCampaign>('/api/email/campaigns', 'POST', data);
}

export async function sendCampaign(campaignId: number): Promise<{
  message: string;
  sent_count: number;
  total_recipients: number;
}> {
  return apiRequest<{
    message: string;
    sent_count: number;
    total_recipients: number;
  }>(`/api/email/campaigns/${campaignId}/send`, 'POST');
}

// Email logs API calls
export async function getEmailLogs(campaignId?: number, status?: string, limit: number = 100): Promise<EmailLog[]> {
  const params = new URLSearchParams();
  if (campaignId) params.append('campaign_id', campaignId.toString());
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  
  return apiRequest<EmailLog[]>(`/api/email/logs?${params}`, 'GET');
}

export async function getEmailAnalytics(): Promise<EmailAnalytics> {
  return apiRequest<EmailAnalytics>('/api/email/logs/analytics', 'GET');
}

// Helper functions
export function getTemplateVariables(body: string): string[] {
  const pattern = /\{\{(\w+(?:\.\w+)*)\}\}/g;
  const variables: string[] = [];
  let match;
  
  while ((match = pattern.exec(body)) !== null) {
    variables.push(match[1]);
  }
  
  return [...new Set(variables)];
}

export function getVariableCategory(variable: string): string {
  const parts = variable.split('.');
  return parts[0] || '';
}

export function getVariableField(variable: string): string {
  const parts = variable.split('.');
  return parts[1] || '';
}

export function formatTemplateVariable(variable: string): string {
  const category = getVariableCategory(variable);
  const field = getVariableField(variable);
  
  if (!category || !field) return variable;
  
  const categoryLabels: Record<string, string> = {
    'contact': 'Contact',
    'lead': 'Lead',
    'deal': 'Deal',
    'user': 'User',
    'system': 'System'
  };
  
  const fieldLabels: Record<string, Record<string, string>> = {
    'contact': {
      'name': 'Name',
      'email': 'Email',
      'phone': 'Phone',
      'company': 'Company'
    },
    'lead': {
      'title': 'Title',
      'status': 'Status',
      'source': 'Source',
      'score': 'Score'
    },
    'deal': {
      'title': 'Title',
      'value': 'Value',
      'stage': 'Stage'
    },
    'user': {
      'name': 'Name',
      'email': 'Email'
    },
    'system': {
      'current_date': 'Current Date',
      'current_time': 'Current Time'
    }
  };
  
  const categoryLabel = categoryLabels[category] || category;
  const fieldLabel = fieldLabels[category]?.[field] || field;
  
  return `${categoryLabel} - ${fieldLabel}`;
} 