import { create } from 'zustand'
import type { WebSocketMessage } from '@/types'

interface WebSocketState {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  connect: (url: string) => void
  disconnect: () => void
  sendMessage: (message: WebSocketMessage) => void
  setConnectionState: (connected: boolean, connecting?: boolean) => void
  setError: (error: string | null) => void
}

let ws: WebSocket | null = null
let reconnectTimeout: NodeJS.Timeout | null = null

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  isConnected: false,
  isConnecting: false,
  error: null,

  connect: (url: string) => {
    if (ws?.readyState === WebSocket.OPEN) return

    set({ isConnecting: true, error: null })

    try {
      ws = new WebSocket(url)

      ws.onopen = () => {
        set({ isConnected: true, isConnecting: false, error: null })
        console.log('WebSocket connected')
      }

      ws.onclose = () => {
        set({ isConnected: false, isConnecting: false })
        console.log('WebSocket disconnected')

        // Auto-reconnect
        if (reconnectTimeout) clearTimeout(reconnectTimeout)
        reconnectTimeout = setTimeout(() => {
          get().connect(url)
        }, 5000)
      }

      ws.onerror = (event) => {
        set({ error: 'WebSocket error occurred', isConnected: false, isConnecting: false })
        console.error('WebSocket error:', event)
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          // Handle incoming messages - can be extended with callbacks
          console.log('WebSocket message received:', message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
    } catch (error) {
      set({ error: 'Failed to connect to WebSocket', isConnecting: false })
      console.error('WebSocket connection error:', error)
    }
  },

  disconnect: () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    set({ isConnected: false, isConnecting: false, error: null })
  },

  sendMessage: (message: WebSocketMessage) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  },

  setConnectionState: (connected, connecting = false) =>
    set({ isConnected: connected, isConnecting: connecting }),

  setError: (error) => set({ error }),
}))
