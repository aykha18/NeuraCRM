// Contacts Service
// API calls for contact management

export interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  industry?: string;
  notes?: string;
  owner_id?: number;
  organization_id?: number;
  created_at?: string;
  owner_name?: string;
}

import { apiRequest } from '../utils/api';

export async function fetchContacts(): Promise<Contact[]> {
  return apiRequest<Contact[]>('/api/contacts');
}

export async function getContact(id: number): Promise<Contact> {
  return apiRequest<Contact>(`/api/contacts/${id}`);
}

export async function createContact(data: Partial<Contact>): Promise<Contact> {
  return apiRequest<Contact>('/api/contacts', {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateContact(id: number, data: Partial<Contact>): Promise<Contact> {
  return apiRequest<Contact>(`/api/contacts/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteContact(id: number): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/contacts/${id}`, {
    method: "DELETE",
  });
}