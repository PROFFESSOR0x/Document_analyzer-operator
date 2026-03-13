"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Plus,
  Trash2,
  Edit,
  CheckCircle,
  XCircle,
  Zap,
  Cpu,
  Globe,
  Key,
  Loader2,
  RefreshCw,
  BarChart3,
} from "lucide-react"
import { useState, useEffect } from "react"
import { useAuthStore } from "@/stores/auth-store"
import toast from "react-hot-toast"
import { llmProvidersApi } from "@/lib/llm-providers-api"
import type { LLMProvider, LLMProviderCreate, ProviderType } from "@/types"
import { CreateProviderDialog } from "./create-dialog"
import { UsageStats } from "./usage-stats"

const PROVIDER_TYPE_LABELS: Record<ProviderType, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic",
  ollama: "Ollama",
  lm_studio: "LM Studio",
  vllm: "vLLM",
  custom: "Custom",
}

const PROVIDER_TYPE_COLORS: Record<ProviderType, string> = {
  openai: "bg-green-500",
  anthropic: "bg-orange-500",
  ollama: "bg-blue-500",
  lm_studio: "bg-purple-500",
  vllm: "bg-red-500",
  custom: "bg-gray-500",
}

export default function LLMProvidersPage() {
  const { user } = useAuthStore()
  const [providers, setProviders] = useState<LLMProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [testingId, setTestingId] = useState<string | null>(null)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<LLMProvider | null>(null)

  const loadProviders = async () => {
    try {
      setLoading(true)
      const response = await llmProvidersApi.listProviders()
      setProviders(response.providers)
    } catch (error) {
      toast.error("Failed to load providers")
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProviders()
  }, [])

  const handleTestConnection = async (provider: LLMProvider) => {
    setTestingId(provider.id)
    try {
      const result = await llmProvidersApi.testProvider(provider.id, {
        test_prompt: "Hello, this is a connection test.",
      })

      if (result.success) {
        toast.success(`Connection successful! (${result.response_time_ms}ms)`)
      } else {
        toast.error(result.message || "Connection failed")
      }
    } catch (error) {
      toast.error("Failed to test connection")
      console.error(error)
    } finally {
      setTestingId(null)
    }
  }

  const handleSetDefault = async (provider: LLMProvider) => {
    try {
      await llmProvidersApi.setDefaultProvider(provider.id)
      toast.success("Default provider updated")
      await loadProviders()
    } catch (error) {
      toast.error("Failed to set default provider")
      console.error(error)
    }
  }

  const handleDelete = async (provider: LLMProvider) => {
    if (!confirm(`Are you sure you want to delete "${provider.name}"?`)) {
      return
    }

    try {
      await llmProvidersApi.deleteProvider(provider.id)
      toast.success("Provider deleted")
      await loadProviders()
    } catch (error) {
      toast.error("Failed to delete provider")
      console.error(error)
    }
  }

  const handleEdit = (provider: LLMProvider) => {
    setEditingProvider(provider)
    setCreateDialogOpen(true)
  }

  const handleCreateSuccess = () => {
    setCreateDialogOpen(false)
    setEditingProvider(null)
    loadProviders()
  }

  const defaultProvider = providers.find((p) => p.is_default)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LLM Providers</h1>
            <p className="text-muted-foreground">Manage your AI model providers and API keys</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => loadProviders()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Provider
            </Button>
          </div>
        </div>

        <Tabs defaultValue="providers" className="space-y-4">
          <TabsList>
            <TabsTrigger value="providers">Providers</TabsTrigger>
            <TabsTrigger value="usage">Usage Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="providers" className="space-y-4">
            {loading ? (
              <Card>
                <CardContent className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </CardContent>
              </Card>
            ) : providers.length === 0 ? (
              <Card>
                <CardHeader>
                  <CardTitle>No Providers Configured</CardTitle>
                  <CardDescription>
                    Add your first LLM provider to start using AI models with your agents.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button onClick={() => setCreateDialogOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Provider
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {providers.map((provider) => (
                  <Card key={provider.id} className="relative">
                    {provider.is_default && (
                      <div className="absolute right-4 top-4">
                        <Badge variant="default" className="gap-1">
                          <CheckCircle className="h-3 w-3" />
                          Default
                        </Badge>
                      </div>
                    )}
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-10 w-10 items-center justify-center rounded-full ${PROVIDER_TYPE_COLORS[provider.provider_type]}`}
                          >
                            <Cpu className="h-5 w-5 text-white" />
                          </div>
                          <div>
                            <CardTitle className="text-lg">{provider.name}</CardTitle>
                            <CardDescription className="flex items-center gap-1">
                              <Globe className="h-3 w-3" />
                              {PROVIDER_TYPE_LABELS[provider.provider_type]}
                            </CardDescription>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          <Key className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">
                            {provider.api_key ? "••••••••" : "No API key"}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Zap className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{provider.model_name}</span>
                        </div>
                        <div className="truncate text-xs text-muted-foreground">
                          {provider.base_url}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Badge variant={provider.is_active ? "default" : "secondary"}>
                          {provider.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1"
                          onClick={() => handleTestConnection(provider)}
                          disabled={testingId === provider.id}
                        >
                          {testingId === provider.id ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <Zap className="mr-2 h-4 w-4" />
                          )}
                          Test
                        </Button>
                        {!provider.is_default && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            onClick={() => handleSetDefault(provider)}
                          >
                            Set Default
                          </Button>
                        )}
                      </div>

                      <div className="flex gap-2 border-t pt-3">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="flex-1"
                          onClick={() => handleEdit(provider)}
                        >
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="flex-1 text-destructive hover:text-destructive"
                          onClick={() => handleDelete(provider)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="usage" className="space-y-4">
            <UsageStats />
          </TabsContent>
        </Tabs>
      </div>

      <CreateProviderDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={handleCreateSuccess}
        editingProvider={editingProvider}
      />
    </DashboardLayout>
  )
}
