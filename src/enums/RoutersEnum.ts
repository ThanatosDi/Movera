export const RoutersEnum = {
  Home: '/',
  Login: '/login',
  CreateTask: '/create',
  Tasks: '/tasks',
  TaskDetail: (taskId: string) => `/task/${taskId}`,
  Setting: '/setting',
} as const;

export type RoutersEnum = typeof RoutersEnum[keyof typeof RoutersEnum];