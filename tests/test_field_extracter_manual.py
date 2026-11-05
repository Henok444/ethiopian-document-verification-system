import json


from document_verification_engine.verification_system_tools.field_extracter import extract_fields
from document_verification_engine.image_extracter_model.ocr_model.ocr import read_document
from pathlib import Path


base = Path(__file__).resolve().parents[1]

path = base/ "data" / "test_image" / "id_2.png"

text_img = read_document(path)


text = """ name 
chaltu mulatu

የትወልድ ቀነ / Date of Birth
06/መስከ/1984
11/Sep/1991

መታወቂየው የሚማየበቀበት ቀነ /Date of Expiry


- 11/መስከ/1991

(OHARO ONLY)
Country:of Citi ip( Self-declared)

@

94, / SEX

National 1D
ብሔዕዊ FO?  123456789123"""



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


request_2 = {
  "document_type": "identity_card",
  "extract": {
    "default": ["name", "id" , "birth_date" , "expiry_date"]
  },
  "rules": [
    { "name": "name_required", "field": "name", "check": "exist" },
    { "name": "birth_date required", "field": "birth_date", "check": "exist"},
    { "name": "expiry_date", "field": "expiry_date", "check": "exist"},
    { "name": "id is required", "field": "id", "check": "exist"}
  ],
  "output": {
    "name": "default",
    "region": "all"
  }
}


print(text_img)

print(extract_fields(text_img , request=request_2))