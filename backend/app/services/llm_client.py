"""LLM Client with unified interface for multiple providers."""

import asyncio
import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from dataclasses import dataclass, field

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from app.core.logging_config import get_logger
from app.models.llm_provider import LLMProvider

logger = get_logger(__name__)


@dataclass
class TokenUsage:
    """Token usage information."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    """LLM response data."""

    content: str
    model: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMStreamChunk:
    """Streaming chunk from LLM."""

    content: str
    finish_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None


class LLMError(Exception):
    """Base exception for LLM errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """Initialize LLM error.

        Args:
            message: Error message.
            provider: Provider name.
            model: Model name.
            status_code: HTTP status code if applicable.
        """
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model = model
        self.status_code = status_code


class AuthenticationError(LLMError):
    """Authentication/authorization error."""

    pass


class RateLimitError(LLMError):
    """Rate limit exceeded error."""

    pass


class TimeoutError(LLMError):
    """Request timeout error."""

    pass


class ProviderError(LLMError):
    """Provider-specific error."""

    pass


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        provider: LLMProvider,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize base provider.

        Args:
            provider: LLM provider configuration.
            api_key: Decrypted API key.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.
        """
        self.provider = provider
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = provider.base_url
        self.model_name = provider.model_name
        self.config = provider.config or {}

        # Rate limiting
        self._rate_limit_delay: float = 0.0
        self._last_request_time: float = 0.0

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request.

        Args:
            messages: List of message dictionaries.
            model: Model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Top-p sampling.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.
            stream: Whether to stream response.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse or AsyncIterator[LLMStreamChunk]: Response or stream.
        """
        pass

    @abstractmethod
    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request.

        Args:
            prompt: Text prompt.
            model: Model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Top-p sampling.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.
            stream: Whether to stream response.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse or AsyncIterator[LLMStreamChunk]: Response or stream.
        """
        pass

    @abstractmethod
    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings.

        Args:
            text: Text or list of texts.
            model: Model to use.
            **kwargs: Additional provider-specific arguments.

        Returns:
            List[List[float]]: Embedding vectors.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models.

        Returns:
            List[str]: List of model names.
        """
        pass

    @abstractmethod
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: Model name.

        Returns:
            Decimal: Estimated cost in USD.
        """
        pass

    def _get_request_params(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Get request parameters with defaults from config.

        Args:
            temperature: Sampling temperature.
            max_tokens: Maximum tokens.
            top_p: Top-p sampling.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.

        Returns:
            Dict: Request parameters.
        """
        params: Dict[str, Any] = {}

        if temperature is not None:
            params["temperature"] = temperature
        elif "temperature" in self.config:
            params["temperature"] = self.config["temperature"]

        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        elif "max_tokens" in self.config:
            params["max_tokens"] = self.config["max_tokens"]

        if top_p is not None:
            params["top_p"] = top_p
        elif "top_p" in self.config:
            params["top_p"] = self.config["top_p"]

        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        elif "frequency_penalty" in self.config:
            params["frequency_penalty"] = self.config["frequency_penalty"]

        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        elif "presence_penalty" in self.config:
            params["presence_penalty"] = self.config["presence_penalty"]

        return params

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting if configured."""
        if self._rate_limit_delay > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._rate_limit_delay:
                await asyncio.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _handle_rate_limit(self, retry_after: Optional[str]) -> None:
        """Handle rate limit response.

        Args:
            retry_after: Retry-After header value.
        """
        if retry_after:
            try:
                self._rate_limit_delay = float(retry_after)
            except ValueError:
                self._rate_limit_delay = 1.0
        else:
            self._rate_limit_delay = 1.0

    def _count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Text to count tokens for.

        Returns:
            int: Estimated token count.
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4


class OpenAIProvider(BaseProvider):
    """OpenAI API provider implementation."""

    # Pricing per 1K tokens (USD)
    PRICING = {
        "gpt-4": {"input": Decimal("0.03"), "output": Decimal("0.06")},
        "gpt-4-turbo": {"input": Decimal("0.01"), "output": Decimal("0.03")},
        "gpt-4o": {"input": Decimal("0.005"), "output": Decimal("0.015")},
        "gpt-3.5-turbo": {"input": Decimal("0.0005"), "output": Decimal("0.0015")},
    }

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize OpenAI provider.

        Args:
            provider: LLM provider configuration.
            api_key: Decrypted API key.
            **kwargs: Additional arguments.
        """
        super().__init__(provider, api_key, **kwargs)
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url.rstrip('/')}/v1"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()

        params = self._get_request_params(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        payload = {
            "model": model or self.model_name,
            "messages": messages,
            "stream": stream,
            **params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._stream_chat(client, url, headers, payload)
            else:
                return await self._complete_chat(client, url, headers, payload)

    async def _complete_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> LLMResponse:
        """Complete chat request."""
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            usage = data.get("usage", {})

            return LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", self.model_name),
                usage=TokenUsage(
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                finish_reason=choice.get("finish_reason"),
                raw_response=data,
            )
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise

    async def _stream_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream chat response."""
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        chunk_data = json.loads(data)
                        choice = chunk_data["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield LLMStreamChunk(
                                content=content,
                                finish_reason=choice.get("finish_reason"),
                            )
                    except json.JSONDecodeError:
                        continue

    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            **kwargs,
        )

    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/embeddings"
        headers = self._get_headers()

        payload = {
            "model": model or self.model_name,
            "input": text,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return [item["embedding"] for item in data["data"]]

    async def list_models(self) -> List[str]:
        """List available models."""
        url = f"{self.base_url}/models"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return [model["id"] for model in data.get("data", [])]

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage."""
        model_name = model or self.model_name
        pricing = self.PRICING.get(model_name, self.PRICING.get("gpt-3.5-turbo"))

        if not pricing:
            return Decimal("0")

        input_cost = Decimal(input_tokens) / 1000 * pricing["input"]
        output_cost = Decimal(output_tokens) / 1000 * pricing["output"]

        return input_cost + output_cost

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error."""
        status = error.response.status_code
        if status == 401:
            raise AuthenticationError(
                "Invalid API key",
                provider="openai",
                status_code=status,
            ) from error
        elif status == 429:
            retry_after = error.response.headers.get("Retry-After")
            self._handle_rate_limit(retry_after)
            raise RateLimitError(
                "Rate limit exceeded",
                provider="openai",
                status_code=status,
            ) from error
        elif status >= 500:
            raise ProviderError(
                f"Provider error: {status}",
                provider="openai",
                status_code=status,
            ) from error


class AnthropicProvider(BaseProvider):
    """Anthropic API provider implementation."""

    PRICING = {
        "claude-3-opus-20240229": {"input": Decimal("0.015"), "output": Decimal("0.075")},
        "claude-3-sonnet-20240229": {"input": Decimal("0.003"), "output": Decimal("0.015")},
        "claude-3-haiku-20240307": {"input": Decimal("0.00025"), "output": Decimal("0.00125")},
    }

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize Anthropic provider."""
        super().__init__(provider, api_key, **kwargs)
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url.rstrip('/')}/v1"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/messages"
        headers = self._get_headers()

        # Convert OpenAI format to Anthropic format
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": "assistant" if msg["role"] == "assistant" else "user",
                    "content": msg["content"],
                })

        params = self._get_request_params(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        payload = {
            "model": model or self.model_name,
            "messages": anthropic_messages,
            "stream": stream,
            **params,
        }

        if system_message:
            payload["system"] = system_message

        # Anthropic requires max_tokens
        if "max_tokens" not in payload:
            payload["max_tokens"] = self.config.get("max_tokens", 4096)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._stream_chat(client, url, headers, payload)
            else:
                return await self._complete_chat(client, url, headers, payload)

    async def _complete_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> LLMResponse:
        """Complete chat request."""
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["content"][0]["text"] if data["content"] else ""

            # Anthropic doesn't provide token usage in the same format
            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                model=data.get("model", self.model_name),
                usage=TokenUsage(
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                ),
                finish_reason=data.get("stop_reason"),
                raw_response=data,
            )
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise

    async def _stream_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream chat response."""
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    try:
                        import json
                        event = json.loads(data)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            content = delta.get("text", "")
                            if content:
                                yield LLMStreamChunk(content=content)
                        elif event.get("type") == "message_stop":
                            break
                    except json.JSONDecodeError:
                        continue

    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            **kwargs,
        )

    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings."""
        raise NotImplementedError("Anthropic does not support embeddings API")

    async def list_models(self) -> List[str]:
        """List available models."""
        # Anthropic doesn't have a models endpoint, return known models
        return list(self.PRICING.keys())

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage."""
        model_name = model or self.model_name
        pricing = self.PRICING.get(model_name, self.PRICING.get("claude-3-sonnet-20240229"))

        if not pricing:
            return Decimal("0")

        input_cost = Decimal(input_tokens) / 1000 * pricing["input"]
        output_cost = Decimal(output_tokens) / 1000 * pricing["output"]

        return input_cost + output_cost

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
        }
        return headers

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error."""
        status = error.response.status_code
        if status == 401:
            raise AuthenticationError(
                "Invalid API key",
                provider="anthropic",
                status_code=status,
            ) from error
        elif status == 429:
            retry_after = error.response.headers.get("Retry-After")
            self._handle_rate_limit(retry_after)
            raise RateLimitError(
                "Rate limit exceeded",
                provider="anthropic",
                status_code=status,
            ) from error
        elif status >= 500:
            raise ProviderError(
                f"Provider error: {status}",
                provider="anthropic",
                status_code=status,
            ) from error


class OllamaProvider(BaseProvider):
    """Local Ollama provider implementation."""

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize Ollama provider."""
        super().__init__(provider, api_key, **kwargs)
        # Ollama uses /v1 for OpenAI compatibility
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url.rstrip('/')}/v1"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}

        params = self._get_request_params(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        payload = {
            "model": model or self.model_name,
            "messages": messages,
            "stream": stream,
            **params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._stream_chat(client, url, headers, payload)
            else:
                return await self._complete_chat(client, url, headers, payload)

    async def _complete_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> LLMResponse:
        """Complete chat request."""
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.model_name),
            usage=TokenUsage(
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            finish_reason=choice.get("finish_reason"),
            raw_response=data,
        )

    async def _stream_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream chat response."""
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        chunk_data = json.loads(data)
                        choice = chunk_data["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield LLMStreamChunk(
                                content=content,
                                finish_reason=choice.get("finish_reason"),
                            )
                    except json.JSONDecodeError:
                        continue

    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            **kwargs,
        )

    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings."""
        # Use native Ollama embeddings endpoint
        url = f"{self.base_url.replace('/v1', '')}/api/embeddings"

        texts = [text] if isinstance(text, str) else text
        embeddings = []

        for t in texts:
            payload = {
                "model": model or self.model_name,
                "prompt": t,
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings.append(data["embedding"])

        return embeddings

    async def list_models(self) -> List[str]:
        """List available models."""
        url = f"{self.base_url.replace('/v1', '')}/api/tags"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            return [model["name"] for model in data.get("models", [])]

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage."""
        # Ollama is free (local)
        return Decimal("0")


class LMStudioProvider(OllamaProvider):
    """Local LM Studio provider implementation."""

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize LM Studio provider."""
        super().__init__(provider, api_key, **kwargs)
        # LM Studio uses OpenAI-compatible API


class VLLMProvider(OllamaProvider):
    """Local vLLM provider implementation."""

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize vLLM provider."""
        super().__init__(provider, api_key, **kwargs)
        # vLLM uses OpenAI-compatible API


class OpenAICompatibleProvider(BaseProvider):
    """Provider for custom OpenAI-compatible APIs.
    
    This provider supports any API that follows the OpenAI API specification,
    including LocalAI, FastChat, Together AI, Anyscale, Groq, and others.
    
    Examples:
        - LocalAI: http://localhost:8080/v1
        - FastChat: http://localhost:8000/v1
        - Together AI: https://api.together.xyz/v1
        - Anyscale: https://api.endpoints.anyscale.com/v1
        - Groq: https://api.groq.com/openai/v1
    """

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize OpenAI-compatible provider.

        Args:
            provider: LLM provider configuration.
            api_key: Decrypted API key (optional for some providers).
            **kwargs: Additional arguments.
        """
        super().__init__(provider, api_key, **kwargs)
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url.rstrip('/')}/v1"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()

        params = self._get_request_params(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        payload = {
            "model": model or self.model_name,
            "messages": messages,
            "stream": stream,
            **params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                return self._stream_chat(client, url, headers, payload)
            else:
                return await self._complete_chat(client, url, headers, payload)

    async def _complete_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> LLMResponse:
        """Complete chat request."""
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            usage = data.get("usage", {})

            return LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", self.model_name),
                usage=TokenUsage(
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                ),
                finish_reason=choice.get("finish_reason"),
                raw_response=data,
            )
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
            raise

    async def _stream_chat(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream chat response."""
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        chunk_data = json.loads(data)
                        choice = chunk_data["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield LLMStreamChunk(
                                content=content,
                                finish_reason=choice.get("finish_reason"),
                            )
                    except json.JSONDecodeError:
                        continue

    async def text_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            **kwargs,
        )

    async def embeddings(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings."""
        await self._apply_rate_limit()

        url = f"{self.base_url}/embeddings"
        headers = self._get_headers()

        payload = {
            "model": model or self.model_name,
            "input": text,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return [item["embedding"] for item in data["data"]]

    async def list_models(self) -> List[str]:
        """List available models."""
        url = f"{self.base_url}/models"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return [model["id"] for model in data.get("data", [])]

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage.
        
        Uses pricing from config if available, otherwise returns 0.
        Config pricing format:
        {
            "pricing": {
                "input": 0.001,  # per 1K tokens
                "output": 0.002  # per 1K tokens
            }
        }
        """
        cost_config = self.config.get("pricing", {})
        if cost_config:
            input_cost = Decimal(input_tokens) / 1000 * Decimal(str(cost_config.get("input", 0)))
            output_cost = Decimal(output_tokens) / 1000 * Decimal(str(cost_config.get("output", 0)))
            return input_cost + output_cost
        return Decimal("0")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key and self.api_key != "not-needed":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error."""
        status = error.response.status_code
        if status == 401:
            raise AuthenticationError(
                "Invalid or missing API key",
                provider="openai_compatible",
                status_code=status,
            ) from error
        elif status == 429:
            retry_after = error.response.headers.get("Retry-After")
            self._handle_rate_limit(retry_after)
            raise RateLimitError(
                "Rate limit exceeded",
                provider="openai_compatible",
                status_code=status,
            ) from error
        elif status >= 500:
            raise ProviderError(
                f"Provider error: {status}",
                provider="openai_compatible",
                status_code=status,
            ) from error


class CustomProvider(OpenAIProvider):
    """Generic OpenAI-compatible custom provider."""

    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize custom provider."""
        super().__init__(provider, api_key, **kwargs)

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage."""
        # Custom provider - use config or return 0
        cost_config = self.config.get("pricing", {})
        if cost_config:
            input_cost = Decimal(input_tokens) / 1000 * Decimal(str(cost_config.get("input", 0)))
            output_cost = Decimal(output_tokens) / 1000 * Decimal(str(cost_config.get("output", 0)))
            return input_cost + output_cost
        return Decimal("0")


class LLMClient:
    """Unified LLM client with auto-detection and provider management."""

    PROVIDER_CLASSES = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "lm_studio": LMStudioProvider,
        "vllm": VLLMProvider,
        "openai_compatible": OpenAICompatibleProvider,
        "custom": CustomProvider,
    }

    def __init__(
        self,
        default_provider: Optional[LLMProvider] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize LLM client.

        Args:
            default_provider: Default LLM provider configuration.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.
        """
        self.default_provider = default_provider
        self.timeout = timeout
        self.max_retries = max_retries
        self._providers: Dict[str, BaseProvider] = {}

    def register_provider(
        self,
        provider: LLMProvider,
        api_key: Optional[str] = None,
    ) -> BaseProvider:
        """Register an LLM provider.

        Args:
            provider: LLM provider configuration.
            api_key: Decrypted API key.

        Returns:
            BaseProvider: Provider instance.
        """
        provider_class = self.PROVIDER_CLASSES.get(
            provider.provider_type,
            CustomProvider,
        )

        instance = provider_class(
            provider=provider,
            api_key=api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        self._providers[provider.id] = instance
        return instance

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """Get registered provider by ID.

        Args:
            provider_id: Provider ID.

        Returns:
            Optional[BaseProvider]: Provider instance.
        """
        return self._providers.get(provider_id)

    def get_default_provider(self) -> Optional[BaseProvider]:
        """Get default provider.

        Returns:
            Optional[BaseProvider]: Default provider instance.
        """
        if self.default_provider:
            return self.get_provider(self.default_provider.id)
        return None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        use_fallback: bool = True,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send chat completion request.

        Args:
            messages: List of message dictionaries.
            provider_id: Provider ID to use.
            model: Model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Top-p sampling.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.
            stream: Whether to stream response.
            use_fallback: Whether to use fallback provider on failure.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse or AsyncIterator[LLMStreamChunk]: Response or stream.

        Raises:
            LLMError: If request fails.
        """
        provider = self.get_provider(provider_id) if provider_id else self.get_default_provider()

        if not provider:
            raise LLMError("No provider configured")

        try:
            return await provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=stream,
                **kwargs,
            )
        except LLMError:
            if use_fallback and provider_id:
                # Try default provider as fallback
                if self.default_provider and self.default_provider.id != provider_id:
                    return await self.chat_completion(
                        messages=messages,
                        provider_id=self.default_provider.id,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        stream=stream,
                        use_fallback=False,
                        **kwargs,
                    )
            raise

    async def text_completion(
        self,
        prompt: str,
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        use_fallback: bool = True,
        **kwargs: Any,
    ) -> Union[LLMResponse, AsyncIterator[LLMStreamChunk]]:
        """Send text completion request.

        Args:
            prompt: Text prompt.
            provider_id: Provider ID to use.
            model: Model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Top-p sampling.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.
            stream: Whether to stream response.
            use_fallback: Whether to use fallback provider on failure.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse or AsyncIterator[LLMStreamChunk]: Response or stream.
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(
            messages=messages,
            provider_id=provider_id,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            use_fallback=use_fallback,
            **kwargs,
        )

    async def embeddings(
        self,
        text: Union[str, List[str]],
        provider_id: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[List[float]]:
        """Generate embeddings.

        Args:
            text: Text or list of texts.
            provider_id: Provider ID to use.
            model: Model to use.
            **kwargs: Additional provider-specific arguments.

        Returns:
            List[List[float]]: Embedding vectors.
        """
        provider = self.get_provider(provider_id) if provider_id else self.get_default_provider()

        if not provider:
            raise LLMError("No provider configured")

        return await provider.embeddings(text=text, model=model, **kwargs)

    async def list_models(self, provider_id: str) -> List[str]:
        """List available models for a provider.

        Args:
            provider_id: Provider ID.

        Returns:
            List[str]: List of model names.
        """
        provider = self.get_provider(provider_id)
        if not provider:
            raise LLMError(f"Provider {provider_id} not found")

        return await provider.list_models()

    def estimate_cost(
        self,
        provider_id: str,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
    ) -> Decimal:
        """Estimate cost for token usage.

        Args:
            provider_id: Provider ID.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: Model name.

        Returns:
            Decimal: Estimated cost in USD.
        """
        provider = self.get_provider(provider_id)
        if not provider:
            return Decimal("0")

        return provider.estimate_cost(input_tokens, output_tokens, model)


def create_llm_client(
    default_provider: Optional[LLMProvider] = None,
    timeout: float = 60.0,
    max_retries: int = 3,
) -> LLMClient:
    """Create LLM client instance.

    Args:
        default_provider: Default LLM provider configuration.
        timeout: Request timeout in seconds.
        max_retries: Maximum retry attempts.

    Returns:
        LLMClient: LLM client instance.
    """
    return LLMClient(
        default_provider=default_provider,
        timeout=timeout,
        max_retries=max_retries,
    )
