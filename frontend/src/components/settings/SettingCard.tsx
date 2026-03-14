/**
 * SettingCard component for displaying individual setting information.
 */

"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import type { ApplicationSetting } from "@/types"
import { Eye, EyeOff, RotateCcw, Save, X } from "lucide-react"
import { useState } from "react"

interface SettingCardProps {
  setting: ApplicationSetting
  onSave?: (key: string, value: string, reason?: string) => Promise<void>
  onReset?: (key: string) => Promise<void>
}

export function SettingCard({ setting, onSave, onReset }: SettingCardProps) {
  const [value, setValue] = useState(setting.value || "")
  const [showSecret, setShowSecret] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [reason, setReason] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSave = async () => {
    if (!onSave || !isEditing) return
    
    setIsLoading(true)
    try {
      await onSave(setting.key, value, reason || undefined)
      setIsEditing(false)
      setReason("")
    } catch (error) {
      console.error("Failed to save setting:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setValue(setting.value || "")
    setIsEditing(false)
    setReason("")
  }

  const handleReset = async () => {
    if (!onReset) return
    
    setIsLoading(true)
    try {
      await onReset(setting.key)
    } catch (error) {
      console.error("Failed to reset setting:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const renderValueInput = () => {
    if (!isEditing) {
      // Display mode
      if (setting.is_secret) {
        return (
          <div className="flex items-center gap-2">
            <code className="text-sm font-mono">
              {showSecret ? (setting.value || "••••••••") : "••••••••"}
            </code>
            {setting.value && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSecret(!showSecret)}
              >
                {showSecret ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
        )
      }

      if (setting.value_type === "boolean") {
        return (
          <Badge variant={value === "true" ? "default" : "secondary"}>
            {value === "true" ? "Enabled" : "Disabled"}
          </Badge>
        )
      }

      return (
        <code className="text-sm font-mono">
          {setting.value || <span className="text-muted-foreground">null</span>}
        </code>
      )
    }

    // Edit mode
    if (setting.value_type === "boolean") {
      return (
        <Switch
          checked={value === "true"}
          onCheckedChange={(checked) => setValue(checked ? "true" : "false")}
        />
      )
    }

    return (
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        type={setting.value_type === "integer" || setting.value_type === "float" ? "number" : "text"}
        step={setting.value_type === "float" ? "any" : undefined}
        placeholder={setting.default_value || ""}
      />
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
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
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge variant="outline" className="text-xs">
                  {setting.value_type}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                <p>Value type: {setting.value_type}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Value</Label>
          {renderValueInput()}
        </div>

        {isEditing && setting.is_editable && (
          <div className="space-y-2">
            <Label htmlFor={`reason-${setting.key}`}>Change Reason (optional)</Label>
            <Input
              id={`reason-${setting.key}`}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why are you making this change?"
            />
          </div>
        )}

        <div className="flex items-center gap-2">
          {isEditing && setting.is_editable ? (
            <>
              <Button
                size="sm"
                onClick={handleSave}
                disabled={isLoading || value === setting.value}
              >
                <Save className="mr-2 h-4 w-4" />
                Save
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCancel}
                disabled={isLoading}
              >
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
            </>
          ) : (
            <>
              {setting.is_editable && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setIsEditing(true)}
                  disabled={isLoading}
                >
                  Edit
                </Button>
              )}
              {setting.default_value && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleReset}
                        disabled={isLoading || !onReset}
                      >
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Reset
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Reset to default: {setting.default_value}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
