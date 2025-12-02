"""
샘플 데이터 생성 스크립트
배포용 데모 데이터 4종 생성
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 시드 설정 (재현성)
np.random.seed(42)
random.seed(42)

print("[INFO] 샘플 데이터 생성 시작...")

# ========== 1. 네이버 영화 리뷰 500개 ==========
print("\n[1/4] 네이버 영화 리뷰 생성 중...")

movie_positive_reviews = [
    "정말 재밌게 봤어요! 강력 추천합니다", "배우들 연기가 정말 훌륭했어요",
    "스토리가 탄탄하고 몰입도 최고", "CGI 퀄리티가 엄청나네요",
    "가족과 함께 보기 좋은 영화", "기대 이상이었어요 대박",
    "감동적인 장면이 많았습니다", "연출이 정말 센스있어요",
    "OST도 좋고 영상미도 최고", "재관람 의사 100%",
    "올해 본 영화 중 최고", "웃음 포인트가 많아서 즐거웠어요",
    "액션 신이 박진감 넘쳐요", "예상 못한 반전이 좋았습니다"
]

movie_negative_reviews = [
    "기대했는데 실망이에요", "스토리가 너무 뻔해요",
    "지루해서 중간에 졸았어요", "배우들 연기가 아쉽네요",
    "돈이 아깝습니다 비추", "재미없어요 보지마세요",
    "스토리 전개가 너무 느려요", "결말이 이해 안 돼요",
    "CG가 어색하고 저렴해 보여요", "평점 조작 의심됩니다",
    "전편보다 못한 속편", "2시간이 너무 길게 느껴졌어요"
]

movie_neutral_reviews = [
    "그냥 그래요 평범한 영화", "볼만은 한데 특별하진 않아요",
    "기대 안 하고 보면 괜찮아요", "시간 때우기용으로 적당해요"
]

movie_reviews = []
start_date = datetime(2024, 1, 1)

for i in range(500):
    score = random.choices([10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                          weights=[15, 20, 25, 15, 10, 5, 4, 3, 2, 1])[0]

    if score >= 8:
        review_text = random.choice(movie_positive_reviews)
    elif score <= 4:
        review_text = random.choice(movie_negative_reviews)
    else:
        review_text = random.choice(movie_neutral_reviews)

    date = start_date + timedelta(days=random.randint(0, 365))

    movie_reviews.append({
        'movie_id': '12345',
        'author': f'user{i+1:03d}',
        'score': score,
        'review': review_text,
        'date': date.strftime('%Y.%m.%d'),
        'likes': random.randint(0, 50),
        'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

df_movie = pd.DataFrame(movie_reviews)
df_movie.to_csv('C:/claude/분석크롤링/auto-insight-platform/sample_data/naver_movie_reviews.csv',
                index=False, encoding='utf-8-sig')
print(f"[OK] 영화 리뷰 {len(df_movie)}개 생성 완료")

# ========== 2. 네이버 플레이스 리뷰 500개 ==========
print("\n[2/4] 네이버 플레이스 리뷰 생성 중...")

place_positive_reviews = [
    "음식이 정말 맛있어요!", "사장님이 친절하세요",
    "가성비 최고입니다", "재방문 의사 있어요",
    "분위기도 좋고 맛도 좋아요", "서비스가 정말 좋습니다",
    "메뉴 구성이 알차네요", "청결도가 완벽해요",
    "대기 시간이 있어도 기다릴 가치가 있어요", "강력 추천합니다"
]

place_negative_reviews = [
    "별로예요 비추천", "가격 대비 실망스러워요",
    "서비스가 불친절해요", "음식이 느려요",
    "위생 상태가 별로예요", "재방문 의사 없어요",
    "맛이 평범해요", "가격이 너무 비싸요"
]

place_reviews = []

for i in range(500):
    rating = random.choices([5, 4, 3, 2, 1],
                           weights=[40, 30, 15, 10, 5])[0]

    if rating >= 4:
        review_text = random.choice(place_positive_reviews)
    else:
        review_text = random.choice(place_negative_reviews)

    date = start_date + timedelta(days=random.randint(0, 365))

    place_reviews.append({
        'place_id': '1234567890',
        'author': f'reviewer{i+1:03d}',
        'rating': rating,
        'review': review_text,
        'date': date.strftime('%Y.%m.%d'),
        'image_count': random.randint(0, 5),
        'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

df_place = pd.DataFrame(place_reviews)
df_place.to_csv('C:/claude/분석크롤링/auto-insight-platform/sample_data/naver_place_reviews.csv',
                index=False, encoding='utf-8-sig')
print(f"[OK] 플레이스 리뷰 {len(df_place)}개 생성 완료")

# ========== 3. E-commerce 데이터 1000건 ==========
print("\n[3/4] E-commerce 샘플 데이터 생성 중...")

products = [
    '무선 이어폰', '스마트폰 케이스', '노트북 거치대', 'USB 충전기',
    '블루투스 스피커', '마우스 패드', '키보드', '웹캠', '모니터',
    'HDMI 케이블', '노트북 파우치', '스마트 워치', '보조배터리',
    '태블릿 펜', 'SD 카드', '마우스', '헤드셋', '스탠드 조명'
]

ecommerce_data = []
customer_ids = list(range(1, 201))  # 200명 고객

for i in range(1000):
    customer_id = random.choice(customer_ids)
    invoice_date = start_date + timedelta(days=random.randint(0, 365))
    product = random.choice(products)
    quantity = random.randint(1, 5)
    unit_price = random.randint(5, 100) * 1000  # 5,000원 ~ 100,000원

    ecommerce_data.append({
        'CustomerID': customer_id,
        'InvoiceDate': invoice_date.strftime('%Y-%m-%d'),
        'Description': product,
        'Quantity': quantity,
        'UnitPrice': unit_price
    })

df_ecommerce = pd.DataFrame(ecommerce_data)
df_ecommerce.to_csv('C:/claude/분석크롤링/auto-insight-platform/sample_data/ecommerce_sample.csv',
                    index=False, encoding='utf-8-sig')
print(f"[OK] E-commerce 데이터 {len(df_ecommerce)}개 생성 완료")

# ========== 4. 판매 데이터 1000건 ==========
print("\n[4/4] 판매 데이터 생성 중...")

categories = ['전자제품', '의류', '식품', '생활용품', '도서']
product_names = {
    '전자제품': ['노트북', '스마트폰', '태블릿', '이어폰', '스피커'],
    '의류': ['티셔츠', '청바지', '자켓', '운동화', '모자'],
    '식품': ['과자', '음료수', '라면', '과일', '우유'],
    '생활용품': ['세제', '휴지', '샴푸', '칫솔', '수건'],
    '도서': ['소설', '에세이', '자기계발서', '만화책', '잡지']
}

sales_data = []

for i in range(1000):
    date = start_date + timedelta(days=random.randint(0, 365))
    category = random.choice(categories)
    product = random.choice(product_names[category])

    # 카테고리별 매출 분포 차이
    if category == '전자제품':
        sales = random.randint(500000, 2000000)
    elif category == '의류':
        sales = random.randint(30000, 150000)
    elif category == '식품':
        sales = random.randint(5000, 50000)
    elif category == '생활용품':
        sales = random.randint(10000, 80000)
    else:  # 도서
        sales = random.randint(10000, 50000)

    sales_data.append({
        'Date': date.strftime('%Y-%m-%d'),
        'Product': f'{category}_{product}',
        'Category': category,
        'Sales': sales,
        'Quantity': random.randint(1, 20)
    })

df_sales = pd.DataFrame(sales_data)
df_sales.to_csv('C:/claude/분석크롤링/auto-insight-platform/sample_data/sales_sample.csv',
                index=False, encoding='utf-8-sig')
print(f"[OK] 판매 데이터 {len(df_sales)}개 생성 완료")

# ========== 요약 ==========
print("\n" + "="*60)
print("[SUCCESS] 샘플 데이터 생성 완료!")
print("="*60)
print(f"\n1. naver_movie_reviews.csv: {len(df_movie):,}행")
print(f"   - 평균 평점: {df_movie['score'].mean():.2f}/10")
print(f"   - 긍정(8점 이상): {len(df_movie[df_movie['score'] >= 8])}개")

print(f"\n2. naver_place_reviews.csv: {len(df_place):,}행")
print(f"   - 평균 평점: {df_place['rating'].mean():.2f}/5")
print(f"   - 긍정(4점 이상): {len(df_place[df_place['rating'] >= 4])}개")

print(f"\n3. ecommerce_sample.csv: {len(df_ecommerce):,}행")
print(f"   - 고유 고객 수: {df_ecommerce['CustomerID'].nunique()}명")
print(f"   - 총 매출: {(df_ecommerce['Quantity'] * df_ecommerce['UnitPrice']).sum():,}원")

print(f"\n4. sales_sample.csv: {len(df_sales):,}행")
print(f"   - 총 매출: {df_sales['Sales'].sum():,}원")
print(f"   - 상위 카테고리: {df_sales.groupby('Category')['Sales'].sum().idxmax()}")

print("\n✅ 모든 샘플 데이터가 sample_data/ 폴더에 저장되었습니다.")
