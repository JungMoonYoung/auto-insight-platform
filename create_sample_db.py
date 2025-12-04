"""
샘플 데이터베이스 생성 스크립트
Streamlit Cloud 배포용 analytics.db 생성
"""

import pandas as pd
from datetime import datetime, timedelta
import random
from modules.db_manager import DatabaseManager

def create_sample_data():
    """샘플 데이터 생성 및 DB 저장"""

    print("Creating sample database for Streamlit Cloud...")

    # DB 초기화
    db = DatabaseManager('data/analytics.db')

    # ========== 1. 샘플 판매 데이터 생성 (sales 테이블) ==========
    print("Creating sample sales data...")

    products = ['노트북', '마우스', '키보드', '모니터', '헤드셋', 'USB', '외장하드', 'SSD']
    categories = ['전자제품', '액세서리', '저장장치']

    sales_data = []
    start_date = datetime(2024, 1, 1)

    for i in range(180):  # 6개월 데이터
        date = start_date + timedelta(days=i)
        for _ in range(random.randint(5, 15)):  # 하루 5-15건
            product = random.choice(products)
            quantity = random.randint(1, 10)
            price = random.randint(10000, 200000)

            sales_data.append({
                'sales_date': date.strftime('%Y-%m-%d'),
                'product': product,
                'category': random.choice(categories),
                'quantity': quantity,
                'price': price
            })

    df_sales = pd.DataFrame(sales_data)
    db.insert_sales(df_sales)
    print(f"Inserted {len(df_sales)} sales records")

    # ========== 2. 샘플 거래 데이터 생성 (transactions 테이블) ==========
    print("Creating sample transaction data...")

    transaction_data = []
    customers = [f'C{str(i).zfill(5)}' for i in range(1, 201)]  # 200명 고객

    for i in range(500):  # 500건 거래
        customer_id = random.choice(customers)
        invoice_no = f'INV{str(i+1000).zfill(6)}'
        invoice_date = (start_date + timedelta(days=random.randint(0, 179))).strftime('%Y-%m-%d')
        product = random.choice(products)
        quantity = random.randint(1, 5)
        unit_price = random.randint(10000, 200000)

        transaction_data.append({
            'customer_id': customer_id,
            'invoice_no': invoice_no,
            'invoice_date': invoice_date,
            'product': product,
            'description': f'{product} 상품 설명',
            'quantity': quantity,
            'unit_price': unit_price,
            'country': 'South Korea'
        })

    df_transactions = pd.DataFrame(transaction_data)
    db.insert_transactions(df_transactions)
    print(f"Inserted {len(df_transactions)} transaction records")

    # ========== 3. 샘플 리뷰 데이터 생성 (reviews 테이블) ==========
    print("Creating sample review data...")

    reviews_positive = [
        '정말 좋은 제품이에요!',
        '만족스럽습니다. 추천합니다.',
        '가성비 최고네요',
        '배송도 빠르고 품질도 좋아요',
        '재구매 의사 있습니다'
    ]

    reviews_negative = [
        '기대 이하입니다',
        '가격 대비 별로에요',
        '배송이 너무 늦었어요',
        '불량품 같아요',
        '환불하고 싶습니다'
    ]

    review_data = []
    authors = [f'user{i}' for i in range(1, 101)]

    for i in range(300):  # 300개 리뷰
        rating = random.choice([1, 2, 3, 4, 5, 5, 5, 4, 4])  # 긍정 리뷰 많게

        if rating >= 4:
            review_text = random.choice(reviews_positive)
        else:
            review_text = random.choice(reviews_negative)

        review_date = (start_date + timedelta(days=random.randint(0, 179))).strftime('%Y-%m-%d')

        review_data.append({
            'rating': rating,
            'review_text': review_text,
            'author': random.choice(authors),
            'review_date': review_date
        })

    df_reviews = pd.DataFrame(review_data)
    db.insert_reviews(df_reviews, source='sample_data')
    print(f"Inserted {len(df_reviews)} review records")

    # ========== 4. 테이블 정보 출력 ==========
    print("\n" + "="*50)
    print("Database Summary:")
    print("="*50)

    for table in ['sales', 'transactions', 'reviews']:
        info = db.get_table_info(table)
        print(f"\n{table.upper()} 테이블:")
        print(f"  - 총 행 수: {info['row_count']:,}개")
        print(f"  - 컬럼 수: {len(info['columns'])}개")

    db.close()
    print("\nSample database created successfully!")
    print("Location: data/analytics.db")

if __name__ == "__main__":
    create_sample_data()
