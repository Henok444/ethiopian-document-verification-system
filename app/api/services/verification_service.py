import json
import tempfile
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.api.schemas.verification import (
    VerificationResponse,
    BatchItemResponse,
    BatchVerificationResponse,
)
from src.input_validation.input_contract import Request as VerificationConfigRequest
from src.document_verification_engine.pipeline import verify_request


class VerificationService:
    @staticmethod
    def parse_and_validate_config(config_bytes: bytes) -> dict:
        """Parses raw JSON bytes and validates against the Pydantic schema."""
        try:
            raw_data = json.loads(config_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON configuration file: {exc}",
            )

        # Validate structure with Pydantic
        try:
            validated = VerificationConfigRequest.model_validate(raw_data)
            return validated.model_dump()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Configuration schema validation failed: {exc}",
            )

    @staticmethod
    def validate_image_metadata(image_file: UploadFile):
        """Ensures the uploaded file is a valid image type."""
        if image_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid file type '{image_file.content_type}'. "
                    f"Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
                ),
            )

    def process_single_document(
        self, image_bytes: bytes, filename: str, config_dict: dict
    ) -> VerificationResponse:
        """Saves image bytes safely to a temp file, runs the engine, and formats the response."""
        suffix = Path(filename).suffix or ".png"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as temp_img:
            temp_img.write(image_bytes)
            temp_img.flush()

            # Synchronous heavy OCR engine execution
            engine_result = verify_request(
                img_path=temp_img.name,
                request=config_dict,
            )

            return VerificationResponse.from_engine_result(engine_result)

    async def verify_single(
        self, json_file: UploadFile, image_file: UploadFile
    ) -> VerificationResponse:
        """Orchestrates single-document verification with non-blocking execution."""
        self.validate_image_metadata(image_file)

        config_bytes = await json_file.read()
        config_dict = self.parse_and_validate_config(config_bytes)

        image_bytes = await image_file.read()
        
        # Offload CPU-heavy OCR to threadpool so the async event loop stays responsive
        return await run_in_threadpool(
            self.process_single_document,
            image_bytes=image_bytes,
            filename=image_file.filename or "uploaded_image.png",
            config_dict=config_dict,
        )

    async def verify_batch(
        self, json_file: UploadFile, image_files: list[UploadFile]
    ) -> BatchVerificationResponse:
        """Orchestrates batch verification across multiple document images."""
        config_bytes = await json_file.read()
        config_dict = self.parse_and_validate_config(config_bytes)

        batch_results: list[BatchItemResponse] = []

        for img in image_files:
            fname = img.filename or "unknown_image.png"
            try:
                self.validate_image_metadata(img)
                image_bytes = await img.read()
                doc_result = await run_in_threadpool(
                    self.process_single_document,
                    image_bytes=image_bytes,
                    filename=fname,
                    config_dict=config_dict,
                )
                batch_results.append(
                    BatchItemResponse(filename=fname, result=doc_result)
                )
            except Exception as exc:
                batch_results.append(
                    BatchItemResponse(filename=fname, error=str(exc))
                )

        return BatchVerificationResponse(
            total_documents=len(image_files),
            results=batch_results,
        )
