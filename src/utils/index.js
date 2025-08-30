import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * 合併 CSS 類名
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

/**
 * 格式化日期時間
 */
export function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

/**
 * 延遲執行
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 防抖函數
 */
export function debounce(func, wait) {
  let timeout = null

  return (...args) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 節流函數
 */
export function throttle(func, limit) {
  let inThrottle = false

  return (...args) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * 深拷貝對象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime())
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item))
  }

  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }

  return obj
}

/**
 * 檢查是否為空值
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 生成隨機 ID
 */
export function generateId() {
  return Math.random().toString(36).substr(2, 9)
}

/**
 * 正規表達式預覽工具
 */
export function previewRegex(srcRegex, dstRegex, testFilename) {
  if (!srcRegex || !testFilename) {
    return { isValid: false, matches: [], groups: [], renamedFilename: '' }
  }

  try {
    const regex = new RegExp(srcRegex, 'gi')
    const matches = [...testFilename.matchAll(regex)]

    if (matches.length === 0) {
      return { isValid: false, matches: [], groups: [], renamedFilename: '' }
    }

    const firstMatch = matches[0]
    const groups = firstMatch.slice(1)
    let renamedFilename = ''

    if (dstRegex) {
      try {
        // 將 Python 風格的 \1, \2 轉換為 JavaScript 風格的 $1, $2
        const jsStyleDstRegex = dstRegex.replace(/\\(\d+)/g, '$$$1')
        const sourceRegex = new RegExp(srcRegex, 'gi')
        renamedFilename = testFilename.replace(sourceRegex, jsStyleDstRegex)
      } catch (e) {
        renamedFilename = `重新命名格式錯誤: ${e.message}`
      }
    }

    return {
      isValid: true,
      matches,
      groups,
      renamedFilename,
      fullMatch: firstMatch[0],
    }
  } catch (error) {
    return {
      isValid: false,
      matches: [],
      groups: [],
      renamedFilename: '',
      error: error.message,
    }
  }
}

/**
 * 高亮顯示匹配的文字
 */
export function highlightMatch(text, match) {
  if (!match) {
    return { before: text, match: '', after: '' }
  }

  const startIndex = text.indexOf(match)
  if (startIndex === -1) {
    return { before: text, match: '', after: '' }
  }

  const endIndex = startIndex + match.length
  return {
    before: text.substring(0, startIndex),
    match: match,
    after: text.substring(endIndex),
  }
}

/**
 * 驗證正規表達式
 */
export function validateRegex(pattern) {
  try {
    new RegExp(pattern)
    return true
  } catch {
    return false
  }
}

/**
 * 安全的 JSON 解析
 */
export function safeJsonParse(jsonString, fallback) {
  try {
    return JSON.parse(jsonString)
  } catch {
    return fallback
  }
}

/**
 * 格式化檔案大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}


/**
 * 判斷 HEX 色碼是否為亮色系
 */
export function isColorLight(hexColor) {
  if (!hexColor)
    return false
  const color = hexColor.charAt(0) === '#' ? hexColor.slice(1) : hexColor
  const r = Number.parseInt(color.substring(0, 2), 16)
  const g = Number.parseInt(color.substring(2, 4), 16)
  const b = Number.parseInt(color.substring(4, 6), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b)
  return luminance > 149
}