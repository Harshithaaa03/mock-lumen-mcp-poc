import axios from 'axios';
import type { Task, TaskCreate, TaskListResponse, TaskUpdate, FilterParams, TaskStatus } from '../types/task';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export const taskApi = {
  list: async (filters: FilterParams = {}): Promise<TaskListResponse> => {
    const params: Record<string, string> = {};
    if (filters.status) params.status = filters.status;
    if (filters.assignee) params.assignee = filters.assignee;
    const response = await api.get<TaskListResponse>('/tasks/', { params });
    return response.data;
  },

  get: async (id: string): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  create: async (payload: TaskCreate): Promise<Task> => {
    const response = await api.post<Task>('/tasks/', payload);
    return response.data;
  },

  update: async (id: string, payload: TaskUpdate): Promise<Task> => {
    const response = await api.patch<Task>(`/tasks/${id}`, payload);
    return response.data;
  },

  complete: async (id: string): Promise<Task> => {
    const response = await api.post<Task>(`/tasks/${id}/complete`);
    return response.data;
  },

  reopen: async (id: string): Promise<Task> => {
    const response = await api.post<Task>(`/tasks/${id}/reopen`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },
};

export const STATUS_LABELS: Record<TaskStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  completed: 'Completed',
  cancelled: 'Cancelled',
};
