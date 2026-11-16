from fastapi import APIRouter, Depends, File, UploadFile
from app.api.schemas.verification import (
    VerificationResponse,
    BatchVerificationResponse,
)
from app.api.services.verification_service import VerificationService

router = APIRouter()


@router.post(
    "/verify",
    response_model=VerificationResponse,
    summary="Verify single identity document",
    description="Accepts a JSON verification rules configuration and a document image.",
)
async def verify_single_document(
    json_file: UploadFile = File(..., description="JSON file containing extraction and rule configs"),
    image_file: UploadFile = File(..., description="Document image to verify (PNG, JPEG)"),
    service: VerificationService = Depends(),
) -> VerificationResponse:
    return await service.verify_single(json_file=json_file, image_file=image_file)


@router.post(
    "/verify_batch",
    response_model=BatchVerificationResponse,
    summary="Verify multiple identity documents in batch",
    description="Accepts a JSON verification rules configuration and a list of document images.",
)
async def verify_batch_documents(
    json_file: UploadFile = File(..., description="JSON file containing extraction and rule configs"),
    image_files: list[UploadFile] = File(..., description="List of document images to verify"),
    service: VerificationService = Depends(),
) -> BatchVerificationResponse:
    return await service.verify_batch(json_file=json_file, image_files=image_files)
