import { apiRequest } from '../utils/api';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  organization_id: number;
  created_at?: string;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
}

export const userService = {
  // Get all users in the organization
  async getOrganizationUsers(orgId: number): Promise<User[]> {
    return apiRequest<User[]>(`/api/organizations/${orgId}/users`, 'GET');
  },

  // Create a new user in the organization
  async createUser(orgId: number, userData: CreateUserRequest): Promise<User> {
    return apiRequest<User>(`/api/organizations/${orgId}/users`, 'POST', userData);
  },

  // Delete a user from the organization
  async deleteUser(orgId: number, userId: number): Promise<void> {
    return apiRequest<void>(`/api/organizations/${orgId}/users/${userId}`, 'DELETE');
  }
};
