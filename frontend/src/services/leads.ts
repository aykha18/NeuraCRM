import { apiRequest } from '../utils/api';
import { getStoredUtmAttribution } from '../utils/utm';

export interface Lead {
  id: number;
  name: string;
  company?: string;
  email?: string;
  phone?: string;
  source?: string;
  // UTM fields (frontend mirror; optional on read)
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  referrer_url?: string;
  landing_page_url?: string;
  gclid?: string;
  fbclid?: string;
  status?: string;
  priority?: string;
  estimated_value?: number;
  notes?: string;
  owner_id?: number;
  organization_id?: number;
  created_at?: string;
  owner_name?: string;
}

export async function fetchLeads(): Promise<Lead[]> {
  return apiRequest<Lead[]>('/api/leads');
}

export async function getLead(id: number): Promise<Lead> {
  return apiRequest<Lead>(`/api/leads/${id}`);
}

export async function createLead(data: Partial<Lead>): Promise<Lead> {
  const utm = getStoredUtmAttribution() || {};
  return apiRequest<Lead>('/api/leads', {
    method: "POST",
    body: JSON.stringify({ ...utm, ...data }),
  });
}

export async function updateLead(id: number, data: Partial<Lead>): Promise<Lead> {
  return apiRequest<Lead>(`/api/leads/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteLead(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/leads/${id}`, {
    method: "DELETE"
  });
}

export async function convertLeadToDeal(id: number, dealData?: any): Promise<any> {
  return apiRequest<any>(`/api/leads/${id}/convert-to-deal`, {
    method: "POST",
    body: JSON.stringify(dealData || {
      title: `Deal from Lead ${id}`,
      description: "Deal converted from lead",
      value: 0
    }),
  });
}

export async function convertContactToLead(contactId: number, leadData?: any): Promise<any> {
  return apiRequest<any>(`/api/contacts/${contactId}/convert-to-lead`, {
    method: "POST",
    body: JSON.stringify(leadData || {
      title: `Lead from Contact ${contactId}`,
      status: 'new',
      source: 'contact_conversion',
      score: 50
    }),
  });
} 