"use client"

import { useEffect, useMemo, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { useSettingsStore } from "@/stores/settings-store"
import { SettingCard } from "@/components/settings/SettingCard"
import { ExportImportButtons } from "@/components/settings/ExportImportButtons"
import { ArrowLeft, Save, X, RotateCcw, Eye, EyeOff } from "lucide-react"
import toast from "react-hot-toast"
import { useAuthStore } from "@/stores/auth-store"
import { Textarea } from "@/components/ui/textarea"
import type { ApplicationSetting } from "@/types"

export default function SettingsCategoryPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  const category = params.category as string

  const {
    settings,
    isLoading,
    error,
    fetchSettings,
    updateSetting,
    resetSetting,
    exportSettings,
    importSettings,
  } = useSettingsStore()

  const [editedValues, setEditedValues] = useState<Record<string, string>>({})
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})
  const [changeReason, setChangeReason] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  // Check admin access
  useEffect(() => {
    if (user && user.role !== "admin" && user.role !== "superadmin") {
      toast.error("Admin privileges required")
      router.push("/dashboard/settings/management")
    }
  }, [user, router])

  // Load category settings
  useEffect(() => {
    if (category) {
      fetchSettings(category)
    }
  }, [category])

  const categorySettings = useMemo(() => {
    return settings.filter((s) => s.category === category)
  }, [settings, category])

  const handleEdit = (key: string, value: string) => {
    setEditedValues((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async (key: string) => {
    if (!editedValues[key]) return

    setIsSaving(true)
    try {
      await updateSetting(key, editedValues[key], changeReason || undefined)
      toast.success(`Setting "${key}" updated successfully`)
      setEditedValues((prev) => {
        const { [key]: _, ...rest } = prev
        return rest
      })
    } catch (error) {
      toast.error(`Failed to update "${key}"`)
      console.error("Update error:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleSaveAll = async () => {
    if (Object.keys(editedValues).length === 0) return

    setIsSaving(true)
    try {
      await updateSetting(
        Object.keys(editedValues)[0],
        editedValues[Object.keys(editedValues)[0]],
        changeReason || undefined
      )
      toast.success("Settings updated successfully")
      setEditedValues({})
    } catch (error) {
      toast.error("Failed to update settings")
      console.error("Update error:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = async (key: string) => {
    try {
      await resetSetting(key)
      toast.success(`Setting "${key}" reset to default`)
    } catch (error) {
      toast.error(`Failed to reset "${key}"`)
      console.error("Reset error:", error)
    }
  }

  const toggleShowSecret = (key: string) => {
    setShowSecrets((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleExport = async () => {
    const blob = await exportSettings()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `settings-${category}-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const handleImport = async (file: File, overwrite: boolean) => {
    await importSettings(file, overwrite)
  }

  if (!user || (user.role !== "admin" && user.role !== "superadmin")) {
    return null
  }

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
            <h1 className="text-3xl font-bold tracking-tight capitalize">{category} Settings</h1>
            <p className="text-muted-foreground">
              Configure {category} related settings
            </p>
          </div>
          <div className="flex gap-2">
            <ExportImportButtons onExport={handleExport} onImport={handleImport} />
          </div>
        </div>

        {/* Change Reason */}
        {Object.keys(editedValues).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Pending Changes</CardTitle>
              <CardDescription>
                {Object.keys(editedValues).length} setting(s) modified
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="change-reason">Change Reason (optional)</Label>
                <Textarea
                  id="change-reason"
                  value={changeReason}
                  onChange={(e) => setChangeReason(e.target.value)}
                  placeholder="Why are you making these changes?"
                  rows={2}
                />
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSaveAll} disabled={isSaving}>
                  <Save className="mr-2 h-4 w-4" />
                  Save All
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEditedValues({})
                    setChangeReason("")
                  }}
                  disabled={isSaving}
                >
                  <X className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
          </Card>
        )}

        {/* Settings List */}
        {isLoading ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              Loading settings...
            </CardContent>
          </Card>
        ) : categorySettings.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No settings found in this category
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {categorySettings.map((setting) => {
              const isEdited = editedValues[setting.key] !== undefined
              const showSecret = showSecrets[setting.key] || false
              const displayValue = isEdited
                ? editedValues[setting.key]
                : setting.is_secret && !showSecret
                ? "••••••••"
                : setting.value

              return (
                <Card key={setting.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-base font-medium">
                          <div className="flex items-center gap-2">
                            {setting.key}
                            {setting.is_secret && (
                              <Badge variant="destructive" className="text-xs">
                                Secret
                              </Badge>
                            )}
                            {!setting.is_editable && (
                              <Badge variant="secondary" className="text-xs">
                                Read-only
                              </Badge>
                            )}
                          </div>
                        </CardTitle>
                        {setting.description && (
                          <CardDescription>{setting.description}</CardDescription>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {setting.value_type}
                        </Badge>
                        {setting.is_secret && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleShowSecret(setting.key)}
                          >
                            {showSecret ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor={`value-${setting.key}`}>Value</Label>
                      {setting.is_editable ? (
                        <>
                          {setting.value_type === "boolean" ? (
                            <Switch
                              id={`value-${setting.key}`}
                              checked={(isEdited ? editedValues[setting.key] : setting.value) === "true"}
                              onCheckedChange={(checked) =>
                                handleEdit(setting.key, checked ? "true" : "false")
                              }
                              disabled={!setting.is_editable || isSaving}
                            />
                          ) : (
                            <Input
                              id={`value-${setting.key}`}
                              value={isEdited ? editedValues[setting.key] : (setting.value || "")}
                              onChange={(e) => handleEdit(setting.key, e.target.value)}
                              type={
                                setting.value_type === "integer" || setting.value_type === "float"
                                  ? "number"
                                  : "text"
                              }
                              step={setting.value_type === "float" ? "any" : undefined}
                              placeholder={setting.default_value || ""}
                              disabled={!setting.is_editable || isSaving}
                            />
                          )}
                        </>
                      ) : (
                        <code className="text-sm font-mono">
                          {displayValue || <span className="text-muted-foreground">null</span>}
                        </code>
                      )}
                    </div>

                    {setting.is_editable && (
                      <div className="flex gap-2">
                        {isEdited ? (
                          <>
                            <Button
                              size="sm"
                              onClick={() => handleSave(setting.key)}
                              disabled={isSaving}
                            >
                              <Save className="mr-2 h-4 w-4" />
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                setEditedValues((prev) => {
                                  const { [setting.key]: _, ...rest } = prev
                                  return rest
                                })
                              }
                              disabled={isSaving}
                            >
                              <X className="mr-2 h-4 w-4" />
                              Cancel
                            </Button>
                          </>
                        ) : (
                          setting.default_value && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleReset(setting.key)}
                              disabled={isSaving}
                            >
                              <RotateCcw className="mr-2 h-4 w-4" />
                              Reset to Default
                            </Button>
                          )
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{categorySettings.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Secret Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {categorySettings.filter((s) => s.is_secret).length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Editable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {categorySettings.filter((s) => s.is_editable).length}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
