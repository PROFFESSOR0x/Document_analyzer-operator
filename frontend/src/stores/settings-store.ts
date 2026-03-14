/**
 * Settings store for managing application configuration state.
 */

import { create } from 'zustand'
import type { ApplicationSetting, SettingCategory, SettingAuditLog } from '@/types'
import * as settingsApi from '@/lib/settings-api'

interface SettingsState {
  // State
  settings: ApplicationSetting[]
  categories: SettingCategory[]
  selectedCategory: string | null
  searchQuery: string
  isLoading: boolean
  error: string | null
  auditLogs: Record<string, SettingAuditLog[]>

  // Actions - Settings
  fetchSettings: (category?: string) => Promise<void>
  fetchSetting: (key: string) => Promise<ApplicationSetting>
  updateSetting: (key: string, value: string, reason?: string) => Promise<ApplicationSetting>
  bulkUpdateSettings: (settings: Record<string, string>, reason?: string) => Promise<Record<string, boolean>>
  resetSetting: (key: string) => Promise<ApplicationSetting>

  // Actions - Categories
  fetchCategories: () => Promise<void>
  setSelectedCategory: (category: string | null) => void

  // Actions - Audit Log
  fetchAuditLog: (key: string, limit?: number) => Promise<SettingAuditLog[]>

  // Actions - Import/Export
  exportSettings: () => Promise<Blob>
  importSettings: (file: File, overwrite?: boolean) => Promise<Record<string, boolean>>

  // Actions - Search
  setSearchQuery: (query: string) => void

  // Actions - General
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clear: () => void
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  // Initial state
  settings: [],
  categories: [],
  selectedCategory: null,
  searchQuery: '',
  isLoading: false,
  error: null,
  auditLogs: {},

  // Fetch all settings or by category
  fetchSettings: async (category?: string) => {
    set({ isLoading: true, error: null })
    try {
      const settings = await settingsApi.getSettings(category)
      set({ settings, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch settings'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Fetch a single setting
  fetchSetting: async (key: string) => {
    try {
      return await settingsApi.getSetting(key)
    } catch (error) {
      throw error
    }
  },

  // Update a setting
  updateSetting: async (key: string, value: string, reason?: string) => {
    set({ isLoading: true, error: null })
    try {
      const updated = await settingsApi.updateSetting(key, value, reason)
      
      set((state) => ({
        settings: state.settings.map((s) => (s.key === key ? updated : s)),
        isLoading: false,
      }))
      
      return updated
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update setting'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Bulk update settings
  bulkUpdateSettings: async (settings: Record<string, string>, reason?: string) => {
    set({ isLoading: true, error: null })
    try {
      const results = await settingsApi.bulkUpdateSettings(settings, reason)
      
      set((state) => ({
        settings: state.settings.map((s) => {
          if (results[s.key] && settings[s.key] !== undefined) {
            return { ...s, value: settings[s.key] }
          }
          return s
        }),
        isLoading: false,
      }))
      
      return results
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to bulk update settings'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Reset a setting to default
  resetSetting: async (key: string) => {
    set({ isLoading: true, error: null })
    try {
      const reset = await settingsApi.resetSetting(key)
      
      set((state) => ({
        settings: state.settings.map((s) => (s.key === key ? reset : s)),
        isLoading: false,
      }))
      
      return reset
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to reset setting'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Fetch categories
  fetchCategories: async () => {
    set({ isLoading: true, error: null })
    try {
      const categories = await settingsApi.getCategories()
      set({ categories, isLoading: false })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch categories'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Set selected category
  setSelectedCategory: (category: string | null) => {
    set({ selectedCategory: category })
  },

  // Fetch audit log for a setting
  fetchAuditLog: async (key: string, limit: number = 50) => {
    try {
      const logs = await settingsApi.getAuditLog(key, limit)
      set((state) => ({
        auditLogs: { ...state.auditLogs, [key]: logs },
      }))
      return logs
    } catch (error) {
      throw error
    }
  },

  // Export settings
  exportSettings: async () => {
    try {
      return await settingsApi.exportSettings()
    } catch (error) {
      throw error
    }
  },

  // Import settings
  importSettings: async (file: File, overwrite: boolean = false) => {
    set({ isLoading: true, error: null })
    try {
      const results = await settingsApi.importSettings(file, overwrite)
      
      // Refresh settings after import
      await get().fetchSettings()
      
      set({ isLoading: false })
      return results
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to import settings'
      set({ error: message, isLoading: false })
      throw error
    }
  },

  // Set search query
  setSearchQuery: (query: string) => {
    set({ searchQuery: query })
  },

  // Set loading state
  setLoading: (loading: boolean) => {
    set({ isLoading: loading })
  },

  // Set error
  setError: (error: string | null) => {
    set({ error })
  },

  // Clear all state
  clear: () => {
    set({
      settings: [],
      categories: [],
      selectedCategory: null,
      searchQuery: '',
      isLoading: false,
      error: null,
      auditLogs: {},
    })
  },
}))
