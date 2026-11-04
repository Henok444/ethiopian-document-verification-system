from document_verification_engine.pipeline import verify_request

from pathlib import Path


base = Path(__file__).resolve().parents[1]

path = base/ "data" / "test_image" / "id.jpg"


request = {
  "document_type": "identity_card",
  "extract": {
    "default": ["name", "id"],
    "custom_keyword": ["region"],
    "key_and_pattern": {
      "passport number": "[A-Z]{2}\\d{6}"
    }
  },
  "rules": [
    { "name": "name_required", "field": "name", "check": "exist" },
    { "name": "passport_format", "field": "passport number", "check": "pattern", "pattern": "[A-Z]{2}\\d{6}" },
    { "name": "region_match", "field": "region", "check": "exact_match", "exact_match": "Addis Ababa" },
    { "name": "id_greater", "field": "id", "check": "comparison", "compare": "find_greater" }
  ],
  "output": {
    "name": "default",
    "region": "all"
  }
}



print(verify_request(img_path=path , request=request))

"""
def test_pipeline()->None:
    extracted = process_document(path)
    assert "raw_text" and "fields" in list(extracted.keys())
    assert type(extracted["raw_text"]) == str
    
"""
