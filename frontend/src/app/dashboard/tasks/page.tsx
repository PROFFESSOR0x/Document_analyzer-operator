"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { Task, TaskStatus } from "@/types"
import { formatRelativeTime, getPriorityColor } from "@/lib/utils"
import { Clock, CheckCircle, XCircle, AlertCircle, Play, RefreshCw } from "lucide-react"
import toast from "react-hot-toast"

const mockTasks: Task[] = [
  {
    id: "1",
    type: "document_analysis",
    status: "running",
    priority: "high",
    payload: { document_id: "doc-1" },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
  },
  {
    id: "2",
    type: "web_research",
    status: "pending",
    priority: "normal",
    payload: { query: "AI trends" },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "3",
    type: "validation",
    status: "completed",
    priority: "low",
    payload: { content_id: "content-1" },
    result: { valid: true },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
  },
  {
    id: "4",
    type: "code_generation",
    status: "failed",
    priority: "critical",
    payload: { spec: "API endpoint" },
    error: "Timeout exceeded",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
  },
]

const statusConfig: Record<TaskStatus, { label: string; icon: React.ReactNode; color: string }> = {
  pending: {
    label: "Pending",
    icon: <Clock className="h-3 w-3" />,
    color: "text-gray-500 bg-gray-100 dark:bg-gray-800",
  },
  running: {
    label: "Running",
    icon: <Play className="h-3 w-3" />,
    color: "text-green-600 bg-green-100 dark:bg-green-900",
  },
  completed: {
    label: "Completed",
    icon: <CheckCircle className="h-3 w-3" />,
    color: "text-blue-600 bg-blue-100 dark:bg-blue-900",
  },
  failed: {
    label: "Failed",
    icon: <XCircle className="h-3 w-3" />,
    color: "text-red-600 bg-red-100 dark:bg-red-900",
  },
  cancelled: {
    label: "Cancelled",
    icon: <AlertCircle className="h-3 w-3" />,
    color: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900",
  },
}

export default function TasksPage() {
  const handleRetry = (task: Task) => {
    toast.success(`Retrying task: ${task.id}`)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground">Monitor and manage task execution</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Object.entries(statusConfig).map(([status, config]) => {
            const count = mockTasks.filter((t) => t.status === status).length
            return (
              <Card key={status}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{config.label}</CardTitle>
                  <div className={config.color}>{config.icon}</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{count}</div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <ScrollArea className="h-[600px]">
          <div className="space-y-4">
            {mockTasks.map((task) => {
              const status = statusConfig[task.status]
              return (
                <Card key={task.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base">{task.type}</CardTitle>
                          <Badge className={getPriorityColor(task.priority)}>
                            {task.priority}
                          </Badge>
                        </div>
                        <CardDescription>Task ID: {task.id}</CardDescription>
                      </div>
                      <div className={`flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${status.color}`}>
                        {status.icon}
                        {status.label}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">
                        Created {formatRelativeTime(task.created_at)}
                      </div>
                      {task.status === "failed" && (
                        <Button size="sm" variant="outline" onClick={() => handleRetry(task)}>
                          <RefreshCw className="mr-2 h-3 w-3" />
                          Retry
                        </Button>
                      )}
                    </div>
                    {task.error && (
                      <div className="mt-2 rounded-md bg-destructive/10 p-2 text-sm text-destructive">
                        {task.error}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </ScrollArea>
      </div>
    </DashboardLayout>
  )
}
