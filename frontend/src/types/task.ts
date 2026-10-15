export type TaskStatus = 'todo' | 'in_progress' | 'completed' | 'cancelled';

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  assignee: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  assignee?: string;
  status?: TaskStatus;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  assignee?: string;
  status?: TaskStatus;
}

export interface FilterParams {
  status?: TaskStatus | '';
  assignee?: string;
}
