# /// script
# dependencies = [
#   "transformers",
#   "torch",
#   "accelerate"
# ]
# ///

import os
import json
from transformers import pipeline

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("Loading CPU-optimized generative model...")
generator = pipeline(
    "text-generation", 
    model="Qwen/Qwen2.5-0.5B-Instruct", 
    device=-1
)

ocr_text = """


EP8273953

ሃ 4 AD " ገ ሣ
WEF/PASSPORT ይ ETH
የኢያት ሰም/ኣህጠጩክር

ተሰማ/ገፐር5፻እፅ4ላ

ሰም ከነእባት/‹፤/8ርበ Name

መነን ተማም/እ፡እ፻እ TEMAM

ዜግነት/እ30683ቨ6, ፆታ/5ኗ

ETHIOPIAN

የትውልድ ቀን/04( of Birth

26 JUN 84

የተሰጠበት ቀን;13(ር of Issue

11 AUG 23 ም
ነ :

የሰጠዉ ባለሰልጣን/ Issuing Authority ANS) vase
MAIN DEPARTMENT FOR IMMIGRATION AND NATIONALITY AFFAIRS

ዖ ተገጭዥይ # . ሐ
PSETHTESEMA<<MENEN<TEMAM<<<<<edeeeeee emma
EP82739530ETH8406262 F28080930<<<<<ccceccccga
"""

system_instruction = (
    "You are a precise document data extraction engine. "
    "Extract the person's full name and date of birth from the text. "
    "Respond ONLY with a valid JSON object containing the keys 'name' and 'date_of_birth'. "
    "Do not include any conversational words, intro text, markdown code blocks like ```json, or explanations."
)

messages = [
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": f"Text:\n\"\"\"{ocr_text}\"\"\""}
]

print("Extracting data fields...")
outputs = generator(
    messages, 
    max_new_tokens=60,  
    temperature=0.1, 
    clean_up_tokenization_spaces=True
)

# FIXED INDEXING: Grab the first list item, then pull the generated chat content
raw_output = outputs[0]["generated_text"][-1]["content"].strip()

print("\n--- Raw Model Output ---")
print(raw_output)

print("\n--- Parsed Python Dictionary ---")
try:
    data = json.loads(raw_output)
    print(f"Name Found:         {data.get('name')}")
    print(f"Date of Birth Found: {data.get('date_of_birth')}")
except json.JSONDecodeError:
    print("Failed to cleanly parse JSON structure. Raw string was:")
    print(raw_output)
