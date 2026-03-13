"use client"

import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { AgentStatusIndicator } from "@/components/domain/agent-status"
import { LoadingSpinner } from "@/components/domain/loading-spinner"
import { ArrowLeft, Play, Pause, RotateCcw, Square, Trash2, Activity, Clock, CheckCircle, AlertCircle } from "lucide-react"
import type { Agent } from "@/types"
import { formatRelativeTime } from "@/lib/utils"
import toast from "react-hot-toast"

// Mock data - will be replaced with API call
const mockAgent: Agent = {
  id: "1",
  name: "Research Agent",
  type: "cognitive",
  status: "running",
  capabilities: {
    skill1: "Web Research",
    skill2: "Information Gathering",
    skill3: "Data Synthesis",
  },
  config: { max_iterations: 10, timeout: 300 },
  created_at: new Date(Date.now() - 86400000).toISOString(),
  updated_at: new Date().toISOString(),
  created_by: "user-1",
}

export default function AgentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const agentId = params.id as string

  // In real app, fetch agent data from API
  const agent = mockAgent

  if (!agent) {
    return (
      <DashboardLayout>
        <div className="flex h-full items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    )
  }

  const handleAction = (action: string) => {
    toast.success(`${action} action triggered`)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{agent.name}</h1>
            <p className="text-muted-foreground">Agent ID: {agent.id}</p>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <AgentStatusIndicator status={agent.status} showLabel className="text-sm" />
          <div className="flex gap-2">
            {agent.status === "idle" && (
              <Button size="sm" onClick={() => handleAction("start")}>
                <Play className="mr-2 h-4 w-4" />
                Start
              </Button>
            )}
            {agent.status === "running" && (
              <Button size="sm" variant="secondary" onClick={() => handleAction("pause")}>
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </Button>
            )}
            {agent.status === "paused" && (
              <Button size="sm" onClick={() => handleAction("resume")}>
                <RotateCcw className="mr-2 h-4 w-4" />
                Resume
              </Button>
            )}
            <Button size="sm" variant="outline" onClick={() => handleAction("stop")}>
              <Square className="mr-2 h-4 w-4" />
              Stop
            </Button>
            <Button size="sm" variant="destructive" onClick={() => handleAction("delete")}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="history">Execution History</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Type</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold capitalize">{agent.type}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Created</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatRelativeTime(agent.created_at)}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatRelativeTime(agent.updated_at)}</div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Capabilities</CardTitle>
                <CardDescription>Skills and abilities of this agent</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(agent.capabilities).map(([key, value]) => (
                    <Badge key={key} variant="secondary">
                      {value}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Configuration</CardTitle>
                <CardDescription>Agent configuration settings</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-40">
                  <pre className="text-sm">
                    {JSON.stringify(agent.config, null, 2)}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Agent execution statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <div className="flex items-center gap-4">
                    <Activity className="h-10 w-10 text-primary" />
                    <div>
                      <p className="text-sm text-muted-foreground">Total Tasks</p>
                      <p className="text-2xl font-bold">0</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <CheckCircle className="h-10 w-10 text-green-600" />
                    <div>
                      <p className="text-sm text-muted-foreground">Success Rate</p>
                      <p className="text-2xl font-bold">0%</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Clock className="h-10 w-10 text-blue-600" />
                    <div>
                      <p className="text-sm text-muted-foreground">Avg Execution</p>
                      <p className="text-2xl font-bold">0ms</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <AlertCircle className="h-10 w-10 text-red-600" />
                    <div>
                      <p className="text-sm text-muted-foreground">Failed Tasks</p>
                      <p className="text-2xl font-bold">0</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Execution History</CardTitle>
                <CardDescription>Recent execution sessions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center text-muted-foreground py-8">
                  No execution history available
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Agent Logs</CardTitle>
                <CardDescription>Real-time log stream</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <div className="space-y-2 font-mono text-sm">
                    <div className="text-muted-foreground">No logs available</div>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
