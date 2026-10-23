from src.document_verification.ocr import read_document
from pathlib import Path


base = Path(__file__).resolve().parents[1]

path = base/ "data" / "test_image" / "id.jpg"

text = read_document(path)

print(text)