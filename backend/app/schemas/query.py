"""Pydantic schemas for natural language query processing and API contracts."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class Condition(BaseModel):
    """Represents a single filter condition in the Intermediate Representation."""

    column: str = Field(..., description="Target database column")
    operator: str = Field(..., description="Comparison operator (e.g. =, >, <)")
    value: Any = Field(..., description="Filter threshold or literal value")


class IntermediateRepresentation(BaseModel):
    """Structured intermediate representation (IR) representing parsed user intent."""

    intent: str = Field(..., description="Query intent (e.g., FILTER, SELECT_ALL, SORT)")
    table: str = Field(..., description="Target table name")
    columns: List[str] = Field(..., description="Columns to project in the result set")
    conditions: List[Condition] = Field(
        default_factory=list, description="Filter conditions"
    )
    order_by: Optional[str] = Field(
        default=None, description="Optional sorting clause"
    )
    limit: Optional[int] = Field(
        default=None, description="Optional limit clause"
    )


class ExecutionResult(BaseModel):
    """Execution metadata and tabular results (mock or real PostgreSQL execution)."""

    status: str = Field(
        default="mock_success",
        description="Execution status code (mock_success or database_success)",
    )
    columns: List[str] = Field(
        default_factory=list, description="Result column header names"
    )
    rows: List[List[Any]] = Field(
        default_factory=list, description="Result row records matching the columns"
    )
    row_count: int = Field(
        default=0, description="Total number of returned records"
    )
    execution_time_ms: int = Field(
        default=0, description="Execution latency in milliseconds"
    )
    error: Optional[str] = Field(
        default=None, description="Execution error detail if query failed"
    )


class QueryRequest(BaseModel):
    """Incoming user request containing natural language query string."""

    query: str = Field(
        ...,
        description="Natural language database query string",
        examples=["Show students with CGPA above 8.5"],
    )
    execution_mode: Optional[str] = Field(
        default=None,
        description="Optional execution mode override: 'mock' or 'database'. Defaults to QUERYMIND_MODE.",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        """Validate and sanitize user query string."""
        if not isinstance(value, str):
            raise ValueError("Query must be a string.")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Query cannot be empty or contain only whitespace.")
        if len(trimmed) > 500:
            raise ValueError(
                f"Query exceeds maximum allowed length of 500 characters (received {len(trimmed)})."
            )
        return trimmed

    @field_validator("execution_mode")
    @classmethod
    def validate_mode(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional execution mode parameter."""
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in ("mock", "database"):
            raise ValueError("execution_mode must be either 'mock' or 'database'.")
        return normalized


class QueryResponse(BaseModel):
    """Full end-to-end response payload returned to the frontend."""

    success: bool = Field(default=True, description="Request success indicator")
    message: str = Field(
        default="Query processed successfully",
        description="Human-readable processing message",
    )
    original_query: str = Field(
        ..., description="Sanitized original natural language input"
    )
    intent: str = Field(..., description="Detected query intent")
    ir: IntermediateRepresentation = Field(
        ..., description="Intermediate Representation (IR) structure"
    )
    generated_sql: str = Field(
        ..., description="Generated ANSI/PostgreSQL query string"
    )
    execution: ExecutionResult = Field(
        ..., description="Tabular results and execution metadata"
    )
