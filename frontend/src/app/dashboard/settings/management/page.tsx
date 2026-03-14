"use client"

import { useEffect, useMemo, useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useSettingsStore } from "@/stores/settings-store"
import { CategorySelector } from "@/components/settings/CategorySelector"
import { SettingSearch } from "@/components/settings/SettingSearch"
import { SettingCard } from "@/components/settings/SettingCard"
import { ExportImportButtons } from "@/components/settings/ExportImportButtons"
import { BulkEditor } from "@/components/settings/BulkEditor"
import { AuditLogTimeline } from "@/components/settings/AuditLogTimeline"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Settings, History, Download, Upload } from "lucide-react"
import toast from "react-hot-toast"
import { useAuthStore } from "@/stores/auth-store"
import { useRouter } from "next/navigation"

export default function SettingsManagementPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  
  const {
    settings,
    categories,
    selectedCategory,
    searchQuery,
    isLoading,
    error,
    auditLogs,
    fetchSettings,
    fetchCategories,
    updateSetting,
    bulkUpdateSettings,
    resetSetting,
    exportSettings,
    importSettings,
    fetchAuditLog,
    setSelectedCategory,
    setSearchQuery,
  } = useSettingsStore()

  const [activeTab, setActiveTab] = useState("settings")

  // Check admin access
  useEffect(() => {
    if (user && user.role !== "admin" && user.role !== "superadmin") {
      toast.error("Admin privileges required")
      router.push("/dashboard")
    }
  }, [user, router])

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([fetchCategories(), fetchSettings()])
      } catch (error) {
        console.error("Failed to load settings:", error)
      }
    }
    loadData()
  }, [])

  // Filter settings based on search and category
  const filteredSettings = useMemo(() => {
    return settings.filter((setting) => {
      const matchesCategory = !selectedCategory || setting.category === selectedCategory
      const matchesSearch =
        !searchQuery ||
        setting.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
        setting.description?.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCategory && matchesSearch
    })
  }, [settings, selectedCategory, searchQuery])

  const handleSave = async (key: string, value: string, reason?: string) => {
    await updateSetting(key, value, reason)
    toast.success(`Setting "${key}" updated successfully`)
  }

  const handleReset = async (key: string) => {
    await resetSetting(key)
    toast.success(`Setting "${key}" reset to default`)
  }

  const handleExport = async () => {
    const blob = await exportSettings()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `settings-export-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const handleImport = async (file: File, overwrite: boolean) => {
    await importSettings(file, overwrite)
  }

  const handleViewAuditLog = async (key: string) => {
    await fetchAuditLog(key)
    setActiveTab("audit")
  }

  if (!user || (user.role !== "admin" && user.role !== "superadmin")) {
    return null
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Application Settings</h1>
            <p className="text-muted-foreground">
              Manage all application configuration and environment variables
            </p>
          </div>
          <div className="flex gap-2">
            <ExportImportButtons onExport={handleExport} onImport={handleImport} />
            <BulkEditor settings={settings} onSave={bulkUpdateSettings} />
          </div>
        </div>

        {/* Category Selector */}
        <CategorySelector
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />

        {/* Search */}
        <SettingSearch
          value={searchQuery}
          onChange={setSearchQuery}
          onClear={() => setSearchQuery("")}
        />

        {/* Error Display */}
        {error && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
          </Card>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="settings">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </TabsTrigger>
            <TabsTrigger value="audit">
              <History className="h-4 w-4 mr-2" />
              Audit Log
            </TabsTrigger>
          </TabsList>

          <TabsContent value="settings" className="space-y-4">
            {/* Settings Grid */}
            {isLoading ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  Loading settings...
                </CardContent>
              </Card>
            ) : filteredSettings.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  {searchQuery
                    ? "No settings match your search"
                    : "No settings found in this category"}
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {filteredSettings.map((setting) => (
                  <SettingCard
                    key={setting.id}
                    setting={setting}
                    onSave={handleSave}
                    onReset={handleReset}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="audit" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Changes</CardTitle>
                <CardDescription>
                  View the audit log of all setting changes
                </CardDescription>
              </CardHeader>
              <CardContent>
                {Object.keys(auditLogs).length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    Select a setting to view its change history
                  </p>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(auditLogs).map(([key, logs]) => (
                      <div key={key}>
                        <h3 className="font-medium mb-2">{key}</h3>
                        <AuditLogTimeline logs={logs} settingKey={key} />
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{settings.length}</div>
              <p className="text-xs text-muted-foreground">
                Across {categories.length} categories
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Secret Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {settings.filter((s) => s.is_secret).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Encrypted values
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Editable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {settings.filter((s) => s.is_editable).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Can be modified via UI
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
