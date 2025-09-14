export interface DashboardMetrics {
  active_leads: number;
  closed_deals: number;
  total_revenue: number;
  ai_score: number;
  lead_quality_score: number;
  conversion_rate: number;
  target_achievement: number;
}

export interface PerformanceData {
  month: string;
  leads: number;
  deals: number;
  revenue: number;
}

export interface LeadQualityData {
  name: string;
  value: number;
  color: string;
}

export interface ActivityFeedItem {
  icon: string;
  color: string;
  title: string;
  time: string;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  performance: PerformanceData[];
  lead_quality: LeadQualityData[];
  activity_feed: ActivityFeedItem[];
}

import { apiRequest } from '../utils/api';

export async function fetchDashboardData(): Promise<DashboardData> {
  return apiRequest<DashboardData>('/api/dashboard/');
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  return apiRequest<DashboardMetrics>('/api/dashboard/metrics');
}

export async function fetchPerformanceData(): Promise<PerformanceData[]> {
  return apiRequest<PerformanceData[]>('/api/dashboard/performance');
}

export async function fetchLeadQualityData(): Promise<LeadQualityData[]> {
  return apiRequest<LeadQualityData[]>('/api/dashboard/lead-quality');
}

export async function fetchActivityFeed(): Promise<ActivityFeedItem[]> {
  return apiRequest<ActivityFeedItem[]>('/api/dashboard/activity-feed');
} 