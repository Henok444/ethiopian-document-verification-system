from dataclasses import dataclass
from typing import Any


@dataclass
class ExtractedField:
    name: str
    value: str | None
    confidence: float | None = None


@dataclass
class VerificationRequest:
    document_type: str
    fields: dict[str, ExtractedField]
    rules: list[dict[str, Any]]


@dataclass
class RuleResult:
    rule_name: str
    status: str
    message: str


@dataclass
class VerificationResult:
    status: str
    rule_results: list[RuleResult]