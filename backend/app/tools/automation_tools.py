"""Automation tools for system operations and task scheduling."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime, timezone
import logging
import shlex
import re

from app.tools.base import BaseTool, ToolMetadata, ToolCategory, ToolError


# ========== Shell Executor Tool ==========

class ShellExecutorInput(BaseModel):
    """Shell executor input model."""

    command: str = Field(..., description="Command to execute")
    working_directory: Optional[str] = Field(default=None, description="Working directory")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    timeout_seconds: float = Field(default=60.0, description="Command timeout")
    shell: bool = Field(default=False, description="Run in shell")
    capture_output: bool = Field(default=True, description="Capture stdout/stderr")


class ShellExecutorOutput(BaseModel):
    """Shell executor output model."""

    return_code: int
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float
    command: str


class ShellExecutorTool(BaseTool[ShellExecutorInput, ShellExecutorOutput]):
    """Tool for safe shell command execution."""

    metadata = ToolMetadata(
        name="shell_executor",
        description="Execute shell commands safely",
        category=ToolCategory.AUTOMATION,
        version="1.0.0",
        tags=["shell", "command", "automation", "system"],
        requires_auth=True,
        rate_limit_per_minute=30,
        timeout_seconds=300.0,
    )

    InputModel = ShellExecutorInput
    OutputModel = ShellExecutorOutput

    # Dangerous commands that should be blocked
    BLOCKED_COMMANDS = [
        "rm -rf /",
        "rm -rf /*",
        "mkfs",
        "dd if=/dev/zero",
        ":(){:|:&};:",
        "chmod -R 777 /",
        "chown -R",
    ]

    # Dangerous patterns
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"sudo\s+rm\s+-rf",
        r"chmod\s+-R\s+777\s+/",
        r">\s*/dev/sd",
        r"dd\s+if=/dev/zero",
    ]

    async def _execute(self, input_data: ShellExecutorInput) -> ShellExecutorOutput:
        """Execute shell command.

        Args:
            input_data: Execution parameters.

        Returns:
            ShellExecutorOutput: Command output.
        """
        # Validate command
        self._validate_command(input_data.command)

        self._logger.info(f"Executing command: {input_data.command}")

        import asyncio

        start_time = datetime.now(timezone.utc)

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                input_data.command if input_data.shell else shlex.split(input_data.command),
                stdout=asyncio.subprocess.PIPE if input_data.capture_output else None,
                stderr=asyncio.subprocess.PIPE if input_data.capture_output else None,
                cwd=input_data.working_directory,
                env=input_data.environment,
                shell=input_data.shell,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=input_data.timeout_seconds,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise ToolError(f"Command timed out after {input_data.timeout_seconds}s")

            execution_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            return ShellExecutorOutput(
                return_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace") if stdout else "",
                stderr=stderr.decode("utf-8", errors="replace") if stderr else "",
                execution_time_ms=execution_time_ms,
                command=input_data.command,
            )

        except Exception as e:
            execution_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return ShellExecutorOutput(
                return_code=-1,
                stderr=str(e),
                execution_time_ms=execution_time_ms,
                command=input_data.command,
            )

    def _validate_command(self, command: str) -> None:
        """Validate command for safety.

        Args:
            command: Command to validate.

        Raises:
            ToolError: If command is dangerous.
        """
        command_lower = command.lower()

        # Check blocked commands
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in command_lower:
                raise ToolError(f"Command blocked for safety: {blocked}")

        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, command_lower):
                raise ToolError(f"Command blocked for safety: pattern matched")


# ========== Git Operations Tool ==========

class GitOperationsInput(BaseModel):
    """Git operations input model."""

    operation: str = Field(..., description="Git operation (clone, pull, commit, etc.)")
    repository_url: Optional[str] = Field(default=None, description="Repository URL")
    directory: Optional[str] = Field(default=None, description="Working directory")
    branch: Optional[str] = Field(default=None, description="Branch name")
    commit_message: Optional[str] = Field(default=None, description="Commit message")
    files: Optional[List[str]] = Field(default=None, description="Files to operate on")
    username: Optional[str] = Field(default=None, description="Git username")
    password: Optional[str] = Field(default=None, description="Git password/token")


class GitOperationsOutput(BaseModel):
    """Git operations output model."""

    success: bool
    output: str = ""
    error: str = ""
    operation: str
    repository: Optional[str] = None


class GitOperationsTool(BaseTool[GitOperationsInput, GitOperationsOutput]):
    """Tool for Git operations."""

    metadata = ToolMetadata(
        name="git_operations",
        description="Perform Git operations (clone, pull, commit, etc.)",
        category=ToolCategory.AUTOMATION,
        version="1.0.0",
        tags=["git", "version-control", "automation"],
        requires_auth=True,
        timeout_seconds=300.0,
    )

    InputModel = GitOperationsInput
    OutputModel = GitOperationsOutput

    async def _execute(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Execute Git operation.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Operation result.
        """
        operation = input_data.operation.lower()

        if operation == "clone":
            return await self._clone(input_data)
        elif operation == "pull":
            return await self._pull(input_data)
        elif operation == "commit":
            return await self._commit(input_data)
        elif operation == "push":
            return await self._push(input_data)
        elif operation == "status":
            return await self._status(input_data)
        else:
            raise ToolError(f"Unsupported Git operation: {operation}")

    async def _clone(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Clone a repository.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Result.
        """
        if not input_data.repository_url:
            raise ToolError("repository_url is required for clone operation")

        import asyncio

        cmd = ["git", "clone"]
        if input_data.branch:
            cmd.extend(["-b", input_data.branch])

        repo_url = input_data.repository_url
        if input_data.username and input_data.password:
            repo_url = repo_url.replace(
                "https://",
                f"https://{input_data.username}:{input_data.password}@",
            )

        cmd.extend([repo_url, input_data.directory or "."])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            return GitOperationsOutput(
                success=process.returncode == 0,
                output=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace") if process.returncode != 0 else "",
                operation="clone",
                repository=input_data.repository_url,
            )
        except Exception as e:
            return GitOperationsOutput(
                success=False,
                error=str(e),
                operation="clone",
                repository=input_data.repository_url,
            )

    async def _pull(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Pull changes from remote.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Result.
        """
        return await self._run_git_command(input_data, "pull")

    async def _commit(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Commit changes.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Result.
        """
        if not input_data.commit_message:
            raise ToolError("commit_message is required for commit operation")

        import asyncio

        # Stage files
        if input_data.files:
            stage_cmd = ["git", "add"] + input_data.files
            process = await asyncio.create_subprocess_exec(
                *stage_cmd,
                cwd=input_data.directory,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

        # Commit
        commit_cmd = ["git", "commit", "-m", input_data.commit_message]
        process = await asyncio.create_subprocess_exec(
            *commit_cmd,
            cwd=input_data.directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        return GitOperationsOutput(
            success=process.returncode == 0,
            output=stdout.decode("utf-8", errors="replace"),
            error=stderr.decode("utf-8", errors="replace") if process.returncode != 0 else "",
            operation="commit",
        )

    async def _push(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Push changes to remote.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Result.
        """
        return await self._run_git_command(input_data, "push")

    async def _status(self, input_data: GitOperationsInput) -> GitOperationsOutput:
        """Get repository status.

        Args:
            input_data: Operation parameters.

        Returns:
            GitOperationsOutput: Result.
        """
        return await self._run_git_command(input_data, "status")

    async def _run_git_command(
        self,
        input_data: GitOperationsInput,
        command: str,
    ) -> GitOperationsOutput:
        """Run a generic Git command.

        Args:
            input_data: Operation parameters.
            command: Git command to run.

        Returns:
            GitOperationsOutput: Result.
        """
        import asyncio

        cmd = ["git", command]
        if input_data.branch and command in ["pull", "push", "checkout"]:
            cmd.append(input_data.branch)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=input_data.directory,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            return GitOperationsOutput(
                success=process.returncode == 0,
                output=stdout.decode("utf-8", errors="replace"),
                error=stderr.decode("utf-8", errors="replace") if process.returncode != 0 else "",
                operation=command,
            )
        except Exception as e:
            return GitOperationsOutput(
                success=False,
                error=str(e),
                operation=command,
            )


# ========== File Converter Tool ==========

class FileConverterInput(BaseModel):
    """File converter input model."""

    input_path: str = Field(..., description="Input file path")
    output_path: Optional[str] = Field(default=None, description="Output file path")
    output_format: str = Field(..., description="Output format (pdf, docx, txt, html, md)")
    preserve_formatting: bool = Field(default=True, description="Preserve formatting")


class FileConverterOutput(BaseModel):
    """File converter output model."""

    success: bool
    output_path: str
    input_format: str
    output_format: str
    file_size_bytes: int = 0


class FileConverterTool(BaseTool[FileConverterInput, FileConverterOutput]):
    """Tool for converting files between formats."""

    metadata = ToolMetadata(
        name="file_converter",
        description="Convert files between different formats",
        category=ToolCategory.AUTOMATION,
        version="1.0.0",
        tags=["conversion", "file", "format", "automation"],
        timeout_seconds=120.0,
    )

    InputModel = FileConverterInput
    OutputModel = FileConverterOutput

    async def _execute(self, input_data: FileConverterInput) -> FileConverterOutput:
        """Convert file.

        Args:
            input_data: Conversion parameters.

        Returns:
            FileConverterOutput: Conversion result.
        """
        input_path = Path(input_data.input_path)
        if not input_path.exists():
            raise ToolError(f"Input file not found: {input_data.input_path}")

        input_format = input_path.suffix.lower().lstrip(".")
        output_format = input_data.output_format.lower()

        # Determine output path
        if input_data.output_path:
            output_path = Path(input_data.output_path)
        else:
            output_path = input_path.with_suffix(f".{output_format}")

        # Perform conversion based on formats
        conversion_key = f"{input_format}_to_{output_format}"

        if conversion_key == "pdf_to_txt":
            return await self._pdf_to_txt(input_data, output_path)
        elif conversion_key == "docx_to_pdf":
            return await self._docx_to_pdf(input_data, output_path)
        elif conversion_key == "docx_to_txt":
            return await self._docx_to_txt(input_data, output_path)
        elif conversion_key == "md_to_html":
            return await self._md_to_html(input_data, output_path)
        elif conversion_key == "html_to_pdf":
            return await self._html_to_pdf(input_data, output_path)
        else:
            raise ToolError(f"Unsupported conversion: {input_format} -> {output_format}")

    async def _pdf_to_txt(
        self,
        input_data: FileConverterInput,
        output_path: Path,
    ) -> FileConverterOutput:
        """Convert PDF to TXT.

        Args:
            input_data: Conversion parameters.
            output_path: Output file path.

        Returns:
            FileConverterOutput: Result.
        """
        try:
            import pypdf
        except ImportError:
            raise ToolError("pypdf not installed")

        reader = pypdf.PdfReader(input_data.input_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        output_path.write_text(text, encoding="utf-8")

        return FileConverterOutput(
            success=True,
            output_path=str(output_path),
            input_format="pdf",
            output_format="txt",
            file_size_bytes=output_path.stat().st_size,
        )

    async def _docx_to_pdf(
        self,
        input_data: FileConverterInput,
        output_path: Path,
    ) -> FileConverterOutput:
        """Convert DOCX to PDF.

        Args:
            input_data: Conversion parameters.
            output_path: Output file path.

        Returns:
            FileConverterOutput: Result.
        """
        # This would typically use LibreOffice or similar
        # For now, return a placeholder implementation
        raise ToolError("DOCX to PDF conversion requires external tool (LibreOffice)")

    async def _docx_to_txt(
        self,
        input_data: FileConverterInput,
        output_path: Path,
    ) -> FileConverterOutput:
        """Convert DOCX to TXT.

        Args:
            input_data: Conversion parameters.
            output_path: Output file path.

        Returns:
            FileConverterOutput: Result.
        """
        try:
            from docx import Document
        except ImportError:
            raise ToolError("python-docx not installed")

        doc = Document(input_data.input_path)
        text = "\n\n".join([para.text for para in doc.paragraphs if para.text])

        output_path.write_text(text, encoding="utf-8")

        return FileConverterOutput(
            success=True,
            output_path=str(output_path),
            input_format="docx",
            output_format="txt",
            file_size_bytes=output_path.stat().st_size,
        )

    async def _md_to_html(
        self,
        input_data: FileConverterInput,
        output_path: Path,
    ) -> FileConverterOutput:
        """Convert Markdown to HTML.

        Args:
            input_data: Conversion parameters.
            output_path: Output file path.

        Returns:
            FileConverterOutput: Result.
        """
        try:
            import markdown
        except ImportError:
            raise ToolError("markdown not installed")

        content = Path(input_data.input_path).read_text(encoding="utf-8")
        html = markdown.markdown(content, extensions=["extra", "codehilite"])

        output_path.write_text(html, encoding="utf-8")

        return FileConverterOutput(
            success=True,
            output_path=str(output_path),
            input_format="md",
            output_format="html",
            file_size_bytes=output_path.stat().st_size,
        )

    async def _html_to_pdf(
        self,
        input_data: FileConverterInput,
        output_path: Path,
    ) -> FileConverterOutput:
        """Convert HTML to PDF.

        Args:
            input_data: Conversion parameters.
            output_path: Output file path.

        Returns:
            FileConverterOutput: Result.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ToolError("playwright not installed")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            content = Path(input_data.input_path).read_text(encoding="utf-8")
            await page.set_content(content)
            await page.pdf(path=str(output_path))

            await browser.close()

        return FileConverterOutput(
            success=True,
            output_path=str(output_path),
            input_format="html",
            output_format="pdf",
            file_size_bytes=output_path.stat().st_size,
        )


# ========== Scheduled Task Tool ==========

class ScheduledTaskInput(BaseModel):
    """Scheduled task input model."""

    operation: str = Field(..., description="Operation (create, cancel, list, run)")
    task_id: Optional[str] = Field(default=None, description="Task ID")
    cron_expression: Optional[str] = Field(default=None, description="Cron expression")
    command: Optional[str] = Field(default=None, description="Command to execute")
    enabled: bool = Field(default=True, description="Enable task")


class ScheduledTaskInfo(BaseModel):
    """Scheduled task information."""

    task_id: str
    cron_expression: str
    command: str
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0


class ScheduledTaskOutput(BaseModel):
    """Scheduled task output model."""

    success: bool
    task_id: Optional[str] = None
    message: str = ""
    tasks: List[ScheduledTaskInfo] = Field(default_factory=list)


class ScheduledTaskTool(BaseTool[ScheduledTaskInput, ScheduledTaskOutput]):
    """Tool for managing scheduled tasks."""

    metadata = ToolMetadata(
        name="scheduled_task",
        description="Manage cron-like scheduled tasks",
        category=ToolCategory.AUTOMATION,
        version="1.0.0",
        tags=["scheduling", "cron", "automation", "tasks"],
        timeout_seconds=30.0,
    )

    InputModel = ScheduledTaskInput
    OutputModel = ScheduledTaskOutput

    _tasks: Dict[str, ScheduledTaskInfo] = {}
    _running_tasks: Dict[str, Any] = {}

    async def _execute(self, input_data: ScheduledTaskInput) -> ScheduledTaskOutput:
        """Execute scheduled task operation.

        Args:
            input_data: Operation parameters.

        Returns:
            ScheduledTaskOutput: Operation result.
        """
        operation = input_data.operation.lower()

        if operation == "create":
            return await self._create_task(input_data)
        elif operation == "cancel":
            return await self._cancel_task(input_data)
        elif operation == "list":
            return await self._list_tasks()
        elif operation == "run":
            return await self._run_task(input_data)
        elif operation == "enable":
            return await self._toggle_task(input_data, True)
        elif operation == "disable":
            return await self._toggle_task(input_data, False)
        else:
            raise ToolError(f"Unsupported operation: {operation}")

    async def _create_task(self, input_data: ScheduledTaskInput) -> ScheduledTaskOutput:
        """Create a scheduled task.

        Args:
            input_data: Operation parameters.

        Returns:
            ScheduledTaskOutput: Result.
        """
        if not input_data.cron_expression or not input_data.command:
            raise ToolError("cron_expression and command are required")

        import uuid
        from croniter import croniter

        task_id = input_data.task_id or str(uuid.uuid4())

        # Calculate next run time
        cron = croniter(input_data.cron_expression, datetime.now(timezone.utc))
        next_run = cron.get_next(datetime)

        task_info = ScheduledTaskInfo(
            task_id=task_id,
            cron_expression=input_data.cron_expression,
            command=input_data.command,
            enabled=input_data.enabled,
            next_run=next_run,
        )

        self._tasks[task_id] = task_info

        # Start the scheduler
        if input_data.enabled:
            await self._start_scheduler(task_info)

        return ScheduledTaskOutput(
            success=True,
            task_id=task_id,
            message=f"Scheduled task created: {task_id}",
        )

    async def _cancel_task(self, input_data: ScheduledTaskInput) -> ScheduledTaskOutput:
        """Cancel a scheduled task.

        Args:
            input_data: Operation parameters.

        Returns:
            ScheduledTaskOutput: Result.
        """
        if not input_data.task_id:
            raise ToolError("task_id is required")

        if input_data.task_id not in self._tasks:
            raise ToolError(f"Task not found: {input_data.task_id}")

        # Stop scheduler
        if input_data.task_id in self._running_tasks:
            self._running_tasks[input_data.task_id].cancel()
            del self._running_tasks[input_data.task_id]

        del self._tasks[input_data.task_id]

        return ScheduledTaskOutput(
            success=True,
            message=f"Task cancelled: {input_data.task_id}",
        )

    async def _list_tasks(self) -> ScheduledTaskOutput:
        """List all scheduled tasks.

        Returns:
            ScheduledTaskOutput: Task list.
        """
        return ScheduledTaskOutput(
            success=True,
            tasks=list(self._tasks.values()),
        )

    async def _run_task(self, input_data: ScheduledTaskInput) -> ScheduledTaskOutput:
        """Run a task immediately.

        Args:
            input_data: Operation parameters.

        Returns:
            ScheduledTaskOutput: Result.
        """
        if not input_data.task_id:
            raise ToolError("task_id is required")

        if input_data.task_id not in self._tasks:
            raise ToolError(f"Task not found: {input_data.task_id}")

        task = self._tasks[input_data.task_id]

        import asyncio

        try:
            process = await asyncio.create_subprocess_shell(
                task.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            task.run_count += 1
            task.last_run = datetime.now(timezone.utc)

            return ScheduledTaskOutput(
                success=process.returncode == 0,
                task_id=input_data.task_id,
                message=f"Task executed with return code: {process.returncode}",
            )
        except Exception as e:
            return ScheduledTaskOutput(
                success=False,
                task_id=input_data.task_id,
                message=f"Task execution failed: {e}",
            )

    async def _toggle_task(
        self,
        input_data: ScheduledTaskInput,
        enabled: bool,
    ) -> ScheduledTaskOutput:
        """Enable or disable a task.

        Args:
            input_data: Operation parameters.
            enabled: Enable flag.

        Returns:
            ScheduledTaskOutput: Result.
        """
        if not input_data.task_id:
            raise ToolError("task_id is required")

        if input_data.task_id not in self._tasks:
            raise ToolError(f"Task not found: {input_data.task_id}")

        task = self._tasks[input_data.task_id]
        task.enabled = enabled

        if enabled:
            await self._start_scheduler(task)
        else:
            if input_data.task_id in self._running_tasks:
                self._running_tasks[input_data.task_id].cancel()
                del self._running_tasks[input_data.task_id]

        return ScheduledTaskOutput(
            success=True,
            task_id=input_data.task_id,
            message=f"Task {'enabled' if enabled else 'disabled'}",
        )

    async def _start_scheduler(self, task: ScheduledTaskInfo) -> None:
        """Start scheduler for a task.

        Args:
            task: Task to schedule.
        """
        import asyncio
        from croniter import croniter

        async def scheduler_loop():
            while task.enabled:
                now = datetime.now(timezone.utc)
                cron = croniter(task.cron_expression, now)
                next_run = cron.get_next(datetime)
                wait_seconds = (next_run - now).total_seconds()

                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)

                if task.enabled:
                    # Run task
                    asyncio.create_task(self._run_task(
                        ScheduledTaskInput(operation="run", task_id=task.task_id)
                    ))

        # Start in background
        import uuid
        task_handle = asyncio.create_task(scheduler_loop())
        self._running_tasks[task.task_id] = task_handle
