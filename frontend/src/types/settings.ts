/**
 * Application settings types for configuration management.
 */

import type { User } from './index'

export type SettingValueType = 'string' | 'integer' | 'float' | 'boolean' | 'json' | 'secret'

export interface ApplicationSetting {
  id: string
  key: string
  value: string | null
  value_type: SettingValueType
  category: string
  description: string | null
  is_secret: boolean
  is_editable: boolean
  validation_schema?: Record<string, unknown>
  default_value: string | null
  updated_at: string
  updated_by?: Pick<User, 'id' | 'email' | 'username'> | null
}

export interface SettingCategory {
  id: string
  name: string
  description: string | null
  icon: string
  setting_count: number
  settings?: ApplicationSetting[]
}

export interface SettingAuditLog {
  id: string
  setting_id: string
  setting_key: string
  old_value: string | null
  new_value: string | null
  changed_by?: Pick<User, 'id' | 'email' | 'username'> | null
  change_reason: string | null
  created_at: string
}

export interface ApplicationSettingList {
  settings: ApplicationSetting[]
  total: number
}

export interface SettingAuditLogList {
  logs: SettingAuditLog[]
  total: number
}

export interface BulkSettingsUpdate {
  settings: Record<string, string>
  change_reason?: string
}

export interface SettingsExport {
  exported_at: string
  exported_by: string
  settings: ApplicationSetting[]
  total: number
}

export interface SettingsImport {
  settings: ApplicationSetting[]
  overwrite_existing: boolean
}
