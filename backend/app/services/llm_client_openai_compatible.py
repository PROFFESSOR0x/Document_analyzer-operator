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
