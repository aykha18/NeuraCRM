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

const API_BASE = "http://localhost:8000/api";

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/dashboard/`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  return res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/dashboard/metrics`);
  if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
  return res.json();
}

export async function fetchPerformanceData(): Promise<PerformanceData[]> {
  const res = await fetch(`${API_BASE}/dashboard/performance`);
  if (!res.ok) throw new Error("Failed to fetch performance data");
  return res.json();
}

export async function fetchLeadQualityData(): Promise<LeadQualityData[]> {
  const res = await fetch(`${API_BASE}/dashboard/lead-quality`);
  if (!res.ok) throw new Error("Failed to fetch lead quality data");
  return res.json();
}

export async function fetchActivityFeed(): Promise<ActivityFeedItem[]> {
  const res = await fetch(`${API_BASE}/dashboard/activity-feed`);
  if (!res.ok) throw new Error("Failed to fetch activity feed");
  return res.json();
} 