
import re
def clean(text)->str:

    cleaned = re.sub(r"\s+" , "" , text).lower()

    return cleaned


def extract_lable_fields(text: str) -> dict:



    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print(lines)


    labels = {
        "ethiopian_date_of_birth": ["የትወልድቀነ" ],
        "ethiopian_date_of_expiry": ["የሚማየበቀበትቀነ" ],
    }

    date_pattern = re.compile(
         r"\d{1,2}/[\u1200-\u137F]+/\d{4}"
    )
    fields = {}
    for field_name, possible_labels in labels.items():
        fields[field_name] = None

        for i, line in enumerate(lines):
            
            if any(label.lower() in clean(line.lower()) for label in possible_labels):
                
                match = date_pattern.search(line)

                if not match:
                    for next_line in lines[i + 1:i + 3]:
                        match = date_pattern.search(next_line)
                        if match:
                            break

                if match:
                    fields[field_name] = match.group()
                break
    print(fields)
    return fields        





















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
ብሔዕዊ FO?"""

print(extract_lable_fields(text))