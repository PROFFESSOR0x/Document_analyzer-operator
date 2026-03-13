"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Eye, EyeOff, Zap, Loader2 } from "lucide-react"
import toast from "react-hot-toast"
import { llmProvidersApi } from "@/lib/llm-providers-api"
import type { LLMProvider, LLMProviderCreate, ProviderType } from "@/types"

const providerSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  provider_type: z.enum([
    "openai",
    "anthropic",
    "ollama",
    "lm_studio",
    "vllm",
    "openai_compatible",
    "custom",
  ]),
  base_url: z.string().url("Must be a valid URL"),
  model_name: z.string().min(1, "Model name is required"),
  api_key: z.string().optional(),
  is_active: z.boolean().default(true),
  is_default: z.boolean().default(false),
  config: z.object({
    temperature: z.number().min(0).max(2).default(0.7),
    max_tokens: z.number().min(1).max(128000).default(4096),
    top_p: z.number().min(0).max(1).default(1),
    frequency_penalty: z.number().min(-2).max(2).default(0),
    presence_penalty: z.number().min(-2).max(2).default(0),
  }),
})

type ProviderFormData = z.infer<typeof providerSchema>

const PRESET_PROVIDERS: Array<{
  value: ProviderType
  label: string
  baseUrl: string
  defaultModel: string
  requiresApiKey: boolean
  description?: string
}> = [
  {
    value: "openai",
    label: "OpenAI",
    baseUrl: "https://api.openai.com/v1",
    defaultModel: "gpt-4",
    requiresApiKey: true,
  },
  {
    value: "anthropic",
    label: "Anthropic",
    baseUrl: "https://api.anthropic.com/v1",
    defaultModel: "claude-3-sonnet-20240229",
    requiresApiKey: true,
  },
  {
    value: "ollama",
    label: "Ollama (Local)",
    baseUrl: "http://localhost:11434/v1",
    defaultModel: "llama2",
    requiresApiKey: false,
  },
  {
    value: "lm_studio",
    label: "LM Studio (Local)",
    baseUrl: "http://localhost:1234/v1",
    defaultModel: "local-model",
    requiresApiKey: false,
  },
  {
    value: "vllm",
    label: "vLLM (Local)",
    baseUrl: "http://localhost:8000/v1",
    defaultModel: "facebook/opt-125m",
    requiresApiKey: false,
  },
  {
    value: "openai_compatible",
    label: "OpenAI-Compatible",
    baseUrl: "",
    defaultModel: "",
    requiresApiKey: false,
    description: "Custom OpenAI-compatible APIs (LocalAI, FastChat, Together AI, Anyscale, etc.)",
  },
  {
    value: "custom",
    label: "Custom",
    baseUrl: "",
    defaultModel: "",
    requiresApiKey: false,
  },
]

const COMPATIBLE_PRESETS: Array<{
  name: string
  baseUrl: string
  defaultModel: string
  requiresApiKey: boolean
  description: string
}> = [
  {
    name: "LocalAI",
    baseUrl: "http://localhost:8080/v1",
    defaultModel: "",
    requiresApiKey: false,
    description: "Self-hosted LocalAI instance",
  },
  {
    name: "FastChat",
    baseUrl: "http://localhost:8000/v1",
    defaultModel: "",
    requiresApiKey: false,
    description: "FastChat local server",
  },
  {
    name: "Together AI",
    baseUrl: "https://api.together.xyz/v1",
    defaultModel: "",
    requiresApiKey: true,
    description: "Cloud hosted open-source models",
  },
  {
    name: "Anyscale Endpoints",
    baseUrl: "https://api.endpoints.anyscale.com/v1",
    defaultModel: "",
    requiresApiKey: true,
    description: "Ray-powered model serving",
  },
  {
    name: "Groq",
    baseUrl: "https://api.groq.com/openai/v1",
    defaultModel: "",
    requiresApiKey: true,
    description: "Ultra-fast LPU inference",
  },
  {
    name: "DeepInfra",
    baseUrl: "https://api.deepinfra.com/v1",
    defaultModel: "",
    requiresApiKey: true,
    description: "Serverless model inference",
  },
  {
    name: "Lepton AI",
    baseUrl: "https://<workspace>.lepton.run/api/v1",
    defaultModel: "",
    requiresApiKey: true,
    description: "Lepton AI cloud platform",
  },
  {
    name: "Custom",
    baseUrl: "",
    defaultModel: "",
    requiresApiKey: false,
    description: "Enter custom URL",
  },
]

interface CreateProviderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  editingProvider?: LLMProvider | null
}

export function CreateProviderDialog({
  open,
  onOpenChange,
  onSuccess,
  editingProvider,
}: CreateProviderDialogProps) {
  const [showApiKey, setShowApiKey] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [compatiblePreset, setCompatiblePreset] = useState<string>("")

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
    reset,
  } = useForm<ProviderFormData>({
    resolver: zodResolver(providerSchema),
    defaultValues: {
      name: "",
      provider_type: "openai",
      base_url: "https://api.openai.com/v1",
      model_name: "gpt-4",
      api_key: "",
      is_active: true,
      is_default: false,
      config: {
        temperature: 0.7,
        max_tokens: 4096,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0,
      },
    },
  })

  const providerType = watch("provider_type")
  const requiresApiKey = PRESET_PROVIDERS.find((p) => p.value === providerType)?.requiresApiKey
  const isCompatibleProvider = providerType === "openai_compatible"

  useEffect(() => {
    if (editingProvider) {
      reset({
        name: editingProvider.name,
        provider_type: editingProvider.provider_type as ProviderType,
        base_url: editingProvider.base_url,
        model_name: editingProvider.model_name,
        api_key: "",
        is_active: editingProvider.is_active,
        is_default: editingProvider.is_default,
        config: {
          temperature: (editingProvider.config?.temperature as number) || 0.7,
          max_tokens: (editingProvider.config?.max_tokens as number) || 4096,
          top_p: (editingProvider.config?.top_p as number) || 1,
          frequency_penalty: (editingProvider.config?.frequency_penalty as number) || 0,
          presence_penalty: (editingProvider.config?.presence_penalty as number) || 0,
        },
      })
    } else if (open) {
      reset({
        name: "",
        provider_type: "openai",
        base_url: "https://api.openai.com/v1",
        model_name: "gpt-4",
        api_key: "",
        is_active: true,
        is_default: false,
        config: {
          temperature: 0.7,
          max_tokens: 4096,
          top_p: 1,
          frequency_penalty: 0,
          presence_penalty: 0,
        },
      })
      setCompatiblePreset("")
    }
  }, [editingProvider, open, reset])

  const handlePresetChange = (value: ProviderType) => {
    const preset = PRESET_PROVIDERS.find((p) => p.value === value)
    if (preset) {
      setValue("provider_type", value)
      setValue("base_url", preset.baseUrl)
      setValue("model_name", preset.defaultModel)
    }
  }

  const handleCompatiblePresetChange = (presetName: string) => {
    setCompatiblePreset(presetName)
    const preset = COMPATIBLE_PRESETS.find((p) => p.name === presetName)
    if (preset) {
      setValue("base_url", preset.baseUrl)
      setValue("model_name", preset.defaultModel)
      if (!preset.requiresApiKey) {
        setValue("api_key", "")
      }
    }
  }

  const handleTestConnection = async () => {
    const formData = watch()
    setTesting(true)
    setTestResult(null)

    try {
      // Create temporary provider for testing
      const data: LLMProviderCreate = {
        name: formData.name || "Test",
        provider_type: formData.provider_type,
        base_url: formData.base_url,
        model_name: formData.model_name,
        api_key: formData.api_key,
        is_active: true,
        config: formData.config,
      }

      // If editing, test existing provider
      if (editingProvider) {
        const result = await llmProvidersApi.testProvider(editingProvider.id, {
          test_prompt: "Hello, this is a connection test.",
        })

        setTestResult({
          success: result.success,
          message: result.success
            ? `Connection successful! (${result.response_time_ms}ms)`
            : result.message || result.error || "Connection failed",
        })

        if (result.success) {
          toast.success("Connection test passed!")
        } else {
          toast.error(result.message || "Connection test failed")
        }
      } else {
        // For new providers, we can't test without saving first
        toast.error("Please save the provider first, then test the connection")
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: "Failed to test connection",
      })
      toast.error("Failed to test connection")
    } finally {
      setTesting(false)
    }
  }

  const onSubmit = async (data: ProviderFormData) => {
    try {
      const providerData: LLMProviderCreate = {
        name: data.name,
        provider_type: data.provider_type,
        base_url: data.base_url,
        model_name: data.model_name,
        api_key: data.api_key || undefined,
        is_active: data.is_active,
        is_default: data.is_default,
        config: data.config,
      }

      if (editingProvider) {
        await llmProvidersApi.updateProvider(editingProvider.id, providerData)
        toast.success("Provider updated successfully")
      } else {
        await llmProvidersApi.createProvider(providerData)
        toast.success("Provider created successfully")
      }

      onSuccess()
    } catch (error) {
      toast.error(editingProvider ? "Failed to update provider" : "Failed to create provider")
      console.error(error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{editingProvider ? "Edit Provider" : "Add LLM Provider"}</DialogTitle>
          <DialogDescription>
            {editingProvider
              ? "Update your LLM provider configuration."
              : "Configure a new LLM provider to use with your agents."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-6 py-4">
            {/* Preset Selection */}
            <div className="space-y-2">
              <Label>Quick Setup</Label>
              <Select
                value={providerType}
                onValueChange={(value: ProviderType) => handlePresetChange(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a provider preset" />
                </SelectTrigger>
                <SelectContent>
                  {PRESET_PROVIDERS.map((preset) => (
                    <SelectItem key={preset.value} value={preset.value}>
                      {preset.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {PRESET_PROVIDERS.find((p) => p.value === providerType)?.description && (
                <p className="text-xs text-muted-foreground">
                  {PRESET_PROVIDERS.find((p) => p.value === providerType)?.description}
                </p>
              )}
            </div>

            {/* OpenAI-Compatible Presets */}
            {isCompatibleProvider && (
              <div className="space-y-2 rounded-lg border p-4 bg-muted/50">
                <Label>OpenAI-Compatible Service Preset</Label>
                <Select value={compatiblePreset} onValueChange={handleCompatiblePresetChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a compatible service" />
                  </SelectTrigger>
                  <SelectContent>
                    {COMPATIBLE_PRESETS.map((preset) => (
                      <SelectItem key={preset.name} value={preset.name}>
                        {preset.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {compatiblePreset && (
                  <p className="text-xs text-muted-foreground">
                    {COMPATIBLE_PRESETS.find((p) => p.name === compatiblePreset)?.description}
                  </p>
                )}
              </div>
            )}

            <Tabs defaultValue="basic">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="config">Configuration</TabsTrigger>
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Provider Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., OpenAI, Local Ollama"
                    {...register("name")}
                  />
                  {errors.name && (
                    <p className="text-sm text-destructive">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="base_url">Base URL</Label>
                  <Input
                    id="base_url"
                    placeholder="https://api.example.com/v1"
                    {...register("base_url")}
                  />
                  {errors.base_url && (
                    <p className="text-sm text-destructive">{errors.base_url.message}</p>
                  )}
                  {isCompatibleProvider && (
                    <p className="text-xs text-muted-foreground">
                      Enter the base URL of your OpenAI-compatible API endpoint.
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="model_name">Default Model</Label>
                  <Input
                    id="model_name"
                    placeholder="e.g., gpt-4, llama2"
                    {...register("model_name")}
                  />
                  {errors.model_name && (
                    <p className="text-sm text-destructive">{errors.model_name.message}</p>
                  )}
                  {isCompatibleProvider && (
                    <p className="text-xs text-muted-foreground">
                      Enter the model name supported by your compatible API.
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="api_key">API Key (Optional)</Label>
                  <div className="relative">
                    <Input
                      id="api_key"
                      type={showApiKey ? "text" : "password"}
                      placeholder={requiresApiKey ? "sk-..." : "Optional for some providers"}
                      {...register("api_key")}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {requiresApiKey
                      ? "Your API key will be encrypted and stored securely."
                      : "Some OpenAI-compatible services don't require an API key. Leave empty if not needed."}
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="config" className="space-y-4">
                <div className="space-y-2">
                  <Label>Temperature: {watch("config.temperature")}</Label>
                  <Slider
                    value={[watch("config.temperature")]}
                    onValueChange={([value]) => setValue("config.temperature", value)}
                    min={0}
                    max={2}
                    step={0.1}
                  />
                  <p className="text-xs text-muted-foreground">
                    Higher values make output more random, lower values more deterministic.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max_tokens">Max Tokens</Label>
                  <Input
                    id="max_tokens"
                    type="number"
                    {...register("config.max_tokens", { valueAsNumber: true })}
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum number of tokens in the response.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Top P: {watch("config.top_p")}</Label>
                  <Slider
                    value={[watch("config.top_p")]}
                    onValueChange={([value]) => setValue("config.top_p", value)}
                    min={0}
                    max={1}
                    step={0.05}
                  />
                </div>
              </TabsContent>

              <TabsContent value="advanced" className="space-y-4">
                <div className="space-y-2">
                  <Label>Frequency Penalty: {watch("config.frequency_penalty")}</Label>
                  <Slider
                    value={[watch("config.frequency_penalty")]}
                    onValueChange={([value]) => setValue("config.frequency_penalty", value)}
                    min={-2}
                    max={2}
                    step={0.1}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Presence Penalty: {watch("config.presence_penalty")}</Label>
                  <Slider
                    value={[watch("config.presence_penalty")]}
                    onValueChange={([value]) => setValue("config.presence_penalty", value)}
                    min={-2}
                    max={2}
                    step={0.1}
                  />
                </div>

                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <Label>Active</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable or disable this provider
                    </p>
                  </div>
                  <Switch
                    checked={watch("is_active")}
                    onCheckedChange={(checked) => setValue("is_active", checked)}
                  />
                </div>

                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <Label>Set as Default</Label>
                    <p className="text-sm text-muted-foreground">
                      Use this provider by default for all agents
                    </p>
                  </div>
                  <Switch
                    checked={watch("is_default")}
                    onCheckedChange={(checked) => setValue("is_default", checked)}
                  />
                </div>
              </TabsContent>
            </Tabs>

            {/* Test Connection */}
            {editingProvider && (
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Test Connection</Label>
                    <p className="text-sm text-muted-foreground">
                      Verify the provider configuration is working
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleTestConnection}
                    disabled={testing}
                  >
                    {testing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Testing...
                      </>
                    ) : (
                      <>
                        <Zap className="mr-2 h-4 w-4" />
                        Test
                      </>
                    )}
                  </Button>
                </div>
                {testResult && (
                  <p
                    className={`mt-2 text-sm ${
                      testResult.success ? "text-green-600" : "text-destructive"
                    }`}
                  >
                    {testResult.message}
                  </p>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : editingProvider ? (
                "Update Provider"
              ) : (
                "Create Provider"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
