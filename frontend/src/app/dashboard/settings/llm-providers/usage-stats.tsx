"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { BarChart3, TrendingUp, DollarSign, Clock, Download, Loader2 } from "lucide-react"
import { llmProvidersApi } from "@/lib/llm-providers-api"
import type { LLMUsageStats, LLMProviderList } from "@/types"
import toast from "react-hot-toast"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, LineChart, Line } from "recharts"

export function UsageStats() {
  const [stats, setStats] = useState<LLMUsageStats | null>(null)
  const [providers, setProviders] = useState<LLMProviderList | null>(null)
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [selectedProvider, setSelectedProvider] = useState<string>("all")

  const loadStats = async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      if (selectedProvider !== "all") params.provider_id = selectedProvider

      const [statsResponse, providersResponse] = await Promise.all([
        llmProvidersApi.getUsageStats(params),
        llmProvidersApi.listProviders(),
      ])

      setStats(statsResponse)
      setProviders(providersResponse)
    } catch (error) {
      toast.error("Failed to load usage statistics")
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  const handleExport = () => {
    if (!stats) return

    const csvContent = [
      ["Metric", "Value"],
      ["Total Requests", stats.total_requests],
      ["Total Input Tokens", stats.total_tokens_input],
      ["Total Output Tokens", stats.total_tokens_output],
      ["Total Cost (USD)", stats.total_cost_usd],
      ["Success Rate (%)", stats.success_rate],
      ["Avg Response Time (ms)", stats.avg_response_time_ms],
    ]

    const blob = new Blob([csvContent.map((row) => row.join(",")).join("\n")], {
      type: "text/csv",
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `llm-usage-stats-${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)

    toast.success("Usage data exported")
  }

  const chartData = stats
    ? Object.entries(stats.requests_by_provider).map(([provider, count]) => ({
        provider,
        requests: count,
      }))
    : []

  const chartConfig: ChartConfig = {
    requests: {
      label: "Requests",
      color: "hsl(var(--chart-1))",
    },
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter usage statistics by date range and provider</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="provider">Provider</Label>
              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger>
                  <SelectValue placeholder="All providers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Providers</SelectItem>
                  {providers?.providers.map((provider) => (
                    <SelectItem key={provider.id} value={provider.id}>
                      {provider.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end gap-2">
              <Button onClick={loadStats} className="flex-1">
                Apply Filters
              </Button>
              <Button variant="outline" onClick={handleExport}>
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_requests.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.success_rate.toFixed(1)}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((stats?.total_tokens_input || 0) + (stats?.total_tokens_output || 0)).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Input: {(stats?.total_tokens_input || 0).toLocaleString()} |
              Output: {(stats?.total_tokens_output || 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${stats?.total_cost_usd?.toFixed(4) || "0.0000"}
            </div>
            <p className="text-xs text-muted-foreground">USD equivalent</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avg_response_time_ms.toFixed(0) || 0}ms
            </div>
            <p className="text-xs text-muted-foreground">Per request</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Requests by Provider</CardTitle>
            <CardDescription>Number of requests per LLM provider</CardDescription>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <ChartContainer config={chartConfig} className="h-[300px]">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="provider" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="requests" fill="var(--color-requests)" />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                No data available
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost by Provider</CardTitle>
            <CardDescription>Total cost (USD) per provider</CardDescription>
          </CardHeader>
          <CardContent>
            {stats && Object.entries(stats.cost_by_provider).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(stats.cost_by_provider).map(([provider, cost]) => {
                  const providerName =
                    providers?.providers.find((p) => p.id === provider)?.name || provider
                  return (
                    <div key={provider} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{providerName}</span>
                      <span className="text-sm font-mono">${cost.toFixed(4)}</span>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                No cost data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tokens by Model */}
      <Card>
        <CardHeader>
          <CardTitle>Tokens by Model</CardTitle>
          <CardDescription>Total tokens used per model</CardDescription>
        </CardHeader>
        <CardContent>
          {stats && Object.entries(stats.tokens_by_model).length > 0 ? (
            <div className="space-y-4">
              {Object.entries(stats.tokens_by_model)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([model, tokens]) => (
                  <div key={model} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{model}</span>
                    <span className="text-sm font-mono">{tokens.toLocaleString()} tokens</span>
                  </div>
                ))}
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground">No model data available</div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
