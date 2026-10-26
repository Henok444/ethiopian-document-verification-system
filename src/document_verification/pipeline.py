from src.document_verification.ocr import read_document
from src.document_verification.field_extracter import build_extractedfield_object



def process_document(img_path: str)->dict:
     text = read_document(img_path)
     fields = build_extractedfield_object(text)
     return {
          "raw_text" : text, 
          "fields": fields
     }

