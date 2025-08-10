// Lead Scoring Service
// API calls for lead scoring functionality

export interface LeadScore {
  score: number;
  confidence: number;
  factors: Record<string, number>;
  explanation: string[];
  category: string;
  recommendations: string[];
}

export interface ScoringAnalytics {
  total_leads: number;
  average_score: number;
  score_distribution: Record<string, number>;
  top_scoring_leads: Array<{
    id: number;
    title: string;
    score: number;
    status: string;
  }>;
}

// Score a single lead
export async function scoreLead(leadId: number): Promise<LeadScore> {
  const response = await fetch(`http://localhost:8000/api/leads/${leadId}/score`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to score lead');
  }
  
  return response.json();
}

// Score all leads
export async function scoreAllLeads(): Promise<{ message: string; results: any[] }> {
  const response = await fetch('http://localhost:8000/api/leads/score-all', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to score all leads');
  }
  
  return response.json();
}

// Get scoring analytics
export async function getScoringAnalytics(): Promise<ScoringAnalytics> {
  const response = await fetch('http://localhost:8000/api/leads/scoring-analytics');
  
  if (!response.ok) {
    throw new Error('Failed to get scoring analytics');
  }
  
  return response.json();
}

// Get score category color
export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-red-600 bg-red-100';
  if (score >= 60) return 'text-orange-600 bg-orange-100';
  if (score >= 40) return 'text-yellow-600 bg-yellow-100';
  return 'text-gray-600 bg-gray-100';
}

// Get score category label
export function getScoreCategory(score: number): string {
  if (score >= 80) return 'Hot Lead';
  if (score >= 60) return 'Warm Lead';
  if (score >= 40) return 'Lukewarm Lead';
  return 'Cold Lead';
} 