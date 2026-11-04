import json


from fastapi import   HTTPException
from pydantic import ValidationError

from input_validation.input_contract import Request




def validate_request(data , image_file):
    if not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="The second file must be an image.")





    try:
        
        validated_request = Request.model_validate(
            data
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The request field must contain valid JSON.",
        )
    
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    