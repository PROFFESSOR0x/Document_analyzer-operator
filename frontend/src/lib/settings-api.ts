/**
 * Settings API client for managing application configuration.
 */

import type {
  ApplicationSetting,
  ApplicationSettingList,
  SettingCategory,
  SettingAuditLog,
  SettingAuditLogList,
  BulkSettingsUpdate,
  SettingsExport,
} from '@/types'
import { apiClient } from './api-client'

/**
 * Get all settings, optionally filtered by category.
 * @param category - Optional category filter
 * @returns Promise with list of settings
 */
export async function getSettings(category?: string): Promise<ApplicationSetting[]> {
  const url = category
    ? `/api/v1/settings/category/${encodeURIComponent(category)}`
    : '/api/v1/settings'
  
  const response = await apiClient.get<ApiResponse<ApplicationSettingList>>(url)
  return response.data.settings
}

/**
 * Get a single setting by key.
 * @param key - Setting key
 * @returns Promise with setting details
 */
export async function getSetting(key: string): Promise<ApplicationSetting> {
  const response = await apiClient.get<ApiResponse<ApplicationSetting>>(
    `/api/v1/settings/${encodeURIComponent(key)}`
  )
  return response.data
}

/**
 * Update a setting.
 * @param key - Setting key
 * @param value - New value
 * @param reason - Optional reason for the change
 * @returns Promise with updated setting
 */
export async function updateSetting(
  key: string,
  value: string,
  reason?: string
): Promise<ApplicationSetting> {
  const response = await apiClient.put<ApiResponse<ApplicationSetting>>(
    `/api/v1/settings/${encodeURIComponent(key)}`,
    {
      value,
      change_reason: reason,
    }
  )
  return response.data
}

/**
 * Bulk update multiple settings.
 * @param settings - Dictionary of setting key to value
 * @param reason - Optional reason for the changes
 * @returns Promise with update results
 */
export async function bulkUpdateSettings(
  settings: Record<string, string>,
  reason?: string
): Promise<Record<string, boolean>> {
  const response = await apiClient.put<ApiResponse<Record<string, boolean>>>(
    '/api/v1/settings/bulk',
    {
      settings,
      change_reason: reason,
    }
  )
  return response.data
}

/**
 * Reset a setting to its default value.
 * @param key - Setting key
 * @returns Promise with reset setting
 */
export async function resetSetting(key: string): Promise<ApplicationSetting> {
  const response = await apiClient.post<ApiResponse<ApplicationSetting>>(
    `/api/v1/settings/${encodeURIComponent(key)}/reset`
  )
  return response.data
}

/**
 * Get audit log for a setting.
 * @param key - Setting key
 * @param limit - Maximum number of entries (default: 50)
 * @returns Promise with audit log entries
 */
export async function getAuditLog(
  key: string,
  limit: number = 50
): Promise<SettingAuditLog[]> {
  const response = await apiClient.get<ApiResponse<SettingAuditLogList>>(
    `/api/v1/settings/${encodeURIComponent(key)}/audit?limit=${limit}`
  )
  return response.data.logs
}

/**
 * Export all settings as JSON.
 * @returns Promise with blob containing exported settings
 */
export async function exportSettings(): Promise<Blob> {
  const response = await apiClient.post<Blob>(
    '/api/v1/settings/export',
    {},
    {
      responseType: 'blob',
    }
  )
  return response.data
}

/**
 * Import settings from a JSON file.
 * @param file - JSON file with settings
 * @param overwrite - Whether to overwrite existing settings
 * @returns Promise with import results
 */
export async function importSettings(
  file: File,
  overwrite: boolean = false
): Promise<Record<string, boolean>> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await apiClient.post<ApiResponse<Record<string, boolean>>>(
    `/api/v1/settings/import?overwrite=${overwrite}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  return response.data
}

/**
 * Get all setting categories.
 * @returns Promise with list of categories
 */
export async function getCategories(): Promise<SettingCategory[]> {
  const response = await apiClient.get<ApiResponse<SettingCategory[]>>(
    '/api/v1/settings/categories'
  )
  return response.data
}

/**
 * Get validation schema for a category.
 * @param category - Category name
 * @returns Promise with validation schemas
 */
export async function getValidationSchema(
  category: string
): Promise<Record<string, unknown>> {
  const response = await apiClient.get<ApiResponse<Record<string, unknown>>>(
    `/api/v1/settings/schema/${encodeURIComponent(category)}`
  )
  return response.data
}

// Re-export apiClient for direct access if needed
export { apiClient }
