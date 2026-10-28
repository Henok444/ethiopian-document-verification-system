
import json
import tempfile
from pathlib import Path


from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from src.input_validation.input_validation import validate_request
from src.document_verification.pipeline import verify_request


from typing import Literal
from pydantic import BaseModel, Field


app = FastAPI(
    title="Document Verification API",
    description="Verify uploaded documents using configurable rules.",
    version="0.1.0",
)


@app.post("/verify")

async def verify_document(
    file: UploadFile = File(...) ,
    request : str = Form(...)
):
    

    

    validate_request(request , file)

    request_data = json.loads(request)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "uploaded_image"

            image_path.write_bytes(await file.read())




            result = verify_request(str(image_path) , dict(request_data))

    finally:
        await file.close()
        

    return result

    
    