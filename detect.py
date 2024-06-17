import contextlib
import sys
import json
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO
import pytesseract
import re
import os
from openai import OpenAI
# Load YOLOv8 model
model = YOLO('./train/weights/best.pt')
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

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

def main(image_path, api_openAI):
    client = OpenAI(
        api_key=api_openAI
    )
    detections = detect_objects(image_path)
    texts, result_data = extract_text_from_boxes(image_path, detections, '')
#     respones = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "system", "content": '''You are an AI language model. When the user asks you to extract important keywords from an English passage, you must provide the information in the exact format: English keyword|English meaning|Vietnamese meaning|Simple sentence in English|Simple sentence in Vietnamese. Do not change the format. 
# Here is an example of the format:
# Education|The process of receiving or giving systematic instruction|Giáo dục|Education is important for everyone's future.|Giáo dục rất quan trọng cho tương lai của mỗi người.'''},
#               {"role": "user", "content": '''Extract important keywords from the following English passage, filter out irrelevant words, and provide the following information for each keyword in the format specified in the system prompt.

# Passage: ''' + result_data}]
#     )
#    data = respones.choices[0].message.content
    data = '''Penguins|Birds that cannot fly but are excellent swimmers|Chim cánh cụt|Penguins are known for their swimming abilities.|Chim cánh cụt nổi tiếng với khả năng bơi của chúng.
Flightless birds|Birds that cannot fly|Chim không biết bay|There are about 40 species of flightless birds.|Có khoảng 40 loài chim không biết bay.
Southern Hemisphere|The half of the Earth south of the equator|Bán cầu Nam|Most penguins live in the Southern Hemisphere.|Hầu hết chim cánh cụt sống ở Bán cầu Nam.
North Pole|The northernmost point of the Earth|Bắc Cực|No penguins live in the North Pole.|Không có chim cánh cụt nào sống ở Bắc Cực.
Colony|A group of penguins living together|Bầy đàn|Penguins are very social and live in colonies.|Chim cánh cụt rất xã hội và sống thành bầy đàn.
Swimmers|Animals that move through water using their bodies|Người/động vật bơi lội|Penguins are great swimmers using their wings.|Chim cánh cụt là những kẻ bơi xuất sắc dùng cánh của chúng.
Underwater|Beneath the surface of the water|Dưới nước|Penguins can stay underwater for 10-15 minutes.|Chim cánh cụt có thể ở dưới nước trong 10-15 phút.
Feet|The lower part of a penguin's leg|Bàn chân|Penguins have small feet to avoid losing heat.|Chân của chim cánh cụt rất nhỏ để tránh mất nhiệt.
Diet|The food penguins eat|Chế độ ăn|The main diet of penguins is fish and krill.|Chế độ ăn chính của chim cánh cụt là cá và nhuyễn thể.
Predators|Animals that hunt other animals|Kẻ săn mồi|Penguins use camouflage to avoid predators.|Chim cánh cụt dùng ngụy trang để tránh kẻ săn mồi.'''
    lines = data.strip().split('\n')
    # Sử dụng regex để tách từng cặp thông tin
    pattern = re.compile(r'([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)')

    results = []
    for line in lines:
        match = pattern.match(line)
        if match:
            entry = {
                'keyword': match.group(1).strip(),
                'engMeaning': match.group(2).strip(),
                'vietMeaning': match.group(3).strip(),
                'engSentence': match.group(4).strip(),
                'vietSentence': match.group(5).strip(),
            }
            results.append(entry)

    # Chuyển đổi danh sách từ điển thành định dạng JSON
    json_data = json.dumps(results, ensure_ascii=False, indent=4)
    # # Ghi chuỗi JSON vào file
    # with open('data.json', 'w', encoding='utf-8') as file:
    #     file.write(json_data)
    # # In kết quả để kiểm tra
    print(json_data)
    #print(json.dumps(respones, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    image_path = sys.argv[1]
    api_openAI = sys.argv[2]
    main(image_path,api_openAI)
