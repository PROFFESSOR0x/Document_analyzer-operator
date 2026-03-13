"""Data processing tools for database operations and ETL."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from datetime import datetime, timezone
import logging
import json

from app.tools.base import BaseTool, ToolMetadata, ToolCategory, ToolError


# ========== Database Query Tool ==========

class DatabaseQueryInput(BaseModel):
    """Database query input model."""

    query: str = Field(..., description="SQL query to execute")
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")
    fetch_size: int = Field(default=100, ge=1, le=10000, description="Number of rows to fetch")
    timeout_seconds: float = Field(default=30.0, description="Query timeout")


class DatabaseQueryOutput(BaseModel):
    """Database query output model."""

    success: bool
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class DatabaseQueryTool(BaseTool[DatabaseQueryInput, DatabaseQueryOutput]):
    """Tool for executing SQL queries."""

    metadata = ToolMetadata(
        name="database_query",
        description="Execute SQL queries against databases",
        category=ToolCategory.DATA,
        version="1.0.0",
        tags=["database", "sql", "query", "data"],
        requires_auth=True,
        rate_limit_per_minute=60,
        timeout_seconds=120.0,
    )

    InputModel = DatabaseQueryInput
    OutputModel = DatabaseQueryOutput

    # Blocked SQL patterns for security
    BLOCKED_PATTERNS = [
        r"\bDROP\s+TABLE\b",
        r"\bTRUNCATE\b",
        r"\bDELETE\s+FROM\s+\w+\s*;?\s*--",
        r"\bUPDATE\s+\w+\s+SET.*;.*--",
        r"\bALTER\s+\w+\s+DROP\b",
        r"\bCREATE\s+USER\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
    ]

    async def _execute(self, input_data: DatabaseQueryInput) -> DatabaseQueryOutput:
        """Execute database query.

        Args:
            input_data: Query parameters.

        Returns:
            DatabaseQueryOutput: Query result.
        """
        # Validate query for safety
        self._validate_query(input_data.query)

        start_time = datetime.now(timezone.utc)

        try:
            from sqlalchemy.ext.asyncio import create_async_engine
            from sqlalchemy import text
        except ImportError:
            raise ToolError("SQLAlchemy not installed")

        db_url = input_data.database_url
        if not db_url:
            raise ToolError("database_url is required")

        engine = create_async_engine(db_url, echo=False)

        try:
            async with engine.connect() as connection:
                # Set timeout
                await connection.execute(text(f"SET statement_timeout = {int(input_data.timeout_seconds * 1000)}"))

                # Execute query
                result = await connection.execute(
                    text(input_data.query),
                    input_data.parameters or {},
                )

                # Fetch results
                if result.returns_rows:
                    rows = result.fetchmany(input_data.fetch_size)
                    columns = list(result.keys())
                    row_data = [dict(zip(columns, row)) for row in rows]
                else:
                    columns = []
                    row_data = []

                await connection.commit()

                execution_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

                return DatabaseQueryOutput(
                    success=True,
                    columns=columns,
                    rows=row_data,
                    row_count=len(row_data),
                    execution_time_ms=execution_time_ms,
                )

        except Exception as e:
            execution_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return DatabaseQueryOutput(
                success=False,
                error=str(e),
                execution_time_ms=execution_time_ms,
            )
        finally:
            await engine.dispose()

    def _validate_query(self, query: str) -> None:
        """Validate SQL query for safety.

        Args:
            query: SQL query to validate.

        Raises:
            ToolError: If query is dangerous.
        """
        import re

        query_upper = query.upper()

        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query_upper):
                raise ToolError(f"Query blocked for safety: {pattern}")


# ========== Data Validation Tool ==========

class DataValidationInput(BaseModel):
    """Data validation input model."""

    data: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Data to validate")
    schema: Dict[str, Any] = Field(..., description="Validation schema")
    strict: bool = Field(default=False, description="Strict validation mode")


class ValidationError(BaseModel):
    """Validation error details."""

    field: str
    error: str
    value: Any


class DataValidationOutput(BaseModel):
    """Data validation output model."""

    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    error_count: int = 0
    warnings: List[str] = Field(default_factory=list)


class DataValidationTool(BaseTool[DataValidationInput, DataValidationOutput]):
    """Tool for validating data against schemas."""

    metadata = ToolMetadata(
        name="data_validator",
        description="Validate data against JSON schemas",
        category=ToolCategory.DATA,
        version="1.0.0",
        tags=["validation", "schema", "data", "quality"],
        timeout_seconds=30.0,
    )

    InputModel = DataValidationInput
    OutputModel = DataValidationOutput

    async def _execute(self, input_data: DataValidationInput) -> DataValidationOutput:
        """Validate data.

        Args:
            input_data: Validation parameters.

        Returns:
            DataValidationOutput: Validation result.
        """
        try:
            from jsonschema import validate, ValidationError as JsonSchemaError, Draft7Validator
        except ImportError:
            raise ToolError("jsonschema library not installed")

        data = input_data.data
        schema = input_data.schema

        # Handle list of records
        if isinstance(data, list):
            all_errors = []
            for idx, record in enumerate(data):
                errors = self._validate_record(record, schema, idx)
                all_errors.extend(errors)

            return DataValidationOutput(
                valid=len(all_errors) == 0,
                errors=all_errors,
                error_count=len(all_errors),
            )
        else:
            errors = self._validate_record(data, schema)
            return DataValidationOutput(
                valid=len(errors) == 0,
                errors=errors,
                error_count=len(errors),
            )

    def _validate_record(
        self,
        record: Dict[str, Any],
        schema: Dict[str, Any],
        index: Optional[int] = None,
    ) -> List[ValidationError]:
        """Validate a single record.

        Args:
            record: Data record.
            schema: Validation schema.
            index: Optional record index.

        Returns:
            List[ValidationError]: Validation errors.
        """
        errors = []

        try:
            validate(instance=record, schema=schema)
        except JsonSchemaError as e:
            field_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            if index is not None:
                field_path = f"[{index}].{field_path}"

            errors.append(
                ValidationError(
                    field=field_path,
                    error=e.message,
                    value=e.instance,
                )
            )

        # Additional type checking
        for field, rules in schema.get("properties", {}).items():
            if field in record:
                value = record[field]
                expected_type = rules.get("type")

                if expected_type and not self._check_type(value, expected_type):
                    errors.append(
                        ValidationError(
                            field=field,
                            error=f"Expected type {expected_type}, got {type(value).__name__}",
                            value=value,
                        )
                    )

                # Check constraints
                if expected_type == "string":
                    if "minLength" in rules and len(value) < rules["minLength"]:
                        errors.append(
                            ValidationError(
                                field=field,
                                error=f"String length {len(value)} < minLength {rules['minLength']}",
                                value=value,
                            )
                        )
                    if "maxLength" in rules and len(value) > rules["maxLength"]:
                        errors.append(
                            ValidationError(
                                field=field,
                                error=f"String length {len(value)} > maxLength {rules['maxLength']}",
                                value=value,
                            )
                        )
                    if "pattern" in rules:
                        import re
                        if not re.match(rules["pattern"], value):
                            errors.append(
                                ValidationError(
                                    field=field,
                                    error=f"Value does not match pattern {rules['pattern']}",
                                    value=value,
                                )
                            )

                # Numeric constraints
                if expected_type in ["number", "integer"]:
                    if "minimum" in rules and value < rules["minimum"]:
                        errors.append(
                            ValidationError(
                                field=field,
                                error=f"Value {value} < minimum {rules['minimum']}",
                                value=value,
                            )
                        )
                    if "maximum" in rules and value > rules["maximum"]:
                        errors.append(
                            ValidationError(
                                field=field,
                                error=f"Value {value} > maximum {rules['maximum']}",
                                value=value,
                            )
                        )

        return errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type.

        Args:
            value: Value to check.
            expected_type: Expected type.

        Returns:
            bool: True if type matches.
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected = type_map.get(expected_type)
        if not expected:
            return True

        return isinstance(value, expected)


# ========== Data Transformation Tool ==========

class DataTransformationInput(BaseModel):
    """Data transformation input model."""

    data: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Input data")
    operations: List[Dict[str, Any]] = Field(..., description="Transformation operations")


class DataTransformationOutput(BaseModel):
    """Data transformation output model."""

    success: bool
    data: Any
    operations_applied: int = 0
    error: Optional[str] = None


class DataTransformationTool(BaseTool[DataTransformationInput, DataTransformationOutput]):
    """Tool for ETL data transformations."""

    metadata = ToolMetadata(
        name="data_transformer",
        description="Transform data using ETL operations",
        category=ToolCategory.DATA,
        version="1.0.0",
        tags=["etl", "transformation", "data", "processing"],
        timeout_seconds=60.0,
    )

    InputModel = DataTransformationInput
    OutputModel = DataTransformationOutput

    async def _execute(self, input_data: DataTransformationInput) -> DataTransformationOutput:
        """Transform data.

        Args:
            input_data: Transformation parameters.

        Returns:
            DataTransformationOutput: Transformed data.
        """
        data = input_data.data
        operations = input_data.operations

        try:
            operations_applied = 0

            for op in operations:
                op_type = op.get("type")
                op_params = op.get("params", {})

                if op_type == "filter":
                    data = self._apply_filter(data, op_params)
                elif op_type == "map":
                    data = self._apply_map(data, op_params)
                elif op_type == "select":
                    data = self._apply_select(data, op_params)
                elif op_type == "rename":
                    data = self._apply_rename(data, op_params)
                elif op_type == "sort":
                    data = self._apply_sort(data, op_params)
                elif op_type == "group_by":
                    data = self._apply_group_by(data, op_params)
                elif op_type == "aggregate":
                    data = self._apply_aggregate(data, op_params)
                elif op_type == "flatten":
                    data = self._apply_flatten(data, op_params)
                else:
                    raise ToolError(f"Unknown operation type: {op_type}")

                operations_applied += 1

            return DataTransformationOutput(
                success=True,
                data=data,
                operations_applied=operations_applied,
            )

        except Exception as e:
            return DataTransformationOutput(
                success=False,
                data=data,
                error=str(e),
            )

    def _apply_filter(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply filter operation.

        Args:
            data: Input data.
            params: Filter parameters.

        Returns:
            Filtered data.
        """
        if not isinstance(data, list):
            return data

        field = params.get("field")
        condition = params.get("condition", "eq")
        value = params.get("value")

        def matches(record_value: Any) -> bool:
            if condition == "eq":
                return record_value == value
            elif condition == "ne":
                return record_value != value
            elif condition == "gt":
                return record_value > value
            elif condition == "gte":
                return record_value >= value
            elif condition == "lt":
                return record_value < value
            elif condition == "lte":
                return record_value <= value
            elif condition == "in":
                return record_value in value
            elif condition == "contains":
                return value in str(record_value)
            elif condition == "exists":
                return record_value is not None
            return True

        return [record for record in data if matches(record.get(field))]

    def _apply_map(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply map operation.

        Args:
            data: Input data.
            params: Map parameters.

        Returns:
            Mapped data.
        """
        if not isinstance(data, list):
            return data

        transformations = params.get("transformations", {})

        result = []
        for record in data:
            new_record = dict(record)
            for field, transform in transformations.items():
                if transform == "uppercase":
                    new_record[field] = str(new_record.get(field, "")).upper()
                elif transform == "lowercase":
                    new_record[field] = str(new_record.get(field, "")).lower()
                elif transform == "strip":
                    new_record[field] = str(new_record.get(field, "")).strip()
                elif transform == "int":
                    new_record[field] = int(new_record.get(field, 0))
                elif transform == "float":
                    new_record[field] = float(new_record.get(field, 0.0))
                elif transform == "string":
                    new_record[field] = str(new_record.get(field, ""))
            result.append(new_record)

        return result

    def _apply_select(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply select operation.

        Args:
            data: Input data.
            params: Select parameters.

        Returns:
            Selected data.
        """
        if not isinstance(data, list):
            return data

        fields = params.get("fields", [])

        return [{f: record.get(f) for f in fields if f in record} for record in data]

    def _apply_rename(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply rename operation.

        Args:
            data: Input data.
            params: Rename parameters.

        Returns:
            Renamed data.
        """
        if not isinstance(data, list):
            return data

        mappings = params.get("mappings", {})

        result = []
        for record in data:
            new_record = {}
            for key, value in record.items():
                new_key = mappings.get(key, key)
                new_record[new_key] = value
            result.append(new_record)

        return result

    def _apply_sort(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply sort operation.

        Args:
            data: Input data.
            params: Sort parameters.

        Returns:
            Sorted data.
        """
        if not isinstance(data, list):
            return data

        field = params.get("field")
        reverse = params.get("reverse", False)

        return sorted(data, key=lambda x: x.get(field, ""), reverse=reverse)

    def _apply_group_by(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply group by operation.

        Args:
            data: Input data.
            params: Group by parameters.

        Returns:
            Grouped data.
        """
        if not isinstance(data, list):
            return data

        field = params.get("field")

        groups = {}
        for record in data:
            key = record.get(field)
            if key not in groups:
                groups[key] = []
            groups[key].append(record)

        return [{"key": k, "items": v} for k, v in groups.items()]

    def _apply_aggregate(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply aggregate operation.

        Args:
            data: Input data.
            params: Aggregate parameters.

        Returns:
            Aggregated data.
        """
        if not isinstance(data, list):
            return data

        field = params.get("field")
        function = params.get("function", "count")

        values = [record.get(field) for record in data if record.get(field) is not None]

        if function == "count":
            return {"count": len(values)}
        elif function == "sum":
            return {"sum": sum(values)}
        elif function == "avg":
            return {"avg": sum(values) / len(values) if values else 0}
        elif function == "min":
            return {"min": min(values) if values else None}
        elif function == "max":
            return {"max": max(values) if values else None}

        return {}

    def _apply_flatten(self, data: Any, params: Dict[str, Any]) -> Any:
        """Apply flatten operation.

        Args:
            data: Input data.
            params: Flatten parameters.

        Returns:
            Flattened data.
        """
        if not isinstance(data, list):
            return data

        field = params.get("field")

        result = []
        for record in data:
            nested = record.get(field, [])
            if isinstance(nested, list):
                for item in nested:
                    new_record = {k: v for k, v in record.items() if k != field}
                    new_record[field] = item
                    result.append(new_record)
            else:
                result.append(record)

        return result


# ========== CSV/Excel Tool ==========

class CSVExcelInput(BaseModel):
    """CSV/Excel input model."""

    operation: str = Field(..., description="Operation (read, write, merge, transform)")
    file_path: str = Field(..., description="File path")
    file_type: str = Field(default="csv", description="File type (csv, xlsx)")
    sheet_name: Optional[str] = Field(default=None, description="Sheet name for Excel")
    delimiter: str = Field(default=",", description="CSV delimiter")
    encoding: str = Field(default="utf-8", description="File encoding")
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Data for write operation")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional options")


class CSVExcelOutput(BaseModel):
    """CSV/Excel output model."""

    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    columns: List[str] = Field(default_factory=list)
    file_path: Optional[str] = None
    error: Optional[str] = None


class CSVExcelTool(BaseTool[CSVExcelInput, CSVExcelOutput]):
    """Tool for CSV and Excel file operations."""

    metadata = ToolMetadata(
        name="csv_excel",
        description="Read, write, and process CSV/Excel files",
        category=ToolCategory.DATA,
        version="1.0.0",
        tags=["csv", "excel", "spreadsheet", "data"],
        timeout_seconds=120.0,
    )

    InputModel = CSVExcelInput
    OutputModel = CSVExcelOutput

    async def _execute(self, input_data: CSVExcelInput) -> CSVExcelOutput:
        """Execute CSV/Excel operation.

        Args:
            input_data: Operation parameters.

        Returns:
            CSVExcelOutput: Operation result.
        """
        operation = input_data.operation.lower()

        if operation == "read":
            return await self._read_file(input_data)
        elif operation == "write":
            return await self._write_file(input_data)
        elif operation == "merge":
            return await self._merge_files(input_data)
        elif operation == "transform":
            return await self._transform_file(input_data)
        else:
            raise ToolError(f"Unsupported operation: {operation}")

    async def _read_file(self, input_data: CSVExcelInput) -> CSVExcelOutput:
        """Read CSV/Excel file.

        Args:
            input_data: Operation parameters.

        Returns:
            CSVExcelOutput: File data.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ToolError("pandas not installed")

        file_path = Path(input_data.file_path)
        if not file_path.exists():
            raise ToolError(f"File not found: {input_data.file_path}")

        try:
            if input_data.file_type == "csv":
                df = pd.read_csv(
                    file_path,
                    delimiter=input_data.delimiter,
                    encoding=input_data.encoding,
                )
            elif input_data.file_type == "xlsx":
                df = pd.read_excel(
                    file_path,
                    sheet_name=input_data.sheet_name or 0,
                )
            else:
                raise ToolError(f"Unsupported file type: {input_data.file_type}")

            data = df.to_dict(orient="records")

            return CSVExcelOutput(
                success=True,
                data=data,
                row_count=len(data),
                columns=list(df.columns),
            )

        except Exception as e:
            return CSVExcelOutput(
                success=False,
                error=str(e),
            )

    async def _write_file(self, input_data: CSVExcelInput) -> CSVExcelOutput:
        """Write CSV/Excel file.

        Args:
            input_data: Operation parameters.

        Returns:
            CSVExcelOutput: Write result.
        """
        if not input_data.data:
            raise ToolError("data is required for write operation")

        try:
            import pandas as pd
        except ImportError:
            raise ToolError("pandas not installed")

        df = pd.DataFrame(input_data.data)
        file_path = Path(input_data.file_path)

        try:
            if input_data.file_type == "csv":
                df.to_csv(
                    file_path,
                    index=False,
                    sep=input_data.delimiter,
                    encoding=input_data.encoding,
                )
            elif input_data.file_type == "xlsx":
                df.to_excel(
                    file_path,
                    sheet_name=input_data.sheet_name or "Sheet1",
                    index=False,
                )
            else:
                raise ToolError(f"Unsupported file type: {input_data.file_type}")

            return CSVExcelOutput(
                success=True,
                row_count=len(df),
                columns=list(df.columns),
                file_path=str(file_path),
            )

        except Exception as e:
            return CSVExcelOutput(
                success=False,
                error=str(e),
            )

    async def _merge_files(self, input_data: CSVExcelInput) -> CSVExcelOutput:
        """Merge multiple CSV/Excel files.

        Args:
            input_data: Operation parameters.

        Returns:
            CSVExcelOutput: Merged data.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ToolError("pandas not installed")

        options = input_data.options or {}
        file_paths = options.get("file_paths", [])

        if not file_paths:
            raise ToolError("file_paths is required in options")

        dfs = []
        for fp in file_paths:
            path = Path(fp)
            if not path.exists():
                continue

            if input_data.file_type == "csv":
                df = pd.read_csv(path, delimiter=input_data.delimiter)
            elif input_data.file_type == "xlsx":
                df = pd.read_excel(path)
            else:
                continue

            dfs.append(df)

        if not dfs:
            raise ToolError("No valid files to merge")

        merged_df = pd.concat(dfs, ignore_index=True)
        data = merged_df.to_dict(orient="records")

        return CSVExcelOutput(
            success=True,
            data=data,
            row_count=len(data),
            columns=list(merged_df.columns),
        )

    async def _transform_file(self, input_data: CSVExcelInput) -> CSVExcelOutput:
        """Transform CSV/Excel file.

        Args:
            input_data: Operation parameters.

        Returns:
            CSVExcelOutput: Transformed data.
        """
        # First read the file
        read_result = await self._read_file(input_data)

        if not read_result.success or not read_result.data:
            return read_result

        # Apply transformations from options
        options = input_data.options or {}
        transformations = options.get("transformations", [])

        data = read_result.data

        for transform in transformations:
            op_type = transform.get("type")
            params = transform.get("params", {})

            if op_type == "filter_nulls":
                field = params.get("field")
                data = [r for r in data if r.get(field) is not None]
            elif op_type == "deduplicate":
                field = params.get("field")
                seen = set()
                unique_data = []
                for record in data:
                    key = record.get(field)
                    if key not in seen:
                        seen.add(key)
                        unique_data.append(record)
                data = unique_data
            elif op_type == "add_column":
                field = params.get("field")
                value = params.get("value")
                for record in data:
                    record[field] = value

        return CSVExcelOutput(
            success=True,
            data=data,
            row_count=len(data),
            columns=list(data[0].keys()) if data else [],
        )
