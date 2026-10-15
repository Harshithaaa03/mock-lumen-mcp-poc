import { useState } from 'react';
import type { Task } from '../types/task';
import type { TaskStatus } from '../types/task';
import { taskApi, STATUS_LABELS } from '../api/tasks';
import { StatusBadge } from './StatusBadge';

interface TaskDetailPanelProps {
  task: Task;
  onUpdated: (task: Task) => void;
  onDeleted: (id: string) => void;
  onClose: () => void;
  onToast: (msg: string, type: 'success' | 'error') => void;
}

function formatFull(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    weekday: 'short',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function TaskDetailPanel({ task, onUpdated, onDeleted, onClose, onToast }: TaskDetailPanelProps) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description ?? '');
  const [assignee, setAssignee] = useState(task.assignee ?? '');
  const [status, setStatus] = useState<TaskStatus>(task.status);
  const [saving, setSaving] = useState(false);

  // Sync if task prop changes
  if (!editing && (task.title !== title || task.status !== status)) {
    setTitle(task.title);
    setDescription(task.description ?? '');
    setAssignee(task.assignee ?? '');
    setStatus(task.status);
  }

  const handleSave = async () => {
    if (!title.trim()) return;
    setSaving(true);
    try {
      const updated = await taskApi.update(task.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        assignee: assignee.trim() || undefined,
        status,
      });
      onUpdated(updated);
      setEditing(false);
      onToast('Task updated ✓', 'success');
    } catch {
      onToast('Failed to save changes', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${task.title}"?`)) return;
    try {
      await taskApi.delete(task.id);
      onDeleted(task.id);
      onToast('Task deleted', 'success');
    } catch {
      onToast('Failed to delete task', 'error');
    }
  };

  return (
    <div className="detail-panel">
      <div className="detail-panel-title">
        <StatusBadge status={task.status} />
        <span style={{ flex: 1 }}>Task Details</span>
        <button className="btn btn-ghost btn-icon" onClick={onClose} title="Close panel">✕</button>
      </div>

      {editing ? (
        <div className="form">
          <div className="form-group">
            <label className="form-label" htmlFor="edit-title">Title *</label>
            <input
              id="edit-title"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="edit-description">Description</label>
            <textarea
              id="edit-description"
              className="form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="edit-assignee">Assignee (demo)</label>
            <input
              id="edit-assignee"
              className="form-input"
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
              placeholder="Enter assignee name"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="edit-status">Status</label>
            <select
              id="edit-status"
              className="form-select"
              value={status}
              onChange={(e) => setStatus(e.target.value as TaskStatus)}
            >
              {(Object.keys(STATUS_LABELS) as TaskStatus[]).map((s) => (
                <option key={s} value={s}>{STATUS_LABELS[s]}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saving || !title.trim()}
            >
              {saving ? 'Saving…' : '💾 Save Changes'}
            </button>
            <button className="btn btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <>
          <div className="detail-field">
            <div className="detail-label">Title</div>
            <div className="detail-value" style={{ fontSize: '1.1rem', fontWeight: 600 }}>{task.title}</div>
          </div>

          {task.description && (
            <div className="detail-field">
              <div className="detail-label">Description</div>
              <div className="detail-value" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                {task.description}
              </div>
            </div>
          )}

          <div className="detail-field">
            <div className="detail-label">Assignee</div>
            <div className="detail-value">
              {task.assignee
                ? <span className="assignee-chip" style={{ display: 'inline-flex' }}>
                    <span className="avatar">{task.assignee.charAt(0).toUpperCase()}</span>
                    {task.assignee}
                  </span>
                : <span style={{ color: 'var(--color-text-muted)' }}>Unassigned</span>
              }
            </div>
          </div>

          <div className="detail-field">
            <div className="detail-label">Task ID</div>
            <div className="detail-value" style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
              {task.id}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="detail-field">
              <div className="detail-label">Created</div>
              <div className="detail-value" style={{ fontSize: '0.82rem', color: 'var(--color-text-secondary)' }}>
                {formatFull(task.created_at)}
              </div>
            </div>
            <div className="detail-field">
              <div className="detail-label">Last Updated</div>
              <div className="detail-value" style={{ fontSize: '0.82rem', color: 'var(--color-text-secondary)' }}>
                {formatFull(task.updated_at)}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => setEditing(true)} style={{ flex: 1 }}>
              ✏ Edit Task
            </button>
            <button className="btn btn-danger" onClick={handleDelete}>🗑 Delete</button>
          </div>
        </>
      )}
    </div>
  );
}
