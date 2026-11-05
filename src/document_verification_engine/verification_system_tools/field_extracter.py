import re

from document_verification_engine.verification_system_tools.extracter_tools import  extract_default
from document_verification_engine.verification_system_tools.schemas import ExtractedField




def get_field(request):


     default_keys = []
     

     for key , value in request.items():

          if key == "extract":
               for k , v in value.items():
                    if k == "default":

                         default_keys = [item for item in v]
                    """
                    if k == "custom_keys":
                         custom_keys = v 
                    """
     return default_keys  


def extract(text , request):
     default_keys = get_field(request)

     fields = {}

     if default_keys:
          for key in default_keys:
               fields[key] = extract_default(key , text= text)
     return fields 


"""
if custom_keys:
    for key , pattern in custom_keys.items():
        fields[key] = extract_key_pattern(key , pattern , text= text) 
"""


            





def build_extractedfield_object(text , request)-> dict:


    extracted = extract(text , request )
    fields = {}
    for k , v in extracted.items():
            fields[k] = ExtractedField(name= k , value= v , confidence=None)
    #print(list)
    return fields  

def extract_fields(text , request)->dict:
     



     



     fields = build_extractedfield_object(text , request)
     return  fields 

        



















