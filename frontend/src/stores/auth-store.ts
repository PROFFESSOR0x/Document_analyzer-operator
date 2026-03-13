import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthTokens, UserSettings } from '@/types'
import { apiClient } from '@/lib/api-client'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  settings: UserSettings
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, full_name: string) => Promise<void>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
  updateSettings: (settings: Partial<UserSettings>) => void
  clear: () => void
}

const defaultSettings: UserSettings = {
  theme: 'system',
  notifications_enabled: true,
  email_notifications: true,
  language: 'en',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      settings: defaultSettings,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const tokens = await apiClient.login(email, password)
          await get().fetchUser()
          set({ isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (email: string, password: string, full_name: string) => {
        set({ isLoading: true })
        try {
          const tokens = await apiClient.register(email, password, full_name)
          await get().fetchUser()
          set({ isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        try {
          await apiClient.logout()
        } finally {
          get().clear()
        }
      },

      fetchUser: async () => {
        try {
          const userData = await apiClient.getCurrentUser()
          set({ user: userData as User, isAuthenticated: true, isLoading: false })
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      updateSettings: (settings: Partial<UserSettings>) => {
        set((state) => ({
          settings: { ...state.settings, ...settings },
        }))
      },

      clear: () => {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          settings: defaultSettings,
        })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ settings: state.settings }),
    }
  )
)
