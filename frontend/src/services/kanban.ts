import { apiRequest } from '../utils/api';

// Types
export interface Stage {
  id: number;
  name: string;
  order: number;
  wip_limit?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Deal {
  id: number;
  title: string;
  description?: string;
  value?: number;
  contact_id?: number;
  owner_id?: number;
  stage_id: number;
  reminder_date?: string;
  created_at?: string;
  updated_at?: string;
  contact_name?: string;
  owner_name?: string;
  stage_name?: string;
  watchers?: string[];
}

export interface KanbanBoard {
  stages: Stage[];
  deals: Deal[];
}

// Stage management interfaces
export interface StageCreate {
  name: string;
  order: number;
  wip_limit?: number;
}

export interface StageUpdate {
  name?: string;
  order?: number;
  wip_limit?: number;
}

// Stage management API calls
export const stageService = {
  // Get all stages
  async getStages(): Promise<Stage[]> {
    return apiRequest<Stage[]>('/stages', 'GET');
  },

  // Create a new stage
  async createStage(stageData: StageCreate): Promise<Stage> {
    return apiRequest<Stage>('/stages', 'POST', stageData);
  },

  // Update a stage
  async updateStage(stageId: number, stageData: StageUpdate): Promise<Stage> {
    return apiRequest<Stage>(`/stages/${stageId}`, 'PUT', stageData);
  },

  // Delete a stage
  async deleteStage(stageId: number): Promise<void> {
    return apiRequest<void>(`/stages/${stageId}`, 'DELETE');
  }
};

export const getStages = async (): Promise<Stage[]> => {
  return apiRequest<Stage[]>('/api/kanban/stages/');
};

export const createStage = async (stage: Omit<Stage, 'id'>): Promise<Stage> => {
  return apiRequest<Stage>('/api/kanban/stages/', {
    method: 'POST',
    body: JSON.stringify(stage),
  });
};

export const updateStage = async (id: number, stage: Partial<Stage>): Promise<Stage> => {
  return apiRequest<Stage>(`/api/kanban/stages/${id}`, {
    method: 'PUT',
    body: JSON.stringify(stage),
  });
};

export const deleteStage = async (id: number): Promise<void> => {
  return apiRequest<void>(`/api/kanban/stages/${id}`, {
    method: 'DELETE',
  });
};

// API calls
export const getKanbanBoard = async (): Promise<KanbanBoard> => {
  return apiRequest<KanbanBoard>('/api/kanban/board');
};

export const createDeal = async (deal: Omit<Deal, 'id'>): Promise<Deal> => {
  return apiRequest<Deal>('/api/kanban/deals/', {
    method: 'POST',
    body: JSON.stringify(deal),
  });
};

export const updateDeal = async (id: number, deal: Partial<Deal>): Promise<Deal> => {
  return apiRequest<Deal>(`/api/kanban/deals/${id}`, {
    method: 'PUT',
    body: JSON.stringify(deal),
  });
};

export const deleteDeal = async (id: number): Promise<void> => {
  return apiRequest<void>(`/api/kanban/deals/${id}`, {
    method: 'DELETE',
  });
};

export const moveDeal = async (dealId: number, newStageId: number, position: number): Promise<Deal> => {
  return apiRequest<Deal>(`/api/kanban/deals/${dealId}/move`, {
    method: 'POST',
    body: JSON.stringify({
      to_stage_id: newStageId,
      position,
    }),
  });
};

export const watchDeal = async (dealId: number): Promise<Deal> => {
  return apiRequest<Deal>(`/api/kanban/deals/${dealId}/watch`, {
    method: 'POST',
  });
};

export const unwatchDeal = async (dealId: number): Promise<Deal> => {
  return apiRequest<Deal>(`/api/kanban/deals/${dealId}/watch`, {
    method: 'DELETE',
  });
};
