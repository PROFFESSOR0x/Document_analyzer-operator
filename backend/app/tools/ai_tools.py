"""AI/ML tools for LLM operations and text processing."""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging

from app.tools.base import BaseTool, ToolMetadata, ToolCategory, ToolError


# ========== LLM Client Tool ==========

class LLMClientInput(BaseModel):
    """LLM client input model."""

    prompt: str = Field(..., description="Input prompt")
    model: str = Field(default="gpt-3.5-turbo", description="Model to use")
    system_prompt: Optional[str] = Field(default=None, description="System prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=1024, ge=1, le=128000, description="Max tokens")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top P")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop_sequences: Optional[List[str]] = Field(default=None, description="Stop sequences")
    stream: bool = Field(default=False, description="Stream response")


class LLMMessage(BaseModel):
    """LLM message."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMClientOutput(BaseModel):
    """LLM client output model."""

    response: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: Optional[str] = None
    completion_tokens: int = 0


class LLMClientTool(BaseTool[LLMClientInput, LLMClientOutput]):
    """Tool for interacting with LLM APIs."""

    metadata = ToolMetadata(
        name="llm_client",
        description="Interact with LLM APIs (OpenAI, Anthropic, etc.)",
        category=ToolCategory.AI,
        version="1.0.0",
        tags=["llm", "ai", "text-generation", "chat"],
        requires_auth=True,
        rate_limit_per_minute=60,
        timeout_seconds=120.0,
    )

    InputModel = LLMClientInput
    OutputModel = LLMClientOutput

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize LLM client.

        Args:
            config: Configuration with API keys.
        """
        super().__init__(config)
        self.default_provider = self.config.get("provider", "openai")
        self.api_keys = {
            "openai": self.config.get("openai_api_key"),
            "anthropic": self.config.get("anthropic_api_key"),
            "google": self.config.get("google_api_key"),
        }

    async def _execute(self, input_data: LLMClientInput) -> LLMClientOutput:
        """Execute LLM request.

        Args:
            input_data: Request parameters.

        Returns:
            LLMClientOutput: LLM response.
        """
        provider = self._detect_provider(input_data.model)

        if provider == "openai":
            return await self._call_openai(input_data)
        elif provider == "anthropic":
            return await self._call_anthropic(input_data)
        elif provider == "google":
            return await self._call_google(input_data)
        else:
            raise ToolError(f"Unsupported provider for model: {input_data.model}")

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name.

        Args:
            model: Model name.

        Returns:
            str: Provider name.
        """
        model_lower = model.lower()
        if "claude" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower:
            return "google"
        else:
            return "openai"

    async def _call_openai(self, input_data: LLMClientInput) -> LLMClientOutput:
        """Call OpenAI API.

        Args:
            input_data: Request parameters.

        Returns:
            LLMClientOutput: Response.
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ToolError("openai library not installed")

        api_key = self.api_keys.get("openai")
        if not api_key:
            # Return mock response for development
            return self._mock_llm_response(input_data)

        client = AsyncOpenAI(api_key=api_key)

        messages = []
        if input_data.system_prompt:
            messages.append({"role": "system", "content": input_data.system_prompt})
        messages.append({"role": "user", "content": input_data.prompt})

        try:
            response = await client.chat.completions.create(
                model=input_data.model,
                messages=messages,
                temperature=input_data.temperature,
                max_tokens=input_data.max_tokens,
                top_p=input_data.top_p,
                frequency_penalty=input_data.frequency_penalty,
                presence_penalty=input_data.presence_penalty,
                stop=input_data.stop_sequences,
            )

            choice = response.choices[0]
            return LLMClientOutput(
                response=choice.message.content or "",
                model=input_data.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=choice.finish_reason,
                completion_tokens=response.usage.completion_tokens,
            )
        finally:
            await client.close()

    async def _call_anthropic(self, input_data: LLMClientInput) -> LLMClientOutput:
        """Call Anthropic API.

        Args:
            input_data: Request parameters.

        Returns:
            LLMClientOutput: Response.
        """
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ToolError("anthropic library not installed")

        api_key = self.api_keys.get("anthropic")
        if not api_key:
            return self._mock_llm_response(input_data)

        client = AsyncAnthropic(api_key=api_key)

        try:
            response = await client.messages.create(
                model=input_data.model,
                max_tokens=input_data.max_tokens,
                system=input_data.system_prompt or "",
                messages=[{"role": "user", "content": input_data.prompt}],
            )

            return LLMClientOutput(
                response=response.content[0].text,
                model=input_data.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
                completion_tokens=response.usage.output_tokens,
            )
        finally:
            await client.close()

    async def _call_google(self, input_data: LLMClientInput) -> LLMClientOutput:
        """Call Google AI API.

        Args:
            input_data: Request parameters.

        Returns:
            LLMClientOutput: Response.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ToolError("google-generativeai library not installed")

        api_key = self.api_keys.get("google")
        if not api_key:
            return self._mock_llm_response(input_data)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(input_data.model)

        response = await model.generate_content_async(
            input_data.prompt,
            generation_config={
                "temperature": input_data.temperature,
                "max_output_tokens": input_data.max_tokens,
                "top_p": input_data.top_p,
            },
        )

        return LLMClientOutput(
            response=response.text,
            model=input_data.model,
            usage={},
            finish_reason="stop",
        )

    def _mock_llm_response(self, input_data: LLMClientInput) -> LLMClientOutput:
        """Generate mock LLM response for development.

        Args:
            input_data: Request parameters.

        Returns:
            LLMClientOutput: Mock response.
        """
        self._logger.warning("Using mock LLM response (no API key configured)")
        return LLMClientOutput(
            response=f"[Mock Response] This is a simulated response for prompt: {input_data.prompt[:100]}...",
            model=input_data.model,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
            completion_tokens=20,
        )


# ========== Embedding Generator Tool ==========

class EmbeddingGeneratorInput(BaseModel):
    """Embedding generator input model."""

    text: str = Field(..., description="Text to embed")
    model: str = Field(default="text-embedding-ada-002", description="Embedding model")
    dimensions: Optional[int] = Field(default=None, description="Output dimensions")


class EmbeddingGeneratorOutput(BaseModel):
    """Embedding generator output model."""

    embedding: List[float]
    model: str
    dimensions: int
    usage: Dict[str, int] = Field(default_factory=dict)


class EmbeddingGeneratorTool(BaseTool[EmbeddingGeneratorInput, EmbeddingGeneratorOutput]):
    """Tool for generating text embeddings."""

    metadata = ToolMetadata(
        name="embedding_generator",
        description="Generate text embeddings using various models",
        category=ToolCategory.AI,
        version="1.0.0",
        tags=["embedding", "vector", "ai", "similarity"],
        requires_auth=True,
        rate_limit_per_minute=100,
        timeout_seconds=30.0,
    )

    InputModel = EmbeddingGeneratorInput
    OutputModel = EmbeddingGeneratorOutput

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize embedding generator.

        Args:
            config: Configuration with API keys.
        """
        super().__init__(config)
        self.api_keys = {
            "openai": self.config.get("openai_api_key"),
        }

    async def _execute(self, input_data: EmbeddingGeneratorInput) -> EmbeddingGeneratorOutput:
        """Generate embedding.

        Args:
            input_data: Generation parameters.

        Returns:
            EmbeddingGeneratorOutput: Embedding vector.
        """
        if "text-embedding" in input_data.model.lower():
            return await self._generate_openai_embedding(input_data)
        else:
            raise ToolError(f"Unsupported embedding model: {input_data.model}")

    async def _generate_openai_embedding(
        self,
        input_data: EmbeddingGeneratorInput,
    ) -> EmbeddingGeneratorOutput:
        """Generate OpenAI embedding.

        Args:
            input_data: Generation parameters.

        Returns:
            EmbeddingGeneratorOutput: Embedding vector.
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ToolError("openai library not installed")

        api_key = self.api_keys.get("openai")
        if not api_key:
            # Return mock embedding
            return self._mock_embedding(input_data)

        client = AsyncOpenAI(api_key=api_key)

        try:
            kwargs = {"model": input_data.model, "input": input_data.text}
            if input_data.dimensions:
                kwargs["dimensions"] = input_data.dimensions

            response = await client.embeddings.create(**kwargs)

            embedding_data = response.data[0]
            return EmbeddingGeneratorOutput(
                embedding=embedding_data.embedding,
                model=input_data.model,
                dimensions=len(embedding_data.embedding),
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            )
        finally:
            await client.close()

    def _mock_embedding(self, input_data: EmbeddingGeneratorInput) -> EmbeddingGeneratorOutput:
        """Generate mock embedding for development.

        Args:
            input_data: Generation parameters.

        Returns:
            EmbeddingGeneratorOutput: Mock embedding.
        """
        self._logger.warning("Using mock embedding (no API key configured)")
        # Generate deterministic mock embedding based on text hash
        import hashlib

        dimensions = input_data.dimensions or 1536
        hash_val = int(hashlib.md5(input_data.text.encode()).hexdigest(), 16)

        embedding = [
            ((hash_val >> (i % 64)) & 1) * 2 - 1 + (i % 100) / 1000
            for i in range(dimensions)
        ]

        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        embedding = [x / norm for x in embedding]

        return EmbeddingGeneratorOutput(
            embedding=embedding,
            model=input_data.model,
            dimensions=dimensions,
            usage={"prompt_tokens": len(input_data.text) // 4, "total_tokens": len(input_data.text) // 4},
        )


# ========== Text Classifier Tool ==========

class TextClassifierInput(BaseModel):
    """Text classifier input model."""

    text: str = Field(..., description="Text to classify")
    labels: List[str] = Field(..., description="Possible labels")
    model: str = Field(default="zero-shot", description="Classification model")
    top_k: int = Field(default=3, ge=1, le=10, description="Top K predictions")


class ClassificationResult(BaseModel):
    """Classification result."""

    label: str
    score: float


class TextClassifierOutput(BaseModel):
    """Text classifier output model."""

    predictions: List[ClassificationResult]
    top_label: str
    model: str


class TextClassifierTool(BaseTool[TextClassifierInput, TextClassifierOutput]):
    """Tool for text classification."""

    metadata = ToolMetadata(
        name="text_classifier",
        description="Classify text into categories",
        category=ToolCategory.AI,
        version="1.0.0",
        tags=["classification", "nlp", "ai", "categorization"],
        timeout_seconds=30.0,
    )

    InputModel = TextClassifierInput
    OutputModel = TextClassifierOutput

    async def _execute(self, input_data: TextClassifierInput) -> TextClassifierOutput:
        """Classify text.

        Args:
            input_data: Classification parameters.

        Returns:
            TextClassifierOutput: Classification results.
        """
        if input_data.model == "zero-shot":
            return await self._zero_shot_classify(input_data)
        else:
            raise ToolError(f"Unsupported classification model: {input_data.model}")

    async def _zero_shot_classify(
        self,
        input_data: TextClassifierInput,
    ) -> TextClassifierOutput:
        """Perform zero-shot classification.

        Args:
            input_data: Classification parameters.

        Returns:
            TextClassifierOutput: Classification results.
        """
        try:
            from transformers import pipeline
        except ImportError:
            raise ToolError("transformers library not installed")

        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

        result = classifier(
            input_data.text,
            candidate_labels=input_data.labels,
            top_k=input_data.top_k,
        )

        predictions = [
            ClassificationResult(label=label, score=score)
            for label, score in zip(result["labels"], result["scores"])
        ]

        return TextClassifierOutput(
            predictions=predictions,
            top_label=predictions[0].label if predictions else "",
            model=input_data.model,
        )


# ========== Summarization Tool ==========

class SummarizationInput(BaseModel):
    """Summarization input model."""

    text: str = Field(..., description="Text to summarize")
    model: str = Field(default="extractive", description="Summarization model")
    max_length: int = Field(default=150, ge=10, le=1000, description="Max summary length")
    min_length: int = Field(default=30, ge=10, description="Min summary length")
    do_sample: bool = Field(default=False, description="Use sampling")


class SummarizationOutput(BaseModel):
    """Summarization output model."""

    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    model: str


class SummarizationTool(BaseTool[SummarizationInput, SummarizationOutput]):
    """Tool for text summarization."""

    metadata = ToolMetadata(
        name="summarization",
        description="Summarize long text documents",
        category=ToolCategory.AI,
        version="1.0.0",
        tags=["summarization", "nlp", "ai", "compression"],
        timeout_seconds=60.0,
    )

    InputModel = SummarizationInput
    OutputModel = SummarizationOutput

    async def _execute(self, input_data: SummarizationInput) -> SummarizationOutput:
        """Summarize text.

        Args:
            input_data: Summarization parameters.

        Returns:
            SummarizationOutput: Summary.
        """
        if input_data.model == "extractive":
            return await self._extractive_summarize(input_data)
        elif input_data.model == "abstractive":
            return await self._abstractive_summarize(input_data)
        else:
            raise ToolError(f"Unsupported summarization model: {input_data.model}")

    async def _extractive_summarize(
        self,
        input_data: SummarizationInput,
    ) -> SummarizationOutput:
        """Perform extractive summarization.

        Args:
            input_data: Summarization parameters.

        Returns:
            SummarizationOutput: Summary.
        """
        try:
            from summa import summarizer
        except ImportError:
            # Fallback to simple extractive summarization
            return self._simple_extractive(input_data)

        summary = summarizer.summarize(
            input_data.text,
            ratio=0.2,
            max_length=input_data.max_length,
        )

        return SummarizationOutput(
            summary=summary or "",
            original_length=len(input_data.text),
            summary_length=len(summary) if summary else 0,
            compression_ratio=len(summary) / len(input_data.text) if summary and input_data.text else 0,
            model=input_data.model,
        )

    async def _abstractive_summarize(
        self,
        input_data: SummarizationInput,
    ) -> SummarizationOutput:
        """Perform abstractive summarization.

        Args:
            input_data: Summarization parameters.

        Returns:
            SummarizationOutput: Summary.
        """
        try:
            from transformers import pipeline
        except ImportError:
            raise ToolError("transformers library not installed")

        summarizer_pipe = pipeline("summarization", model="facebook/bart-large-cnn")

        result = summarizer_pipe(
            input_data.text,
            max_length=input_data.max_length,
            min_length=input_data.min_length,
            do_sample=input_data.do_sample,
        )

        summary = result[0]["summary_text"] if result else ""

        return SummarizationOutput(
            summary=summary,
            original_length=len(input_data.text),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(input_data.text) if input_data.text else 0,
            model=input_data.model,
        )

    def _simple_extractive(self, input_data: SummarizationInput) -> SummarizationOutput:
        """Simple extractive summarization fallback.

        Args:
            input_data: Summarization parameters.

        Returns:
            SummarizationOutput: Summary.
        """
        sentences = input_data.text.split(".")
        target_sentences = max(3, len(sentences) // 5)
        summary = ". ".join(sentences[:target_sentences]) + "."

        return SummarizationOutput(
            summary=summary,
            original_length=len(input_data.text),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(input_data.text) if input_data.text else 0,
            model=input_data.model,
        )


# ========== Question Answering Tool ==========

class QuestionAnsweringInput(BaseModel):
    """Question answering input model."""

    question: str = Field(..., description="Question to answer")
    context: str = Field(..., description="Context for answering")
    model: str = Field(default="extractive", description="QA model")


class QuestionAnsweringOutput(BaseModel):
    """Question answering output model."""

    answer: str
    confidence: float
    model: str


class QuestionAnsweringTool(BaseTool[QuestionAnsweringInput, QuestionAnsweringOutput]):
    """Tool for question answering based on context."""

    metadata = ToolMetadata(
        name="question_answering",
        description="Answer questions based on provided context",
        category=ToolCategory.AI,
        version="1.0.0",
        tags=["qa", "nlp", "ai", "answering"],
        timeout_seconds=30.0,
    )

    InputModel = QuestionAnsweringInput
    OutputModel = QuestionAnsweringOutput

    async def _execute(self, input_data: QuestionAnsweringInput) -> QuestionAnsweringOutput:
        """Answer question.

        Args:
            input_data: QA parameters.

        Returns:
            QuestionAnsweringOutput: Answer.
        """
        if input_data.model == "extractive":
            return await self._extractive_qa(input_data)
        else:
            raise ToolError(f"Unsupported QA model: {input_data.model}")

    async def _extractive_qa(
        self,
        input_data: QuestionAnsweringInput,
    ) -> QuestionAnsweringOutput:
        """Perform extractive question answering.

        Args:
            input_data: QA parameters.

        Returns:
            QuestionAnsweringOutput: Answer.
        """
        try:
            from transformers import pipeline
        except ImportError:
            raise ToolError("transformers library not installed")

        qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

        result = qa_pipeline(
            question=input_data.question,
            context=input_data.context,
        )

        return QuestionAnsweringOutput(
            answer=result.get("answer", ""),
            confidence=result.get("score", 0.0),
            model=input_data.model,
        )
