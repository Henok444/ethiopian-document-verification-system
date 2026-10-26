from src.document_verification.pipeline import process_document

from pathlib import Path


base = Path(__file__).resolve().parents[1]

path = base/ "data" / "test_image" / "id.jpg"

def test_pipeline()->None:
    extracted = process_document(path)
    assert "raw_text" and "fields" in list(extracted.keys())
    assert type(extracted["raw_text"]) == str
    
    
