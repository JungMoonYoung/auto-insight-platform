"""
샘플 데이터 생성 스크립트
DAY 36: Phase 4 - SQL Analytics 테스트용
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.db_manager import DatabaseManager


def generate_transactions(n_customers=100, n_transactions=1000):
    """E-commerce 거래 데이터 생성"""
    np.random.seed(42)

    customers = [f'C{i:04d}' for i in range(1, n_customers + 1)]
    products = ['노트북', '마우스', '키보드', '모니터', '헤드셋',
                '웹캠', 'USB', 'HDMI케이블', '스피커', '마이크']

    data = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(n_transactions):
        customer = np.random.choice(customers)
        product = np.random.choice(products)
        quantity = np.random.randint(1, 10)
        unit_price = np.random.uniform(10, 500)
        invoice_date = base_date + timedelta(days=np.random.randint(0, 365))

        data.append({
            'CustomerID': customer,
            'InvoiceNo': f'INV{i+1:06d}',
            'InvoiceDate': invoice_date,
            'Description': product,
            'Quantity': quantity,
            'UnitPrice': round(unit_price, 2),
            'Country': 'Korea'
        })

    return pd.DataFrame(data)


def generate_sales(n_days=365):
    """판매 데이터 생성"""
    np.random.seed(42)

    products = ['노트북', '마우스', '키보드', '모니터', '헤드셋']
    categories = ['전자제품', '주변기기', '주변기기', '전자제품', '음향기기']

    data = []
    base_date = datetime.now() - timedelta(days=n_days)

    for i in range(n_days):
        for product, category in zip(products, categories):
            sales_date = base_date + timedelta(days=i)
            quantity = np.random.randint(5, 50)
            price = np.random.uniform(50, 1000)

            data.append({
                'sales_date': sales_date,
                'product': product,
                'category': category,
                'quantity': quantity,
                'price': round(price, 2)
            })

    return pd.DataFrame(data)


def generate_reviews(n_reviews=500):
    """리뷰 데이터 생성"""
    np.random.seed(42)

    positive_reviews = [
        '정말 좋아요!', '최고입니다', '강력 추천합니다', '만족스러워요',
        '품질이 훌륭합니다', '가성비 최고', '배송도 빠르고 좋아요'
    ]

    neutral_reviews = [
        '보통이에요', '그냥 그래요', '평범합니다', '괜찮아요',
        '무난한 제품', '기대했던 정도'
    ]

    negative_reviews = [
        '별로였어요', '실망했습니다', '기대 이하', '다시는 안 살 듯',
        '품질이 좋지 않아요', '배송이 너무 늦어요', '불량품인 것 같아요'
    ]

    data = []
    base_date = datetime.now() - timedelta(days=180)

    for i in range(n_reviews):
        # 평점에 따라 리뷰 텍스트 선택
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3])

        if rating >= 4:
            review_text = np.random.choice(positive_reviews)
        elif rating == 3:
            review_text = np.random.choice(neutral_reviews)
        else:
            review_text = np.random.choice(negative_reviews)

        review_date = base_date + timedelta(days=np.random.randint(0, 180))

        data.append({
            'rating': rating,
            'review_text': review_text,
            'author': f'user{i+1}',
            'review_date': review_date
        })

    return pd.DataFrame(data)


def main():
    """메인 함수"""
    print("=" * 60)
    print("샘플 데이터 생성 시작")
    print("=" * 60)

    # 데이터베이스 초기화
    db = DatabaseManager(db_path='data/analytics.db')

    # 1. 거래 데이터 생성 및 삽입
    print("\n1. 거래 데이터 생성 중...")
    transactions_df = generate_transactions(n_customers=100, n_transactions=1000)
    inserted = db.insert_transactions(transactions_df)
    print(f"   OK: {inserted}건의 거래 데이터 삽입 완료")

    # 2. 판매 데이터 생성 및 삽입
    print("\n2. 판매 데이터 생성 중...")
    sales_df = generate_sales(n_days=365)
    inserted = db.insert_sales(sales_df)
    print(f"   OK: {inserted}건의 판매 데이터 삽입 완료")

    # 3. 리뷰 데이터 생성 및 삽입
    print("\n3. 리뷰 데이터 생성 중...")
    reviews_df = generate_reviews(n_reviews=500)
    inserted = db.insert_reviews(reviews_df, source='sample')
    print(f"   OK: {inserted}건의 리뷰 데이터 삽입 완료")

    # 데이터베이스 상태 확인
    print("\n" + "=" * 60)
    print("데이터베이스 상태")
    print("=" * 60)

    for table_name in ['transactions', 'sales', 'reviews']:
        info = db.get_table_info(table_name)
        print(f"\n[{table_name}] 테이블:")
        print(f"   - 총 행 수: {info['row_count']:,}개")
        print(f"   - 컬럼 수: {len(info['columns'])}개")

    db.close()

    print("\n" + "=" * 60)
    print("샘플 데이터 생성 완료!")
    print("=" * 60)
    print("\n다음 명령어로 Streamlit 앱을 실행하세요:")
    print("streamlit run app.py")


if __name__ == "__main__":
    main()
