from document_verification_engine.verification_system_tools.field_extracter import extract_fields
import json 

text = """Test Test Test

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


print(extract_fields(text , request=request))