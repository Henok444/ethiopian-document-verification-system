from src.document_verification_engine.image_extracter_model.ocr_model.ocr import read_document
from document_verification_engine.verification_system_tools.field_extracter import build_extractedfield_object

from document_verification_engine.verification_system_tools.verification import verify
from document_verification_engine.verification_system_tools.create_verification_request import create_verification_request




def process_document(img_path: str )->dict:
     text = read_document(img_path)
     return text
def fields_to_extract(request):


     default_keys = []
     custom_keys = []
     key_and_pattern = {}

     for key , value in request.item():

          if key == "extract":
               for k , v in key.item():
                    if k == "default":

                         default_keys = [item for item in v]
                    if k == "custom_keyword":
                         custom_keys = [item for item in v]
                    if k == "key_and_pattern":
                         key_and_pattern = v 





     


def extract_fields(text , fields_to_extract)->dict:

     fields = build_extractedfield_object(text)
     return {
          "raw_text" : text, 
          "fields": fields
     }



# =---------------main 



def verify_request(path , request ):


    docs = process_document(path)
    created_request = create_verification_request(docs , request)


    result = verify(created_request)
    return result 








     
