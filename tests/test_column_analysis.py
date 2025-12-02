"""
데이터 샘플 분석 로직 테스트 (DAY 25)
컬럼 통계 분석 및 타입 추론 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from utils.column_mapper import ColumnMapper


def test_analyze_id_column():
    """테스트 1: ID 컬럼 분석"""
    print("\n" + "="*60)
    print("테스트 1: ID 컬럼 분석 (고유값 비율 90% 이상)")
    print("="*60)

    df = pd.DataFrame({
        'CustomerID': range(1, 101),  # 100개 고유값
        'Name': ['Customer' + str(i) for i in range(1, 101)]
    })

    mapper = ColumnMapper(data_type='ecommerce')
    analysis = mapper.analyze_column_data(df, 'CustomerID')

    print(f"\n컬럼: CustomerID")
    print(f"  dtype: {analysis['dtype']}")
    print(f"  unique_ratio: {analysis['unique_ratio']:.2%}")
    print(f"  is_id: {analysis['is_id']}")
    print(f"  is_numeric: {analysis['is_numeric']}")
    print(f"  is_date: {analysis['is_date']}")

    assert analysis['is_id'] == True, "고유값 100%이므로 ID로 판정되어야 함"
    assert analysis['is_numeric'] == True, "숫자형이어야 함"

    # 타입 추론
    type_scores = mapper.infer_column_type(df, 'CustomerID', analysis)
    print(f"\n타입 추론 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    assert type_scores['id'] >= 80, "ID 점수가 높아야 함"

    print("\n[PASS] 테스트 1 통과!")
    return True


def test_analyze_date_column():
    """테스트 2: 날짜 컬럼 분석"""
    print("\n" + "="*60)
    print("테스트 2: 날짜 컬럼 분석")
    print("="*60)

    df = pd.DataFrame({
        'OrderDate': [
            '2024-01-01', '2024-01-02', '2024-01-03',
            '2024-01-04', '2024-01-05', '2024-01-06',
            '2024-01-07', '2024-01-08', '2024-01-09',
            '2024-01-10'
        ]
    })

    mapper = ColumnMapper(data_type='ecommerce')
    analysis = mapper.analyze_column_data(df, 'OrderDate')

    print(f"\n컬럼: OrderDate")
    print(f"  dtype: {analysis['dtype']}")
    print(f"  is_date: {analysis['is_date']}")
    print(f"  is_numeric: {analysis['is_numeric']}")

    assert analysis['is_date'] == True, "날짜 형식이므로 is_date=True여야 함"

    type_scores = mapper.infer_column_type(df, 'OrderDate', analysis)
    print(f"\n타입 추론 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    assert type_scores['date'] >= 80, "날짜 점수가 높아야 함"

    print("\n[PASS] 테스트 2 통과!")
    return True


def test_analyze_numeric_column():
    """테스트 3: 숫자형 컬럼 분석 (가격)"""
    print("\n" + "="*60)
    print("테스트 3: 숫자형 컬럼 분석 (가격)")
    print("="*60)

    df = pd.DataFrame({
        'Price': [100, 200, 150, 300, 250, 180, 220, 190, 210, 240]
    })

    mapper = ColumnMapper(data_type='ecommerce')
    analysis = mapper.analyze_column_data(df, 'Price')

    print(f"\n컬럼: Price")
    print(f"  dtype: {analysis['dtype']}")
    print(f"  is_numeric: {analysis['is_numeric']}")
    print(f"  numeric_range: {analysis['numeric_range']}")

    assert analysis['is_numeric'] == True, "숫자형이어야 함"
    assert analysis['numeric_range'] is not None, "숫자 범위가 계산되어야 함"

    min_val, max_val, mean_val = analysis['numeric_range']
    print(f"  min: {min_val}, max: {max_val}, mean: {mean_val:.2f}")

    type_scores = mapper.infer_column_type(df, 'Price', analysis)
    print(f"\n타입 추론 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    assert type_scores['numeric'] >= 70, "숫자 점수가 높아야 함"

    print("\n[PASS] 테스트 3 통과!")
    return True


def test_analyze_rating_column():
    """테스트 4: 평점 컬럼 분석 (1-10 범위)"""
    print("\n" + "="*60)
    print("테스트 4: 평점 컬럼 분석 (1-10 범위)")
    print("="*60)

    df = pd.DataFrame({
        'Rating': [5, 4, 3, 5, 2, 4, 5, 3, 4, 5]
    })

    mapper = ColumnMapper(data_type='review')
    analysis = mapper.analyze_column_data(df, 'Rating')

    print(f"\n컬럼: Rating")
    print(f"  dtype: {analysis['dtype']}")
    print(f"  is_numeric: {analysis['is_numeric']}")
    print(f"  numeric_range: {analysis['numeric_range']}")

    type_scores = mapper.infer_column_type(df, 'Rating', analysis)
    print(f"\n타입 추론 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    assert type_scores['rating'] >= 60, "평점 점수가 높아야 함"

    print("\n[PASS] 테스트 4 통과!")
    return True


def test_analyze_text_column():
    """테스트 5: 텍스트 컬럼 분석 (리뷰)"""
    print("\n" + "="*60)
    print("테스트 5: 텍스트 컬럼 분석 (리뷰)")
    print("="*60)

    df = pd.DataFrame({
        'Review': [
            '이 제품은 정말 좋습니다. 디자인이 세련되고 품질도 우수합니다.',
            '배송이 빨라서 좋았어요. 포장도 깔끔하고 만족스럽습니다.',
            '가격 대비 성능이 뛰어납니다. 추천합니다!',
            '생각보다 크기가 작아서 조금 아쉽지만 그래도 괜찮습니다.',
            '색상이 사진과 다르게 와서 실망했지만 품질은 좋습니다.'
        ]
    })

    mapper = ColumnMapper(data_type='review')
    analysis = mapper.analyze_column_data(df, 'Review')

    print(f"\n컬럼: Review")
    print(f"  dtype: {analysis['dtype']}")
    print(f"  is_numeric: {analysis['is_numeric']}")
    print(f"  is_date: {analysis['is_date']}")

    type_scores = mapper.infer_column_type(df, 'Review', analysis)
    print(f"\n타입 추론 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    assert 'text' in type_scores, "텍스트 점수가 계산되어야 함"
    assert type_scores.get('text', 0) >= 50, "텍스트 점수가 높아야 함"

    print("\n[PASS] 테스트 5 통과!")
    return True


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("데이터 샘플 분석 로직 테스트 시작 (DAY 25)")
    print("="*60)

    tests = [
        test_analyze_id_column,
        test_analyze_date_column,
        test_analyze_numeric_column,
        test_analyze_rating_column,
        test_analyze_text_column
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__} 실패: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__} 에러: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"테스트 결과: {passed}개 통과, {failed}개 실패")
    print("="*60)

    if failed == 0:
        print("\n[SUCCESS] 모든 테스트 통과!")
        return True
    else:
        print(f"\n[WARNING] {failed}개 테스트 실패")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
