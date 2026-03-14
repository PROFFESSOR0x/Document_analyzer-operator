/**
 * BulkEditor component for editing multiple settings at once.
 */

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import type { ApplicationSetting } from "@/types"
import { Edit3, Save, X } from "lucide-react"
import toast from "react-hot-toast"

interface BulkEditorProps {
  settings: ApplicationSetting[]
  onSave: (settings: Record<string, string>, reason?: string) => Promise<void>
}

export function BulkEditor({ settings, onSave }: BulkEditorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [values, setValues] = useState<Record<string, string>>({})
  const [reason, setReason] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  const openEditor = () => {
    const initialValues: Record<string, string> = {}
    settings.forEach((setting) => {
      if (setting.is_editable) {
        initialValues[setting.key] = setting.value || ""
      }
    })
    setValues(initialValues)
    setReason("")
    setIsOpen(true)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(values, reason || undefined)
      toast.success("Settings updated successfully")
      setIsOpen(false)
    } catch (error) {
      toast.error("Failed to update settings")
      console.error("Bulk update error:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleValueChange = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  const editableSettings = settings.filter((s) => s.is_editable)

  return (
    <>
      <Button variant="outline" size="sm" onClick={openEditor}>
        <Edit3 className="mr-2 h-4 w-4" />
        Bulk Edit
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Bulk Edit Settings</DialogTitle>
            <DialogDescription>
              Edit multiple settings at once. All changes will be applied together.
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto py-4">
            <div className="space-y-4">
              {editableSettings.map((setting) => (
                <div key={setting.key} className="space-y-2">
                  <Label htmlFor={`bulk-${setting.key}`}>
                    {setting.key}
                    {setting.is_secret && (
                      <span className="ml-2 text-xs text-destructive">(Secret)</span>
                    )}
                  </Label>
                  {setting.description && (
                    <p className="text-xs text-muted-foreground">{setting.description}</p>
                  )}
                  <Input
                    id={`bulk-${setting.key}`}
                    value={values[setting.key] || ""}
                    onChange={(e) => handleValueChange(setting.key, e.target.value)}
                    type={
                      setting.value_type === "integer" || setting.value_type === "float"
                        ? "number"
                        : "text"
                    }
                    step={setting.value_type === "float" ? "any" : undefined}
                    placeholder={setting.default_value || ""}
                  />
                </div>
              ))}

              <div className="space-y-2 pt-4 border-t">
                <Label htmlFor="bulk-reason">Change Reason (optional)</Label>
                <Textarea
                  id="bulk-reason"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Why are you making these changes?"
                  rows={3}
                />
              </div>
            </div>
          </div>

          <DialogFooter className="border-t pt-4">
            <Button variant="outline" onClick={() => setIsOpen(false)} disabled={isSaving}>
              <X className="mr-2 h-4 w-4" />
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              <Save className="mr-2 h-4 w-4" />
              Save All Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
