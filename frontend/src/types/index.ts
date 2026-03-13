// User types
export interface User {
  id: string
  email: string
  full_name: string
  role: 'user' | 'admin' | 'superadmin'
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface PasswordResetRequest {
  email: string
}

// Agent types
export interface Agent {
  id: string
  name: string
  type: string
  status: AgentStatus
  capabilities: Record<string, string>
  config: Record<string, unknown>
  workspace_id?: string
  created_at: string
  updated_at: string
  created_by: string
}

export type AgentStatus = 'idle' | 'running' | 'paused' | 'stopped' | 'error'

export interface AgentType {
  id: string
  name: string
  description: string
  capabilities: Record<string, string>
  default_config: Record<string, unknown>
  created_at: string
}

export interface AgentMetrics {
  agent_id: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  avg_execution_time_ms: number
  success_rate: number
  last_execution_at?: string
}

export interface AgentSession {
  id: string
  agent_id: string
  status: 'active' | 'completed' | 'failed'
  started_at: string
  ended_at?: string
  context: Record<string, unknown>
}

// Workflow types
export interface Workflow {
  id: string
  name: string
  description?: string
  definition: WorkflowDefinition
  status: WorkflowStatus
  created_at: string
  updated_at: string
  created_by: string
}

export type WorkflowStatus = 'draft' | 'active' | 'paused' | 'completed' | 'failed'

export interface WorkflowDefinition {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: {
    label: string
    agent_type?: string
    config?: Record<string, unknown>
  }
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
}

export interface WorkflowExecution {
  id: string
  workflow_id: string
  status: WorkflowStatus
  progress: number
  current_node_id?: string
  started_at: string
  completed_at?: string
  result?: Record<string, unknown>
  error?: string
}

// Task types
export interface Task {
  id: string
  type: string
  status: TaskStatus
  priority: TaskPriority
  payload: Record<string, unknown>
  result?: Record<string, unknown>
  error?: string
  agent_id?: string
  workflow_id?: string
  parent_task_id?: string
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export type TaskPriority = 'low' | 'normal' | 'high' | 'critical'

// Knowledge types
export interface KnowledgeEntity {
  id: string
  type: KnowledgeEntityType
  content: string
  metadata: Record<string, unknown>
  workspace_id: string
  created_at: string
  updated_at: string
  created_by: string
}

export type KnowledgeEntityType = 'document' | 'concept' | 'relationship' | 'fact'

export interface KnowledgeGraph {
  entities: KnowledgeGraphNode[]
  relationships: KnowledgeGraphRelationship[]
}

export interface KnowledgeGraphNode {
  id: string
  type: string
  label: string
  data: Record<string, unknown>
  position?: { x: number; y: number }
}

export interface KnowledgeGraphRelationship {
  id: string
  source: string
  target: string
  type: string
  label?: string
}

export interface SemanticSearchResult {
  entity: KnowledgeEntity
  relevance_score: number
  highlights: string[]
}

// Workspace types
export interface Workspace {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
  created_by: string
}

export interface WorkspaceFile {
  id: string
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  created_at: string
  updated_at: string
  children?: WorkspaceFile[]
}

// API types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  detail: string
  status_code: number
  headers?: Record<string, string>
}

// Notification types
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  read: boolean
  created_at: string
}

// WebSocket types
export interface WebSocketMessage {
  type: 'agent_update' | 'workflow_update' | 'task_update' | 'notification'
  payload: unknown
  timestamp: string
}

// Settings types
export interface UserSettings {
  theme: 'light' | 'dark' | 'system'
  notifications_enabled: boolean
  email_notifications: boolean
  language: string
  timezone: string
}

export interface ApiKey {
  id: string
  name: string
  key_prefix: string
  created_at: string
  expires_at?: string
  last_used_at?: string
}

export interface Integration {
  id: string
  name: string
  enabled: boolean
  config: Record<string, unknown>
}

// LLM Provider types
export type ProviderType = 'openai' | 'anthropic' | 'ollama' | 'lm_studio' | 'vllm' | 'custom'

export interface LLMProvider {
  id: string
  name: string
  provider_type: ProviderType
  base_url: string
  model_name: string
  api_key?: string | null
  is_active: boolean
  is_default: boolean
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface LLMProviderCreate {
  name: string
  provider_type: ProviderType
  base_url: string
  model_name: string
  api_key?: string
  is_active?: boolean
  is_default?: boolean
  config?: Record<string, unknown>
}

export interface LLMProviderUpdate {
  name?: string
  provider_type?: string
  base_url?: string
  model_name?: string
  api_key?: string
  is_active?: boolean
  is_default?: boolean
  config?: Record<string, unknown>
}

export interface LLMProviderList {
  providers: LLMProvider[]
  total: number
}

export interface LLMProviderPreset {
  name: string
  provider_type: ProviderType
  base_url: string
  model_name: string
  requires_api_key: boolean
  description: string
  config_template: Record<string, unknown>
}

export interface LLMProviderPresets {
  presets: LLMProviderPreset[]
}

export interface LLMTestRequest {
  model_name?: string
  test_prompt?: string
}

export interface LLMTestResponse {
  success: boolean
  message: string
  model_tested: string
  response_time_ms: number
  error?: string
}

export interface LLMUsageLog {
  id: string
  provider_id: string
  user_id: string
  agent_id?: string | null
  model_used: string
  tokens_input: number
  tokens_output: number
  cost_usd?: number | null
  request_type: string
  status: string
  error_message?: string | null
  response_time_ms: number
  created_at: string
}

export interface LLMUsageLogList {
  logs: LLMUsageLog[]
  total: number
  page: number
  page_size: number
}

export interface LLMUsageStats {
  total_requests: number
  total_tokens_input: number
  total_tokens_output: number
  total_cost_usd: number
  success_rate: number
  avg_response_time_ms: number
  requests_by_provider: Record<string, number>
  tokens_by_model: Record<string, number>
  cost_by_provider: Record<string, number>
}

export interface LLMUsageStatsRequest {
  start_date?: string
  end_date?: string
  provider_id?: string
  user_id?: string
  agent_id?: string
}
