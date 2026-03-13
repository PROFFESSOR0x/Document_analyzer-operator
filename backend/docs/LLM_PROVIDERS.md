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
8. [OpenAI-Compatible Providers](#openai-compatible-providers)
9. [Troubleshooting](#troubleshooting)

## Overview

The Document Analyzer Operator Platform supports multiple LLM providers through a unified API interface:

| Provider | Type | API Key Required | Cost |
|----------|------|------------------|------|
| OpenAI | Cloud | Yes | Paid |
| Anthropic | Cloud | Yes | Paid |
| Ollama | Local | No | Free |
| LM Studio | Local | No | Free |
| vLLM | Local | No | Free |
| OpenAI-Compatible | Cloud/Local | Optional | Varies |
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

## OpenAI-Compatible Providers

The `openai_compatible` provider type allows you to connect to any API service that implements the OpenAI API specification. This includes both self-hosted solutions and cloud services.

### What is OpenAI-Compatible?

OpenAI-compatible APIs follow the same request/response format as OpenAI's API, making them drop-in replacements. They use the same endpoints:
- `/v1/chat/completions` - Chat completions
- `/v1/completions` - Text completions
- `/v1/embeddings` - Embeddings
- `/v1/models` - List models

### Popular OpenAI-Compatible Services

#### Local Deployment (Self-Hosted)

**LocalAI**
- URL: `http://localhost:8080/v1`
- API Key: Not required
- Description: Self-hosted LocalAI instance with multi-model support
- Website: https://localai.io/

**FastChat**
- URL: `http://localhost:8000/v1`
- API Key: Not required
- Description: FastChat local server for running open-source models
- Website: https://github.com/lm-sys/FastChat

**vLLM API Server**
- URL: `http://localhost:8000/v1`
- API Key: Not required
- Description: High-throughput inference server
- Website: https://github.com/vllm-project/vllm

**Text Generation Inference**
- URL: `http://localhost:8080/v1`
- API Key: Not required
- Description: Hugging Face's optimized inference server
- Website: https://github.com/huggingface/text-generation-inference

#### Cloud Services

**Together AI**
- URL: `https://api.together.xyz/v1`
- API Key: Required
- Description: Cloud-hosted open-source models with competitive pricing
- Website: https://together.ai/
- Models: Llama, Mistral, CodeLlama, and more

**Anyscale Endpoints**
- URL: `https://api.endpoints.anyscale.com/v1`
- API Key: Required
- Description: Ray-powered model serving platform
- Website: https://anyscale.com/
- Models: Llama, Mistral, Zephyr

**Groq**
- URL: `https://api.groq.com/openai/v1`
- API Key: Required
- Description: Ultra-fast LPU (Language Processing Unit) inference
- Website: https://groq.com/
- Models: Llama, Mixtral, Gemma

**DeepInfra**
- URL: `https://api.deepinfra.com/v1`
- API Key: Required
- Description: Serverless model inference with pay-per-use pricing
- Website: https://deepinfra.com/
- Models: 100+ open-source models

**Lepton AI**
- URL: `https://<workspace>.lepton.run/api/v1`
- API Key: Required
- Description: Cloud platform for deploying and serving models
- Website: https://lepton.ai/
- Models: Custom deployments

**Replicate**
- URL: `https://api.replicate.com/v1`
- API Key: Required
- Description: Hosted ML models with simple API
- Website: https://replicate.com/
- Models: Various ML models including LLMs

### Configuration Examples

#### LocalAI Setup

```json
{
  "name": "LocalAI",
  "provider_type": "openai_compatible",
  "base_url": "http://localhost:8080/v1",
  "model_name": "llama-2-7b",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

#### Together AI Setup

```json
{
  "name": "Together AI",
  "provider_type": "openai_compatible",
  "base_url": "https://api.together.xyz/v1",
  "api_key": "your-together-api-key",
  "model_name": "togethercomputer/llama-2-70b-chat",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096,
    "pricing": {
      "input": 0.0009,
      "output": 0.0009
    }
  }
}
```

#### Groq Setup

```json
{
  "name": "Groq",
  "provider_type": "openai_compatible",
  "base_url": "https://api.groq.com/openai/v1",
  "api_key": "your-groq-api-key",
  "model_name": "llama3-70b-8192",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

#### Anyscale Endpoints Setup

```json
{
  "name": "Anyscale Endpoints",
  "provider_type": "openai_compatible",
  "base_url": "https://api.endpoints.anyscale.com/v1",
  "api_key": "your-anyscale-api-key",
  "model_name": "meta-llama/Llama-2-7b-chat-hf",
  "is_active": true,
  "is_default": false,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### Benefits of OpenAI-Compatible Providers

1. **Cost-Effective**: Many services offer lower prices than OpenAI
2. **Model Variety**: Access to hundreds of open-source models
3. **Privacy**: Self-hosted options keep data on-premises
4. **Performance**: Specialized hardware (like Groq's LPU) for faster inference
5. **Flexibility**: Choose the right model for your use case
6. **No Vendor Lock-in**: Easy to switch between providers

### Using the Frontend UI

1. Navigate to Settings > LLM Providers
2. Click "Add Provider"
3. Select "OpenAI-Compatible" from the Quick Setup dropdown
4. Choose a preset (LocalAI, Together AI, Groq, etc.) or enter custom URL
5. Enter API key if required
6. Configure model name and settings
7. Click "Create Provider"
8. Test the connection before using

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
        "name": "Together AI",
        "provider_type": "openai_compatible",
        "base_url": "https://api.together.xyz/v1",
        "api_key": "your-api-key",
        "model_name": "togethercomputer/llama-2-70b-chat",
        "is_active": True,
        "is_default": False
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
    name="Together AI",
    provider_type="openai_compatible",
    base_url="https://api.together.xyz/v1",
    api_key="decrypted-key",
    model_name="togethercomputer/llama-2-70b-chat",
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
    model="togethercomputer/llama-2-70b-chat"
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

### OpenAI-Compatible Services Pricing (per 1K tokens)

| Service | Model | Input | Output |
|---------|-------|-------|--------|
| Together AI | Llama-2-70B | $0.0009 | $0.0009 |
| Together AI | Mixtral-8x7B | $0.0009 | $0.0009 |
| Anyscale | Llama-2-7B | $0.0001 | $0.0001 |
| Anyscale | Llama-2-70B | $0.0010 | $0.0010 |
| Groq | Llama-3-70B | $0.00059 | $0.00079 |
| Groq | Mixtral-8x7B | $0.00024 | $0.00024 |
| DeepInfra | Llama-2-7B | $0.0001 | $0.0001 |
| DeepInfra | Llama-2-70B | $0.0007 | $0.0007 |

*Note: Pricing is approximate and subject to change. Check provider websites for current rates.*

### Local Providers

Ollama, LM Studio, vLLM, and LocalAI are **free** when running locally (your hardware costs only).

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

### LocalAI Quick Start

```bash
# Using Docker
docker run -p 8080:8080 localai/localai:latest

# Or with docker-compose
git clone https://github.com/mudler/LocalAI.git
cd LocalAI
docker-compose up -d

# Test
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-2-7b",
    "messages": [{"role": "user", "content": "Hello!"}]
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

**6. OpenAI-Compatible Connection Failed**

```
AuthenticationError: Invalid or missing API key
```

**Solution:**
- Check if the service requires an API key
- Some services need keys even for local deployments
- Verify the base URL is correct (should end with /v1)
- Test the endpoint directly with curl

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
5. For OpenAI-Compatible providers, test the endpoint directly with curl to verify it's working
