# Component Usage Examples

## UI Components

### Button

```tsx
import { Button } from '@/components/ui/button'

// Default
<Button>Click me</Button>

// Variants
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Search /></Button>

// Disabled
<Button disabled>Disabled</Button>

// As child
<Button asChild>
  <Link href="/page">Navigate</Link>
</Button>
```

### Input

```tsx
import { Input } from '@/components/ui/input'

// Text input
<Input type="text" placeholder="Enter text" />

// Email
<Input type="email" placeholder="email@example.com" />

// Password
<Input type="password" placeholder="Password" />

// Disabled
<Input disabled placeholder="Disabled" />

// With label
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" />
```

### Card

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Dialog

```tsx
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

<Dialog>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description goes here.
      </DialogDescription>
    </DialogHeader>
    <div>Dialog content</div>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Save</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Select

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

<Select defaultValue="option1">
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
    <SelectItem value="option3">Option 3</SelectItem>
  </SelectContent>
</Select>
```

### Badge

```tsx
import { Badge } from '@/components/ui/badge'

<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
<Badge variant="success">Success</Badge>
<Badge variant="warning">Warning</Badge>
```

### Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

### Toast

```tsx
import toast from 'react-hot-toast'

// Success
toast.success('Operation successful!')

// Error
toast.error('Something went wrong')

// Loading
const loadingToast = toast.loading('Processing...')
toast.success('Done!', { id: loadingToast })

// Custom
toast((t) => (
  <span>
    {t.visible ? 'Hello' : 'Bye'}
  </span>
))
```

## Domain Components

### AgentCard

```tsx
import { AgentCard } from '@/components/domain/agent-card'

<AgentCard
  agent={agent}
  onView={(agent) => router.push(`/dashboard/agents/${agent.id}`)}
  onAction={(agent, action) => handleAgentAction(agent, action)}
/>
```

### AgentStatus

```tsx
import { AgentStatusIndicator } from '@/components/domain/agent-status'

<AgentStatusIndicator status="running" showLabel />
<AgentStatusIndicator status="idle" />
```

### SearchBar

```tsx
import { SearchBar } from '@/components/domain/search-bar'

<SearchBar
  placeholder="Search..."
  value={search}
  onChange={setSearch}
  className="w-64"
/>
```

### LoadingSpinner

```tsx
import { LoadingSpinner } from '@/components/domain/loading-spinner'

<LoadingSpinner size="sm" />
<LoadingSpinner size="md" />
<LoadingSpinner size="lg" />
```

### ErrorBoundary

```tsx
import { ErrorBoundary } from '@/components/domain/error-boundary'

<ErrorBoundary fallback={<div>Something went wrong</div>}>
  <MyComponent />
</ErrorBoundary>
```

## Hooks

### useAgents

```tsx
import { useAgents, useAgent, useCreateAgent } from '@/hooks/use-agents'

// List agents
const { data: agents, isLoading } = useAgents({
  status: 'running',
  type: 'cognitive',
  search: 'research',
})

// Single agent
const { data: agent } = useAgent('agent-id')

// Create agent
const createAgent = useCreateAgent()
await createAgent.mutateAsync({
  name: 'My Agent',
  type: 'cognitive',
  config: {},
})

// Update agent
const updateAgent = useUpdateAgent('agent-id')
await updateAgent.mutateAsync({ status: 'paused' })

// Delete agent
const deleteAgent = useDeleteAgent()
await deleteAgent.mutateAsync('agent-id')

// Agent action
const agentAction = useAgentAction('agent-id')
await agentAction.mutateAsync('start')
```

## State Management

### Auth Store

```tsx
import { useAuthStore } from '@/stores/auth-store'

const { user, isAuthenticated, login, logout } = useAuthStore()

// Login
await login('email@example.com', 'password')

// Logout
await logout()

// Update settings
updateSettings({ theme: 'dark' })
```

### Notification Store

```tsx
import { useNotificationStore } from '@/stores/notification-store'

const { notifications, unreadCount, addNotification } = useNotificationStore()

addNotification({
  type: 'success',
  title: 'Task Completed',
  message: 'Your task has been completed successfully',
})
```

## Utilities

### Class Names

```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  "flex items-center",
  isActive && "bg-primary text-primary-foreground",
  className
)} />
```

### Date Formatting

```tsx
import { formatDate, formatRelativeTime } from '@/lib/utils'

formatDate(new Date()) // "Jan 15, 2024, 10:30 AM"
formatRelativeTime(new Date(Date.now() - 3600000)) // "1h ago"
```

### Copy to Clipboard

```tsx
import { copyToClipboard } from '@/lib/utils'

await copyToClipboard('Text to copy')
toast.success('Copied to clipboard')
```

### Download File

```tsx
import { downloadFile } from '@/lib/utils'

downloadFile(JSON.stringify(data, null, 2), 'data.json', 'application/json')
```
