/**
 * SettingSearch component for searching settings.
 */

"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, X } from "lucide-react"

interface SettingSearchProps {
  value: string
  onChange: (value: string) => void
  onClear: () => void
}

export function SettingSearch({ value, onChange, onClear }: SettingSearchProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search settings by key or description..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pl-10"
        />
      </div>
      {value && (
        <Button variant="ghost" size="sm" onClick={onClear}>
          <X className="h-4 w-4" />
          Clear
        </Button>
      )}
    </div>
  )
}
