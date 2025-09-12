import type { Settings } from "@/schemas";
import { request } from "./api";


export const settingService = {
  getAll(): Promise<Settings> {
    return request<Settings>('GET', `/api/v1/settings`);
  },
  update(settings: Settings): Promise<Settings> {
    return request<Settings>('PUT', `/api/v1/settings`, settings);
  },

};