# /// script
# dependencies = [
#   "paddleocr",
#   "paddlepaddle",
#   "transformers",
#   "torch",
#   "accelerate"
# ]
# ///

import os
import json
from paddleocr import PaddleOCR
from transformers import pipeline


from pathlib import Path
base = Path(__file__).resolve().parents[4]
image_path = base / "data" / "test_image" / "id.jpg" 


# 1. Quiet framework logging outputs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# --- PART A: RUN MULTILINGUAL PADDLEOCR ---
print("Initializing PaddleOCR Engine on CPU...")

# FIXED: use_cuda=False explicitly forces PaddleOCR onto your CPU cores in newer versions
# Force CPU cleanly without adding unmapped layout version parameters
# FIXED: use_gpu/use_cuda are removed entirely. PaddleOCR now auto-detects your CPU.
# use_angle_cls is replaced by use_textline_orientation.
ocr = PaddleOCR(use_textline_orientation=True, lang='en')

# Make sure this file exists in your directory!
image_path = "your_id_card_image.jpg" 

print(f"Scanning image pixels: {image_path}...")
full_ocr_text = ""
try:
    ocr_result = ocr.ocr(image_path, cls=True)
    
    extracted_lines = []
    if ocr_result and ocr_result[0]:
        for line in ocr_result[0]:
            # line[1][0] safely grabs just the text string from PaddleOCR's layout structure
            text_str = line[1][0]  
            extracted_lines.append(text_str)
    
    full_ocr_text = "\n".join(extracted_lines)
except Exception as e:
    print(f"OCR Error: {e}")

if not full_ocr_text.strip():
    print("No text could be separated from the image. Please verify image path/quality. Exiting.")
    exit()

print("\n--- Raw OCR Text Separated ---")
print(full_ocr_text)


# --- PART B: EXTRACT TARGET FIELDS VIA LLM ---
print("\nLoading CPU-optimized LLM parser...")
generator = pipeline(
    "text-generation", 
    model="Qwen/Qwen2.5-0.5B-Instruct", 
    device=-1  # Force CPU execution for the LLM
)

system_instruction = (
    "You are a precise data extraction engine. "
    "Extract the person's full name and date of birth from the messy document text. "
    "Respond ONLY with a valid JSON object containing the keys 'name' and 'date_of_birth'. "
    "Do not include any introductory text, markdown code blocks like ```json, or explanations."
)

messages = [
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": f"Messy OCR Text:\n\"\"\"{full_ocr_text}\"\"\""}
]

print("Parsing structural key values...")
outputs = generator(
    messages, 
    max_new_tokens=60, 
    temperature=0.1, 
    clean_up_tokenization_spaces=True
)

raw_json_output = outputs["generated_text"][-1]["content"].strip()

# --- PART C: FINAL PRINT ---
print("\n--- Final Structured Output ---")
try:
    parsed_data = json.loads(raw_json_output)
    print(json.dumps(parsed_data, indent=4))
except json.JSONDecodeError:
    print("Could not parse clean JSON. Raw LLM reply:")
    print(raw_json_output)


