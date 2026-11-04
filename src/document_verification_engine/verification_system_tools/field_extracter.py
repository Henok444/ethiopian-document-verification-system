import re

from src.document_verification_engine.verification_system_tools.extracter_tools import extract_birth_date , extract_exiry_dates , extract_national_id  
from document_verification_engine.verification_system_tools.schemas import ExtractedField

def extract_fields(text : str)->dict:
    return{
        "date_of_birth" : extract_birth_date(text), 
        "date_of_expiry" : extract_exiry_dates(text),
        "id" : extract_national_id(text)
    }
def build_extractedfield_object(text)-> dict:


    extracted = extract_fields(text)
    list = []
    for k , v in extracted.items():
            list.append(ExtractedField(name= k , value= str(v) , confidence=None))
    #print(list)
    return list   

        




















