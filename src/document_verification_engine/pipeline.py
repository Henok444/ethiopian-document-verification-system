from document_verification_engine.image_extracter_model.ocr_model.ocr import read_document
from document_verification_engine.verification_system_tools.field_extracter import extract_fields

from document_verification_engine.verification_system_tools.verification import verify
from document_verification_engine.verification_system_tools.create_verification_request import create_verification_request





     

# =---------------main 



def verify_request(img_path , request ):


    text = read_document(img_path)
    fields = extract_fields(text , request)
    created_request = create_verification_request(request , fields)


    result = verify(created_request)
    return result 








     
