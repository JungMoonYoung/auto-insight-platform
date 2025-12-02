"""
코드 리뷰 후 수정사항 검증 테스트
- 중복 매핑 버그 수정
- 날짜 파싱 성능 개선
- 타입 추론 우선순위
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from utils.column_mapper import ColumnMapper


def test_duplicate_mapping_detection():
    """테스트 1: 중복 매핑 감지 및 해결"""
    print("\n" + "="*60)
    print("테스트 1: 중복 매핑 감지 (price, unit_price 충돌)")
    print("="*60)

    df = pd.DataFrame({
        'CustomerID': [1, 2, 3],
        'InvoiceDate': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Quantity': [5, 10, 3],
        'price': [100, 200, 150],  # 첫 번째 후보
        'unit_price': [100, 200, 150]  # 두 번째 후보 (더 유사)
    })

    print("\n입력 데이터 (price와 unit_price 모두 존재):")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(df)

    print("\n매핑 결과:")
    print(mapper.get_mapping_summary(mapping))

    # 검증
    assert 'unitprice' in mapping, "unitprice가 매핑되어야 함"
    assert mapping['unitprice']['user_column'] in ['price', 'unit_price'], "price 또는 unit_price 중 하나가 선택되어야 함"

    # alternatives 확인
    if 'alternatives' in mapping['unitprice']:
        print(f"\n[INFO] 중복 감지: {mapping['unitprice']['alternatives']} 제외됨")
        print(f"[INFO] 선택된 컬럼: {mapping['unitprice']['user_column']} (신뢰도: {mapping['unitprice']['confidence']}%)")

    print("\n[PASS] 테스트 1 통과! (중복 매핑 정상 처리)")
    return True


def test_date_parsing_performance():
    """테스트 2: 날짜 파싱 성능 테스트 (100개 행)"""
    print("\n" + "="*60)
    print("테스트 2: 날짜 파싱 성능 (100개 행)")
    print("="*60)

    import time

    # 100개 날짜 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100).astype(str).tolist()
    df = pd.DataFrame({
        'OrderDate': dates,
        'Value': range(100)
    })

    print(f"\n입력 데이터: {len(df)}개 행")

    mapper = ColumnMapper(data_type='ecommerce')

    start_time = time.time()
    analysis = mapper.analyze_column_data(df, 'OrderDate')
    elapsed = time.time() - start_time

    print(f"\n분석 시간: {elapsed*1000:.2f}ms")
    print(f"날짜 감지: {analysis['is_date']}")

    # 성능 검증: 100개 행 분석이 100ms 이내여야 함
    assert elapsed < 0.1, f"날짜 파싱이 너무 느림: {elapsed*1000:.2f}ms > 100ms"
    assert analysis['is_date'] == True, "날짜로 감지되어야 함"

    print("\n[PASS] 테스트 2 통과! (성능 기준 충족)")
    return True


def test_type_inference_priority():
    """테스트 3: 타입 추론 우선순위 (날짜 > ID)"""
    print("\n" + "="*60)
    print("테스트 3: 타입 추론 우선순위 (날짜가 ID보다 우선)")
    print("="*60)

    df = pd.DataFrame({
        'OrderDate': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                      '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10']
    })

    print("\n입력 데이터 (고유값 100% 날짜):")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')
    analysis = mapper.analyze_column_data(df, 'OrderDate')
    type_scores = mapper.infer_column_type(df, 'OrderDate', analysis)

    print(f"\n분석 결과:")
    print(f"  is_id: {analysis['is_id']}")
    print(f"  is_date: {analysis['is_date']}")
    print(f"  unique_ratio: {analysis['unique_ratio']:.0%}")

    print(f"\n타입 점수:")
    for col_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col_type}: {score:.0f}점")

    # 검증: 날짜가 1등이어야 함
    top_type = max(type_scores, key=type_scores.get)
    assert top_type == 'date', f"날짜가 1등이어야 하는데 {top_type}가 1등임"
    assert type_scores['date'] > type_scores['id'], "날짜 점수가 ID보다 높아야 함"

    print("\n[PASS] 테스트 3 통과! (우선순위 올바름)")
    return True


def test_empty_dataframe():
    """테스트 4: 빈 데이터프레임 처리"""
    print("\n" + "="*60)
    print("테스트 4: 빈 데이터프레임 처리")
    print("="*60)

    df = pd.DataFrame({
        'CustomerID': [],
        'InvoiceDate': [],
        'Quantity': [],
        'UnitPrice': []
    })

    print("\n입력 데이터: 0개 행")

    mapper = ColumnMapper(data_type='ecommerce')

    try:
        mapping = mapper.auto_map_columns(df)
        print(f"\n매핑 결과: {len(mapping)}개 컬럼 매핑됨")
        print("\n[PASS] 테스트 4 통과! (에러 없이 처리)")
        return True
    except Exception as e:
        print(f"\n[FAIL] 예상치 못한 에러: {e}")
        raise


def test_all_missing_column():
    """테스트 5: 결측치 100% 컬럼"""
    print("\n" + "="*60)
    print("테스트 5: 결측치 100% 컬럼")
    print("="*60)

    df = pd.DataFrame({
        'CustomerID': [1, 2, 3],
        'Price': [None, None, None]
    })

    print("\n입력 데이터 (Price 컬럼 전부 결측):")
    print(df.head())

    mapper = ColumnMapper(data_type='ecommerce')

    try:
        analysis = mapper.analyze_column_data(df, 'Price')
        print(f"\n분석 결과:")
        print(f"  missing_ratio: {analysis['missing_ratio']:.0%}")
        print(f"  is_numeric: {analysis['is_numeric']}")

        assert analysis['missing_ratio'] == 1.0, "결측치 비율이 100%여야 함"
        print("\n[PASS] 테스트 5 통과! (결측치 100% 처리)")
        return True
    except Exception as e:
        print(f"\n[FAIL] 예상치 못한 에러: {e}")
        raise


def test_invalid_data_type_error_message():
    """테스트 6: 잘못된 데이터 타입 에러 메시지"""
    print("\n" + "="*60)
    print("테스트 6: 개선된 에러 메시지 검증")
    print("="*60)

    try:
        mapper = ColumnMapper(data_type='invalid_type')
        print("\n[FAIL] ValueError가 발생하지 않음")
        return False
    except ValueError as e:
        error_msg = str(e)
        print(f"\n에러 메시지: {error_msg}")

        # 검증: 에러 메시지에 사용 가능한 타입 포함되어야 함
        assert 'ecommerce' in error_msg, "에러 메시지에 ecommerce가 포함되어야 함"
        assert 'review' in error_msg, "에러 메시지에 review가 포함되어야 함"
        assert 'sales' in error_msg, "에러 메시지에 sales가 포함되어야 함"

        print("\n[PASS] 테스트 6 통과! (유용한 에러 메시지)")
        return True


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("코드 리뷰 수정사항 검증 테스트 시작")
    print("="*60)

    tests = [
        test_duplicate_mapping_detection,
        test_date_parsing_performance,
        test_type_inference_priority,
        test_empty_dataframe,
        test_all_missing_column,
        test_invalid_data_type_error_message
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
        print("\n[SUCCESS] 모든 수정사항 검증 완료!")
        return True
    else:
        print(f"\n[WARNING] {failed}개 테스트 실패")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
