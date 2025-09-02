export interface Task {
  id: string;
  name: string;
  include: string;
  move_to: string
  src_filename: string | null;
  dst_filename: string | null;
  rename_rule: 'regex' | 'parse' | null;
  enabled: boolean;
  created_at: string; // ISO 8601 date string
}

export type TaskCreate = Omit<Task, 'id' | 'created_at'>;
export type TaskUpdate = Omit<Task, 'id' | 'created_at'>;

export interface Log {
  id: number;
  task_id: number;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  timestamp: string; // ISO 8601 date string
}

export interface TaskStats {
  enabled: number;
  disabled: number;
  total: number;
}

export interface HealthStatus {
  status: 'ok';
}

export interface NotificationOptions {
  html?: boolean;
  position?: string;
  duration?: number;
}

export type ToastType = 'success' | 'error' | 'info' | 'warning'