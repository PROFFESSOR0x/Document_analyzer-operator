# OpenAI-Compatible API Setup Guide

## 🎯 Quick Start

This guide shows you how to configure and use OpenAI-compatible APIs in the Document-Analyzer-Operator Platform.

---

## 📋 Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Provider Configuration](#provider-configuration)
3. [Usage Examples](#usage-examples)
4. [API Reference](#api-reference)
5. [Troubleshooting](#troubleshooting)

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Generate Encryption Key

```bash
# Generate encryption key for API keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Save this key!** You'll need it for the `.env` file.

### 3. Configure Environment Variables

Edit `backend/.env`:

```bash
# Encryption Key (REQUIRED - from step 2)
ENCRYPTION_KEY=your_generated_encryption_key_here

# Default LLM Provider
DEFAULT_LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama Configuration (optional - local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2

# LM Studio Configuration (optional - local)
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# vLLM Configuration (optional - local)
VLLM_BASE_URL=http://localhost:8000/v1
```

### 4. Run Database Migrations

```bash
cd backend
poetry run alembic upgrade head
```

This creates two new tables:
- `llm_providers` - Stores provider configurations
- `llm_usage_logs` - Tracks API usage and costs

### 5. Start the Backend

```bash
poetry run uvicorn app.main:app --reload
```

---

## Provider Configuration

### Via API (Recommended)

#### 1. Add OpenAI Provider

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI GPT-4",
    "provider_type": "openai",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-your-openai-api-key",
    "model_name": "gpt-4",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

#### 2. Add Anthropic Provider

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Anthropic Claude 3",
    "provider_type": "anthropic",
    "base_url": "https://api.anthropic.com/v1",
    "api_key": "sk-ant-your-anthropic-key",
    "model_name": "claude-3-sonnet-20240229",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

#### 3. Add Ollama (Local - No API Key)

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Local Ollama",
    "provider_type": "ollama",
    "base_url": "http://localhost:11434/v1",
    "model_name": "llama2",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

**Note:** First, pull the model:
```bash
ollama pull llama2
```

#### 4. Add LM Studio (Local - No API Key)

1. Open LM Studio
2. Load a model (e.g., `mistral-7b`)
3. Start the local server
4. Add provider:

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LM Studio",
    "provider_type": "lm_studio",
    "base_url": "http://localhost:1234/v1",
    "model_name": "mistral-7b-instruct",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

### Via Frontend Dashboard

1. Navigate to: http://localhost:3000/dashboard/settings/llm-providers
2. Click **"Add Provider"**
3. Select provider type (OpenAI, Anthropic, Ollama, etc.)
4. Fill in the configuration form
5. Click **"Test Connection"** to verify
6. Click **"Save"**

---

## Usage Examples

### Python SDK Usage

```python
from app.services.llm_client import create_llm_client
from app.services.llm_provider_service import LLMProviderService

# Initialize
llm_client = create_llm_client(timeout=60.0, max_retries=3)
provider_service = LLMProviderService()

# Get provider from database
provider = await provider_service.get_provider(provider_id)
api_key = provider_service.decrypt_api_key(provider.api_key)

# Register provider
llm_client.register_provider(provider, api_key=api_key)

# Chat completion
response = await llm_client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    provider_id=provider.id,
    temperature=0.7,
    max_tokens=1024,
)

print(f"Response: {response.content}")
print(f"Tokens used: {response.usage.total_tokens}")
print(f"Estimated cost: ${response.cost_usd}")

# Streaming response
async for chunk in llm_client.chat_completion(
    messages=[{"role": "user", "content": "Write a poem about AI"}],
    provider_id=provider.id,
    stream=True,
):
    print(chunk.content, end="", flush=True)

# Generate embeddings
embeddings = await llm_client.embeddings(
    text="The quick brown fox jumps over the lazy dog",
    provider_id=provider.id,
)
print(f"Embedding dimensions: {len(embeddings[0])}")

# List available models
models = await llm_client.list_models(provider_id=provider.id)
print(f"Available models: {models}")
```

### Using Multiple Providers

```python
# Register multiple providers
openai_key = service.decrypt_api_key(openai_provider.api_key)
anthropic_key = service.decrypt_api_key(anthropic_provider.api_key)

llm_client.register_provider(openai_provider, api_key=openai_key)
llm_client.register_provider(anthropic_provider, api_key=anthropic_key)

# Use OpenAI for one task
response1 = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    provider_id=openai_provider.id,
)

# Use Anthropic for another task
response2 = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Hi there!"}],
    provider_id=anthropic_provider.id,
)
```

### Error Handling

```python
from app.services.llm_client import RateLimitError, AuthenticationError, TimeoutError

try:
    response = await llm_client.chat_completion(
        messages=[{"role": "user", "content": "Test"}],
        provider_id=provider.id,
    )
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except TimeoutError as e:
    print(f"Request timed out after {e.timeout} seconds")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## API Reference

### List Providers

```http
GET /api/v1/llm-providers
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "OpenAI GPT-4",
      "provider_type": "openai",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "is_active": true,
      "is_default": true,
      "created_at": "2026-03-13T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Create Provider

```http
POST /api/v1/llm-providers
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Provider",
  "provider_type": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model_name": "gpt-4",
  "is_active": true,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### Test Provider

```http
POST /api/v1/llm-providers/{id}/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "test_message": "Hello, are you working?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "model": "gpt-4",
  "response_time_ms": 234,
  "test_response": "Hello! Yes, I'm working correctly."
}
```

### Get Usage Statistics

```http
GET /api/v1/llm-providers/usage?start_date=2026-03-01&end_date=2026-03-31
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_requests": 1250,
  "total_tokens_input": 125000,
  "total_tokens_output": 87500,
  "total_cost_usd": 12.50,
  "success_rate": 0.98,
  "average_response_time_ms": 345,
  "by_provider": [
    {
      "provider_name": "OpenAI GPT-4",
      "requests": 800,
      "tokens_input": 80000,
      "tokens_output": 56000,
      "cost_usd": 9.60
    }
  ],
  "by_model": [
    {
      "model": "gpt-4",
      "requests": 800,
      "avg_tokens": 170
    }
  ]
}
```

---

## Troubleshooting

### Issue: "Invalid encryption key"

**Solution:**
1. Verify `ENCRYPTION_KEY` in `.env` is correct
2. Ensure it's a valid Fernet key (44 characters)
3. Regenerate if needed: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### Issue: "Connection refused" for local providers

**Solution:**
1. Ensure Ollama/LM Studio/vLLM is running
2. Check the base URL is correct
3. Verify no firewall is blocking the connection
4. Test with curl:
   ```bash
   curl http://localhost:11434/v1/models  # Ollama
   curl http://localhost:1234/v1/models   # LM Studio
   ```

### Issue: "Authentication failed"

**Solution:**
1. Verify API key is correct (no extra spaces)
2. Check API key has sufficient permissions
3. Ensure API key hasn't expired
4. For OpenAI: Check billing is active at https://platform.openai.com/account/billing

### Issue: "Rate limit exceeded"

**Solution:**
1. Wait and retry (client auto-retries with exponential backoff)
2. Upgrade your API plan for higher limits
3. Use a different provider
4. Implement request queuing

### Issue: "Model not found"

**Solution:**
1. Verify model name is correct
2. Check model is available for your account
3. For local providers, ensure model is downloaded:
   ```bash
   ollama pull llama2  # Ollama
   ```

### Issue: High costs

**Solution:**
1. Monitor usage in dashboard: http://localhost:3000/dashboard/settings/llm-providers/usage
2. Set usage alerts
3. Use cheaper models (gpt-3.5-turbo instead of gpt-4)
4. Reduce max_tokens in config
5. Use local models (Ollama, LM Studio) for development

---

## Provider-Specific Guides

### OpenAI

**Setup:**
1. Get API key: https://platform.openai.com/api-keys
2. Add provider via API or dashboard
3. Test connection

**Models:**
- `gpt-4` - Best quality, $0.03/1K input, $0.06/1K output
- `gpt-4-turbo` - Fast GPT-4, $0.01/1K input, $0.03/1K output
- `gpt-3.5-turbo` - Fast & cheap, $0.0005/1K input, $0.0015/1K output

**Docs:** https://platform.openai.com/docs

### Anthropic

**Setup:**
1. Get API key: https://console.anthropic.com/settings/keys
2. Add provider via API or dashboard
3. Test connection

**Models:**
- `claude-3-opus-20240229` - Most powerful, $15/1M input, $75/1M output
- `claude-3-sonnet-20240229` - Balanced, $3/1M input, $15/1M output
- `claude-3-haiku-20240307` - Fast & cheap, $0.25/1M input, $1.25/1M output

**Docs:** https://docs.anthropic.com/claude/docs

### Ollama (Local)

**Setup:**
1. Install: https://ollama.ai/download
2. Pull model: `ollama pull llama2`
3. Add provider (no API key needed)
4. Test connection

**Popular Models:**
- `llama2` - General purpose
- `mistral` - Fast & capable
- `codellama` - Code generation
- `neural-chat` - Conversational

**Docs:** https://github.com/ollama/ollama

### LM Studio (Local)

**Setup:**
1. Install: https://lmstudio.ai/
2. Download and load a model
3. Start local server (port 1234)
4. Add provider (no API key needed)
5. Test connection

**Supported Models:** Any GGUF format model from Hugging Face

**Docs:** https://lmstudio.ai/docs

### vLLM (Local/Cloud)

**Setup:**
1. Install: `pip install vllm`
2. Deploy model: `python -m vllm.entrypoints.api_server --model mistralai/Mistral-7B-Instruct-v0.2`
3. Add provider (no API key needed for local)
4. Test connection

**Docs:** https://docs.vllm.ai/

---

## Cost Estimation

### OpenAI Pricing (approximate)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| gpt-4 | $0.03 | $0.06 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |

### Anthropic Pricing (approximate)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| claude-3-opus | $15 | $75 |
| claude-3-sonnet | $3 | $15 |
| claude-3-haiku | $0.25 | $1.25 |

### Local Providers

- **Ollama**: Free (uses your hardware)
- **LM Studio**: Free (uses your hardware)
- **vLLM**: Free (uses your hardware)

**Note:** Token counting uses ~4 characters per token for English text.

---

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables** for encryption key
3. **Enable HTTPS** in production
4. **Rotate API keys** periodically
5. **Monitor usage** for anomalies
6. **Set usage limits** with your provider
7. **Use separate keys** for development and production
8. **Backup encryption key** securely (losing it = losing all API keys)

---

## Additional Resources

- **Backend Documentation**: `backend/docs/LLM_PROVIDERS.md`
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:3000/dashboard/settings/llm-providers
- **Usage Statistics**: http://localhost:3000/dashboard/settings/llm-providers/usage

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-13  
**Status:** Production Ready
