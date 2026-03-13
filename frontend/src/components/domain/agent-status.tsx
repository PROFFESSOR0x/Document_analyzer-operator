import { CircleCheck, CircleX, Clock, PauseCircle, PlayCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import type { AgentStatus } from "@/types"

interface AgentStatusIndicatorProps {
  status: AgentStatus
  showLabel?: boolean
  className?: string
}

const statusConfig: Record<AgentStatus, { label: string; icon: React.ReactNode; color: string }> = {
  idle: {
    label: "Idle",
    icon: <Clock className="h-3 w-3" />,
    color: "text-gray-500 bg-gray-100 dark:bg-gray-800",
  },
  running: {
    label: "Running",
    icon: <PlayCircle className="h-3 w-3" />,
    color: "text-green-600 bg-green-100 dark:bg-green-900",
  },
  paused: {
    label: "Paused",
    icon: <PauseCircle className="h-3 w-3" />,
    color: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900",
  },
  stopped: {
    label: "Stopped",
    icon: <CircleCheck className="h-3 w-3" />,
    color: "text-blue-600 bg-blue-100 dark:bg-blue-900",
  },
  error: {
    label: "Error",
    icon: <CircleX className="h-3 w-3" />,
    color: "text-red-600 bg-red-100 dark:bg-red-900",
  },
}

export function AgentStatusIndicator({
  status,
  showLabel = true,
  className,
}: AgentStatusIndicatorProps) {
  const config = statusConfig[status] || statusConfig.idle

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        config.color,
        className
      )}
    >
      {config.icon}
      {showLabel && <span>{config.label}</span>}
    </div>
  )
}
