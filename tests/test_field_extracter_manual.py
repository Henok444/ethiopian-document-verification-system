from src.document_verification.field_extracter import build_extractedfield_object


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

print(build_extractedfield_object(text))