import re
import json
# Chuỗi đầu vào
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
# Tách các dòng thành từng cặp thông tin
lines = data.strip().split('\n')

# Sử dụng regex để tách từng cặp thông tin
pattern = re.compile(r'([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)')

results = []
for line in lines:
    match = pattern.match(line)
    if match:
        entry = {
            'English keyword': match.group(1).strip(),
            'English meaning': match.group(2).strip(),
            'Vietnamese meaning': match.group(3).strip(),
            'Simple sentence in English': match.group(4).strip(),
            'Simple sentence in Vietnamese': match.group(5).strip(),
        }
        results.append(entry)

# Chuyển đổi danh sách từ điển thành định dạng JSON
json_data = json.dumps(results, ensure_ascii=False, indent=4)

# Ghi chuỗi JSON vào file
with open('data.json', 'w', encoding='utf-8') as file:
    file.write(json_data)

# In kết quả để kiểm tra
print(json_data)