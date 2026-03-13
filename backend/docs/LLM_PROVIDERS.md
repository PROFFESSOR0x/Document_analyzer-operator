# LLM Providers Guide

Comprehensive guide for configuring and using LLM providers in the Document Analyzer Operator Platform.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Provider Setup](#provider-setup)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Cost Estimation](#cost-estimation)
7. [Local LLM Deployment](#local-llm-deployment)
8. [Troubleshooting](#troubleshooting)

## Overview

The Document Analyzer Operator Platform supports multiple LLM providers through a unified API interface:

| Provider | Type | API Key Required | Cost |
|----------|------|------------------|------|
| OpenAI | Cloud | Yes | Paid |
| Anthropic | Cloud | Yes | Paid |
| Ollama | Local | No | Free |
| LM Studio | Local | No | Free |
| vLLM | Local | No | Free |
| Custom | Any | Optional | Varies |

### Features

- **Unified Interface**: Same API for all providers
- **Automatic Retry**: Exponential backoff on failures
- **Rate Limiting**: Built-in rate limit handling
- **Token Counting**: Automatic token usage tracking
- **Cost Estimation**: Real-time cost calculation
- **Streaming Support**: Server-sent events for streaming
- **Fallback Support**: Automatic failover to backup providers
- **API Key Encryption**: Secure storage with Fernet encryption

## Quick Start

### 1. Generate Encryption Key

Before adding API keys, generate an encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the key to your `.env` file:

```bash
ENCRYPTION_KEY=your-generated-key-here
```

### 2. Add Your First Provider

**Option A: Using the API**

```bash
# Create OpenAI provider
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

**Option B: Using Environment Variables**

Add to `.env`:

```bash
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 3. Test Connection

```bash
curl -X POST "http://localhost:8000/api/v1/llm-providers/PROVIDER_ID/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "test_prompt": "Hello, this is a test."
  }'
```

## Provider Setup

### OpenAI

**Configuration:**

```json
{
  "name": "OpenAI",
  "provider_type": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model_name": "gpt-4",
  "is_active": true,
  "is_default": true,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

**Available Models:**
- `gpt-4` - Most capable model
- `gpt-4-turbo` - Faster, cheaper GPT-4
- `gpt-4o` - Optimized for speed
- `gpt-3.5-turbo` - Cost-effective option

**Get API Key:** https://platform.openai.com/api-keys

### Anthropic

**Configuration:**

```json
{
  "name": "Anthropic",
  "provider_type": "anthropic",
  "base_url": "https://api.anthropic.com/v1",
  "api_key": "sk-ant-...",
  "model_name": "claude-3-sonnet-20240229",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

**Available Models:**
- `claude-3-opus-20240229` - Most powerful
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fast, cost-effective

**Get API Key:** https://console.anthropic.com/settings/keys

### Ollama (Local)

**Installation:**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

**Pull Models:**

```bash
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

**Configuration:**

```json
{
  "name": "Local Ollama",
  "provider_type": "ollama",
  "base_url": "http://localhost:11434/v1",
  "model_name": "llama2",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

**No API key required for local deployment.**

### LM Studio (Local)

**Installation:**

1. Download from https://lmstudio.ai/
2. Install and launch LM Studio
3. Download a model from the Hub
4. Start the local server (default: http://localhost:1234)

**Configuration:**

```json
{
  "name": "LM Studio",
  "provider_type": "lm_studio",
  "base_url": "http://localhost:1234/v1",
  "model_name": "local-model",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### vLLM (Local)

**Installation:**

```bash
pip install vllm
```

**Run Server:**

```bash
python -m vllm.entrypoints.api_server \
  --model facebook/opt-125m \
  --host 0.0.0.0 \
  --port 8000
```

**Configuration:**

```json
{
  "name": "vLLM",
  "provider_type": "vllm",
  "base_url": "http://localhost:8000/v1",
  "model_name": "facebook/opt-125m",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### Custom Provider

For any OpenAI-compatible API:

```json
{
  "name": "Custom Provider",
  "provider_type": "custom",
  "base_url": "https://your-api.com/v1",
  "api_key": "your-api-key",
  "model_name": "your-model",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096,
    "pricing": {
      "input": 0.001,
      "output": 0.002
    }
  }
}
```

## API Reference

### List Providers

```http
GET /api/v1/llm-providers
```

**Query Parameters:**
- `skip` (int): Records to skip (default: 0)
- `limit` (int): Max records (default: 100)
- `active_only` (bool): Filter active only (default: false)
- `provider_type` (str): Filter by type

### Get Provider

```http
GET /api/v1/llm-providers/{provider_id}
```

### Create Provider

```http
POST /api/v1/llm-providers
```

**Request Body:**

```json
{
  "name": "string (required)",
  "provider_type": "string (required)",
  "base_url": "string (required)",
  "model_name": "string (required)",
  "api_key": "string (optional)",
  "is_active": "boolean (default: true)",
  "is_default": "boolean (default: false)",
  "config": "object (optional)"
}
```

### Update Provider

```http
PUT /api/v1/llm-providers/{provider_id}
```

### Delete Provider

```http
DELETE /api/v1/llm-providers/{provider_id}
```

### Test Connection

```http
POST /api/v1/llm-providers/{provider_id}/test
```

**Request Body:**

```json
{
  "model_name": "string (optional)",
  "test_prompt": "string (default: 'Hello, this is a test.')"
}
```

### Set Default Provider

```http
POST /api/v1/llm-providers/{provider_id}/set-default
```

### Get Usage Statistics

```http
GET /api/v1/llm-providers/usage/stats
```

**Query Parameters:**
- `start_date` (datetime): Start date filter
- `end_date` (datetime): End date filter
- `provider_id` (str): Filter by provider
- `user_id` (str): Filter by user
- `agent_id` (str): Filter by agent

### Get Usage Logs

```http
GET /api/v1/llm-providers/usage/logs
```

**Query Parameters:**
- `provider_id` (str): Filter by provider
- `agent_id` (str): Filter by agent
- `start_date` (datetime): Start date
- `end_date` (datetime): End date
- `status` (str): Filter by status
- `skip` (int): Records to skip
- `limit` (int): Max records

## Usage Examples

### Python SDK Example

```python
import httpx

# Get providers
response = httpx.get(
    "http://localhost:8000/api/v1/llm-providers",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
providers = response.json()

# Create a provider
response = httpx.post(
    "http://localhost:8000/api/v1/llm-providers",
    headers={
        "Authorization": "Bearer YOUR_TOKEN",
        "Content-Type": "application/json"
    },
    json={
        "name": "OpenAI",
        "provider_type": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-...",
        "model_name": "gpt-4",
        "is_active": True,
        "is_default": True
    }
)

# Test connection
response = httpx.post(
    "http://localhost:8000/api/v1/llm-providers/PROVIDER_ID/test",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"test_prompt": "Hello!"}
)
test_result = response.json()

# Get usage stats
response = httpx.get(
    "http://localhost:8000/api/v1/llm-providers/usage/stats",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
stats = response.json()
```

### Using the LLM Client

```python
from app.services.llm_client import create_llm_client, LLMClient
from app.models.llm_provider import LLMProvider

# Create client
client = create_llm_client(timeout=60.0, max_retries=3)

# Register provider
provider = LLMProvider(
    id="provider-id",
    name="OpenAI",
    provider_type="openai",
    base_url="https://api.openai.com/v1",
    api_key="encrypted-key",
    model_name="gpt-4",
    is_active=True,
    config={"temperature": 0.7}
)

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
print(f"Tokens used: {response.usage.total_tokens}")

# Streaming
async for chunk in client.chat_completion(
    messages=[{"role": "user", "content": "Tell me a story"}],
    provider_id="provider-id",
    stream=True
):
    print(chunk.content, end="")

# Embeddings
embeddings = await client.embeddings(
    text="Hello, world!",
    provider_id="provider-id"
)

# List models
models = await client.list_models(provider_id="provider-id")

# Estimate cost
cost = client.estimate_cost(
    provider_id="provider-id",
    input_tokens=1000,
    output_tokens=500,
    model="gpt-4"
)
print(f"Estimated cost: ${cost}")
```

## Cost Estimation

### OpenAI Pricing (per 1K tokens)

| Model | Input | Output |
|-------|-------|--------|
| gpt-4 | $0.03 | $0.06 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-4o | $0.005 | $0.015 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |

### Anthropic Pricing (per 1K tokens)

| Model | Input | Output |
|-------|-------|--------|
| claude-3-opus | $0.015 | $0.075 |
| claude-3-sonnet | $0.003 | $0.015 |
| claude-3-haiku | $0.00025 | $0.00125 |

### Local Providers

Ollama, LM Studio, and vLLM are **free** when running locally.

## Local LLM Deployment

### Ollama Quick Start

```bash
# Install
brew install ollama  # macOS
# or
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Start server (runs automatically on install)
ollama serve

# Pull model
ollama pull llama2

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello!"
}'
```

### LM Studio Quick Start

1. Download from https://lmstudio.ai/
2. Install and open LM Studio
3. Click "Discover" and search for a model
4. Click "Download" on your chosen model
5. Go to "Local Server" tab
6. Select the downloaded model
7. Click "Start Server"
8. Server runs at http://localhost:1234

### vLLM Quick Start

```bash
# Install
pip install vllm

# Run server
python -m vllm.entrypoints.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --host 0.0.0.0 \
  --port 8000

# Test
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "prompt": "Hello!",
    "max_tokens": 100
  }'
```

## Troubleshooting

### Common Issues

**1. Encryption Key Error**

```
EncryptionError: ENCRYPTION_KEY environment variable is not set
```

**Solution:** Generate and set the encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add to `.env`:
```bash
ENCRYPTION_KEY=your-generated-key
```

**2. Authentication Failed**

```
AuthenticationError: Invalid API key
```

**Solution:**
- Verify API key is correct
- Check for extra spaces
- Ensure key hasn't expired
- Test key directly with provider

**3. Rate Limit Exceeded**

```
RateLimitError: Rate limit exceeded
```

**Solution:**
- Wait and retry (automatic with exponential backoff)
- Upgrade your API plan
- Use local models for development

**4. Connection Timeout**

```
TimeoutError: Request timed out
```

**Solution:**
- Check network connection
- Verify base URL is correct
- Increase timeout in config
- For local: ensure service is running

**5. Provider Not Found**

```
HTTP 404: Provider not found
```

**Solution:**
- Verify provider ID is correct
- Check provider exists: `GET /api/v1/llm-providers`

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG
```

Check logs:

```bash
tail -f logs/app.log
```

### Support

For additional help:
1. Check API documentation at `/docs`
2. Review error logs in `logs/app.log`
3. Test connection using the test endpoint
4. Verify environment variables are set correctly
