"use client"

import { useEffect } from "react"
import { useAuthStore } from "@/stores/auth-store"
import { useWebSocketStore } from "@/stores/websocket-store"

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const fetchUser = useAuthStore((state) => state.fetchUser)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const connectWebSocket = useWebSocketStore((state) => state.connect)
  const disconnectWebSocket = useWebSocketStore((state) => state.disconnect)

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  useEffect(() => {
    const handleLogout = () => {
      disconnectWebSocket()
    }

    window.addEventListener("auth:logout", handleLogout)
    return () => window.removeEventListener("auth:logout", handleLogout)
  }, [disconnectWebSocket])

  useEffect(() => {
    if (isAuthenticated && process.env.NEXT_PUBLIC_ENABLE_WEBSOCKET === "true") {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
      connectWebSocket(`${wsUrl}/api/v1/ws`)
    }

    return () => {
      disconnectWebSocket()
    }
  }, [isAuthenticated, connectWebSocket, disconnectWebSocket])

  return <>{children}</>
}
