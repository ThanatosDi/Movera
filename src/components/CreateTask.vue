<script setup>
import { Button } from '@/components/ui/button';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { AlertCircle, CheckCircle, Plus } from 'lucide-vue-next';
import { useForm } from 'vee-validate';
import { computed, ref, watch } from 'vue';

const form = useForm({
  // validationSchema: formSchema,
})

// 測試用的檔案名稱
const testFilename = ref('公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4')
const srcRegex = ref('')
const dstRegex = ref('')

// 正規表達式匹配結果
const regexResult = computed(() => {
  if (!srcRegex.value || !testFilename.value) {
    return { isValid: false, matches: [], groups: [], renamedFilename: '' }
  }

  try {
    const regex = new RegExp(srcRegex.value, 'gi')
    const matches = [...testFilename.value.matchAll(regex)]
    
    if (matches.length === 0) {
      return { isValid: false, matches: [], groups: [], renamedFilename: '' }
    }

    const firstMatch = matches[0]
    const groups = firstMatch.slice(1) // 排除完整匹配，只保留群組
    
    // 計算重新命名後的檔案名稱
    let renamedFilename = ''
    if (dstRegex.value) {
      try {
        // 將 Python 風格的 \1, \2, \3 轉換為 JavaScript 風格的 $1, $2, $3
        let jsStyleDstRegex = dstRegex.value.replace(/\\(\d+)/g, '$$$1')
        
        // 使用正規表達式替換匹配的部分
        const sourceRegex = new RegExp(srcRegex.value, 'gi')
        renamedFilename = testFilename.value.replace(sourceRegex, jsStyleDstRegex)
      } catch (e) {
        renamedFilename = '重新命名格式錯誤: ' + e.message
      }
    }

    return {
      isValid: true,
      matches: matches,
      groups: groups,
      renamedFilename: renamedFilename,
      fullMatch: firstMatch[0]
    }
  } catch (error) {
    return { isValid: false, matches: [], groups: [], renamedFilename: '', error: error.message }
  }
})

// 監聽表單變化來更新預覽
watch(() => form.values, (newValues) => {
  if (newValues.SrcFilenameRegex !== undefined) {
    srcRegex.value = newValues.SrcFilenameRegex
  }
  if (newValues.DstFilenameRegex !== undefined) {
    dstRegex.value = newValues.DstFilenameRegex
  }
}, { deep: true, immediate: true })

const onSubmit = form.handleSubmit((values) => {
  console.log('Form submitted!', values)
})

// 測試案例
const testCases = {
  anime1: {
    filename: '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    srcRegex: '公爵千金的家庭教師 - (\\d{2})(v2)? .+\\.mp4',
    dstRegex: '公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  },
  anime2: {
    filename: '[Sakurato] Dan Da Dan (2025) [13][AVC-8bit 1080p AAC][CHT].mp4',
    srcRegex: '.+ Dan Da Dan \\(2025\\) \\[(\\d{2})\\]\\[AVC-8bit 1080p AAC\\]\\[CHT\\]\\.mp4',
    dstRegex: '[Sakurato] Dan Da Dan (2025) [S02E\\1][AVC-8bit 1080p AAC][CHT].mp4'
  },
  movie: {
    filename: 'Movie.Title.2024.1080p.BluRay.x264-GROUP.mkv',
    srcRegex: '(.+)\\.(\\d{4})\\.1080p\\.BluRay\\.x264-(.+)\\.mkv',
    dstRegex: '\\1 (\\2) [1080p BluRay x264-\\3].mkv'
  }
}

const loadTestCase = (caseKey) => {
  const testCase = testCases[caseKey]
  if (testCase) {
    testFilename.value = testCase.filename
    srcRegex.value = testCase.srcRegex
    dstRegex.value = testCase.dstRegex
    
    // 同時更新表單值
    form.setFieldValue('SrcFilenameRegex', testCase.srcRegex)
    form.setFieldValue('DstFilenameRegex', testCase.dstRegex)
  }
}

// 高亮顯示匹配的文字
const highlightedFilename = computed(() => {
  if (!regexResult.value.isValid || !regexResult.value.fullMatch) {
    return testFilename.value
  }
  
  const match = regexResult.value.fullMatch
  const startIndex = testFilename.value.indexOf(match)
  const endIndex = startIndex + match.length
  
  return {
    before: testFilename.value.substring(0, startIndex),
    match: match,
    after: testFilename.value.substring(endIndex)
  }
})
</script>
<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto min-h-0">
    <div class="pt-2 pb-2 col-span-1 col-start-1">
      <h1 class="text-2xl">建立任務</h1>
    </div>
    <div class="bg-gray-800 p-4 rounded-md">
      <form @submit="onSubmit" class="text-white text-lg flex flex-col gap-6">
        <FormField v-slot="{ componentField }" name="TaskName">
          <FormItem>
            <FormLabel class="text-lg">任務名稱</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2 " />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="FileNameInclude">
          <FormItem>
            <FormLabel class="text-lg">檔案名稱包含</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2 " />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="MoveTo">
          <FormItem>
            <FormLabel class="text-lg">移動至</FormLabel>
            <FormControl>
              <Input type="text" v-bind="componentField" class="rounded-full text-lg border-2" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="SrcFilenameRegex">
          <FormItem>
            <FormLabel class="text-lg">檔案名稱正規表示法</FormLabel>
            <FormControl>
              <Input 
                type="text" 
                v-bind="componentField" 
                @input="(e) => { srcRegex = e.target.value; componentField['onInput'](e) }"
                class="rounded-full text-lg border-2" 
                placeholder="例如: 公爵千金的家庭教師 - (\d{2})(v2)? .+\.mp4"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="DstFilenameRegex">
          <FormItem>
            <FormLabel class="text-lg">重新命名正規表示法</FormLabel>
            <FormControl>
              <Input 
                type="text" 
                v-bind="componentField" 
                @input="(e) => { dstRegex = e.target.value; componentField['onInput'](e) }"
                class="rounded-full text-lg border-2" 
                placeholder="例如: 公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <!-- 正規表達式預覽區域 -->
        <div class="bg-gray-700 p-4 rounded-md border-2 border-gray-600">
          <h3 class="text-lg font-semibold mb-4 flex items-center">
            <span class="mr-2">🔍</span>
            正規表達式預覽
          </h3>
          
          <!-- 測試檔案名稱輸入 -->
          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">測試檔案名稱：</label>
            <Input 
              v-model="testFilename" 
              class="bg-gray-800 border-gray-600 text-white"
              placeholder="輸入要測試的檔案名稱"
            />
            <!-- 快速測試案例 -->
            <div class="mt-2 flex flex-wrap gap-2">
              <button 
                @click="loadTestCase('anime1')"
                class="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded"
              >
                動漫案例1
              </button>
              <button 
                @click="loadTestCase('anime2')"
                class="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded"
              >
                動漫案例2
              </button>
              <button 
                @click="loadTestCase('movie')"
                class="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded"
              >
                電影案例
              </button>
            </div>
          </div>

          <!-- 匹配結果顯示 -->
          <div class="space-y-4">
            <!-- 匹配狀態 -->
            <div class="flex items-center space-x-2">
              <CheckCircle v-if="regexResult.isValid" class="w-5 h-5 text-green-400" />
              <AlertCircle v-else class="w-5 h-5 text-red-400" />
              <span :class="regexResult.isValid ? 'text-green-400' : 'text-red-400'">
                {{ regexResult.isValid ? '匹配成功' : (regexResult.error || '無匹配') }}
              </span>
            </div>

            <!-- 高亮顯示匹配結果 -->
            <div v-if="regexResult.isValid" class="bg-gray-800 p-3 rounded border">
              <div class="text-sm text-gray-400 mb-2">匹配結果：</div>
              <div class="font-mono text-sm">
                <span class="text-gray-300">{{ highlightedFilename.before }}</span>
                <span class="bg-yellow-500 text-black px-1 rounded">{{ highlightedFilename.match }}</span>
                <span class="text-gray-300">{{ highlightedFilename.after }}</span>
              </div>
            </div>

            <!-- 群組顯示 -->
            <div v-if="regexResult.isValid && regexResult.groups.length > 0" class="bg-gray-800 p-3 rounded border">
              <div class="text-sm text-gray-400 mb-2">捕獲群組：</div>
              <div class="space-y-1">
                <div v-for="(group, index) in regexResult.groups" :key="index" class="font-mono text-sm">
                  <span class="text-blue-400">群組 {{ index + 1 }}:</span>
                  <span class="text-green-400 ml-2 bg-gray-900 px-2 py-1 rounded">{{ group }}</span>
                </div>
              </div>
            </div>

            <!-- 重新命名預覽 -->
            <div v-if="regexResult.isValid && regexResult.renamedFilename" class="bg-gray-800 p-3 rounded border">
              <div class="text-sm text-gray-400 mb-2">重新命名後：</div>
              <div class="font-mono text-sm">
                <span class="text-green-400">{{ regexResult.renamedFilename }}</span>
              </div>
            </div>

            <!-- 說明文字 -->
            <div class="text-xs text-gray-500 bg-gray-800 p-3 rounded border">
              <div class="mb-2"><strong>使用說明：</strong></div>
              <ul class="space-y-1 list-disc list-inside">
                <li>在「檔案名稱正規表示法」中使用括號 () 來建立捕獲群組</li>
                <li>在「重新命名正規表示法」中使用 \1, \2, \3 等來引用對應的群組</li>
                <li>例如：(\d{2}) 會捕獲兩位數字，在重新命名時用 \1 引用</li>
                <li>可以在上方修改測試檔案名稱來驗證不同的情況</li>
                <li>點擊上方的測試案例按鈕可以快速載入範例</li>
              </ul>
              <div class="mt-3 pt-2 border-t border-gray-600">
                <div class="mb-1"><strong>群組引用範例：</strong></div>
                <div class="text-xs space-y-1">
                  <div><code>(\d{2})</code> → <code>\1</code> (捕獲兩位數字)</div>
                  <div><code>(.+)</code> → <code>\1</code> (捕獲任意字符)</div>
                  <div><code>(\d{4})</code> → <code>\1</code> (捕獲四位數字，如年份)</div>
                </div>
              </div>
              <div class="mt-3 pt-2 border-t border-gray-600">
                <div class="mb-1"><strong>常用正規表達式符號：</strong></div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div><code>\d</code> - 數字 (0-9)</div>
                  <div><code>\w</code> - 字母數字</div>
                  <div><code>+</code> - 一個或多個</div>
                  <div><code>*</code> - 零個或多個</div>
                  <div><code>?</code> - 零個或一個</div>
                  <div><code>\.</code> - 點號字面值</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 提交按鈕區域 -->
        <div class="mt-6 pt-4 border-t border-gray-600">
          <Button type="submit"
            class="bg-green-400 hover:bg-green-400 text-base text-black font-bold py-2 px-4 rounded-full">
            <Plus class="w-4 h-4 mr-2" />新增任務
          </Button>
        </div>
      </form>
    </div>
    
    <!-- 底部間距和頁腳 -->
    <div class="mt-8 pt-6 border-t border-gray-700">
      <div class="text-center text-gray-500 text-sm">
        <p>設定完成後，系統將自動監控指定資料夾並處理符合條件的檔案</p>
      </div>
    </div>
    
    <!-- 確保底部有足夠間距 -->
    <div class="pb-6"></div>
  </main>
</template>