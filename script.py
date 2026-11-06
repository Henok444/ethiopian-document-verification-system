import logging
from pathlib import Path
import cv2
from paddleocr import PaddleOCR

# 1. Setup paths relative to this script
base = Path(__file__).resolve().parent
image_path = base / "data" / "test_image" / "id.jpg"

# 2. Mute console noise
logging.getLogger("ppocr").setLevel(logging.ERROR)

# 3. Initialize PaddleOCR v3
ocr = PaddleOCR(
    lang="en",
    use_textline_orientation=True,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
)

# 4. Load Image
img = cv2.imread(str(image_path))
if img is None:
    print(f"Error: Could not load image at {image_path}. Check your file name.")
    exit(1)

h, w, _ = img.shape

# 5. Run prediction (do NOT pass cls=True)
results = ocr.predict(input=str(image_path))

# 6. Process and extract segments
for res in results:
    texts = res.get("rec_texts", [])
    scores = res.get("rec_scores", [])
    boxes = res.get("dt_polys", [])

    for text, confidence, box in zip(texts, scores, boxes):
        x_coords = [pt[0] for pt in box]
        y_coords = [pt[1] for pt in box]

        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))

        # Clamp coordinates to image boundaries
        x_min, x_max = max(0, x_min), min(w, x_max)
        y_min, y_max = max(0, y_min), min(h, y_max)

        cropped_part = img[y_min:y_max, x_min:x_max]

        print(f"Text: '{text}' (Confidence: {confidence:.2f})")
        print(f"Bounding Box: X({x_min} to {x_max}), Y({y_min} to {y_max})")
        print("-" * 50)