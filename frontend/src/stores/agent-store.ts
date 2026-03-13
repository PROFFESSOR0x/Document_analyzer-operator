import { create } from 'zustand'
import type { Agent, AgentMetrics, AgentStatus } from '@/types'

interface AgentState {
  agents: Agent[]
  selectedAgent: Agent | null
  metrics: Record<string, AgentMetrics>
  isLoading: boolean
  error: string | null
  filter: {
    status: AgentStatus | 'all'
    type: string | 'all'
    search: string
  }
  setAgents: (agents: Agent[]) => void
  setSelectedAgent: (agent: Agent | null) => void
  updateAgent: (agent: Agent) => void
  removeAgent: (id: string) => void
  setMetrics: (agentId: string, metrics: AgentMetrics) => void
  setFilter: (filter: Partial<AgentState['filter']>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clear: () => void
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  selectedAgent: null,
  metrics: {},
  isLoading: false,
  error: null,
  filter: {
    status: 'all',
    type: 'all',
    search: '',
  },

  setAgents: (agents) => set({ agents }),

  setSelectedAgent: (agent) => set({ selectedAgent: agent }),

  updateAgent: (agent) =>
    set((state) => ({
      agents: state.agents.map((a) => (a.id === agent.id ? agent : a)),
      selectedAgent: state.selectedAgent?.id === agent.id ? agent : state.selectedAgent,
    })),

  removeAgent: (id) =>
    set((state) => ({
      agents: state.agents.filter((a) => a.id !== id),
      selectedAgent: state.selectedAgent?.id === id ? null : state.selectedAgent,
    })),

  setMetrics: (agentId, metrics) =>
    set((state) => ({
      metrics: { ...state.metrics, [agentId]: metrics },
    })),

  setFilter: (filter) =>
    set((state) => ({
      filter: { ...state.filter, ...filter },
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clear: () =>
    set({
      agents: [],
      selectedAgent: null,
      metrics: {},
      isLoading: false,
      error: null,
      filter: { status: 'all', type: 'all', search: '' },
    }),
}))
