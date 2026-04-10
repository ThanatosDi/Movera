export interface TaskStats {
  enabled: number;
  disabled: number;
  total: number;
}

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
  logs: Log[];
}

export type TaskCreate = Omit<Task, 'id' | 'created_at' | 'logs'>;
export type TaskUpdate = Omit<Task, 'id' | 'created_at' | 'logs'>;

export interface Log {
  id: number;
  task_id: number;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  timestamp: string; // ISO 8601 date string
}

export type ToastPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';

export interface NotificationOptions {
  html?: boolean;
  position?: ToastPosition;
  duration?: number;
}

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Settings {
  timezone: string;
  locale: string;
  allowed_directories?: string[];
}

export interface DirectoryItem {
  name: string;
  path: string;
  has_children: boolean;
}

export interface DirectoryListResponse {
  directories: DirectoryItem[];
}
