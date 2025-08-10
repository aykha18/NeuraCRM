export interface Deal {
  id: number;
  title: string;
  amount: number;
  stage_id: number;
  description?: string;
  owner_id?: number;
  created_at: string;
  updated_at?: string;
  closed_at?: string | null;
  probability?: number;
  expected_close_date?: string;
  company_id?: number;
  contact_id?: number | null;
}

export interface Stage {
  id: number;
  name: string;
  order: number;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface KanbanBoard {
  stages: Stage[];
  deals: Deal[];
}

export interface FrontendDeal extends Omit<Deal, 'id' | 'stage_id'> {
  id: string;
  stage: string;
  value: string;
  owner: string;
  tags: string[];
  watchers: string[];
  reminderDate?: Date;
  closedAt?: Date;
  createdAt: Date;
}

export type DealsByStage = Record<number, FrontendDeal[]>;
