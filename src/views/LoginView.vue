<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RoutersEnum } from '@/enums/RoutersEnum'
import { ApiError } from '@/schemas/errors'
import { useAuthStore } from '@/stores/authStore'
import { LogIn, ShieldCheck } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const isSetup = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

onMounted(async () => {
  try {
    isSetup.value = await authStore.fetchStatus()
  } catch {
    // 無法取得狀態時預設為登入模式
    isSetup.value = false
  }
})

async function handleSubmit() {
  errorMessage.value = null
  if (!username.value.trim() || !password.value) return
  isSubmitting.value = true
  try {
    if (isSetup.value) {
      await authStore.setup(username.value.trim(), password.value)
    } else {
      await authStore.login(username.value.trim(), password.value)
    }
    router.replace(RoutersEnum.Home)
  } catch (e) {
    if (e instanceof ApiError && e.statusCode === 401) {
      errorMessage.value = t('login.invalidCredentials')
    } else {
      errorMessage.value = t('login.failed')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="min-h-screen flex items-center justify-center bg-background p-4">
    <Card class="w-full max-w-sm border border-border">
      <CardHeader class="text-center">
        <CardTitle class="flex items-center justify-center gap-2 text-2xl">
          <ShieldCheck class="size-6" />
          Movera
        </CardTitle>
        <CardDescription>
          {{ isSetup ? t('login.setupSubtitle') : t('login.subtitle') }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          class="space-y-4"
          @submit.prevent="handleSubmit"
        >
          <div class="space-y-2">
            <Label for="username">{{ t('login.username') }}</Label>
            <Input
              id="username"
              v-model="username"
              autocomplete="username"
              :placeholder="t('login.usernamePlaceholder')"
            />
          </div>
          <div class="space-y-2">
            <Label for="password">{{ t('login.password') }}</Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              :autocomplete="isSetup ? 'new-password' : 'current-password'"
              :placeholder="t('login.passwordPlaceholder')"
            />
          </div>
          <p
            v-if="errorMessage"
            class="text-sm text-destructive"
          >
            {{ errorMessage }}
          </p>
          <Button
            type="submit"
            class="w-full"
            :disabled="isSubmitting || !username.trim() || !password"
          >
            <LogIn class="size-4 mr-2" />
            {{ isSetup ? t('login.setupSubmit') : t('login.submit') }}
          </Button>
        </form>
      </CardContent>
    </Card>
  </main>
</template>
