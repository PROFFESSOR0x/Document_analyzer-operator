/**
 * CategorySelector component for navigating between setting categories.
 */

"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import type { SettingCategory } from "@/types"
import {
  Cpu,
  Database,
  Server,
  Shield,
  Settings,
  Monitor,
  LayoutGrid,
} from "lucide-react"

interface CategorySelectorProps {
  categories: SettingCategory[]
  selectedCategory: string | null
  onSelectCategory: (category: string | null) => void
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  cpu: Cpu,
  database: Database,
  server: Server,
  shield: Shield,
  settings: Settings,
  monitor: Monitor,
  default: LayoutGrid,
}

export function CategorySelector({
  categories,
  selectedCategory,
  onSelectCategory,
}: CategorySelectorProps) {
  const getIcon = (iconName: string) => {
    const Icon = iconMap[iconName] || iconMap.default
    return <Icon className="h-4 w-4 mr-2" />
  }

  return (
    <Card>
      <CardContent className="p-4">
        <ScrollArea className="w-full whitespace-nowrap">
          <div className="flex gap-2">
            <Button
              variant={selectedCategory === null ? "default" : "outline"}
              size="sm"
              onClick={() => onSelectCategory(null)}
            >
              <LayoutGrid className="h-4 w-4 mr-2" />
              All Settings
              {selectedCategory === null && (
                <Badge variant="secondary" className="ml-2">
                  {categories.reduce((sum, c) => sum + c.setting_count, 0)}
                </Badge>
              )}
            </Button>
            
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "default" : "outline"}
                size="sm"
                onClick={() => onSelectCategory(category.id)}
              >
                {getIcon(category.icon)}
                {category.name}
                <Badge variant="secondary" className="ml-2">
                  {category.setting_count}
                </Badge>
              </Button>
            ))}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
