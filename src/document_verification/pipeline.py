from src.document_verification.ocr import read_document
from src.document_verification.field_extracter import build_extractedfield_object

from src.document_verification.verification import verify
from src.document_verification.create_verification_request import create_verification_request

from pathlib import Path

"""class VerificationRequest:
    document_type: str
    fields: dict[str, ExtractedField]
    rules: list[dict[str, Any]]"""

"""

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

"""

BASE = Path(__file__).resolve().parents[2]

image_path = BASE / "data" / "test_image" / "id.jpg"
config_path = BASE / "config" / "config.yaml"




def process_document(img_path: str)->dict:
     text = read_document(img_path)
     fields = build_extractedfield_object(text)
     return {
          "raw_text" : text, 
          "fields": fields
     }

docs = process_document(image_path)
request = create_verification_request(docs , config_path)
print(request)

result = verify(request)




print(result)






     
