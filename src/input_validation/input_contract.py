"""
from pydantic import BaseModel , Field 
from typing import Literal




# for the input validation of the request body in the /verify endpoint
class RuleInput(BaseModel):
    name: str = Field(min_length=1)
    field: str = Field(min_length=1)
    check: Literal["required", "pattern"]


class API_Input(BaseModel):
    document_type: str = Field(min_length=1)
    rules: list[RuleInput] = Field(min_length=1)
"""

from typing import Annotated, Literal, Union
from pydantic import BaseModel, ConfigDict, Field


class Base(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown keys


class Extract(Base):
    default: list[Literal["name" , "id"]]
    custom_keyword: list[str] = []
    key_and_pattern: dict[str, str] = {}


class Exist(Base):
    name: str
    field: str
    check: Literal["exist"]


class Pattern(Base):
    name: str
    field: str
    check: Literal["pattern"]
    pattern: str


class ExactMatch(Base):
    name: str
    field: str
    check: Literal["exact_match"]
    exact_match: str


class Comparison(Base):
    name: str
    field: str
    check: Literal["comparison"]
    compare: Literal["find_greater", "find_less", "find_equal"]


Rule = Annotated[
    Union[Exist, Pattern, ExactMatch, Comparison],
    Field(discriminator="check"),
]


class Request(Base):
    document_type: str
    extract: Extract
    rules: list[Rule] = []
    output: dict[str, Literal["default", "all"]]


if __name__ == "__main__":
    data = {
        "document_type": "identity_card",
        "extract": {
            "default": ["name", "id"],
            "custom_keyword": ["region"],
            "key_and_pattern": {"passport": r"[A-Z]{2}\d{6}"},
        },
        "rules": [
            {"name": "name_required", "field": "name", "check": "exist"},
            {"name": "fmt", "field": "passport", "check": "pattern", "pattern": r"[A-Z]{2}\d{6}"},
            {"name": "region", "field": "region", "check": "exact_match", "exact_match": "Addis"},
            {"name": "cmp", "field": "id", "check": "comparison", "compare": "find_greater"},
        ],
        "output": {"name": "default", "region": "all"},
    }
    print(Request.model_validate(data))
    