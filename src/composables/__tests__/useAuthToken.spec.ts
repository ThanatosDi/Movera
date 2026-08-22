/**
 * useAuthToken 測試：JWT exp 的前端過期判斷。
 */

import { beforeEach, describe, expect, it } from 'vitest'
import {
  clearToken,
  discardTokenIfExpired,
  getToken,
  isTokenExpired,
  setToken,
} from '@/composables/useAuthToken'

/** 組出僅供解析用的 JWT（簽章為假值，前端不驗簽）。 */
function makeToken(payload: Record<string, unknown>): string {
  const encode = (value: unknown) =>
    btoa(JSON.stringify(value)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `${encode({ alg: 'HS256', typ: 'JWT' })}.${encode(payload)}.signature`
}

const nowSeconds = () => Math.floor(Date.now() / 1000)

describe('isTokenExpired', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('尚未到期時回傳 false', () => {
    expect(isTokenExpired(makeToken({ sub: 'admin', exp: nowSeconds() + 3600 }))).toBe(false)
  })

  it('已超過 exp 且超出時鐘偏移寬容時回傳 true', () => {
    expect(isTokenExpired(makeToken({ sub: 'admin', exp: nowSeconds() - 300 }))).toBe(true)
  })

  it('剛過期但仍在時鐘偏移寬容內時回傳 false', () => {
    expect(isTokenExpired(makeToken({ sub: 'admin', exp: nowSeconds() - 10 }))).toBe(false)
  })

  it('無 token 時回傳 true', () => {
    expect(isTokenExpired(null)).toBe(true)
  })

  it('格式不正確時回傳 true', () => {
    expect(isTokenExpired('not-a-jwt')).toBe(true)
  })

  it('payload 缺少 exp 時回傳 true', () => {
    expect(isTokenExpired(makeToken({ sub: 'admin' }))).toBe(true)
  })

  it('未傳入參數時改讀 localStorage 中的憑證', () => {
    setToken(makeToken({ sub: 'admin', exp: nowSeconds() + 3600 }))
    expect(isTokenExpired()).toBe(false)

    setToken(makeToken({ sub: 'admin', exp: nowSeconds() - 300 }))
    expect(isTokenExpired()).toBe(true)
  })
})

describe('discardTokenIfExpired', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('過期時清除憑證並回傳 true', () => {
    setToken(makeToken({ sub: 'admin', exp: nowSeconds() - 300 }))

    expect(discardTokenIfExpired()).toBe(true)
    expect(getToken()).toBeNull()
  })

  it('仍有效時保留憑證並回傳 false', () => {
    const token = makeToken({ sub: 'admin', exp: nowSeconds() + 3600 })
    setToken(token)

    expect(discardTokenIfExpired()).toBe(false)
    expect(getToken()).toBe(token)
  })

  it('無憑證時回傳 true', () => {
    clearToken()
    expect(discardTokenIfExpired()).toBe(true)
  })
})
