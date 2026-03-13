import apiClient from './api-client'
import type {
  LLMProvider,
  LLMProviderCreate,
  LLMProviderUpdate,
  LLMProviderList,
  LLMTestRequest,
  LLMTestResponse,
  LLMUsageStats,
  LLMUsageStatsRequest,
  LLMUsageLogList,
} from '@/types'

export const llmProvidersApi = {
  /**
   * List all LLM providers
   */
  async listProviders(params?: {
    skip?: number
    limit?: number
    active_only?: boolean
    provider_type?: string
  }): Promise<LLMProviderList> {
    return apiClient.get<LLMProviderList>('/api/v1/llm-providers', { params })
  },

  /**
   * Get a specific LLM provider by ID
   */
  async getProvider(providerId: string): Promise<LLMProvider> {
    return apiClient.get<LLMProvider>(`/api/v1/llm-providers/${providerId}`)
  },

  /**
   * Create a new LLM provider
   */
  async createProvider(data: LLMProviderCreate): Promise<LLMProvider> {
    return apiClient.post<LLMProvider>('/api/v1/llm-providers', data)
  },

  /**
   * Update an existing LLM provider
   */
  async updateProvider(providerId: string, data: LLMProviderUpdate): Promise<LLMProvider> {
    return apiClient.put<LLMProvider>(`/api/v1/llm-providers/${providerId}`, data)
  },

  /**
   * Delete an LLM provider
   */
  async deleteProvider(providerId: string): Promise<void> {
    return apiClient.delete<void>(`/api/v1/llm-providers/${providerId}`)
  },

  /**
   * Test LLM provider connection
   */
  async testProvider(providerId: string, data?: LLMTestRequest): Promise<LLMTestResponse> {
    return apiClient.post<LLMTestResponse>(`/api/v1/llm-providers/${providerId}/test`, data)
  },

  /**
   * Set a provider as the default
   */
  async setDefaultProvider(providerId: string): Promise<LLMProvider> {
    return apiClient.post<LLMProvider>(`/api/v1/llm-providers/${providerId}/set-default`)
  },

  /**
   * Get usage statistics
   */
  async getUsageStats(params?: LLMUsageStatsRequest): Promise<LLMUsageStats> {
    return apiClient.get<LLMUsageStats>('/api/v1/llm-providers/usage/stats', { params })
  },

  /**
   * Get detailed usage logs
   */
  async getUsageLogs(params?: {
    provider_id?: string
    agent_id?: string
    start_date?: string
    end_date?: string
    status?: string
    skip?: number
    limit?: number
  }): Promise<LLMUsageLogList> {
    return apiClient.get<LLMUsageLogList>('/api/v1/llm-providers/usage/logs', { params })
  },
}

export default llmProvidersApi
