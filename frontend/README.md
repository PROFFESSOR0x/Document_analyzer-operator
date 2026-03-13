# Document Analyzer Operator - Frontend

Production-ready Next.js 14 frontend dashboard for the Document Analyzer Operator Platform.

## Features

- **Next.js 14** - App Router with Server and Client Components
- **TypeScript** - Full type safety with strict mode
- **Tailwind CSS** - Utility-first styling with custom design system
- **Radix UI** - Accessible, unstyled components
- **TanStack Query** - Server state management with caching
- **Zustand** - Client state management
- **React Hook Form** - Form handling with Zod validation
- **WebSocket** - Real-time updates for agents, workflows, and tasks
- **Dark/Light Theme** - System-aware theme switching
- **Responsive Design** - Mobile, tablet, and desktop support
- **WCAG AA Compliance** - Accessibility-first development

## Quick Start

### Prerequisites

- Node.js 20+
- npm or pnpm
- Docker (optional, for containerized deployment)

### Installation

1. **Navigate to the frontend directory**

```bash
cd frontend
```

2. **Install dependencies**

```bash
npm install
```

3. **Copy environment file**

```bash
cp .env.example .env.local
```

4. **Update environment variables**

Edit `.env.local` and set:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: ws://localhost:8000)

5. **Start development server**

```bash
npm run dev
```

6. **Open in browser**

Navigate to http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── dashboard/          # Dashboard pages
│   │   │   ├── agents/         # Agent management
│   │   │   ├── workflows/      # Workflow management
│   │   │   ├── tasks/          # Task management
│   │   │   ├── knowledge/      # Knowledge base
│   │   │   ├── workspace/      # Workspace management
│   │   │   └── settings/       # User settings
│   │   ├── login/              # Login page
│   │   ├── register/           # Registration page
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/
│   │   ├── domain/             # Domain-specific components
│   │   ├── layout/             # Layout components (sidebar, header)
│   │   ├── providers/          # Context providers
│   │   └── ui/                 # Reusable UI components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities and API client
│   ├── stores/                 # Zustand stores
│   ├── test/                   # Test setup
│   └── types/                  # TypeScript types
├── e2e/                        # Playwright E2E tests
├── public/                     # Static assets
├── Dockerfile                  # Docker build configuration
├── docker-compose.yml          # Docker Compose configuration
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
├── vitest.config.ts            # Vitest configuration
└── playwright.config.ts        # Playwright configuration
```

## Available Scripts

### Development

```bash
npm run dev          # Start development server
```

### Build

```bash
npm run build        # Build for production
npm run start        # Start production server
```

### Testing

```bash
npm run test         # Run unit tests with Vitest
npm run test:ui      # Run tests with UI
npm run test:coverage # Run tests with coverage
npm run test:e2e     # Run E2E tests with Playwright
npm run test:e2e:ui  # Run E2E tests with UI
```

### Code Quality

```bash
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run format       # Format with Prettier
npm run format:check # Check formatting
npm run type-check   # Type check with TypeScript
```

### Docker

```bash
npm run docker:build # Build Docker image
npm run docker:run   # Run Docker container
```

## Pages and Components

### Pages Created

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | User authentication |
| Register | `/register` | User registration |
| Dashboard | `/dashboard` | System overview |
| Agents | `/dashboard/agents` | Agent list and management |
| Agent Detail | `/dashboard/agents/[id]` | Agent details and metrics |
| Workflows | `/dashboard/workflows` | Workflow list and management |
| Tasks | `/dashboard/tasks` | Task board and monitoring |
| Knowledge | `/dashboard/knowledge` | Knowledge base and graph |
| Workspace | `/dashboard/workspace` | File management and editor |
| Settings | `/dashboard/settings` | User settings and preferences |

### UI Components

**Base Components (Radix-based):**
- Button (variants: default, destructive, outline, secondary, ghost, link)
- Input (text, password, email, number)
- Select (dropdown selection)
- Dialog/Modal (overlays and popups)
- Dropdown Menu (context menus)
- Tabs (tabbed interfaces)
- Toast/Notification (alerts and feedback)
- Tooltip (hover information)
- Badge (status indicators)
- Card (content containers)
- Progress (progress bars)
- ScrollArea (custom scrollbars)
- Switch (toggle switches)
- Label (form labels)

**Domain Components:**
- LoadingSpinner - Loading states
- ErrorBoundary - Error handling
- AgentStatus - Agent status indicators
- AgentCard - Agent display cards
- SearchBar - Search input component

## API Integration

The frontend integrates with the backend API through a typed API client:

```typescript
import { apiClient } from '@/lib/api-client'

// Get agents
const agents = await apiClient.get<Agent[]>('/api/v1/agents')

// Create agent
const agent = await apiClient.post<Agent>('/api/v1/agents', data)

// Update agent
await apiClient.patch(`/api/v1/agents/${id}`, data)

// Delete agent
await apiClient.delete(`/api/v1/agents/${id}`)
```

### React Query Hooks

Custom hooks for common operations:

```typescript
import { useAgents, useAgent, useCreateAgent } from '@/hooks/use-agents'

// List agents
const { data: agents } = useAgents({ status: 'running' })

// Single agent
const { data: agent } = useAgent('agent-id')

// Create agent
const createAgent = useCreateAgent()
await createAgent.mutateAsync({ name: 'My Agent', type: 'cognitive' })
```

## State Management

### Client State (Zustand)

- `auth-store` - Authentication and user settings
- `agent-store` - Agent filtering and selection
- `notification-store` - Notifications management
- `websocket-store` - WebSocket connection

### Server State (TanStack Query)

- Automatic caching and invalidation
- Optimistic updates
- Background refetching
- Retry logic

## Real-time Features

WebSocket integration for:
- Agent status updates
- Workflow progress updates
- Task state changes
- Live notifications
- Log streaming

## Accessibility

The frontend follows WCAG AA guidelines:
- Semantic HTML
- ARIA labels and roles
- Keyboard navigation
- Focus management
- Color contrast (4.5:1 minimum)
- Screen reader support

## Testing Strategy

### Unit Tests (Vitest)

Test individual components and utilities:

```typescript
import { describe, it, expect } from 'vitest'
import { formatDate } from '@/lib/utils'

describe('formatDate', () => {
  it('formats date correctly', () => {
    const result = formatDate('2024-01-15')
    expect(result).toContain('2024')
  })
})
```

### Component Tests (React Testing Library)

Test component rendering and interactions:

```typescript
import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

### E2E Tests (Playwright)

Test full user flows:

```typescript
import { test, expect } from '@playwright/test'

test('login flow', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'user@example.com')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')
})
```

## Build and Deployment

### Production Build

```bash
npm run build
npm run start
```

### Docker Deployment

```bash
# Build image
docker build -t document-analyzer-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api.example.com \
  document-analyzer-frontend
```

### Docker Compose

```bash
docker-compose up -d
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | ws://localhost:8000 | WebSocket URL |
| `NEXT_PUBLIC_APP_NAME` | Document Analyzer Operator | Application name |
| `NEXT_PUBLIC_TOKEN_REFRESH_INTERVAL` | 1800000 | Token refresh interval (ms) |

## Known Limitations and TODOs

### Current Limitations

1. **Mock Data**: Some pages use mock data until backend API is fully implemented
2. **Workflow Builder**: Visual workflow editor needs React Flow integration
3. **Knowledge Graph**: Graph visualization needs D3.js or React Flow implementation
4. **Terminal Emulator**: xterm.js integration pending for workspace terminal
5. **Monaco Editor**: Code editor integration pending for file editing

### TODOs

- [ ] Implement visual workflow builder with React Flow
- [ ] Add knowledge graph visualization with D3.js
- [ ] Integrate Monaco Editor for code editing
- [ ] Add xterm.js terminal emulator
- [ ] Implement file upload/download functionality
- [ ] Add comprehensive E2E test coverage
- [ ] Implement advanced filtering and sorting
- [ ] Add export/import functionality for workflows
- [ ] Implement real-time log streaming
- [ ] Add performance monitoring and analytics
- [ ] Implement offline support with service workers
- [ ] Add PWA capabilities
- [ ] Implement internationalization (i18n)
- [ ] Add comprehensive error handling and error pages
- [ ] Implement rate limiting feedback
- [ ] Add user onboarding flow
- [ ] Implement help documentation

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation as needed

## License

Part of the Document-Analyzer-Operator Platform.
