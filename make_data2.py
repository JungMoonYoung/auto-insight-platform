import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# 저장 경로 설정 (필요하면 수정하세요)
OUTPUT_DIR = 'sample_data'
OUTPUT_FILE = 'new_sales_data_with_price.csv'

# 폴더가 없으면 생성
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 샘플 데이터 생성 설정
num_rows = 100000  
categories = ['Electronics', 'Clothing', 'Food', 'Home', 'Books']
product_names = {
    'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers'],
    'Food': ['Snack', 'Drink', 'Noodles', 'Fruit'],
    'Home': ['Detergent', 'Tissue', 'Shampoo', 'Towel'],
    'Books': ['Novel', 'Essay', 'Self-help', 'Comic']
}

data = []
start_date = datetime(2024, 1, 1)

print("데이터 생성 중...")

for _ in range(num_rows):
    date = start_date + timedelta(days=random.randint(0, 365))
    category = random.choice(categories)
    product = random.choice(product_names[category])
    
    # 랜덤 값 생성
    quantity = random.randint(1, 20)
    
    # 가격 설정 (제품군별로 가격대 차등)
    if category == 'Electronics':
        base_price = random.randint(50, 200) * 1000
    elif category == 'Clothing':
        base_price = random.randint(10, 100) * 1000
    else:
        base_price = random.randint(5, 50) * 1000
        
    price = base_price  # Price 추가
    sales = price * quantity # Sales는 Price * Quantity로 계산하여 정합성 유지
    
    data.append({
        'Date': date.strftime('%Y-%m-%d'),
        'Product': f'{category}_{product}',
        'Category': category,
        'Price': int(price),     # [NEW] 단가 컬럼
        'Quantity': quantity,
        'Sales': int(sales)      # 매출 (단가 * 수량)
    })

# 데이터프레임 생성
new_df = pd.DataFrame(data)

# CSV 파일로 저장
file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
new_df.to_csv(file_path, index=False, encoding='utf-8-sig')

print(f"✅ 파일 생성 완료: {file_path}")
print(f"   - 행 수: {len(new_df)}개")
print(f"   - 컬럼: {list(new_df.columns)}")
print("\n[미리보기]")
print(new_df.head())