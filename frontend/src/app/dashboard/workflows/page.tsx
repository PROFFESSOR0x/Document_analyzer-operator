"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { SearchBar } from "@/components/domain/search-bar"
import { useState } from "react"
import { Plus, Play, Pause, StopCircle } from "lucide-react"
import type { Workflow, WorkflowStatus } from "@/types"
import { formatRelativeTime } from "@/lib/utils"
import { ScrollArea } from "@/components/ui/scroll-area"
import toast from "react-hot-toast"

const mockWorkflows: Workflow[] = [
  {
    id: "1",
    name: "Document Processing Pipeline",
    description: "Multi-stage document analysis workflow",
    definition: { nodes: [], edges: [] },
    status: "active",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: "user-1",
  },
]

const statusColors: Record<WorkflowStatus, string> = {
  draft: "bg-gray-500",
  active: "bg-green-500",
  paused: "bg-yellow-500",
  completed: "bg-blue-500",
  failed: "bg-red-500",
}

export default function WorkflowsPage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | "all">("all")

  const handleAction = (workflow: Workflow, action: string) => {
    toast.success(`${action} action triggered for ${workflow.name}`)
  }

  const filteredWorkflows = mockWorkflows.filter((workflow) => {
    const matchesSearch = workflow.name.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === "all" || workflow.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
            <p className="text-muted-foreground">Orchestrate multi-agent workflows</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              Import
            </Button>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Workflow
            </Button>
          </div>
        </div>

        <div className="flex gap-4">
          <SearchBar
            placeholder="Search workflows..."
            value={search}
            onChange={setSearch}
            className="flex-1 max-w-sm"
          />
        </div>

        {filteredWorkflows.length === 0 ? (
          <Card className="flex h-64 flex-col items-center justify-center">
            <p className="text-muted-foreground">No workflows found</p>
          </Card>
        ) : (
          <ScrollArea className="h-[600px]">
            <div className="space-y-4">
              {filteredWorkflows.map((workflow) => (
                <Card key={workflow.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle>{workflow.name}</CardTitle>
                        <CardDescription>{workflow.description}</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`h-2 w-2 rounded-full ${statusColors[workflow.status]}`}
                        />
                        <span className="text-sm capitalize">{workflow.status}</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        Updated {formatRelativeTime(workflow.updated_at)}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(workflow, "view")}
                        >
                          View
                        </Button>
                        {workflow.status === "active" ? (
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleAction(workflow, "pause")}
                          >
                            <Pause className="mr-2 h-4 w-4" />
                            Pause
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => handleAction(workflow, "start")}
                          >
                            <Play className="mr-2 h-4 w-4" />
                            Start
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleAction(workflow, "stop")}
                        >
                          <StopCircle className="mr-2 h-4 w-4" />
                          Stop
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        )}
      </div>
    </DashboardLayout>
  )
}
