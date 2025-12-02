"""
ColumnMapper 테스트 케이스 모음
DAY 24 요구사항: 5가지 테스트 케이스 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from utils.column_mapper import ColumnMapper


def test_case_1_perfect_english_match():
    """테스트 1: 완벽한 영어 매칭 (표준 컬럼명)"""
    print("\n" + "="*60)
    print("테스트 1: 완벽한 영어 매칭")
    print("="*60)

    df = pd.DataFrame({
        'CustomerID': [1, 2, 3],
        'InvoiceDate': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Quantity': [5, 10, 3],
        'UnitPrice': [100, 200, 150]
    })

    print("\n입력 데이터:")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert is_valid, f"검증 실패: {errors}"
    assert len(mapping) == 4, "4개 컬럼 모두 매핑되어야 함"

    print("\n[PASS] 테스트 1 통과!")
    return True


def test_case_2_korean_columns():
    """테스트 2: 한글 컬럼명 매칭"""
    print("\n" + "="*60)
    print("테스트 2: 한글 컬럼명 매칭")
    print("="*60)

    df = pd.DataFrame({
        '고객ID': [1, 2, 3],
        '주문일': ['2024-01-01', '2024-01-02', '2024-01-03'],
        '수량': [5, 10, 3],
        '가격': [100, 200, 150]
    })

    print("\n입력 데이터:")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert is_valid, f"검증 실패: {errors}"
    assert '고객ID' in [m['user_column'] for m in mapping.values()], "고객ID가 매핑되어야 함"

    print("\n[PASS] 테스트 2 통과!")
    return True


def test_case_3_underscore_lowercase():
    """테스트 3: 언더스코어 + 소문자 혼합"""
    print("\n" + "="*60)
    print("테스트 3: 언더스코어 + 소문자 혼합")
    print("="*60)

    df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'order_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'qty': [5, 10, 3],
        'unit_price': [100, 200, 150]
    })

    print("\n입력 데이터:")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert is_valid, f"검증 실패: {errors}"

    print("\n[PASS] 테스트 3 통과!")
    return True


def test_case_4_review_data():
    """테스트 4: 리뷰 데이터 매칭"""
    print("\n" + "="*60)
    print("테스트 4: 리뷰 데이터 매칭")
    print("="*60)

    df = pd.DataFrame({
        '리뷰': ['좋아요', '별로에요', '최고입니다'],
        '별점': [5, 2, 5],
        '작성일': ['2024-01-01', '2024-01-02', '2024-01-03']
    })

    print("\n입력 데이터:")
    print(df.head())

    mapper = ColumnMapper(data_type='review')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert is_valid, f"검증 실패: {errors}"
    assert 'review_text' in mapping, "리뷰 텍스트 컬럼이 매핑되어야 함"

    print("\n[PASS] 테스트 4 통과!")
    return True


def test_case_5_missing_required_column():
    """테스트 5: 필수 컬럼 누락 (검증 실패 케이스)"""
    print("\n" + "="*60)
    print("테스트 5: 필수 컬럼 누락 검증")
    print("="*60)

    # Quantity 컬럼이 누락됨
    df = pd.DataFrame({
        'CustomerID': [1, 2, 3],
        'InvoiceDate': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'UnitPrice': [100, 200, 150]
    })

    print("\n입력 데이터 (Quantity 누락):")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert not is_valid, "필수 컬럼 누락 시 검증 실패해야 함"
    assert len(errors) > 0, "에러 메시지가 있어야 함"

    print("\n[WARNING] 예상된 검증 실패:")
    for error in errors:
        print(f"  - {error}")

    print("\n[PASS] 테스트 5 통과! (검증 실패 정상 처리)")
    return True


def test_case_6_sales_data():
    """테스트 6 (보너스): 판매 데이터 매칭"""
    print("\n" + "="*60)
    print("테스트 6 (보너스): 판매 데이터 매칭")
    print("="*60)

    df = pd.DataFrame({
        '판매일': ['2024-01-01', '2024-01-02', '2024-01-03'],
        '상품명': ['노트북', '마우스', '키보드'],
        '판매수량': [1, 5, 3],
        '단가': [1000000, 30000, 50000]
    })

    print("\n입력 데이터:")
    print(df.head())

    mapper = ColumnMapper(data_type='sales')
    mapping = mapper.auto_map_columns(df)

    print("\n" + mapper.get_mapping_summary(mapping))

    is_valid, errors = mapper.validate_mapping(mapping)
    assert is_valid, f"검증 실패: {errors}"

    print("\n[PASS] 테스트 6 통과!")
    return True


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("ColumnMapper 전체 테스트 시작")
    print("="*60)

    tests = [
        test_case_1_perfect_english_match,
        test_case_2_korean_columns,
        test_case_3_underscore_lowercase,
        test_case_4_review_data,
        test_case_5_missing_required_column,
        test_case_6_sales_data
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
