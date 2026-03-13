"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { AgentCard } from "@/components/domain/agent-card"
import { SearchBar } from "@/components/domain/search-bar"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Plus, Grid, List } from "lucide-react"
import type { Agent, AgentStatus } from "@/types"
import { useAgentStore } from "@/stores/agent-store"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { AgentStatusIndicator } from "@/components/domain/agent-status"
import toast from "react-hot-toast"
import { Card, CardContent } from "@/components/ui/card"

// Mock data - will be replaced with API calls
const mockAgents: Agent[] = [
  {
    id: "1",
    name: "Research Agent",
    type: "cognitive",
    status: "idle",
    capabilities: { skill1: "Web Research", skill2: "Information Gathering" },
    config: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: "user-1",
  },
  {
    id: "2",
    name: "Document Analyzer",
    type: "cognitive",
    status: "running",
    capabilities: { skill1: "Document Parsing", skill2: "Text Analysis" },
    config: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: "user-1",
  },
]

export default function AgentsPage() {
  const [view, setView] = useState<"grid" | "list">("grid")
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<AgentStatus | "all">("all")
  const [typeFilter, setTypeFilter] = useState<string>("all")
  const { agents, setAgents } = useAgentStore()

  const handleViewAgent = (agent: Agent) => {
    console.log("View agent:", agent)
    // Navigate to agent detail page
  }

  const handleAgentAction = (agent: Agent, action: string) => {
    toast.success(`${action} action triggered for ${agent.name}`)
  }

  const filteredAgents = agents.filter((agent) => {
    const matchesSearch = agent.name.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === "all" || agent.status === statusFilter
    const matchesType = typeFilter === "all" || agent.type === typeFilter
    return matchesSearch && matchesStatus && matchesType
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
            <p className="text-muted-foreground">Manage and monitor your AI agents</p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Agent
          </Button>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <SearchBar
            placeholder="Search agents..."
            value={search}
            onChange={setSearch}
            className="w-full sm:w-64"
          />

          <div className="flex gap-2">
            <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as AgentStatus | "all")}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="idle">Idle</SelectItem>
                <SelectItem value="running">Running</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="stopped">Stopped</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="cognitive">Cognitive</SelectItem>
                <SelectItem value="content">Content</SelectItem>
                <SelectItem value="engineering">Engineering</SelectItem>
                <SelectItem value="programming">Programming</SelectItem>
                <SelectItem value="operational">Operational</SelectItem>
                <SelectItem value="validation">Validation</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex items-center border rounded-md">
              <Button
                variant={view === "grid" ? "default" : "ghost"}
                size="icon"
                onClick={() => setView("grid")}
                className="h-9 w-9 rounded-r-none"
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={view === "list" ? "default" : "ghost"}
                size="icon"
                onClick={() => setView("list")}
                className="h-9 w-9 rounded-l-none"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {filteredAgents.length === 0 ? (
          <Card className="flex h-64 flex-col items-center justify-center">
            <p className="text-muted-foreground">No agents found</p>
          </Card>
        ) : view === "grid" ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredAgents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onView={handleViewAgent}
                onAction={handleAgentAction}
              />
            ))}
          </div>
        ) : (
          <ScrollArea className="h-[600px]">
            <div className="space-y-2">
              {filteredAgents.map((agent) => (
                <div
                  key={agent.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-4">
                    <AgentStatusIndicator status={agent.status} />
                    <div>
                      <h3 className="font-medium">{agent.name}</h3>
                      <p className="text-sm text-muted-foreground">{agent.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {Object.values(agent.capabilities || {}).slice(0, 2).map((cap, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {cap}
                      </Badge>
                    ))}
                    <Button variant="outline" size="sm" onClick={() => handleViewAgent(agent)}>
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </div>
    </DashboardLayout>
  )
}
