from document_verification_engine.image_extracter_model.improved_ocr_model.crop import crop 
from document_verification_engine.image_extracter_model.improved_ocr_model.id_reader import main 
from document_verification_engine.image_extracter_model.improved_ocr_model.make_sense import make_se
import sys
from pathlib import Path


BASE =  Path(__file__).resolve().parents[4]

path = BASE / ""

def run_id_reader(*args):
    old = sys.argv
    sys.argv = ["id_reader.py", *args]
    try:
        main()
    finally:
        sys.argv = old

def run_make_sense(*args):
    old = sys.argv
    sys.argv = ["make_sense.py", *args]
    try:
        result = make_se()
    finally:
        sys.argv = old
    return result

def extract_text_from_image(path):

    crop(path)
    run_id_reader("data/crop", "--txt-conf", "0")
    result = run_make_sense("data/results/id_result.txt", "only_eng")
    return result
