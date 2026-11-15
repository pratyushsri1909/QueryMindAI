"""
Intermediate Representation (IR) Builder and Validator for QueryMind AI (Member 1 - NLP Engine).
Constructs the structured JSON payload matching the integration contract.
"""

from typing import Dict, Any, List, Optional


class IRValidationError(Exception):
    """Raised when the assembled IR does not adhere to the shared integration schema."""
    pass


class IRBuilder:
    """Builds and validates the Intermediate Representation (IR) JSON dictionary."""

    VALID_INTENTS = {"RETRIEVAL", "FILTER", "COUNT", "AGGREGATION", "SORT"}
    VALID_OPERATORS = {">", "<", ">=", "<=", "=", "!=", "LIKE", "LIKE_PREFIX", "LIKE_SUFFIX"}

    def __init__(self):
        pass

    def build_ir(
        self,
        intent: str,
        table: str,
        columns: List[str],
        conditions: List[Dict[str, Any]],
        order_by: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        aggregation: Optional[Dict[str, str]] = None,
        confidence_score: float = 0.90
    ) -> Dict[str, Any]:
        """
        Assembles and returns a validated Intermediate Representation dictionary.
        """
        ir_dict: Dict[str, Any] = {
            "intent": intent,
            "table": table,
            "columns": columns,
            "conditions": conditions,
            "order_by": order_by,
            "limit": limit
        }

        # Include aggregation if present or if intent is COUNT/AGGREGATION
        if aggregation:
            ir_dict["aggregation"] = aggregation

        # Add metadata
        ir_dict["confidence_score"] = round(confidence_score, 2)

        # Validate before returning
        self.validate(ir_dict)
        return ir_dict

    def validate(self, ir_data: Dict[str, Any]) -> bool:
        """
        Validates schema integrity of the IR dictionary.
        """
        required_keys = ["intent", "table", "columns", "conditions", "order_by", "limit"]
        for key in required_keys:
            if key not in ir_data:
                raise IRValidationError(f"Missing mandatory IR contract key: '{key}'")

        if ir_data["intent"] not in self.VALID_INTENTS:
            raise IRValidationError(f"Invalid intent: {ir_data['intent']}")

        if not isinstance(ir_data["columns"], list):
            raise IRValidationError("Columns must be represented as a list of strings.")

        if not isinstance(ir_data["conditions"], list):
            raise IRValidationError("Conditions must be a list of condition objects.")

        for cond in ir_data["conditions"]:
            if not all(k in cond for k in ("column", "operator", "value")):
                raise IRValidationError(f"Malformed condition item: {cond}")
            if cond["operator"] not in self.VALID_OPERATORS:
                raise IRValidationError(f"Unsupported relational operator: {cond['operator']}")

        if ir_data["order_by"] is not None:
            if not isinstance(ir_data["order_by"], dict) or "column" not in ir_data["order_by"] or "direction" not in ir_data["order_by"]:
                raise IRValidationError("order_by must be a dict with 'column' and 'direction' keys.")
            if ir_data["order_by"]["direction"] not in {"ASC", "DESC"}:
                raise IRValidationError("order_by direction must be 'ASC' or 'DESC'.")

        if ir_data["limit"] is not None and not isinstance(ir_data["limit"], int):
            raise IRValidationError("Limit must be an integer or null.")

        return True
