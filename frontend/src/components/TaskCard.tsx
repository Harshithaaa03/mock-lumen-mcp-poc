import { useState } from 'react';
import type { Task } from '../types/task';
import type { TaskStatus } from '../types/task';
import { taskApi, STATUS_LABELS } from '../api/tasks';
import { StatusBadge } from './StatusBadge';

interface TaskCardProps {
  task: Task;
  isSelected: boolean;
  onSelect: (task: Task) => void;
  onUpdated: (task: Task) => void;
  onDeleted: (id: string) => void;
  onToast: (msg: string, type: 'success' | 'error') => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function TaskCard({ task, isSelected, onSelect, onUpdated, onDeleted, onToast }: TaskCardProps) {
  const [loading, setLoading] = useState(false);

  const handleComplete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);
    try {
      const updated = await taskApi.complete(task.id);
      onUpdated(updated);
      onToast('Task marked complete ✓', 'success');
    } catch {
      onToast('Failed to update task', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleReopen = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);
    try {
      const updated = await taskApi.reopen(task.id);
      onUpdated(updated);
      onToast('Task reopened', 'success');
    } catch {
      onToast('Failed to reopen task', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete "${task.title}"?`)) return;
    setLoading(true);
    try {
      await taskApi.delete(task.id);
      onDeleted(task.id);
      onToast('Task deleted', 'success');
    } catch {
      onToast('Failed to delete task', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`task-card status-${task.status} ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(task)}
      role="button"
      tabIndex={0}
      aria-selected={isSelected}
      onKeyDown={(e) => e.key === 'Enter' && onSelect(task)}
    >
      <div className="task-card-top">
        <div className={`task-title ${task.status === 'completed' ? 'completed' : ''}`}>
          {task.title}
        </div>
        <StatusBadge status={task.status} />
      </div>

      {task.description && (
        <p className="task-description">{task.description}</p>
      )}

      <div className="task-meta">
        {task.assignee && (
          <span className="assignee-chip">
            <span className="avatar">{task.assignee.charAt(0).toUpperCase()}</span>
            {task.assignee}
          </span>
        )}
        <span className="task-time">{formatDate(task.updated_at)}</span>
      </div>

      <div className="task-actions">
        {task.status !== 'completed' && task.status !== 'cancelled' && (
          <button
            className="btn btn-success btn-sm"
            onClick={handleComplete}
            disabled={loading}
            title="Mark complete"
          >
            ✓ Complete
          </button>
        )}
        {(task.status === 'completed' || task.status === 'cancelled') && (
          <button
            className="btn btn-warning btn-sm"
            onClick={handleReopen}
            disabled={loading}
            title="Reopen task"
          >
            ↺ Reopen
          </button>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={(e) => { e.stopPropagation(); onSelect(task); }}
          title="Edit task"
        >
          ✏ Edit
        </button>
        <button
          className="btn btn-danger btn-sm"
          onClick={handleDelete}
          disabled={loading}
          title="Delete task"
          style={{ marginLeft: 'auto' }}
        >
          🗑
        </button>
      </div>
    </div>
  );
}

// Status selector for quick-update in detail panel
export function StatusOptions() {
  return (
    <>
      {(Object.keys(STATUS_LABELS) as TaskStatus[]).map((s) => (
        <option key={s} value={s}>{STATUS_LABELS[s]}</option>
      ))}
    </>
  );
}
