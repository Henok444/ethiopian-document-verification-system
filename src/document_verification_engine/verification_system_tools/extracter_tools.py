import re


def clean(text)->str:

    cleaned = re.sub(r"\s+" , "" , text).lower()

    return cleaned


def extract_birth_date(text: str) -> dict:



    lines = [line.strip() for line in text.splitlines() if line.strip()]

    labels = {
        "ethiopian_date_of_birth": ["የትወልድቀነ" ],

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

    return fields["ethiopian_date_of_birth"]
def extract_expiry_dates(text: str) -> dict:



    lines = [line.strip() for line in text.splitlines() if line.strip()]

    labels = {
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

    return fields["ethiopian_date_of_expiry"]    


import re

def extract_name(text: str) -> str | None:

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    labels = {
        "full_name": ["ሙሉስም", "fullname"],
    }

    # 2 to 4 words, Amharic or English letters only (no digits or symbols)
    name_pattern = re.compile(
        r"[\u1200-\u137FA-Za-z]+(?:\s+[\u1200-\u137FA-Za-z]+){1,3}"
    )

    fields = {}
    for field_name, possible_labels in labels.items():
        fields[field_name] = None

        for i, line in enumerate(lines):

            if any(label.lower() in clean(line.lower()) for label in possible_labels):

                for next_line in lines[i + 1:i + 3]:
                    match = name_pattern.fullmatch(next_line)
                    if match:
                        fields[field_name] = match.group()
                        break
                break

    return fields["full_name"]


def extract_id(text : str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    lables = ["national1d" , "id" , "idnumber"]

    
    id_pattern = re.compile(r"\d{12}")

    for possible_lable in lables:
        

        for i,  line in enumerate(lines):
            if any(lable in clean(line) for lable in possible_lable ):
                # the id might be in the same line 
                match = id_pattern.search(clean(line))
                
                if match:
                    field = match.group()
                    break
                if not match:
                    for next_line in lines[i+1 : i+4]:
                        match = id_pattern.search(clean(next_line))
 
                    if match:
                        field=  match.group()
                        break
                    else: field = None 
    #print(field)
    return field
def extract_key_pattern(key , pattern , text): 


    lines = [line.strip() for line in text.splitlines() if line.strip()]

    labels = [key]

    # 2 to 4 words, Amharic or English letters only (no digits or symbols)
    name_pattern = re.compile(
       pattern 
       )

    fields = {}

    fields[key] = None

    for i, line in enumerate(lines):

        if any(label.lower() in clean(line.lower()) for label in labels):

            for next_line in lines[i + 1:i + 3]:
                match = name_pattern.fullmatch(next_line)
                if match:
                    fields[key] = match.group()
                    break
            break

    return fields[key]



#=====================================================main extracter pipeline==============================    


def extract_default(key , text ):
    value = None
    if key == "name":
        value = extract_name(text)
        pass
    if key == "id":
        value = extract_id(text)
    if key == "birth_date":
        value = extract_birth_date(text)
    if key == "id_expiry_date":
        value == extract_expiry_dates(text)



    return value 


"""
def extract_custom_key(key , pattern , text):
    if pattern == "like_name"

"""