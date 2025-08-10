// Contacts Service
// API calls for contact management

export interface Contact {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  owner_id?: number;
  created_at?: string;
  owner_name?: string;
}

import { API_BASE_URL } from '../config';

export async function fetchContacts(): Promise<Contact[]> {
  const res = await fetch(`${API_BASE_URL}/api/contacts`);
  if (!res.ok) throw new Error("Failed to fetch contacts");
  return res.json();
}

export async function getContact(id: number): Promise<Contact> {
  const res = await fetch(`${API_BASE_URL}/api/contacts/${id}`);
  if (!res.ok) throw new Error("Failed to fetch contact");
  return res.json();
}

export async function createContact(data: Partial<Contact>): Promise<Contact> {
  const res = await fetch(`${API_BASE_URL}/api/contacts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create contact");
  return res.json();
}

export async function updateContact(id: number, data: Partial<Contact>): Promise<Contact> {
  const res = await fetch(`${API_BASE_URL}/api/contacts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update contact");
  return res.json();
}

export async function deleteContact(id: number): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/api/contacts/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete contact");
  return res.json();
}