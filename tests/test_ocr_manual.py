from document_verification_engine.image_extracter_model.ocr_model.ocr import read_document
from pathlib import Path


base = Path(__file__).resolve().parents[1]

path = base/ "data" / "test_image" / "id.jpg"

text = read_document(path)

print(text)