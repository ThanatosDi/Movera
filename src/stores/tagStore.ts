import { request } from '@/composables/useHttpService'
import type { Tag, TagCreate, TagUpdate } from '@/schemas'
import { defineStore } from 'pinia'
import { ref } from 'vue'


export const useTagStore = defineStore('tagStore', () => {
  const tags = ref<Tag[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  async function fetchTags() {
    isLoading.value = true
    error.value = null
    try {
      const response = await request<Tag[]>('GET', '/api/v1/tags')
      tags.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createTag(tagData: TagCreate): Promise<Tag> {
    try {
      const response = await request<Tag>('POST', '/api/v1/tags', tagData)
      tags.value.push(response)
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function updateTag(tagId: string, tagData: TagUpdate): Promise<Tag> {
    try {
      const response = await request<Tag>('PUT', `/api/v1/tags/${tagId}`, tagData)
      const index = tags.value.findIndex(t => t.id === tagId)
      if (index !== -1) {
        tags.value[index] = response
      }
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function deleteTag(tagId: string) {
    try {
      await request('DELETE', `/api/v1/tags/${tagId}`)
      tags.value = tags.value.filter(t => t.id !== tagId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  return {
    tags,
    isLoading,
    error,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
  }
})
