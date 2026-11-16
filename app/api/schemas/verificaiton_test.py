from typing import Literal
from pydantic import BaseModel, Field

# Re-export or import the request contract if needed
from src.input_validation.input_contract import Request as VerificationConfigRequest


class RuleResultResponse(BaseModel):
    rule_name: str = Field(..., description="Identifier name of the rule that was evaluated")
    status: Literal["passed", "failed", "needs_review"] = Field(
        ..., description="Result of evaluating this rule"
    )
    message: str = Field(..., description="Expfrom typing import Literal
from pydantic import BaseModel, Field

# Re-export or import the request contract if needed
from src.input_validation.input_contract import Request as VerificationConfigRequest


class RuleResultResponse(BaseModel):
    rule_name: str = Field(..., description="Identifier name of the rule that was evaluated")
    status: Literal["passed", "failed", "needs_review"] = Field(
        ..., description="Result of evaluating this rule"
    )
    message: str = Field(..., description="Explanation of the evaluation result")
    found: str | None = Field(
        default=None, description="The extracted value that was matched or evaluated"
    )


class VerificationResponse(BaseModel):
    status: Literal["passed", "failed", "needs_review"] = Field(
        ..., description="Overall verification status of the document"
    )
    rule_results: list[RuleResultResponse] = Field(
        default_factory=list, description="Detailed list of results for each rule"
    )

    @classmethod
    def from_engine_result(cls, result) -> "VerificationResponse":
        """Helper to safely convert the internal dataclass into a Pydantic response."""
        return cls(
            status=result.status,
            rule_results=[
                RuleResultResponse(
                    rule_name=r.rule_name,
                    status=r.status,
                    message=r.message,
                    found=getattr(r, "found", None),
                )
                for r in result.rule_results
            ],
        )


class BatchItemResponse(BaseModel):
    filename: str
    result: VerificationResponse | None = None
    error: str | None = None


class BatchVerificationResponse(BaseModel):
    total_documents: int
    results: list[BatchItemResponse]lanation of the evaluation result")
    found: str | None = Field(
        default=None, description="The extracted value that was matched or evaluated"
    )


class VerificationResponse(BaseModel):
    status: Literal["passed", "failed", "needs_review"] = Field(
        ..., description="Overall verification status of the document"
    )
    rule_results: list[RuleResultResponse] = Field(
        default_factory=list, description="Detailed list of results for each rule"
    )

    @classmethod
    def from_engine_result(cls, result) -> "VerificationResponse":
        """Helper to safely convert the internal dataclass into a Pydantic response."""
        return cls(
            status=result.status,
            rule_results=[
                RuleResultResponse(
                    rule_name=r.rule_name,
                    status=r.status,
                    message=r.message,
                    found=getattr(r, "found", None),
                )
                for r in result.rule_results
            ],
        )


class BatchItemResponse(BaseModel):
    filename: str
    result: VerificationResponse | None = None
    error: str | None = None


class BatchVerificationResponse(BaseModel):
    total_documents: int
    results: list[BatchItemResponse]