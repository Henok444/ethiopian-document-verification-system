from src.document_verification.schemas import (
    ExtractedField,
    VerificationRequest,
)
from src.document_verification.verification import verify


def test_valid_document():
    request = VerificationRequest(
        document_type="identity_card",
        fields={
            "full_name_object": ExtractedField("full_name", "ሀና ተስፋዬ"),
            "id_number_object": ExtractedField("id_number", "AB123456"),
        },
        rules=[
            {
                "name": "name_required",
                "field": "full_name_object",
                "check": "required",
            },
            {
                "name": "id_format",
                "field": "id_number_object",
                "check": "pattern",
                "pattern": r"[A-Z]{2}\d{6}",
            },
        ],
    )

    result = verify(request)

    assert result.status == "passed"

def test_invalid_document():
    request = VerificationRequest(
        document_type="identity_card",
        fields={
            "full_name": ExtractedField("full_name", "ሀና ተስፋዬ"),
            "id_number": ExtractedField("id_number", "AB123456"),
        },
        rules=[
            {
                "name": "name_required",
                "field": "full_name",
                "check": "requir",
            },
            {
                "name": "id_format",
                "field": "id_number",
                "check": "pat",              #===================>>>>>>>>>>>>>>>>>>>>>>>>>.    testing if it can handel bad rules 
                "pattern": r"[A-Z]{2}\d{6}",
            },
        ],
    )

    result = verify(request)

    assert result.status == "needs_review"
def test_bad_confidence():
    request = VerificationRequest(
        document_type="identity_card",
        fields={
            "full_name": ExtractedField("full_name", "ሀና ተስፋዬ" , 0.7 ),
            "id_number": ExtractedField("id_number", "AB123456" , 0.9),
        },
        rules=[
            {
                "name": "name_required",
                "field": "full_name",
                "check": "required",
            },
            {
                "name": "id_format",
                "field": "id_number",
                "check": "pattern",              #===================>>>>>>>>>>>>>>>>>>>>>>>>>.    testing if it can handel bad rules 
                "pattern": r"[A-Z]{2}\d{6}",
            },
        ],
    )

    result = verify(request)

    assert result.status == "needs_review"
def test_good_confidence():
    request = VerificationRequest(
        document_type="identity_card",
        fields={
            "full_name": ExtractedField("full_name", "ሀና ተስፋዬ" , 0.9 ),
            "id_number": ExtractedField("id_number", "AB123456" , 0.9),
        },
        rules=[
            {
                "name": "name_required",
                "field": "full_name",
                "check": "required",
            },
            {
                "name": "id_format",
                "field": "id_number",
                "check": "pattern",              #===================>>>>>>>>>>>>>>>>>>>>>>>>>.    testing if it can handel bad rules 
                "pattern": r"[A-Z]{2}\d{6}",
            },
        ],
    )

    result = verify(request)

    assert result.status == "passed"

