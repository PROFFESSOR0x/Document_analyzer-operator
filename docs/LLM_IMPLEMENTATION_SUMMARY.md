# LLM Provider Management - Implementation Summary

## Overview

This implementation adds comprehensive OpenAI-compatible API key management to the Document-Analyzer-Operator Platform, supporting multiple LLM providers including OpenAI, Anthropic, and local LLMs (Ollama, LM Studio, vLLM).

## Files Created

### Backend

#### Database Models
- `backend/app/models/llm_provider.py` - LLMProvider model with provider configuration
- `backend/app/models/llm_usage.py` - LLMUsageLog model for tracking API usage
- `backend/app/models/__init__.py` - Updated to export new models

#### Schemas
- `backend/app/schemas/llm_provider.py` - Pydantic schemas for request/response validation
- `backend/app/schemas/__init__.py` - Updated to export new schemas

#### Services
- `backend/app/services/llm_provider_service.py` - Service layer for provider management and encryption
- `backend/app/services/llm_client.py` - Unified LLM client with multi-provider support
- `backend/app/services/__init__.py` - Updated to export new services

#### API Routes
- `backend/app/api/v1/routes/llm_providers.py` - RESTful API endpoints
- `backend/app/api/v1/router.py` - Updated to include LLM providers router

#### Database Migrations
- `backend/alembic/versions/20260101_000100_add_llm_providers.py` - Alembic migration

#### Configuration
- `backend/.env.example` - Updated with LLM provider environment variables
- `backend/pyproject.toml` - Added cryptography, openai, and anthropic dependencies

#### Documentation
- `backend/docs/LLM_PROVIDERS.md` - Comprehensive setup and usage guide

### Frontend

#### Types
- `frontend/src/types/index.ts` - Updated with LLM provider TypeScript types

#### API Client
- `frontend/src/lib/llm-providers-api.ts` - API client for LLM provider operations

#### Pages & Components
- `frontend/src/app/dashboard/settings/llm-providers/page.tsx` - Main LLM providers management page
- `frontend/src/app/dashboard/settings/llm-providers/create-dialog.tsx` - Create/edit provider dialog
- `frontend/src/app/dashboard/settings/llm-providers/usage-stats.tsx` - Usage statistics dashboard
- `frontend/src/app/dashboard/settings/page.tsx` - Updated with LLM providers link

## Features Implemented

### 1. Database Models

**LLMProvider Model:**
- UUID primary key
- Provider name (unique)
- Provider type (enum: openai, anthropic, ollama, lm_studio, vllm, custom)
- Base URL for API endpoint
- Encrypted API key (nullable for local providers)
- Default model name
- Active/inactive status
- Default provider flag
- JSONB config for additional settings (temperature, max_tokens, etc.)
- Timestamps (created_at, updated_at)

**LLMUsageLog Model:**
- UUID primary key
- Foreign keys: provider_id, user_id, agent_id
- Model used
- Token counts (input, output)
- Cost in USD (nullable)
- Request type (completion, embedding, chat)
- Status (success, failed)
- Error message (nullable)
- Response time in milliseconds
- Timestamp

### 2. API Endpoints

```
GET    /api/v1/llm-providers              # List all providers
GET    /api/v1/llm-providers/{id}         # Get provider details
POST   /api/v1/llm-providers              # Create new provider
PUT    /api/v1/llm-providers/{id}         # Update provider
DELETE /api/v1/llm-providers/{id}         # Delete provider
POST   /api/v1/llm-providers/{id}/test    # Test connection
POST   /api/v1/llm-providers/{id}/set-default  # Set as default
GET    /api/v1/llm-providers/usage        # Get usage statistics
GET    /api/v1/llm-providers/usage/logs   # Get detailed usage logs
```

### 3. Service Layer

**LLMProviderService:**
- `create_provider()` - Create new LLM provider with encrypted API key
- `get_provider()` - Get provider by ID
- `list_providers()` - List all providers with filters
- `update_provider()` - Update provider configuration
- `delete_provider()` - Delete provider
- `set_default_provider()` - Set default provider
- `get_default_provider()` - Get current default provider
- `test_connection()` - Test API connection
- `log_usage()` - Log API usage
- `get_usage_stats()` - Get usage statistics
- `encrypt_api_key()` - Fernet encryption
- `decrypt_api_key()` - Fernet decryption

**LLMClient:**
- Unified interface for all providers
- Auto-detect provider type
- Support for chat completions, text completions, embeddings
- Automatic retry with exponential backoff
- Rate limiting support
- Token counting
- Cost estimation
- Error handling and logging
- Streaming support
- Fallback provider support

**Provider Implementations:**
- `OpenAIProvider` - OpenAI API with pricing data
- `AnthropicProvider` - Anthropic API with message format conversion
- `OllamaProvider` - Local Ollama with native embeddings
- `LMStudioProvider` - Local LM Studio (OpenAI-compatible)
- `VLLMProvider` - Local vLLM (OpenAI-compatible)
- `CustomProvider` - Generic OpenAI-compatible provider

### 4. Security Features

- **API Key Encryption**: All API keys encrypted using Fernet symmetric encryption
- **Environment Variable**: Encryption key stored in `ENCRYPTION_KEY` environment variable
- **Key Masking**: API keys masked in API responses (show first 4 and last 4 characters)
- **No Logging**: API keys never logged
- **Access Control**: Admin-only operations for sensitive provider management

### 5. Frontend Features

**LLM Providers Page:**
- List all configured providers in card layout
- Provider status indicators (active/inactive)
- Default provider badge
- Test connection button with loading state
- Set as default button
- Edit and delete actions
- Provider type color coding

**Create/Edit Dialog:**
- Quick setup with provider presets
- Provider type selector
- Base URL input with presets
- API key input with show/hide toggle
- Model name input
- Configuration options:
  - Temperature slider (0-2)
  - Max tokens input
  - Top P slider (0-1)
  - Frequency penalty slider (-2 to 2)
  - Presence penalty slider (-2 to 2)
- Active/inactive toggle
- Set as default toggle
- Test connection button (for existing providers)

**Usage Statistics Page:**
- Date range filters
- Provider filter
- Summary cards:
  - Total requests
  - Total tokens (input/output breakdown)
  - Total cost (USD)
  - Average response time
- Charts:
  - Requests by provider (bar chart)
  - Cost by provider (list)
  - Tokens by model (ranked list)
- Export to CSV functionality

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add to `.env`:
```bash
ENCRYPTION_KEY=your-generated-key-here
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Configure Providers

Use the API or frontend UI to configure providers:

**Example API Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/llm-providers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI",
    "provider_type": "openai",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-your-api-key",
    "model_name": "gpt-4",
    "is_active": true,
    "is_default": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

### 5. Test Connection

```bash
curl -X POST "http://localhost:8000/api/v1/llm-providers/PROVIDER_ID/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "test_prompt": "Hello, this is a test."
  }'
```

## Usage Examples

### Python SDK

```python
from app.services.llm_client import create_llm_client

# Create client
client = create_llm_client(timeout=60.0, max_retries=3)

# Register provider
client.register_provider(provider, api_key="decrypted-key")

# Chat completion
response = await client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    provider_id="provider-id",
    temperature=0.7,
    max_tokens=100
)

print(response.content)
print(f"Tokens: {response.usage.total_tokens}")

# Streaming
async for chunk in client.chat_completion(
    messages=[{"role": "user", "content": "Tell me a story"}],
    provider_id="provider-id",
    stream=True
):
    print(chunk.content, end="")

# Estimate cost
cost = client.estimate_cost(
    provider_id="provider-id",
    input_tokens=1000,
    output_tokens=500,
    model="gpt-4"
)
```

## Provider Presets

| Provider | Base URL | Default Model | API Key Required |
|----------|----------|---------------|------------------|
| OpenAI | https://api.openai.com/v1 | gpt-4 | Yes |
| Anthropic | https://api.anthropic.com/v1 | claude-3-sonnet-20240229 | Yes |
| Ollama | http://localhost:11434/v1 | llama2 | No |
| LM Studio | http://localhost:1234/v1 | local-model | No |
| vLLM | http://localhost:8000/v1 | facebook/opt-125m | No |
| Custom | User-defined | User-defined | Optional |

## Cost Estimation

### OpenAI (per 1K tokens)
- gpt-4: $0.03 input / $0.06 output
- gpt-4-turbo: $0.01 input / $0.03 output
- gpt-4o: $0.005 input / $0.015 output
- gpt-3.5-turbo: $0.0005 input / $0.0015 output

### Anthropic (per 1K tokens)
- claude-3-opus: $0.015 input / $0.075 output
- claude-3-sonnet: $0.003 input / $0.015 output
- claude-3-haiku: $0.00025 input / $0.00125 output

### Local Providers
- Ollama, LM Studio, vLLM: Free (local deployment)

## Known Limitations & TODOs

### Current Limitations

1. **Agent Integration**: The base agent class needs to be updated to use the LLM client for task execution. This requires modifying `backend/app/agents/core/base.py`.

2. **Batch Embeddings**: The embeddings API processes texts sequentially. For large batches, consider implementing parallel processing.

3. **Streaming Error Handling**: Streaming errors may not be caught as gracefully as non-streaming errors.

4. **Token Counting**: Token counting uses a simple character-based estimation. For production accuracy, consider integrating a proper tokenizer library.

### TODOs

1. **Agent Integration**: Update agent base class to use LLM client
   - Add `llm_client` dependency
   - Update `_execute_task()` to use LLM client
   - Support multiple LLM providers per agent
   - Add fallback provider on failure

2. **Model Auto-Discovery**: Add automatic model listing and selection UI for known providers

3. **Usage Alerts**: Implement usage threshold alerts (e.g., notify when approaching cost limit)

4. **Provider Health Checks**: Add periodic health checks for configured providers

5. **Rate Limit Dashboard**: Visualize rate limit status and quotas per provider

6. **Custom Pricing**: Allow users to configure custom pricing for custom providers via UI

7. **Batch Operations**: Add bulk import/export for provider configurations

8. **Audit Log**: Add audit logging for provider configuration changes

9. **Multi-Region Support**: Support for provider endpoints in different regions

10. **Model Switching**: Allow agents to switch models dynamically based on task requirements

## Testing

### Unit Tests (TODO)

```python
# tests/test_llm_provider_service.py
def test_encrypt_decrypt_api_key():
    service = LLMProviderService(db)
    original = "test-api-key"
    encrypted = service.encrypt_api_key(original)
    decrypted = service.decrypt_api_key(encrypted)
    assert decrypted == original

def test_create_provider():
    # Test provider creation with encryption
    pass

def test_log_usage():
    # Test usage logging
    pass
```

### Integration Tests (TODO)

```python
# tests/test_llm_client.py
@pytest.mark.asyncio
async def test_openai_chat_completion():
    # Test OpenAI provider
    pass

@pytest.mark.asyncio
async def test_ollama_chat_completion():
    # Test Ollama provider (requires local Ollama)
    pass
```

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs` (development only)
- ReDoc: `http://localhost:8000/redoc` (development only)

## Support

For issues or questions:
1. Check `backend/docs/LLM_PROVIDERS.md` for detailed documentation
2. Review error logs in `logs/app.log`
3. Test connection using the test endpoint
4. Verify environment variables are set correctly
