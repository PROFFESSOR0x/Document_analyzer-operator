"""Tool Capability Layer for agent task execution.

This module provides a comprehensive tool system that agents can use
to perform various tasks including web operations, document processing,
AI operations, automation, and data manipulation.
"""

from app.tools.base import BaseTool, ToolRegistry, ToolExecutionEngine
from app.tools.web_tools import (
    WebSearchTool,
    WebScraperTool,
    APIClientTool,
    RSSFeedTool,
)
from app.tools.document_tools import (
    PDFParserTool,
    DOCXParserTool,
    MarkdownParserTool,
    TableExtractionTool,
    ImageOCRTool,
)
from app.tools.ai_tools import (
    LLMClientTool,
    EmbeddingGeneratorTool,
    TextClassifierTool,
    SummarizationTool,
    QuestionAnsweringTool,
)
from app.tools.automation_tools import (
    ShellExecutorTool,
    GitOperationsTool,
    FileConverterTool,
    ScheduledTaskTool,
)
from app.tools.data_tools import (
    DatabaseQueryTool,
    DataValidationTool,
    DataTransformationTool,
    CSVExcelTool,
)

__all__ = [
    # Base
    "BaseTool",
    "ToolRegistry",
    "ToolExecutionEngine",
    # Web Tools
    "WebSearchTool",
    "WebScraperTool",
    "APIClientTool",
    "RSSFeedTool",
    # Document Tools
    "PDFParserTool",
    "DOCXParserTool",
    "MarkdownParserTool",
    "TableExtractionTool",
    "ImageOCRTool",
    # AI Tools
    "LLMClientTool",
    "EmbeddingGeneratorTool",
    "TextClassifierTool",
    "SummarizationTool",
    "QuestionAnsweringTool",
    # Automation Tools
    "ShellExecutorTool",
    "GitOperationsTool",
    "FileConverterTool",
    "ScheduledTaskTool",
    # Data Tools
    "DatabaseQueryTool",
    "DataValidationTool",
    "DataTransformationTool",
    "CSVExcelTool",
]
