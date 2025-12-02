import pandas as pd
import random
from datetime import datetime, timedelta

# === 설정 ===
NUM_ROWS = 3000           # 생성할 데이터 개수
NUM_CUSTOMERS = 300       # 고객 수 (300명이 3000건을 사니까, 인당 평균 10회 구매 -> 재구매 분석 용이)
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

# 가상 상품 목록 (상품명, 기본 가격)
products = [
    ("Wireless Mouse", 12.50), ("Mechanical Keyboard", 45.00), ("Gaming Headset", 89.99),
    ("24inch Monitor", 120.00), ("USB-C Cable", 3.50), ("Laptop Stand", 15.00),
    ("Webcam HD", 55.00), ("Office Chair", 250.00), ("Desk Lamp", 30.00),
    ("Bluetooth Speaker", 25.50), ("External SSD 1TB", 150.00), ("Mouse Pad", 9.99),
    ("HDMI Cable", 8.99), ("Notebook", 5.00), ("Sticky Notes", 2.00),
    ("Phone Stand", 8.50), ("Screen Cleaning Kit", 12.00), ("Ergonomic Pillow", 40.00),
    ("Graphics Tablet", 200.00), ("Cable Organizer", 5.00)
]

# 데이터 담을 리스트
data = []

# 고객 ID 리스트 (10001 ~ 10300)
customer_ids = [10001 + i for i in range(NUM_CUSTOMERS)]

print(f"🔄 {NUM_ROWS}개의 가상 데이터를 생성 중입니다...")

for i in range(NUM_ROWS):
    # 1. 랜덤 고객 선택 (재구매 패턴을 위해 중복 허용)
    customer_id = random.choice(customer_ids)
    
    # 2. 랜덤 상품 선택
    product_name, base_price = random.choice(products)
    
    # 3. 랜덤 날짜 생성
    days_diff = (END_DATE - START_DATE).days
    random_days = random.randint(0, days_diff)
    invoice_date = START_DATE + timedelta(days=random_days)
    
    # 4. 송장 번호 (고유값)
    invoice_no = f"5{i:05d}"
    
    # 5. 수량 (1~5개는 흔하고, 10개 이상은 드물게)
    quantity = random.choices([1, 2, 3, 4, 5, 10, 20], weights=[40, 30, 15, 10, 3, 1, 1])[0]
    
    # 6. 데이터 추가
    data.append([customer_id, invoice_date.strftime("%Y-%m-%d"), invoice_no, quantity, base_price, product_name])

# DataFrame 변환
df = pd.DataFrame(data, columns=['CustomerID', 'InvoiceDate', 'InvoiceNo', 'Quantity', 'UnitPrice', 'Description'])

# CSV 파일로 저장
filename = "large_sample_data.csv"
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"✅ 생성 완료! '{filename}' 파일이 생성되었습니다.")
print(f"📊 데이터 크기: {len(df)}행, {len(df.columns)}열")