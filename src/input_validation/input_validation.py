
from typing import Literal
from pydantic import BaseModel, Field
import json


from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import ValidationError


class VerificationRuleInput(BaseModel):
    name: str = Field(min_length=1)
    field: str = Field(min_length=1)
    check: Literal["required", "pattern"]


class VerificationRequestInput(BaseModel):
    document_type: str = Field(min_length=1)
    rules: list[VerificationRuleInput] = Field(min_length=1)

def validate_request(request , file):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")
    try:
        request_data = json.loads(request)
        validated_request = VerificationRequestInput.model_validate(
            request_data
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The request field must contain valid JSON.",
        )
    
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    