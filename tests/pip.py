from document_verification_engine.pipeline import verify_request

from pathlib import Path


base = Path(__file__).resolve().parents[1]
a = "id.jpg"
b = "id_2.png"

path = base/ "data" / "test_image" / b


request = {
  "document_type": "identity_card",
  "extract": {
    "default": ["name" , "expiry_date"],
  },
  "rules": [
    { "name": "name_required", "field": "name", "check": "exist" },
    { "name": "expiry_date_required", "field": "expiry_date", "check": "exist" }
  ],

}



print(verify_request(img_path=path , request=request))

