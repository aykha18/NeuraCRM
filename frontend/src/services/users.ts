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
    // Fast fix: backend doesn't have this route; use global users endpoint scoped by auth
    return apiRequest<User[]>(`/api/users`, 'GET');
  },

  // Create a new user in the organization
  async createUser(orgId: number, userData: CreateUserRequest): Promise<User> {
    return apiRequest<User>(`/api/users`, 'POST', userData);
  },

  // Delete a user from the organization
  async deleteUser(orgId: number, userId: number): Promise<void> {
    return apiRequest<void>(`/api/users/${userId}`, 'DELETE');
  }
};
