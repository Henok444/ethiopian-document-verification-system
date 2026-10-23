import pytesseract 

from PIL import Image


def read_document(image_path: str) -> str :
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image , lang= "amh+eng")

    return text.strip()

