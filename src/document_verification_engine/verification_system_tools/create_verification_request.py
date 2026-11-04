from document_verification_engine.verification_system_tools.schemas import VerificationRequest

from pathlib import Path
import yaml
"""

def create_field_for_verification_request(processed: dict)->dict:

     fields = processed["fields"]
     
     fields_dict = {}

     for field in fields:
          fields_dict[field.name] = field
     return fields_dict

def load_config(config_path: Path)->dict:
     with open(config_path) as file:
          config = yaml.safe_load(file)

     
     return config or {}
def create_document_type_for_verification_request(config_path):
     config = load_config(config_path)
     document_type = config["document_type"]
     return document_type
     
def create_rule_for_verification_request(config_path: Path):
     config = load_config(config_path)
     rules = config["rules"]
     return rules
"""
     
def create_verification_request(request , fields )->VerificationRequest:



     document_type = request["document_type"]
     fields_dict = fields
     rules = request["rules"]

     request = VerificationRequest(document_type= document_type, 
                                   fields= 
                                        fields_dict
                                    , 
                                   rules=  rules , 
                                   )
     #print(request)
     return request


