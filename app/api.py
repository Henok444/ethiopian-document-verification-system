
import json
import tempfile
from pathlib import Path


from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from src.input_validation.input_validation import validate_request
from src.prepare_data_for_engine.prepare import load_request  
from src.document_verification_engine.pipeline import verify_request
from src.output_to_send.output import output 


from typing import Literal
from pydantic import BaseModel, Field


app = FastAPI(
    title="Document Verification API",
    description="Verify uploaded documents using configurable rules.",
    version="0.1.0",
)


@app.post("/verify")





 
# 
async def verify_document(
    json_file: UploadFile = File(...),
    image_file: UploadFile = File(...)
):



    data = await load_request(json_file)
    

    # validation 

    validate_request(data  , image_file )

  # Prepare the request data 

    

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "uploaded_image"

            image_path.write_bytes(await image_file.read())

            # engine processing


            result = verify_request(str(image_path) , dict(data))



    finally:
        await image_file.close()

    # output formatting

    output_result = output(result)
        

    return output_result

    
    