"use client"

import { useEffect, useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useSettingsStore } from "@/stores/settings-store"
import { AuditLogTimeline } from "@/components/settings/AuditLogTimeline"
import { ArrowLeft, Download, Filter } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/stores/auth-store"
import toast from "react-hot-toast"
import { format } from "date-fns"

export default function SettingsAuditPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  
  const { settings, auditLogs, fetchSettings, fetchAuditLog } = useSettingsStore()

  const [selectedSetting, setSelectedSetting] = useState<string>("all")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Check admin access
  useEffect(() => {
    if (user && user.role !== "admin" && user.role !== "superadmin") {
      toast.error("Admin privileges required")
      router.push("/dashboard")
    }
  }, [user, router])

  // Load settings for filter dropdown
  useEffect(() => {
    fetchSettings()
  }, [])

  const handleLoadAuditLog = async () => {
    setIsLoading(true)
    try {
      if (selectedSetting === "all") {
        // Load audit logs for all settings
        await Promise.all(
          settings.map((s) => fetchAuditLog(s.key, 50))
        )
      } else {
        await fetchAuditLog(selectedSetting, 100)
      }
      toast.success("Audit log loaded")
    } catch (error) {
      toast.error("Failed to load audit log")
      console.error("Load error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExport = () => {
    const allLogs = Object.values(auditLogs).flat()
    const exportData = {
      exported_at: new Date().toISOString(),
      total_logs: allLogs.length,
      logs: allLogs.map((log) => ({
        id: log.id,
        setting_key: log.setting_key,
        old_value: log.old_value,
        new_value: log.new_value,
        changed_by: log.changed_by,
        change_reason: log.change_reason,
        created_at: log.created_at,
      })),
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `audit-log-${format(new Date(), "yyyy-MM-dd")}.json`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    toast.success("Audit log exported")
  }

  if (!user || (user.role !== "admin" && user.role !== "superadmin")) {
    return null
  }

  const allLogs = Object.values(auditLogs).flat().sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard/settings/management")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight">Settings Audit Log</h1>
            <p className="text-muted-foreground">
              Track all changes made to application settings
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Filter className="h-4 w-4" />
              Filters
            </CardTitle>
            <CardDescription>
              Filter audit logs by setting and date range
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor="setting-filter">Setting</Label>
                <Select value={selectedSetting} onValueChange={setSelectedSetting}>
                  <SelectTrigger id="setting-filter">
                    <SelectValue placeholder="All settings" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Settings</SelectItem>
                    {settings.map((setting) => (
                      <SelectItem key={setting.id} value={setting.key}>
                        {setting.key}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date-from">From Date</Label>
                <Input
                  id="date-from"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="date-to">To Date</Label>
                <Input
                  id="date-to"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>

              <div className="flex items-end">
                <Button
                  onClick={handleLoadAuditLog}
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? "Loading..." : "Apply Filters"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Audit Logs */}
        {allLogs.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No audit logs found. Click "Apply Filters" to load logs.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.entries(auditLogs).map(([key, logs]) => (
              <div key={key}>
                <h3 className="font-medium mb-2 text-lg">{key}</h3>
                <AuditLogTimeline logs={logs} settingKey={key} />
              </div>
            ))}
          </div>
        )}

        {/* Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <div className="text-2xl font-bold">{allLogs.length}</div>
                <p className="text-xs text-muted-foreground">Total Changes</p>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {new Set(allLogs.map((l) => l.setting_key)).size}
                </div>
                <p className="text-xs text-muted-foreground">Settings Changed</p>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {new Set(allLogs.map((l) => l.changed_by?.id)).size}
                </div>
                <p className="text-xs text-muted-foreground">Unique Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
