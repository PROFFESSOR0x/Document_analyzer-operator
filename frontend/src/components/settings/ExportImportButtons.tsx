/**
 * ExportImportButtons component for settings export/import actions.
 */

"use client"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Download, Upload, FileJson } from "lucide-react"
import { useRef } from "react"
import toast from "react-hot-toast"

interface ExportImportButtonsProps {
  onExport: () => Promise<void>
  onImport: (file: File, overwrite: boolean) => Promise<void>
}

export function ExportImportButtons({ onExport, onImport }: ExportImportButtonsProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleExport = async () => {
    try {
      await onExport()
      toast.success("Settings exported successfully")
    } catch (error) {
      toast.error("Failed to export settings")
      console.error("Export error:", error)
    }
  }

  const handleImportClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type !== "application/json" && !file.name.endsWith(".json")) {
      toast.error("Please select a JSON file")
      return
    }

    try {
      await onImport(file, false)
      toast.success("Settings imported successfully")
    } catch (error) {
      toast.error("Failed to import settings")
      console.error("Import error:", error)
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="flex gap-2">
      <input
        ref={fileInputRef}
        type="file"
        accept=".json,application/json"
        onChange={handleFileChange}
        className="hidden"
      />
      
      <Button variant="outline" size="sm" onClick={handleExport}>
        <Download className="mr-2 h-4 w-4" />
        Export
      </Button>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" onClick={handleImportClick}>
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onClick={handleImportClick}>
            <FileJson className="mr-2 h-4 w-4" />
            Import from JSON
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
