"""Pre-built Workflows - Ready-to-use workflow definitions."""

from __future__ import annotations

from typing import Any, Optional

from temporalio import workflow

from app.workflow.patterns import (
    SequentialWorkflow,
    ParallelWorkflow,
    PipelineWorkflow,
)

with workflow.unsafe.imports_passed_through():
    from app.core.logging_config import get_logger

logger = get_logger(__name__)


@workflow.defn(name="DocumentAnalysisWorkflow")
class DocumentAnalysisWorkflow:
    """Document Analysis Workflow.

    A comprehensive workflow for analyzing documents:
    1. Document ingestion
    2. Structure extraction
    3. Content analysis
    4. Knowledge extraction
    5. Summary generation
    6. Validation

    Workflow Input:
        document_id: Document ID to analyze
        document_path: Path to the document
        analysis_config: Configuration for analysis
        extraction_types: Types of information to extract

    Workflow Output:
        dict: Analysis results including structure, content, knowledge, and summary
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the document analysis workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Complete analysis results.
        """
        workflow.logger.info(
            f"Starting document analysis workflow: {workflow.info().workflow_id}"
        )

        document_id = input_data.get("document_id", "")
        document_path = input_data.get("document_path", "")
        analysis_config = input_data.get("analysis_config", {})
        extraction_types = input_data.get("extraction_types", ["entities", "relationships"])

        if not document_id:
            raise ValueError("document_id is required")

        results = {
            "document_id": document_id,
            "document_path": document_path,
            "stages": {},
        }

        # Stage 1: Document ingestion
        workflow.logger.info("Stage 1: Document ingestion")
        ingestion_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "document-ingestion-agent",
                "task_type": "ingest_document",
                "payload": {
                    "document_id": document_id,
                    "document_path": document_path,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        results["stages"]["ingestion"] = ingestion_result

        # Stage 2: Structure extraction
        workflow.logger.info("Stage 2: Structure extraction")
        structure_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "structure-extraction-agent",
                "task_type": "extract_structure",
                "payload": {
                    "document_id": document_id,
                    "content": ingestion_result.get("output_data", {}).get("content", ""),
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        results["stages"]["structure"] = structure_result

        # Stage 3: Content analysis
        workflow.logger.info("Stage 3: Content analysis")
        analysis_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-analysis-agent",
                "task_type": "analyze_content",
                "payload": {
                    "document_id": document_id,
                    "structure": structure_result.get("output_data", {}),
                    "config": analysis_config,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["analysis"] = analysis_result

        # Stage 4: Knowledge extraction (parallel for different extraction types)
        workflow.logger.info("Stage 4: Knowledge extraction")
        knowledge_tasks = []
        for extraction_type in extraction_types:
            knowledge_tasks.append(
                workflow.execute_activity(
                    "agent_activity",
                    {
                        "agent_id": f"knowledge-extraction-{extraction_type}-agent",
                        "task_type": f"extract_{extraction_type}",
                        "payload": {
                            "document_id": document_id,
                            "analysis": analysis_result.get("output_data", {}),
                        },
                    },
                    start_to_close_timeout=workflow.timedelta(minutes=10),
                )
            )

        knowledge_results = await workflow.gather(*knowledge_tasks)
        results["stages"]["knowledge"] = {
            extraction_type: result
            for extraction_type, result in zip(extraction_types, knowledge_results)
        }

        # Stage 5: Summary generation
        workflow.logger.info("Stage 5: Summary generation")
        summary_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "summary-generation-agent",
                "task_type": "generate_summary",
                "payload": {
                    "document_id": document_id,
                    "analysis": analysis_result.get("output_data", {}),
                    "knowledge": {
                        et: kr for et, kr in zip(extraction_types, knowledge_results)
                    },
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        results["stages"]["summary"] = summary_result

        # Stage 6: Validation
        workflow.logger.info("Stage 6: Validation")
        validation_result = await workflow.execute_activity(
            "validation_activity",
            {
                "data": {
                    "document_id": document_id,
                    "analysis": analysis_result.get("output_data", {}),
                    "summary": summary_result.get("output_data", {}),
                },
                "rules": [
                    {
                        "type": "custom",
                        "field": "summary",
                        "condition": "!= None",
                        "message": "Summary is required",
                    }
                ],
            },
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        results["stages"]["validation"] = validation_result

        # Compile final results
        results["final"] = {
            "document_id": document_id,
            "structure": structure_result.get("output_data", {}),
            "analysis": analysis_result.get("output_data", {}),
            "knowledge": {
                et: kr.get("output_data", {})
                for et, kr in zip(extraction_types, knowledge_results)
            },
            "summary": summary_result.get("output_data", {}),
            "validation": validation_result.get("output_data", {}),
        }

        workflow.logger.info("Document analysis workflow completed")
        return results


@workflow.defn(name="ResearchWorkflow")
class ResearchWorkflow:
    """Research Workflow.

    A comprehensive workflow for conducting research:
    1. Topic analysis
    2. Web research (multiple sources)
    3. Information aggregation
    4. Fact verification
    5. Report generation
    6. Citation formatting

    Workflow Input:
        topic: Research topic
        research_config: Research configuration
        sources: List of sources to research
        depth: Research depth (shallow, medium, deep)

    Workflow Output:
        dict: Research report with findings, citations, and verification
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the research workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Complete research results.
        """
        workflow.logger.info(f"Starting research workflow: {workflow.info().workflow_id}")

        topic = input_data.get("topic", "")
        research_config = input_data.get("research_config", {})
        sources = input_data.get("sources", ["web", "academic", "news"])
        depth = input_data.get("depth", "medium")

        if not topic:
            raise ValueError("topic is required")

        results = {
            "topic": topic,
            "depth": depth,
            "stages": {},
        }

        # Stage 1: Topic analysis
        workflow.logger.info("Stage 1: Topic analysis")
        topic_analysis = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "research-agent",
                "task_type": "analyze_topic",
                "payload": {
                    "topic": topic,
                    "config": research_config,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        results["stages"]["topic_analysis"] = topic_analysis

        # Stage 2: Web research (parallel for multiple sources)
        workflow.logger.info("Stage 2: Web research")
        research_tasks = []
        for source in sources:
            research_tasks.append(
                workflow.execute_activity(
                    "agent_activity",
                    {
                        "agent_id": "web-research-agent",
                        "task_type": "research_source",
                        "payload": {
                            "topic": topic,
                            "source": source,
                            "depth": depth,
                            "keywords": topic_analysis.get("output_data", {}).get(
                                "keywords", []
                            ),
                        },
                    },
                    start_to_close_timeout=workflow.timedelta(minutes=15),
                )
            )

        research_results = await workflow.gather(*research_tasks)
        results["stages"]["research"] = {
            source: result
            for source, result in zip(sources, research_results)
        }

        # Stage 3: Information aggregation
        workflow.logger.info("Stage 3: Information aggregation")
        aggregation_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "aggregation-agent",
                "task_type": "aggregate_information",
                "payload": {
                    "topic": topic,
                    "research_results": {
                        source: result.get("output_data", {})
                        for source, result in zip(sources, research_results)
                    },
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        results["stages"]["aggregation"] = aggregation_result

        # Stage 4: Fact verification
        workflow.logger.info("Stage 4: Fact verification")
        verification_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "fact-verifier-agent",
                "task_type": "verify_facts",
                "payload": {
                    "topic": topic,
                    "claims": aggregation_result.get("output_data", {}).get("claims", []),
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["verification"] = verification_result

        # Stage 5: Report generation
        workflow.logger.info("Stage 5: Report generation")
        report_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "report-generator-agent",
                "task_type": "generate_report",
                "payload": {
                    "topic": topic,
                    "aggregation": aggregation_result.get("output_data", {}),
                    "verification": verification_result.get("output_data", {}),
                    "config": research_config,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["report"] = report_result

        # Stage 6: Citation formatting
        workflow.logger.info("Stage 6: Citation formatting")
        citation_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "citation-agent",
                "task_type": "format_citations",
                "payload": {
                    "sources": {
                        source: result.get("output_data", {})
                        for source, result in zip(sources, research_results)
                    },
                    "style": research_config.get("citation_style", "apa"),
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        results["stages"]["citations"] = citation_result

        # Compile final results
        results["final"] = {
            "topic": topic,
            "depth": depth,
            "aggregated_information": aggregation_result.get("output_data", {}),
            "verified_claims": verification_result.get("output_data", {}),
            "report": report_result.get("output_data", {}),
            "citations": citation_result.get("output_data", {}),
        }

        workflow.logger.info("Research workflow completed")
        return results


@workflow.defn(name="ContentGenerationWorkflow")
class ContentGenerationWorkflow:
    """Content Generation Workflow.

    A comprehensive workflow for generating content:
    1. Content planning
    2. Outline creation
    3. Section drafting (parallel)
    4. Content review
    5. Editing and refinement
    6. Final validation

    Workflow Input:
        topic: Content topic
        content_type: Type of content (article, blog, guide)
        target_audience: Target audience description
        length: Target length (short, medium, long)
        tone: Content tone (formal, casual, technical)

    Workflow Output:
        dict: Generated content with outline, sections, and validation
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the content generation workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Complete generated content.
        """
        workflow.logger.info(
            f"Starting content generation workflow: {workflow.info().workflow_id}"
        )

        topic = input_data.get("topic", "")
        content_type = input_data.get("content_type", "article")
        target_audience = input_data.get("target_audience", "general")
        length = input_data.get("length", "medium")
        tone = input_data.get("tone", "professional")

        if not topic:
            raise ValueError("topic is required")

        results = {
            "topic": topic,
            "content_type": content_type,
            "stages": {},
        }

        # Stage 1: Content planning
        workflow.logger.info("Stage 1: Content planning")
        planning_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-architect-agent",
                "task_type": "plan_content",
                "payload": {
                    "topic": topic,
                    "content_type": content_type,
                    "target_audience": target_audience,
                    "length": length,
                    "tone": tone,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        results["stages"]["planning"] = planning_result

        # Stage 2: Outline creation
        workflow.logger.info("Stage 2: Outline creation")
        outline_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-architect-agent",
                "task_type": "create_outline",
                "payload": {
                    "topic": topic,
                    "plan": planning_result.get("output_data", {}),
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=10),
        )
        results["stages"]["outline"] = outline_result

        # Stage 3: Section drafting (parallel)
        workflow.logger.info("Stage 3: Section drafting")
        outline_sections = outline_result.get("output_data", {}).get("sections", [])

        drafting_tasks = []
        for idx, section in enumerate(outline_sections):
            drafting_tasks.append(
                workflow.execute_activity(
                    "agent_activity",
                    {
                        "agent_id": "writing-agent",
                        "task_type": "draft_section",
                        "payload": {
                            "topic": topic,
                            "section": section,
                            "section_index": idx,
                            "tone": tone,
                            "outline": outline_result.get("output_data", {}),
                        },
                    },
                    start_to_close_timeout=workflow.timedelta(minutes=15),
                )
            )

        drafting_results = await workflow.gather(*drafting_tasks)
        results["stages"]["drafting"] = {
            f"section_{idx}": result
            for idx, result in enumerate(drafting_results)
        }

        # Stage 4: Content review
        workflow.logger.info("Stage 4: Content review")
        review_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-reviewer-agent",
                "task_type": "review_content",
                "payload": {
                    "topic": topic,
                    "outline": outline_result.get("output_data", {}),
                    "sections": {
                        f"section_{idx}": result.get("output_data", {})
                        for idx, result in enumerate(drafting_results)
                    },
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["review"] = review_result

        # Stage 5: Editing and refinement
        workflow.logger.info("Stage 5: Editing and refinement")
        editing_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "editing-agent",
                "task_type": "edit_content",
                "payload": {
                    "sections": {
                        f"section_{idx}": result.get("output_data", {})
                        for idx, result in enumerate(drafting_results)
                    },
                    "feedback": review_result.get("output_data", {}).get("feedback", []),
                    "tone": tone,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["editing"] = editing_result

        # Stage 6: Final validation
        workflow.logger.info("Stage 6: Final validation")
        validation_result = await workflow.execute_activity(
            "validation_activity",
            {
                "data": {
                    "content": editing_result.get("output_data", {}),
                    "topic": topic,
                },
                "rules": [
                    {
                        "type": "custom",
                        "field": "content",
                        "condition": "!= None",
                        "message": "Content is required",
                    }
                ],
            },
            start_to_close_timeout=workflow.timedelta(minutes=5),
        )
        results["stages"]["validation"] = validation_result

        # Compile final results
        results["final"] = {
            "topic": topic,
            "content_type": content_type,
            "outline": outline_result.get("output_data", {}),
            "sections": editing_result.get("output_data", {}).get("sections", {}),
            "full_content": editing_result.get("output_data", {}).get("full_content", ""),
            "review_feedback": review_result.get("output_data", {}).get("feedback", []),
            "validation": validation_result.get("output_data", {}),
        }

        workflow.logger.info("Content generation workflow completed")
        return results


@workflow.defn(name="CodeGenerationWorkflow")
class CodeGenerationWorkflow:
    """Code Generation Workflow.

    A comprehensive workflow for generating code:
    1. Requirements analysis
    2. Architecture design
    3. Code generation (parallel by module)
    4. Code review
    5. Testing
    6. Documentation

    Workflow Input:
        requirements: Functional requirements
        tech_stack: Technology stack to use
        modules: List of modules to generate
        coding_standards: Coding standards to follow

    Workflow Output:
        dict: Generated code with architecture, modules, tests, and docs
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the code generation workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Complete generated code.
        """
        workflow.logger.info(
            f"Starting code generation workflow: {workflow.info().workflow_id}"
        )

        requirements = input_data.get("requirements", {})
        tech_stack = input_data.get("tech_stack", {})
        modules = input_data.get("modules", [])
        coding_standards = input_data.get("coding_standards", {})

        if not requirements:
            raise ValueError("requirements are required")

        results = {
            "requirements": requirements,
            "stages": {},
        }

        # Stage 1: Requirements analysis
        workflow.logger.info("Stage 1: Requirements analysis")
        analysis_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "requirements-analyst-agent",
                "task_type": "analyze_requirements",
                "payload": {
                    "requirements": requirements,
                    "tech_stack": tech_stack,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["analysis"] = analysis_result

        # Stage 2: Architecture design
        workflow.logger.info("Stage 2: Architecture design")
        architecture_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "architecture-analyst-agent",
                "task_type": "design_architecture",
                "payload": {
                    "requirements": requirements,
                    "analysis": analysis_result.get("output_data", {}),
                    "tech_stack": tech_stack,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=20),
        )
        results["stages"]["architecture"] = architecture_result

        # Stage 3: Code generation (parallel by module)
        workflow.logger.info("Stage 3: Code generation")
        generation_tasks = []
        for module in modules:
            generation_tasks.append(
                workflow.execute_activity(
                    "agent_activity",
                    {
                        "agent_id": "code-generator-agent",
                        "task_type": "generate_module",
                        "payload": {
                            "module": module,
                            "architecture": architecture_result.get("output_data", {}),
                            "tech_stack": tech_stack,
                            "standards": coding_standards,
                        },
                    },
                    start_to_close_timeout=workflow.timedelta(minutes=30),
                )
            )

        generation_results = await workflow.gather(*generation_tasks)
        results["stages"]["generation"] = {
            module.get("name", f"module_{idx}"): result
            for idx, (module, result) in enumerate(zip(modules, generation_results))
        }

        # Stage 4: Code review
        workflow.logger.info("Stage 4: Code review")
        review_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "code-reviewer-agent",
                "task_type": "review_code",
                "payload": {
                    "modules": {
                        module.get("name", f"module_{idx}"): result.get("output_data", {})
                        for idx, (module, result) in enumerate(
                            zip(modules, generation_results)
                        )
                    },
                    "standards": coding_standards,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=20),
        )
        results["stages"]["review"] = review_result

        # Stage 5: Testing
        workflow.logger.info("Stage 5: Testing")
        testing_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "test-generator-agent",
                "task_type": "generate_tests",
                "payload": {
                    "modules": {
                        module.get("name", f"module_{idx}"): result.get("output_data", {})
                        for idx, (module, result) in enumerate(
                            zip(modules, generation_results)
                        )
                    },
                    "review_feedback": review_result.get("output_data", {}).get(
                        "feedback", []
                    ),
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=20),
        )
        results["stages"]["testing"] = testing_result

        # Stage 6: Documentation
        workflow.logger.info("Stage 6: Documentation")
        documentation_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "documentation-agent",
                "task_type": "generate_documentation",
                "payload": {
                    "requirements": requirements,
                    "architecture": architecture_result.get("output_data", {}),
                    "modules": {
                        module.get("name", f"module_{idx}"): result.get("output_data", {})
                        for idx, (module, result) in enumerate(
                            zip(modules, generation_results)
                        )
                    },
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=15),
        )
        results["stages"]["documentation"] = documentation_result

        # Compile final results
        results["final"] = {
            "architecture": architecture_result.get("output_data", {}),
            "modules": {
                module.get("name", f"module_{idx}"): result.get("output_data", {})
                for idx, (module, result) in enumerate(zip(modules, generation_results))
            },
            "tests": testing_result.get("output_data", {}),
            "documentation": documentation_result.get("output_data", {}),
            "review_feedback": review_result.get("output_data", {}).get("feedback", []),
        }

        workflow.logger.info("Code generation workflow completed")
        return results


@workflow.defn(name="BookGenerationWorkflow")
class BookGenerationWorkflow:
    """Book Generation Workflow.

    A comprehensive workflow for generating books:
    1. Book planning
    2. Chapter outlining
    3. Chapter writing (parallel)
    4. Cross-chapter consistency check
    5. Editing
    6. Formatting
    7. Final review

    Workflow Input:
        book_title: Book title
        genre: Book genre
        target_audience: Target audience
        chapter_count: Number of chapters
        writing_style: Writing style

    Workflow Output:
        dict: Complete book with chapters, formatting, and review
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the book generation workflow.

        Args:
            input_data: Workflow input data.

        Returns:
            dict: Complete generated book.
        """
        workflow.logger.info(
            f"Starting book generation workflow: {workflow.info().workflow_id}"
        )

        book_title = input_data.get("book_title", "")
        genre = input_data.get("genre", "non-fiction")
        target_audience = input_data.get("target_audience", "general")
        chapter_count = input_data.get("chapter_count", 10)
        writing_style = input_data.get("writing_style", "professional")

        if not book_title:
            raise ValueError("book_title is required")

        results = {
            "book_title": book_title,
            "genre": genre,
            "stages": {},
        }

        # Stage 1: Book planning
        workflow.logger.info("Stage 1: Book planning")
        planning_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-architect-agent",
                "task_type": "plan_book",
                "payload": {
                    "book_title": book_title,
                    "genre": genre,
                    "target_audience": target_audience,
                    "chapter_count": chapter_count,
                    "writing_style": writing_style,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=20),
        )
        results["stages"]["planning"] = planning_result

        # Stage 2: Chapter outlining
        workflow.logger.info("Stage 2: Chapter outlining")
        outlining_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-architect-agent",
                "task_type": "create_chapter_outlines",
                "payload": {
                    "book_title": book_title,
                    "plan": planning_result.get("output_data", {}),
                    "chapter_count": chapter_count,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=30),
        )
        results["stages"]["outlining"] = outlining_result

        # Stage 3: Chapter writing (parallel)
        workflow.logger.info("Stage 3: Chapter writing")
        chapter_outlines = outlining_result.get("output_data", {}).get("chapters", [])

        writing_tasks = []
        for idx, chapter_outline in enumerate(chapter_outlines):
            writing_tasks.append(
                workflow.execute_activity(
                    "agent_activity",
                    {
                        "agent_id": "writing-agent",
                        "task_type": "write_chapter",
                        "payload": {
                            "book_title": book_title,
                            "chapter_outline": chapter_outline,
                            "chapter_number": idx + 1,
                            "writing_style": writing_style,
                            "genre": genre,
                        },
                    },
                    start_to_close_timeout=workflow.timedelta(minutes=45),
                )
            )

        writing_results = await workflow.gather(*writing_tasks)
        results["stages"]["writing"] = {
            f"chapter_{idx + 1}": result
            for idx, result in enumerate(writing_results)
        }

        # Stage 4: Cross-chapter consistency check
        workflow.logger.info("Stage 4: Cross-chapter consistency check")
        consistency_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "consistency-checker-agent",
                "task_type": "check_consistency",
                "payload": {
                    "book_title": book_title,
                    "chapters": {
                        f"chapter_{idx + 1}": result.get("output_data", {})
                        for idx, result in enumerate(writing_results)
                    },
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=30),
        )
        results["stages"]["consistency"] = consistency_result

        # Stage 5: Editing
        workflow.logger.info("Stage 5: Editing")
        editing_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "editing-agent",
                "task_type": "edit_book",
                "payload": {
                    "chapters": {
                        f"chapter_{idx + 1}": result.get("output_data", {})
                        for idx, result in enumerate(writing_results)
                    },
                    "consistency_feedback": consistency_result.get("output_data", {}).get(
                        "feedback", []
                    ),
                    "writing_style": writing_style,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=45),
        )
        results["stages"]["editing"] = editing_result

        # Stage 6: Formatting
        workflow.logger.info("Stage 6: Formatting")
        formatting_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "formatting-agent",
                "task_type": "format_book",
                "payload": {
                    "book_title": book_title,
                    "chapters": editing_result.get("output_data", {}).get("chapters", {}),
                    "genre": genre,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=20),
        )
        results["stages"]["formatting"] = formatting_result

        # Stage 7: Final review
        workflow.logger.info("Stage 7: Final review")
        review_result = await workflow.execute_activity(
            "agent_activity",
            {
                "agent_id": "content-reviewer-agent",
                "task_type": "review_book",
                "payload": {
                    "book_title": book_title,
                    "formatted_book": formatting_result.get("output_data", {}),
                    "genre": genre,
                },
            },
            start_to_close_timeout=workflow.timedelta(minutes=30),
        )
        results["stages"]["review"] = review_result

        # Compile final results
        results["final"] = {
            "book_title": book_title,
            "genre": genre,
            "chapters": editing_result.get("output_data", {}).get("chapters", {}),
            "full_book": formatting_result.get("output_data", {}).get("full_book", ""),
            "formatting": formatting_result.get("output_data", {}),
            "review": review_result.get("output_data", {}),
        }

        workflow.logger.info("Book generation workflow completed")
        return results
