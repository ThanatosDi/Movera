export interface TaskStats {
  enabled: number;
  disabled: number;
  total: number;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
}

export interface TagCreate {
  name: string;
  color: string;
}

export type TagUpdate = TagCreate;

export interface PresetRule {
  id: string;
  name: string;
  rule_type: 'parse' | 'regex';
  field_type: 'src' | 'dst';
  pattern: string;
  created_at: string;
}

export type PresetRuleCreate = Omit<PresetRule, 'id' | 'created_at'>;
export type PresetRuleUpdate = PresetRuleCreate;

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
  tags: Tag[];
}

export type TaskCreate = Omit<Task, 'id' | 'created_at' | 'logs' | 'tags'> & { tag_ids: string[] };
export type TaskUpdate = Omit<Task, 'id' | 'created_at' | 'logs' | 'tags'> & { tag_ids: string[] };

export interface Log {
  id: number;
  task_id: number;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  timestamp: string; // ISO 8601 date string
}

export type ToastPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';

export interface NotificationOptions {
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
