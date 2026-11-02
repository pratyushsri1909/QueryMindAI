"""API routes for natural language query processing."""

import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.query import QueryRequest, QueryResponse
from app.nlp.mock_nlp import process_natural_language
from app.sql_engine.mock_sql_engine import process_ir

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Query Engine"])


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Natural Language Query (Mock Pipeline)",
    description=(
        "Ingests a natural language query, transforms it via mock NLP into an "
        "Intermediate Representation (IR), generates SQL, and returns mock execution results."
    ),
)
def handle_query(request: QueryRequest) -> QueryResponse:
    """End-to-end integration pipeline endpoint for natural language query processing."""
    try:
        # Step 1: Input query is validated by Pydantic QueryRequest
        raw_query = request.query

        # Step 2: Mock NLP module processing
        ir = process_natural_language(raw_query)

        # Step 3: Mock SQL engine processing
        engine_result = process_ir(ir)

        # Step 4: Assemble and validate response against QueryResponse contract
        return QueryResponse(
            success=True,
            message="Query processed successfully",
            original_query=raw_query,
            intent=ir.get("intent", "UNKNOWN"),
            ir=ir,
            generated_sql=engine_result["generated_sql"],
            execution=engine_result["execution"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in query processing pipeline: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred during query processing: {str(exc)}",
        ) from exc

