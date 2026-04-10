/** Detail shape returned by the backend on error responses. */
export interface ApiErrorDetail {
  detail?: string
  message?: string
  error?: string
}

/**
 * Typed error thrown by the HTTP service when an API request fails.
 *
 * Use `instanceof ApiError` for type-safe narrowing in catch blocks.
 */
export class ApiError extends Error {
  /** HTTP status code of the failed response. */
  readonly statusCode: number
  /** Parsed error detail from the response body. */
  readonly detail: ApiErrorDetail

  constructor(statusCode: number, detail: ApiErrorDetail) {
    super(detail.detail || detail.message || 'Network request failed')
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.detail = detail
  }
}
