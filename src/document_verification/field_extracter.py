import re


from src.document_verification.schemas import ExtractedField

def clean(text)->str:

    cleaned = re.sub(r"\s+" , "" , text).lower()

    return cleaned


def extract_dates(text: str) -> dict:



    lines = [line.strip() for line in text.splitlines() if line.strip()]

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

    return fields        


def extract_national_id(text : str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    lables = {
        "national_id" : ["national1d"]
    }

    field = {}
    id_pattern = re.compile(r"\d{12}")

    for name , possible_lable in lables.items():
        

        for i,  line in enumerate(lines):
            if any(lable in clean(line) for lable in possible_lable ):
                # the id might be in the same line 
                match = id_pattern.search(clean(line))
                
                if match:
                    field[name] = match.group()
                    break
                if not match:
                    for next_line in lines[i+1 : i+4]:
                        match = id_pattern.search(clean(next_line))
 
                    if match:
                        field[name] =  match.group()
                        break
    return field
def extract_fields(text : str)->dict:
    return{
        "dates" : extract_dates(text), 
        "id" : extract_national_id(text)
    }

def build_extractedfield_object(text)-> dict:


    extracted = extract_fields(text)
    list = []
    for k , v in extracted.items():
        try: 
            for k , v2 in v.items():
                list.append(ExtractedField(name= k  , value= str(v2) , confidence=None))
        except Exception as e :
            print(e)
            list.append(ExtractedField(name= k , value= str(v) , confidence=None))
    return list   

        




















