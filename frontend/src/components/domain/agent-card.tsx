"use client"

import { formatRelativeTime } from "@/lib/utils"
import { AgentStatusIndicator } from "./agent-status"
import type { Agent } from "@/types"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MoreVertical, Play, Pause, Square, Trash2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface AgentCardProps {
  agent: Agent
  onView?: (agent: Agent) => void
  onAction?: (agent: Agent, action: "start" | "stop" | "pause" | "resume" | "delete") => void
}

export function AgentCard({ agent, onView, onAction }: AgentCardProps) {
  const capabilities = Object.values(agent.capabilities || {}).slice(0, 3)

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="font-semibold text-lg">{agent.name}</h3>
            <p className="text-sm text-muted-foreground">{agent.type}</p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onView?.(agent)}>View Details</DropdownMenuItem>
              {agent.status === "idle" && (
                <DropdownMenuItem onClick={() => onAction?.(agent, "start")}>Start</DropdownMenuItem>
              )}
              {agent.status === "running" && (
                <DropdownMenuItem onClick={() => onAction?.(agent, "pause")}>Pause</DropdownMenuItem>
              )}
              {agent.status === "paused" && (
                <DropdownMenuItem onClick={() => onAction?.(agent, "resume")}>Resume</DropdownMenuItem>
              )}
              <DropdownMenuItem
                onClick={() => onAction?.(agent, "delete")}
                className="text-destructive"
              >
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <AgentStatusIndicator status={agent.status} />
          <span className="text-xs text-muted-foreground">
            Updated {formatRelativeTime(agent.updated_at)}
          </span>
        </div>

        {capabilities.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {capabilities.map((capability, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {capability}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          {agent.status === "idle" && (
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onAction?.(agent, "start")}>
              <Play className="h-3 w-3 mr-1" />
              Start
            </Button>
          )}
          {agent.status === "running" && (
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onAction?.(agent, "pause")}>
              <Pause className="h-3 w-3 mr-1" />
              Pause
            </Button>
          )}
          {agent.status === "paused" && (
            <Button size="sm" variant="outline" className="flex-1" onClick={() => onAction?.(agent, "resume")}>
              Resume
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onView?.(agent)}
          >
            Details
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
