"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import type { Agent, AgentMetrics, PaginatedResponse } from "@/types"

export function useAgents(filters?: { status?: string; type?: string; search?: string }) {
  return useQuery({
    queryKey: ["agents", filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.status) params.append("status", filters.status)
      if (filters?.type) params.append("type", filters.type)
      if (filters?.search) params.append("search", filters.search)

      const response = await apiClient.get<PaginatedResponse<Agent>>(
        `/api/v1/agents?${params.toString()}`
      )
      return response
    },
  })
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: ["agent", id],
    queryFn: async () => {
      const response = await apiClient.get<Agent>(`/api/v1/agents/${id}`)
      return response
    },
    enabled: !!id,
  })
}

export function useAgentMetrics(id: string) {
  return useQuery({
    queryKey: ["agent-metrics", id],
    queryFn: async () => {
      const response = await apiClient.get<AgentMetrics>(`/api/v1/agents/${id}/metrics`)
      return response
    },
    enabled: !!id,
  })
}

export function useCreateAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Partial<Agent>) => {
      const response = await apiClient.post<Agent>("/api/v1/agents", data)
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    },
  })
}

export function useUpdateAgent(id: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Partial<Agent>) => {
      const response = await apiClient.patch<Agent>(`/api/v1/agents/${id}`, data)
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
      queryClient.invalidateQueries({ queryKey: ["agent", id] })
    },
  })
}

export function useDeleteAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/agents/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    },
  })
}

export function useAgentAction(id: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (action: "start" | "stop" | "pause" | "resume") => {
      const response = await apiClient.post<Agent>(`/api/v1/agents/${id}/${action}`)
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
      queryClient.invalidateQueries({ queryKey: ["agent", id] })
    },
  })
}
