import { apiRequest } from '../utils/api';

export interface SubscriptionPlan {
  id: number;
  name: string;
  display_name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  user_limit: number;
  features: string[];
  is_active: boolean;
}

export interface OrganizationSignupRequest {
  organization_name: string;
  organization_domain?: string;
  admin_name: string;
  admin_email: string;
  admin_password: string;
  plan: string;
}

export interface OrganizationSignupResponse {
  organization: {
    id: number;
    name: string;
    domain?: string;
    created_at: string;
  };
  admin_user: {
    id: number;
    name: string;
    email: string;
    role: string;
    organization_id: number;
    created_at: string;
  };
  subscription: {
    id: number;
    plan: string;
    status: string;
    user_limit: number;
    features: string[];
    created_at: string;
  };
  access_token: string;
  token_type: string;
}

export interface UserLimitCheck {
  current_users: number;
  user_limit: number;
  can_add_user: boolean;
  plan: string;
}

export const organizationService = {
  // Get available subscription plans
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    return apiRequest<SubscriptionPlan[]>('/api/subscription-plans');
  },

  // Sign up a new organization
  async signupOrganization(data: OrganizationSignupRequest): Promise<OrganizationSignupResponse> {
    return apiRequest<OrganizationSignupResponse>('/api/organizations/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Check user limit for organization
  async checkUserLimit(orgId: number): Promise<UserLimitCheck> {
    return apiRequest<UserLimitCheck>(`/api/organizations/${orgId}/user-limit`);
  },
};
