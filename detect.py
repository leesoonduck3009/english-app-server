import contextlib
import sys
import json
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO
import pytesseract
import os
from openai import OpenAI
# Load YOLOv8 model
model = YOLO('./train/weights/best.pt')
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
client = OpenAI(
  api_key='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'
)
@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
def detect_objects(image_path):
    img = Image.open(image_path)
    img = np.array(img)

    # Chuyển ảnh từ RGB sang BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    with suppress_output():
        results = model(img)
    detections = []
    for result in results:
        for box in result.boxes.data.cpu().numpy():
            x1, y1, x2, y2, score, class_id = box
            detections.append({
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "score": float(score),
                "class_id": int(class_id)
            })
    detections = sorted(detections, key=lambda d: (d['y1'], d['x1']))
    return detections
def extract_text_from_boxes(image_path, detections, result_data):
    img = Image.open(image_path)
    texts = []
    for box in detections:
        x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
        cropped_img = img.crop((x1, y1, x2, y2))
        text = pytesseract.image_to_string(cropped_img, lang='eng')
        texts.append({
            "box": box,
            "text": text.strip()
        })
        result_data = result_data + "\n\n" + text.strip() 
    return texts, result_data

def main(image_path):
    detections = detect_objects(image_path)
    texts, result_data = extract_text_from_boxes(image_path, detections, '')
    respones = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "Be an English teacher and help me to find all the keywords in the block of text as well as definite their meaning and situation that can applied  "},
              {"role": "user", "content": result_data}]
    )
    print(respones.choices[0].message.content)
    #print(json.dumps(respones, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    image_path = sys.argv[1]
    main(image_path)
