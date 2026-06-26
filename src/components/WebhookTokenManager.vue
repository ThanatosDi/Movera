<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useNotification } from '@/composables/useNotification'
import type { WebhookTokenCreated } from '@/schemas'
import { useWebhookTokenStore } from '@/stores/webhookTokenStore'
import { Ban, Copy, KeyRound, Plus, Trash2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const store = useWebhookTokenStore()
const { tokens, isLoading } = storeToRefs(store)

const newName = ref('')
// 剛建立的 token 明文（僅顯示一次）
const createdToken = ref<WebhookTokenCreated | null>(null)

onMounted(() => {
  store.fetchTokens().catch(() => {})
})

async function handleCreate() {
  const name = newName.value.trim()
  if (!name) return
  try {
    createdToken.value = await store.createToken(name)
    newName.value = ''
  } catch {
    useNotification.showError(t('webhookToken.createFailed'))
  }
}

async function handleRevoke(id: string) {
  try {
    await store.revokeToken(id)
  } catch {
    useNotification.showError(t('webhookToken.revokeFailed'))
  }
}

async function handleDelete(id: string) {
  try {
    await store.deleteToken(id)
  } catch {
    useNotification.showError(t('webhookToken.deleteFailed'))
  }
}

async function copyToken() {
  if (!createdToken.value) return
  await navigator.clipboard.writeText(createdToken.value.token)
  useNotification.showSuccess(t('webhookToken.copied'))
}

function dismissCreated() {
  createdToken.value = null
}
</script>

<template>
  <Card class="border border-border">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <KeyRound class="size-5" />
        {{ t('webhookToken.title') }}
      </CardTitle>
      <CardDescription>{{ t('webhookToken.description') }}</CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- 新增 -->
      <div class="flex gap-2">
        <Input
          v-model="newName"
          :placeholder="t('webhookToken.namePlaceholder')"
          @keyup.enter="handleCreate"
        />
        <Button
          :disabled="!newName.trim()"
          class="shrink-0"
          @click="handleCreate"
        >
          <Plus class="size-4 mr-1" />
          {{ t('webhookToken.create') }}
        </Button>
      </div>

      <!-- 剛建立的 token 明文（僅顯示一次） -->
      <div
        v-if="createdToken"
        class="rounded-md border border-amber-500/50 bg-amber-500/10 p-3 space-y-2"
      >
        <p class="text-sm text-amber-500">{{ t('webhookToken.copyWarning') }}</p>
        <div class="flex items-center gap-2">
          <code class="flex-1 break-all text-sm bg-background rounded px-2 py-1">{{ createdToken.token }}</code>
          <Button
            size="sm"
            variant="outline"
            @click="copyToken"
          >
            <Copy class="size-4" />
          </Button>
        </div>
        <Button
          size="sm"
          variant="ghost"
          @click="dismissCreated"
        >
          {{ t('webhookToken.dismiss') }}
        </Button>
      </div>

      <!-- 清單 -->
      <div
        v-if="tokens.length > 0"
        class="space-y-2"
      >
        <div
          v-for="token in tokens"
          :key="token.id"
          class="flex items-center justify-between rounded-md border border-border px-3 py-2"
        >
          <div>
            <p class="font-medium">{{ token.name }}</p>
            <p class="text-xs text-muted-foreground">
              <span v-if="token.revoked_at" class="text-destructive">{{ t('webhookToken.revoked') }}</span>
              <span v-else class="text-green-500">{{ t('webhookToken.active') }}</span>
            </p>
          </div>
          <Button
            v-if="!token.revoked_at"
            size="sm"
            variant="ghost"
            class="text-destructive"
            @click="handleRevoke(token.id)"
          >
            <Ban class="size-4 mr-1" />
            {{ t('webhookToken.revoke') }}
          </Button>
          <Button
            v-else
            size="sm"
            variant="ghost"
            class="text-destructive"
            @click="handleDelete(token.id)"
          >
            <Trash2 class="size-4 mr-1" />
            {{ t('webhookToken.delete') }}
          </Button>
        </div>
      </div>
      <p
        v-else-if="!isLoading"
        class="text-sm text-muted-foreground text-center py-2"
      >
        {{ t('webhookToken.empty') }}
      </p>
    </CardContent>
  </Card>
</template>
