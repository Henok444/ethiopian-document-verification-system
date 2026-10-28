from src.document_verification.ocr import read_document
from src.document_verification.field_extracter import build_extractedfield_object

from src.document_verification.verification import verify
from src.document_verification.create_verification_request import create_verification_request

from pathlib import Path



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

def verify_request(path , request ):


    docs = process_document(path)
    created_request = create_verification_request(docs , request)


    result = verify(created_request)
    return result 








     
