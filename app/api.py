
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





async def process_document(json_data, image_file):

    with tempfile.TemporaryDirectory() as temp_dir:

        image_path = Path(temp_dir) / "uploaded_image"

        image_path.write_bytes(await image_file.read())

        validate_request(json_data, image_file)

        result = verify_request(
            str(image_path),
            dict(json_data)
        )

        return output(result)
    

@app.post("/verify") 
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




@app.post("/verify_batch")
async def verify_batch(
    json_file: UploadFile = File(...),
    image_files: list[UploadFile] = File(...)
):

    data = await load_request(json_file)

    results = []

    for image_file in image_files:

        try:
            result = await process_document(data, image_file)

            results.append({
                "filename": image_file.filename,
                "result": result
            })

        except Exception as exc:

            results.append({
                "filename": image_file.filename,
                "error": str(exc)
            })

        finally:
            await image_file.close()

    await json_file.close()

    return {
        "total_documents": len(image_files),
        "results": results
    }