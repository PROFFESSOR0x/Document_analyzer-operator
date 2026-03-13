# Frontend Architecture

## Overview

The Document Analyzer Operator frontend is built with Next.js 14 using the App Router architecture. It follows a component-driven design with clear separation of concerns.

## Architecture Principles

### 1. Server Components First

- Default to Server Components for data fetching
- Use Client Components only for interactivity
- Minimize JavaScript bundle size

### 2. Component Hierarchy

```
App (Root Layout)
├── Providers (Theme, Query, Auth)
└── Pages
    ├── Authentication (Login, Register)
    └── Dashboard
        ├── Layout (Sidebar + Header)
        └── Feature Pages
            ├── Agents
            ├── Workflows
            ├── Tasks
            ├── Knowledge
            ├── Workspace
            └── Settings
```

### 3. State Management Layers

```
┌─────────────────────────────────────┐
│         Server State                │
│    (TanStack Query / API)          │
├─────────────────────────────────────┤
│         Client State                │
│      (Zustand Stores)              │
├─────────────────────────────────────┤
│         Local State                 │
│    (React useState/useReducer)     │
└─────────────────────────────────────┘
```

## Directory Structure

### `/src/app`

Next.js App Router pages and layouts:
- `layout.tsx` - Root layout with providers
- `page.tsx` - Home page (redirects to dashboard)
- `dashboard/` - Protected dashboard pages
- `login/` - Authentication pages

### `/src/components`

Reusable React components:

**`/ui`** - Base UI components (Radix-based):
- Button, Input, Select, Dialog, etc.
- Fully accessible and composable
- No business logic

**`/domain`** - Domain-specific components:
- AgentCard, AgentStatus, TaskCard, etc.
- Contain business logic
- Compose UI components

**`/layout`** - Layout components:
- Sidebar, Header, DashboardLayout
- App shell structure

**`/providers`** - Context providers:
- ThemeProvider, QueryProvider, AuthProvider
- Wrap application with contexts

### `/src/lib`

Core utilities and configuration:
- `api-client.ts` - Axios-based API client
- `utils.ts` - Utility functions
- Shared constants and helpers

### `/src/hooks`

Custom React hooks:
- `use-agents.ts` - Agent-related hooks
- Data fetching with TanStack Query
- Business logic encapsulation

### `/src/stores`

Zustand stores for client state:
- `auth-store.ts` - Authentication state
- `agent-store.ts` - Agent filtering/selection
- `notification-store.ts` - Notifications
- `websocket-store.ts` - WebSocket connection

### `/src/types`

TypeScript type definitions:
- Shared interfaces
- API response types
- Domain models

### `/src/test`

Test configuration and utilities:
- Vitest setup
- Mocks and fixtures
- Test utilities

## Data Flow

### Server State (TanStack Query)

```
Component → Hook → Query Client → API Client → Backend
                     ↓
                  Cache
                     ↓
              Auto-refetch
```

### Client State (Zustand)

```
Component → Store → Action → State Update
    ↓                     ↓
 Subscribe            Persist
    ↓                     ↓
  Re-render            Storage
```

### Real-time Updates (WebSocket)

```
Backend → WebSocket → Store → Components
                           ↓
                      Auto-update
```

## Authentication Flow

```
1. User enters credentials
2. POST /api/v1/auth/login
3. Store tokens in localStorage
4. Redirect to dashboard
5. Include token in all requests
6. Auto-refresh on 401
7. Logout on refresh failure
```

## API Integration

### API Client

```typescript
class ApiClient {
  - Axios instance with interceptors
  - Automatic token injection
  - Token refresh on 401
  - Error handling
  - Retry logic
}
```

### Query Hooks

```typescript
useAgents(filters)     // List agents with filtering
useAgent(id)           // Single agent by ID
useAgentMetrics(id)    // Agent performance metrics
useCreateAgent()       // Create new agent
useUpdateAgent(id)     // Update existing agent
useDeleteAgent()       // Delete agent
useAgentAction(id)     // Start/stop/pause/resume
```

## Component Patterns

### Base Components

```tsx
// Simple, composable, no business logic
export function Button({ variant, size, children }) {
  return <button className={cn(buttonVariants({ variant, size }))}>{children}</button>
}
```

### Domain Components

```tsx
// Business logic, data fetching
export function AgentCard({ agent }) {
  const actionMutation = useAgentAction(agent.id)
  
  const handleStart = () => {
    actionMutation.mutate('start')
  }
  
  return <Card>...</Card>
}
```

### Page Components

```tsx
// Layout, data composition
export default function AgentsPage() {
  const { data: agents } = useAgents()
  
  return (
    <DashboardLayout>
      <AgentList agents={agents} />
    </DashboardLayout>
  )
}
```

## Styling System

### Design Tokens

```javascript
// tailwind.config.js
colors: {
  primary: 'hsl(var(--primary))',
  secondary: 'hsl(var(--secondary))',
  // ...
}
```

### CSS Variables

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  // ...
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  // ...
}
```

### Utility Classes

```tsx
<div className={cn(
  "flex items-center gap-2",
  "rounded-md border",
  "bg-card text-card-foreground",
  "hover:bg-accent transition-colors"
)}>
```

## Testing Strategy

### Unit Tests

- Test utility functions
- Test hooks in isolation
- Mock external dependencies

### Component Tests

- Render components
- Test user interactions
- Verify accessibility

### E2E Tests

- Test full user flows
- Cross-browser testing
- Visual regression (future)

## Performance Optimization

### Code Splitting

- Automatic with Next.js
- Dynamic imports for heavy components
- Route-based splitting

### Image Optimization

- Next.js Image component
- Automatic optimization
- Lazy loading

### Bundle Analysis

```bash
npm run build
# Analyze .next/build-manifest.json
```

## Accessibility

### WCAG AA Compliance

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Color contrast

### Testing

- Manual keyboard testing
- Screen reader testing
- Automated tools (axe)

## Security

### Client-side

- Token storage in localStorage
- XSS prevention through React
- CSRF protection via tokens
- Input validation

### Server-side

- JWT authentication
- Rate limiting (backend)
- CORS configuration

## Deployment

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_WS_URL=wss://api.example.com
```

### Build Process

```bash
npm install
npm run build
npm run start
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Monitoring

### Client-side Metrics

- Page load time
- Time to interactive
- First contentful paint
- Error tracking (future)

### Logging

- Console in development
- Structured logging in production (future)
- Error boundaries

## Future Enhancements

1. **PWA Support**
   - Service workers
   - Offline mode
   - Push notifications

2. **Internationalization**
   - i18n framework
   - Multiple languages
   - RTL support

3. **Advanced Features**
   - Workflow visual builder
   - Knowledge graph visualization
   - Real-time collaboration
   - Advanced analytics

4. **Performance**
   - Virtual scrolling for large lists
   - Progressive hydration
   - Streaming SSR

## Best Practices

1. **TypeScript**
   - Strict mode enabled
   - No `any` types
   - Proper type definitions

2. **Component Design**
   - Single responsibility
   - Composable
   - Accessible by default

3. **Code Organization**
   - Co-locate related files
   - Clear naming conventions
   - Document complex logic

4. **Testing**
   - Test critical paths
   - Mock external dependencies
   - Maintain test coverage

5. **Performance**
   - Lazy load heavy components
   - Optimize images
   - Minimize re-renders
