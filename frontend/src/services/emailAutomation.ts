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
  
  const res = await fetch(`http://localhost:8000/api/email/templates?${params}`);
  if (!res.ok) throw new Error("Failed to fetch email templates");
  return res.json();
}

export async function createEmailTemplate(data: {
  name: string;
  subject: string;
  body: string;
  category?: string;
}): Promise<EmailTemplate> {
  const res = await fetch("http://localhost:8000/api/email/templates", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create email template");
  return res.json();
}

export async function updateEmailTemplate(id: number, data: Partial<{
  name: string;
  subject: string;
  body: string;
  category: string;
  is_active: boolean;
}>): Promise<EmailTemplate> {
  const res = await fetch(`http://localhost:8000/api/email/templates/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update email template");
  return res.json();
}

export async function deleteEmailTemplate(id: number): Promise<{ message: string }> {
  const res = await fetch(`http://localhost:8000/api/email/templates/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete email template");
  return res.json();
}

export async function previewTemplate(templateId: number, recipientType: string, recipientId: number): Promise<TemplatePreview> {
  const res = await fetch("http://localhost:8000/api/email/templates/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template_id: templateId,
      recipient_type: recipientType,
      recipient_id: recipientId
    }),
  });
  if (!res.ok) throw new Error("Failed to preview template");
  return res.json();
}

export async function createSampleTemplates(): Promise<{ message: string }> {
  const res = await fetch("http://localhost:8000/api/email/templates/sample", {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create sample templates");
  return res.json();
}

// Campaign API calls
export async function getEmailCampaigns(status?: string): Promise<EmailCampaign[]> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  
  const res = await fetch(`http://localhost:8000/api/email/campaigns?${params}`);
  if (!res.ok) throw new Error("Failed to fetch email campaigns");
  return res.json();
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
  const res = await fetch("http://localhost:8000/api/email/campaigns", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create email campaign");
  return res.json();
}

export async function sendCampaign(campaignId: number): Promise<{
  message: string;
  sent_count: number;
  total_recipients: number;
}> {
  const res = await fetch(`http://localhost:8000/api/email/campaigns/${campaignId}/send`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to send campaign");
  return res.json();
}

// Email logs API calls
export async function getEmailLogs(campaignId?: number, status?: string, limit: number = 100): Promise<EmailLog[]> {
  const params = new URLSearchParams();
  if (campaignId) params.append('campaign_id', campaignId.toString());
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  
  const res = await fetch(`http://localhost:8000/api/email/logs?${params}`);
  if (!res.ok) throw new Error("Failed to fetch email logs");
  return res.json();
}

export async function getEmailAnalytics(): Promise<EmailAnalytics> {
  const res = await fetch("http://localhost:8000/api/email/logs/analytics");
  if (!res.ok) throw new Error("Failed to fetch email analytics");
  return res.json();
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