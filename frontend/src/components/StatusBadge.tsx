import type { TaskStatus } from '../types/task';
import { STATUS_LABELS } from '../api/tasks';

interface StatusBadgeProps {
  status: TaskStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge ${status}`}>
      <span className="status-dot" />
      {STATUS_LABELS[status]}
    </span>
  );
}
