# OpenAI-Compatible Providers Guide

## 🎯 What Are OpenAI-Compatible Providers?

OpenAI-Compatible providers are services that implement the same API interface as OpenAI, allowing you to use them as drop-in replacements. This includes:

- **Local deployments** (LocalAI, FastChat, vLLM)
- **Cloud services** (Together AI, Anyscale, Groq, DeepInfra)
- **Custom implementations** using the OpenAI SDK

---

## ⚡ Quick Setup

### 1. Via Frontend Dashboard

1. Navigate to: **http://localhost:3000/dashboard/settings/llm-providers**
2. Click **"Add Provider"**
3. Select **"OpenAI-Compatible"** from provider type
4. Choose a preset or enter custom URL
5. Enter API key (if required)
6. Click **"Test Connection"**
7. Click **"Save"**

### 2. Via API

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Together AI",
    "provider_type": "openai_compatible",
    "base_url": "https://api.together.xyz/v1",
    "api_key": "your-api-key",
    "model_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

---

## 📋 Available Presets

### Local Deployments (No API Key Required)

| Provider | Base URL | Description |
|----------|----------|-------------|
| **LocalAI** | `http://localhost:8080/v1` | Self-hosted AI, drop-in OpenAI replacement |
| **FastChat** | `http://localhost:8000/v1` | Berkeley's distributed LLM serving |
| **vLLM** | `http://localhost:8000/v1` | High-throughput LLM inference |
| **Text Generation Inference** | `http://localhost:8080` | Hugging Face's optimized inference |

### Cloud Services (API Key Required)

| Provider | Base URL | Pricing | Description |
|----------|----------|---------|-------------|
| **Together AI** | `https://api.together.xyz/v1` | ~$0.90/1M tokens | Open-source models, fast inference |
| **Anyscale Endpoints** | `https://api.endpoints.anyscale.com/v1` | ~$0.15/1M tokens | Ray-powered model serving |
| **Groq** | `https://api.groq.com/openai/v1` | Free (beta) | Ultra-fast LPU inference |
| **DeepInfra** | `https://api.deepinfra.com/v1` | ~$0.08/1M tokens | Low-cost model hosting |
| **Lepton AI** | `https://<workspace>.lepton.run/api/v1` | ~$0.50/1M tokens | Serverless LLM deployment |

---

## 🔧 Setup Examples

### LocalAI (Self-Hosted)

**1. Install LocalAI:**
```bash
# Using Docker
docker run -p 8080:8080 localai/localai:latest

# Or download from: https://localai.io/basics/getting_started/
```

**2. Pull a Model:**
```bash
# Models are auto-downloaded on first use
# Configure in LocalAI's models directory
```

**3. Add Provider:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LocalAI",
    "provider_type": "openai_compatible",
    "base_url": "http://localhost:8080/v1",
    "model_name": "ggml-gpt4all-j",
    "is_active": true
  }'
```

**4. Test:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers/{id}/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Together AI (Cloud)

**1. Get API Key:**
- Sign up: https://together.ai
- Get API key: https://api.together.ai/settings/api-keys

**2. Add Provider:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Together AI - Mixtral",
    "provider_type": "openai_compatible",
    "base_url": "https://api.together.xyz/v1",
    "api_key": "your-together-api-key",
    "model_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

**3. Available Models:**
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Best quality
- `mistralai/Mistral-7B-Instruct-v0.2` - Fast & capable
- `togethercomputer/RedPajama-INCITE-7B-Chat` - Lightweight
- `togethercomputer/LLaMA-2-7B-32K-Instruct` - Long context

**Docs:** https://docs.together.ai/docs

---

### Groq (Ultra-Fast)

**1. Get API Key:**
- Sign up: https://console.groq.com
- Get API key: https://console.groq.com/keys
- **Currently free during beta!**

**2. Add Provider:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groq",
    "provider_type": "openai_compatible",
    "base_url": "https://api.groq.com/openai/v1",
    "api_key": "your-groq-api-key",
    "model_name": "mixtral-8x7b-32768",
    "is_active": true,
    "config": {
      "temperature": 0.6,
      "max_tokens": 32768
    }
  }'
```

**3. Available Models:**
- `mixtral-8x7b-32768` - Mixtral 8x7B (32K context)
- `llama2-70b-4096` - Llama 2 70B (4K context)
- `gemma-7b-it` - Google Gemma 7B

**Why Groq?** 10-100x faster than GPU inference!

**Docs:** https://console.groq.com/docs

---

### Anyscale Endpoints

**1. Get API Key:**
- Sign up: https://app.endpoints.anyscale.com
- Get API key from dashboard

**2. Add Provider:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Anyscale",
    "provider_type": "openai_compatible",
    "base_url": "https://api.endpoints.anyscale.com/v1",
    "api_key": "your-anyscale-api-key",
    "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
    "is_active": true
  }'
```

**3. Available Models:**
- `mistralai/Mistral-7B-Instruct-v0.2`
- `meta-llama/Llama-2-7b-chat-hf`
- `meta-llama/Llama-2-13b-chat-hf`
- `meta-llama/Llama-2-70b-chat-hf`

**Docs:** https://docs.endpoints.anyscale.com

---

### DeepInfra (Low-Cost)

**1. Get API Key:**
- Sign up: https://deepinfra.com
- Get API key from dashboard

**2. Add Provider:**
```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DeepInfra",
    "provider_type": "openai_compatible",
    "base_url": "https://api.deepinfra.com/v1",
    "api_key": "your-deepinfra-api-key",
    "model_name": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

**3. Pricing (per 1M tokens):**
- Mixtral 8x7B: ~$0.24
- Mistral 7B: ~$0.08
- Llama 2 70B: ~$0.28

**Docs:** https://deepinfra.com/docs

---

### Custom OpenAI-Compatible API

If you have a custom OpenAI-compatible endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/llm-providers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom API",
    "provider_type": "openai_compatible",
    "base_url": "https://your-custom-domain.com/v1",
    "api_key": "your-api-key-or-null",
    "model_name": "your-model-name",
    "is_active": true,
    "config": {
      "temperature": 0.7,
      "max_tokens": 4096,
      "pricing": {
        "input_cost_per_token": 0.000001,
        "output_cost_per_token": 0.000002
      }
    }
  }'
```

---

## 💻 Usage Examples

### Python SDK

```python
from app.services.llm_client import create_llm_client
from app.services.llm_provider_service import LLMProviderService

# Initialize
llm_client = create_llm_client()
provider_service = LLMProviderService()

# Get provider
provider = await provider_service.get_provider(provider_id)
api_key = provider_service.decrypt_api_key(provider.api_key)

# Register provider
llm_client.register_provider(provider, api_key=api_key)

# Use Groq for ultra-fast response
response = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    provider_id=provider.id,
    model="mixtral-8x7b-32768",
    temperature=0.6,
)

print(f"Response: {response.content}")
print(f"Time: {response.response_time_ms}ms")
print(f"Cost: ${response.cost_usd}")
```

### Using Different Providers for Different Tasks

```python
# Use Groq for fast chat
groq_response = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Quick question!"}],
    provider_id=groq_provider.id,
)

# Use Together AI for complex reasoning
together_response = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Solve this complex problem..."}],
    provider_id=together_provider.id,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

# Use LocalAI for development/testing (free)
local_response = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Test message"}],
    provider_id=localai_provider.id,
)
```

### Streaming Response

```python
async for chunk in await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Write a story"}],
    provider_id=provider.id,
    stream=True,
):
    print(chunk.content, end="", flush=True)
```

---

## 📊 Comparison Table

| Provider | Speed | Cost | Quality | Best For |
|----------|-------|------|---------|----------|
| **Groq** | ⚡⚡⚡⚡⚡ | Free (beta) | ⭐⭐⭐⭐ | Real-time apps |
| **Together AI** | ⚡⚡⚡⚡ | $ | ⭐⭐⭐⭐⭐ | Production workloads |
| **Anyscale** | ⚡⚡⚡ | $ | ⭐⭐⭐⭐ | Enterprise apps |
| **DeepInfra** | ⚡⚡⚡ | ¢ | ⭐⭐⭐⭐ | Cost-sensitive apps |
| **LocalAI** | ⚡⚡ | Free | ⭐⭐⭐ | Development/Testing |
| **FastChat** | ⚡⚡⚡ | Free | ⭐⭐⭐⭐ | Research |
| **vLLM** | ⚡⚡⚡⚡ | Free | ⭐⭐⭐⭐ | High-throughput |

---

## 🔍 Troubleshooting

### Issue: "Connection refused"

**Solution:**
1. Verify the service is running
2. Check the base URL is correct
3. Test with curl:
   ```bash
   curl http://localhost:8080/v1/models  # LocalAI
   curl https://api.together.xyz/v1/models -H "Authorization: Bearer YOUR_KEY"  # Together
   ```

### Issue: "Invalid API key"

**Solution:**
1. Verify API key is correct (no extra spaces)
2. Check API key has sufficient permissions
3. Ensure API key hasn't expired
4. For cloud services, check billing is active

### Issue: "Model not found"

**Solution:**
1. Verify model name matches provider's format
2. Check model is available for your account
3. Review provider documentation for supported models

### Issue: "Rate limit exceeded"

**Solution:**
1. Wait and retry (auto-retries with backoff)
2. Upgrade your plan for higher limits
3. Use a different provider
4. Implement request queuing

---

## 💰 Cost Comparison

### Cloud Provider Pricing (per 1M tokens)

| Provider | Input | Output | Example Cost (100K tokens) |
|----------|-------|--------|---------------------------|
| **Groq** | Free | Free | $0.00 |
| **DeepInfra** | $0.08 | $0.08 | $0.008 |
| **Together AI** | $0.90 | $0.90 | $0.09 |
| **Anyscale** | $0.15 | $0.15 | $0.015 |
| **OpenAI GPT-4** | $30.00 | $60.00 | $4.50 |
| **Anthropic Claude 3** | $3.00 | $15.00 | $0.45 |

**Note:** Local deployments cost only electricity and hardware.

---

## 🎯 Best Practices

1. **Use Local for Development**: Save money by using LocalAI/FastChat during development
2. **Use Groq for Speed**: When you need ultra-fast responses
3. **Use Together/Anyscale for Quality**: For production workloads requiring high quality
4. **Monitor Usage**: Track token usage and costs in the dashboard
5. **Set Up Multiple Providers**: Have fallback providers for redundancy
6. **Cache Responses**: Cache frequent queries to reduce API calls
7. **Batch Requests**: Combine multiple queries when possible

---

## 📚 Additional Resources

- **OpenAI API Reference**: https://platform.openai.com/docs/api-reference
- **LocalAI Docs**: https://localai.io/basics/getting_started/
- **Together AI Docs**: https://docs.together.ai/docs
- **Groq Docs**: https://console.groq.com/docs
- **Anyscale Docs**: https://docs.endpoints.anyscale.com
- **DeepInfra Docs**: https://deepinfra.com/docs

---

## 🚀 Next Steps

1. **Choose a Provider**: Select based on your needs (speed, cost, quality)
2. **Get API Key** (if cloud): Sign up and get your API key
3. **Add Provider**: Use dashboard or API to configure
4. **Test Connection**: Verify it's working
5. **Start Using**: Integrate with your agents!

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-13  
**Status:** Production Ready
