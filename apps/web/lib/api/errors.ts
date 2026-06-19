export interface ApiErrorResponse {
  detail: string
  error_code: string
  request_id: string
  timestamp: string
}

export class ApiError extends Error {
  public readonly statusCode: number
  public readonly errorCode: string
  public readonly requestId: string
  public readonly timestamp: string

  constructor(message: string, statusCode: number, errorCode: string, requestId: string, timestamp: string) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.errorCode = errorCode
    this.requestId = requestId
    this.timestamp = timestamp
  }

  static fromResponse(response: ApiErrorResponse, statusCode: number): ApiError {
    return new ApiError(response.detail, statusCode, response.error_code, response.request_id, response.timestamp)
  }

  get isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500
  }

  get isServerError(): boolean {
    return this.statusCode >= 500
  }

  get isNotFound(): boolean {
    return this.statusCode === 404
  }

  get isRateLimited(): boolean {
    return this.statusCode === 429
  }

  get isUnauthorized(): boolean {
    return this.statusCode === 401
  }

  get isForbidden(): boolean {
    return this.statusCode === 403
  }

  get isValidationError(): boolean {
    return this.statusCode === 422
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network request failed. Check your internet connection.') {
    super(message)
    this.name = 'NetworkError'
  }
}

export class TimeoutError extends Error {
  constructor(message = 'Request timed out. Please try again.') {
    super(message)
    this.name = 'TimeoutError'
  }
}
