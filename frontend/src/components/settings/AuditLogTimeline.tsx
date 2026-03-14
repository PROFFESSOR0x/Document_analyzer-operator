/**
 * AuditLogTimeline component for displaying setting change history.
 */

"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { SettingAuditLog } from "@/types"
import { formatDistanceToNow } from "date-fns"
import { History, ArrowRight } from "lucide-react"

interface AuditLogTimelineProps {
  logs: SettingAuditLog[]
  settingKey?: string
}

export function AuditLogTimeline({ logs, settingKey }: AuditLogTimelineProps) {
  if (logs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <History className="h-4 w-4" />
            Change History
          </CardTitle>
          <CardDescription>
            {settingKey ? `No changes recorded for ${settingKey}` : "No changes recorded"}
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <History className="h-4 w-4" />
          Change History
        </CardTitle>
        <CardDescription>
          {logs.length} {logs.length === 1 ? "change" : "changes"} recorded
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-4">
            {logs.map((log, index) => (
              <div key={log.id} className="relative">
                {index < logs.length - 1 && (
                  <div className="absolute left-4 top-8 h-full w-px bg-border" />
                )}
                <div className="flex gap-4">
                  <div className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    {logs.length - index}
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium">
                        {log.changed_by ? (
                          <>
                            {log.changed_by.username || log.changed_by.email}
                          </>
                        ) : (
                          "System"
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(log.created_at), {
                          addSuffix: true,
                        })}
                      </div>
                    </div>
                    
                    {log.change_reason && (
                      <div className="rounded-md bg-muted p-2 text-sm">
                        <span className="text-muted-foreground">Reason: </span>
                        {log.change_reason}
                      </div>
                    )}

                    <div className="flex items-center gap-2 text-sm font-mono">
                      <Badge variant="secondary">
                        {log.old_value || "null"}
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      <Badge variant="default">
                        {log.new_value || "null"}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
