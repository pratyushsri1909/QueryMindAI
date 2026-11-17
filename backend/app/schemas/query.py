"""Pydantic schemas for natural-language query processing and API contracts."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class Condition(BaseModel):
    column: str
    operator: str
    value: Any


class OrderBy(BaseModel):
    column: str
    direction: str = "ASC"


class IntermediateRepresentation(BaseModel):
    """Canonical IR plus compatibility for the earlier mock IR."""

    intent: str
    table: str
    columns: List[str] = Field(default_factory=list)
    conditions: List[Condition] = Field(default_factory=list)
    joins: List[Dict[str, Any]] = Field(default_factory=list)
    aggregations: List[Dict[str, Any]] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    # The mock engine emits a string; the real engine emits a list of objects.
    order_by: Optional[Union[List[OrderBy], str]] = None
    limit: Optional[int] = None


class ExecutionResult(BaseModel):
    status: str = 'mock_success'
    columns: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: int = 0
    error: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., examples=['Show students with CGPA above 8.5'])
    execution_mode: Optional[str] = None

    @field_validator('query')
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError('Query must be a string.')
        trimmed = value.strip()
        if not trimmed:
            raise ValueError('Query cannot be empty or contain only whitespace.')
        if len(trimmed) > 500:
            raise ValueError(
                f'Query exceeds maximum allowed length of 500 characters (received {len(trimmed)}).'
            )
        return trimmed

    @field_validator('execution_mode')
    @classmethod
    def validate_mode(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in ('mock', 'database'):
            raise ValueError('execution_mode must be either mock or database.')
        return normalized


class QueryResponse(BaseModel):
    success: bool = True
    message: str = 'Query processed successfully'
    original_query: str
    intent: str
    ir: IntermediateRepresentation
    generated_sql: str
    params: Dict[str, Any] = Field(default_factory=dict)
    execution: ExecutionResult
