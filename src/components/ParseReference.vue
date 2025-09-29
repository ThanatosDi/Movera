<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BookMarked } from 'lucide-vue-next';
import { useI18n } from 'vue-i18n';

const { t } = useI18n()
</script>

<template>
  <Card class="bg-gray-800 border-gray-700 text-white">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <BookMarked class="w-5 h-5 text-yellow-400" />
        {{ t('components.parseReference.title') }}</CardTitle>
      <CardDescription>
        {{ t('components.parseReference.description') }}
        <a
          href="https://github.com/r1chardj0n3s/parse#format-specification"
          target="_blank"
          class="text-blue-400 hover:underline"
        >
          {{ t('components.parseReference.documentationLink') }}
        </a>
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <div>
        <h3 class="text-lg font-semibold">{{ t('components.parseReference.example1.title') }}</h3>
        <p>{{ t('components.parseReference.example1.description') }}</p>
        <ul class="list-disc list-inside pl-4 mt-2 space-y-1">
          <li>
            <code class="bg-gray-700 p-1 rounded">{{ t('components.parseReference.example1.step1.src') }}</code>
            <span>{{ t('components.parseReference.example1.step1.description') }}</span>
            <code class="bg-gray-700 p-1 rounded">The.Big.Bang.Theory.S01E01.mkv</code>
          </li>
          <li>
            <code class="bg-gray-700 p-1 rounded">{{ t('components.parseReference.example1.step2.dst') }}</code>
            <span>{{ t('components.parseReference.example1.step2.description') }}</span>
            <code class="bg-gray-700 p-1 rounded">The.Big.Bang.Theory S01E01.mkv</code>
          </li>
        </ul>
      </div>
      <div>
        <h3 class="text-lg font-semibold">{{ t('components.parseReference.example2.title') }}</h3>
        <p>{{ t('components.parseReference.example2.description') }}</p>
        <ul class="list-disc list-inside pl-4 mt-2 space-y-1">
          <li>
            <code class="bg-gray-700 p-1 rounded">{{ t('components.parseReference.example2.step1.src') }}</code>
            <span>{{ t('components.parseReference.example2.step1.description') }}</span>
            <code class="bg-gray-700 p-1 rounded">[SubsPlease] Jujutsu Kaisen - 01 (1080p) [F02B96E2].mkv</code>
          </li>
          <li>
            <code class="bg-gray-700 p-1 rounded">{{ t('components.parseReference.example2.step2.dst') }}</code>
            <span>{{ t('components.parseReference.example2.step2.description') }}</span>
            <code class="bg-gray-700 p-1 rounded">Jujutsu Kaisen - S01E01.mkv</code>
          </li>
        </ul>
      </div>
    </CardContent>
  </Card>
</template>
