import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse, ApiError, AuthTokens } from '@/types'

class ApiClient {
  private client: AxiosInstance
  private refreshTokenPromise: Promise<AuthTokens> | null = null

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getAccessToken()
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.refreshTokenPromise) {
            try {
              await this.refreshTokenPromise
              return this.client(originalRequest)
            } catch {
              return Promise.reject(error)
            }
          }

          originalRequest._retry = true

          try {
            this.refreshTokenPromise = this.refreshAccessToken()
            await this.refreshTokenPromise
            this.refreshTokenPromise = null
            return this.client(originalRequest)
          } catch (refreshError) {
            this.refreshTokenPromise = null
            this.clearAuth()
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('refresh_token')
  }

  private setAuthTokens(tokens: AuthTokens): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  private clearAuth(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.dispatchEvent(new Event('auth:logout'))
  }

  private async refreshAccessToken(): Promise<AuthTokens> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await axios.post<ApiResponse<AuthTokens>>(
      `${this.client.defaults.baseURL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken }
    )

    const tokens = response.data.data
    this.setAuthTokens(tokens)
    return tokens
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/api/v1/auth/login', {
      email,
      password,
    })

    const tokens = response.data.data
    this.setAuthTokens(tokens)
    return tokens
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout')
    } finally {
      this.clearAuth()
    }
  }

  async register(email: string, password: string, full_name: string): Promise<AuthTokens> {
    const response = await this.client.post<ApiResponse<AuthTokens>>('/api/v1/auth/register', {
      email,
      password,
      full_name,
    })

    const tokens = response.data.data
    this.setAuthTokens(tokens)
    return tokens
  }

  async getCurrentUser(): Promise<{ id: string; email: string; full_name: string; role: string }> {
    const response = await this.client.get<ApiResponse<{ id: string; email: string; full_name: string; role: string }>>(
      '/api/v1/auth/me'
    )
    return response.data.data
  }

  get<T>(url: string, config?: object): Promise<T> {
    return this.client.get<T>(url, config).then((response) => response.data)
  }

  post<T>(url: string, data?: unknown, config?: object): Promise<T> {
    return this.client.post<T>(url, data, config).then((response) => response.data)
  }

  put<T>(url: string, data?: unknown, config?: object): Promise<T> {
    return this.client.put<T>(url, data, config).then((response) => response.data)
  }

  patch<T>(url: string, data?: unknown, config?: object): Promise<T> {
    return this.client.patch<T>(url, data, config).then((response) => response.data)
  }

  delete<T>(url: string, config?: object): Promise<T> {
    return this.client.delete<T>(url, config).then((response) => response.data)
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const apiClient = new ApiClient(API_URL)
export default apiClient
