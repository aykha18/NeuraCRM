import axios from 'axios';

import { API_BASE_URL } from '../config';

const API_URL = `${API_BASE_URL}/api`;

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

export const getStages = async (): Promise<Stage[]> => {
  const response = await axios.get<Stage[]>(`${API_URL}/kanban/stages/`);
  return response.data;
};

export const createStage = async (stage: Omit<Stage, 'id'>): Promise<Stage> => {
  const response = await axios.post<Stage>(`${API_URL}/kanban/stages/`, stage);
  return response.data;
};

export const updateStage = async (id: number, stage: Partial<Stage>): Promise<Stage> => {
  const response = await axios.put<Stage>(`${API_URL}/kanban/stages/${id}`, stage);
  return response.data;
};

export const deleteStage = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/kanban/stages/${id}`);
};

// API calls
export const getKanbanBoard = async (): Promise<KanbanBoard> => {
  const response = await axios.get<KanbanBoard>(`${API_URL}/kanban/board`);
  return response.data;
};

export const createDeal = async (deal: Omit<Deal, 'id'>): Promise<Deal> => {
  const response = await axios.post<Deal>(`${API_URL}/kanban/deals/`, deal);
  return response.data;
};

export const updateDeal = async (id: number, deal: Partial<Deal>): Promise<Deal> => {
  const response = await axios.put<Deal>(`${API_URL}/kanban/deals/${id}`, deal);
  return response.data;
};

export const deleteDeal = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/kanban/deals/${id}`);
};

export const moveDeal = async (dealId: number, newStageId: number, position: number): Promise<Deal> => {
  const response = await axios.post<Deal>(`${API_URL}/kanban/deals/${dealId}/move`, {
    to_stage_id: newStageId,
    position,
  });
  return response.data;
};

export const watchDeal = async (dealId: number): Promise<Deal> => {
  const response = await axios.post<Deal>(`${API_URL}/kanban/deals/${dealId}/watch`);
  return response.data;
};

export const unwatchDeal = async (dealId: number): Promise<Deal> => {
  const response = await axios.delete<Deal>(`${API_URL}/kanban/deals/${dealId}/watch`);
  return response.data;
};
