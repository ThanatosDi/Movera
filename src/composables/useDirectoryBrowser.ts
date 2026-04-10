import { request } from '@/composables/useHttpService'
import type { DirectoryItem, DirectoryListResponse } from '@/schemas'
import { ref } from 'vue'

export function useDirectoryBrowser() {
  const directories = ref<DirectoryItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDirectories(path?: string) {
    loading.value = true
    error.value = null

    try {
      const endpoint = path
        ? `/api/v1/directories?path=${encodeURIComponent(path)}`
        : '/api/v1/directories'

      const response = await request<DirectoryListResponse>('GET', endpoint)
      directories.value = response?.directories ?? []
    } catch (e) {
      error.value = (e as Error).message
      directories.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    directories,
    loading,
    error,
    fetchDirectories,
  }
}
