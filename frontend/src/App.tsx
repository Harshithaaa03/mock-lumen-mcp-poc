import { useState, useEffect, useCallback } from 'react';
import type { Task, FilterParams, TaskStatus } from './types/task';
import { taskApi, STATUS_LABELS } from './api/tasks';
import { TaskCard } from './components/TaskCard';
import { TaskDetailPanel } from './components/TaskDetailPanel';
import './index.css';

// ===== Toast system =====
interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

let toastCounter = 0;

export default function App() {
  // Task list state
  const [tasks, setTasks] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filters, setFilters] = useState<FilterParams>({ status: '', assignee: '' });

  // Selected task for detail panel
  const [selected, setSelected] = useState<Task | null>(null);

  // Create form
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newAssignee, setNewAssignee] = useState('');
  const [newStatus, setNewStatus] = useState<TaskStatus>('todo');
  const [creating, setCreating] = useState(false);

  // Toasts
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    const id = ++toastCounter;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  }, []);

  // Fetch tasks
  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await taskApi.list({
        status: filters.status || undefined,
        assignee: filters.assignee || undefined,
      } as FilterParams);
      setTasks(result.items);
      setTotal(result.total);
    } catch {
      setError('Failed to load tasks. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { loadTasks(); }, [loadTasks]);

  // Create task
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const task = await taskApi.create({
        title: newTitle.trim(),
        description: newDescription.trim() || undefined,
        assignee: newAssignee.trim() || undefined,
        status: newStatus,
      });
      setTasks((prev) => [task, ...prev]);
      setTotal((t) => t + 1);
      setNewTitle('');
      setNewDescription('');
      setNewAssignee('');
      setNewStatus('todo');
      showToast('Task created ✓', 'success');
    } catch {
      showToast('Failed to create task', 'error');
    } finally {
      setCreating(false);
    }
  };

  // Update task in list
  const handleUpdated = useCallback((updated: Task) => {
    setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    setSelected(updated);
  }, []);

  // Delete task from list
  const handleDeleted = useCallback((id: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
    setTotal((t) => t - 1);
    if (selected?.id === id) setSelected(null);
  }, [selected]);

  // Stats
  const stats = {
    total: tasks.length,
    todo: tasks.filter((t) => t.status === 'todo').length,
    inProgress: tasks.filter((t) => t.status === 'in_progress').length,
    completed: tasks.filter((t) => t.status === 'completed').length,
  };

  return (
    <div className="app">
      {/* ===== Header ===== */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">✓</div>
            TaskFlow
            <span className="logo-badge">POC</span>
          </div>
          <div className="header-stats">
            <span className="stat-chip">
              <strong>{stats.total}</strong> visible
            </span>
            <span className="stat-chip">
              <span style={{ color: '#fbbf24' }}>●</span>
              <strong>{stats.inProgress}</strong> in progress
            </span>
            <span className="stat-chip">
              <span style={{ color: '#34d399' }}>●</span>
              <strong>{stats.completed}</strong> done
            </span>
          </div>
        </div>
      </header>

      {/* ===== Main layout ===== */}
      <main className="main">
        {/* ===== Sidebar ===== */}
        <aside className="sidebar">
          {/* Create form */}
          <div className="card">
            <h2 className="card-title">➕ New Task</h2>
            <form className="form" onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label" htmlFor="new-title">Title *</label>
                <input
                  id="new-title"
                  className="form-input"
                  placeholder="What needs to be done?"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-description">Description</label>
                <textarea
                  id="new-description"
                  className="form-textarea"
                  placeholder="Add details…"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-assignee">Assignee (demo)</label>
                <input
                  id="new-assignee"
                  className="form-input"
                  placeholder="User name (no auth in POC)"
                  value={newAssignee}
                  onChange={(e) => setNewAssignee(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-status">Initial Status</label>
                <select
                  id="new-status"
                  className="form-select"
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as TaskStatus)}
                >
                  {(Object.keys(STATUS_LABELS) as TaskStatus[]).map((s) => (
                    <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={creating || !newTitle.trim()}
              >
                {creating ? 'Creating…' : '+ Create Task'}
              </button>
            </form>
          </div>

          {/* Filters */}
          <div className="card">
            <h2 className="card-title">🔍 Filter Tasks</h2>
            <div className="filter-row">
              <div className="form-group">
                <label className="form-label" htmlFor="filter-status">Status</label>
                <select
                  id="filter-status"
                  className="form-select"
                  value={filters.status}
                  onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value as TaskStatus | '' }))}
                >
                  <option value="">All statuses</option>
                  {(Object.keys(STATUS_LABELS) as TaskStatus[]).map((s) => (
                    <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="filter-assignee">Assignee</label>
                <input
                  id="filter-assignee"
                  className="form-input"
                  placeholder="Filter by name"
                  value={filters.assignee}
                  onChange={(e) => setFilters((f) => ({ ...f, assignee: e.target.value }))}
                />
              </div>
            </div>
            <button
              className="btn btn-ghost"
              style={{ width: '100%' }}
              onClick={() => setFilters({ status: '', assignee: '' })}
            >
              Clear Filters
            </button>
          </div>
        </aside>

        {/* ===== Task list + detail ===== */}
        <section className="task-list-area">
          <div className="task-list-header">
            <h1 className="task-list-title">Tasks</h1>
            <span className="task-count">{total} total</span>
          </div>

          {error && (
            <div className="error-banner">⚠ {error}</div>
          )}

          {loading ? (
            <div className="loading-wrapper">
              <div className="spinner" />
              <span>Loading tasks…</span>
            </div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <h3>No tasks yet</h3>
              <p>Create your first task using the form on the left.</p>
            </div>
          ) : (
            <>
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isSelected={selected?.id === task.id}
                  onSelect={setSelected}
                  onUpdated={handleUpdated}
                  onDeleted={handleDeleted}
                  onToast={showToast}
                />
              ))}
            </>
          )}

          {selected && (
            <div style={{ marginTop: '1.5rem' }}>
              <TaskDetailPanel
                task={selected}
                onUpdated={handleUpdated}
                onDeleted={handleDeleted}
                onClose={() => setSelected(null)}
                onToast={showToast}
              />
            </div>
          )}
        </section>
      </main>

      {/* ===== Toast container ===== */}
      <div className="toast-container" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.type === 'success' ? '✓' : '✕'} {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}
