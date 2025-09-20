import { apiRequest } from '../utils/api';

export interface CompanySettings {
  id: number;
  organization_id: number;
  company_name: string;
  company_mobile?: string;
  city?: string;
  area?: string;
  complete_address?: string;
  trn?: string;
  currency: string;
  timezone: string;
  trial_date_enabled: boolean;
  trial_date_days: number;
  delivery_date_enabled: boolean;
  delivery_date_days: number;
  advance_payment_enabled: boolean;
  created_at: string;
  updated_at: string;
  created_by: number;
}

export interface CompanySettingsUpdate {
  company_name?: string;
  company_mobile?: string;
  city?: string;
  area?: string;
  complete_address?: string;
  trn?: string;
  currency?: string;
  timezone?: string;
  trial_date_enabled?: boolean;
  trial_date_days?: number;
  delivery_date_enabled?: boolean;
  delivery_date_days?: number;
  advance_payment_enabled?: boolean;
}

export interface CompanySettingsCreate {
  company_name: string;
  company_mobile?: string;
  city?: string;
  area?: string;
  complete_address?: string;
  trn?: string;
  currency: string;
  timezone: string;
  trial_date_enabled: boolean;
  trial_date_days: number;
  delivery_date_enabled: boolean;
  delivery_date_days: number;
  advance_payment_enabled: boolean;
}

export const companySettingsService = {
  /**
   * Get company settings for the current organization
   */
  async getSettings(): Promise<CompanySettings> {
    return apiRequest('/api/company-settings') as Promise<CompanySettings>;
  },

  /**
   * Update company settings (creates if doesn't exist)
   */
  async updateSettings(settings: CompanySettingsUpdate): Promise<CompanySettings> {
    return apiRequest('/api/company-settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
      headers: {
        'Content-Type': 'application/json',
      },
    }) as Promise<CompanySettings>;
  },

  /**
   * Create new company settings
   */
  async createSettings(settings: CompanySettingsCreate): Promise<CompanySettings> {
    return apiRequest('/api/company-settings', {
      method: 'POST',
      body: JSON.stringify(settings),
      headers: {
        'Content-Type': 'application/json',
      },
    }) as Promise<CompanySettings>;
  },
};
