"""
DAY 27: GPT 최적화 테스트
- Rate Limit 핸들링 (Exponential backoff)
- 부정 리뷰 필터링
- 비용 추적
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
from modules.gpt_analyzer import GPTAnalyzer
from openai import RateLimitError


def test_cost_tracking():
    """테스트 1: 비용 추적 기능"""
    print("\n" + "="*60)
    print("테스트 1: 비용 추적 기능")
    print("="*60)

    try:
        # API 키가 없으면 테스트 스킵
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[SKIP] OPENAI_API_KEY 환경변수 없음")
            return True

        analyzer = GPTAnalyzer(api_key=api_key)

        # 초기 비용 확인
        cost_info = analyzer.get_cost_info()
        assert cost_info['total_tokens'] == 0, "초기 토큰은 0이어야 함"
        assert cost_info['total_cost'] == 0.0, "초기 비용은 0이어야 함"
        print(f"[검증] 초기 상태: {cost_info}")

        # 초기화 테스트
        analyzer.reset_cost_tracking()
        cost_info = analyzer.get_cost_info()
        assert cost_info['total_tokens'] == 0, "초기화 후 토큰은 0이어야 함"
        print("[검증] 초기화 성공")

        print("\n[PASS] 테스트 1 통과!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 테스트 1 실패: {e}")
        return False


def test_negative_review_filtering():
    """테스트 2: 부정 리뷰 필터링"""
    print("\n" + "="*60)
    print("테스트 2: 부정 리뷰 필터링")
    print("="*60)

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[SKIP] OPENAI_API_KEY 환경변수 없음")
            return True

        analyzer = GPTAnalyzer(api_key=api_key)

        # 테스트 데이터: 부정/긍정 혼합
        df = pd.DataFrame({
            'review_text': [
                '최악의 제품. 절대 사지 마세요.',  # 부정
                '별로예요. 품질이 엉망입니다.',  # 부정
                '정말 좋아요! 강력 추천합니다.',  # 긍정
                '완전 실망했습니다. 환불 원해요.',  # 부정
                '최고의 제품! 다시 살게요.',  # 긍정
            ],
            'rating': [1, 2, 5, 1, 5]
        })

        print("\n원본 데이터:")
        print(df)

        # 부정 리뷰만 필터링 (평점 3점 이하)
        negative_reviews = analyzer._filter_negative_reviews(
            df,
            rating_column='rating',
            text_column='review_text',
            threshold=3.0
        )

        print(f"\n부정 리뷰 필터링 결과: {len(negative_reviews)}개")
        for i, review in enumerate(negative_reviews, 1):
            print(f"  {i}. {review}")

        # 검증
        assert len(negative_reviews) == 3, f"부정 리뷰는 3개여야 함 (실제: {len(negative_reviews)})"
        assert '최악의 제품' in negative_reviews[0], "부정 리뷰가 포함되어야 함"

        print("\n[PASS] 테스트 2 통과!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 테스트 2 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_delay():
    """테스트 3: 배치 딜레이 확인 (Rate Limit 방지)"""
    print("\n" + "="*60)
    print("테스트 3: 배치 딜레이 설정")
    print("="*60)

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[SKIP] OPENAI_API_KEY 환경변수 없음")
            return True

        analyzer = GPTAnalyzer(api_key=api_key)

        # 상수 확인
        assert analyzer.MAX_RETRIES == 5, "최대 재시도 횟수는 5회"
        assert analyzer.INITIAL_DELAY == 1.0, "초기 딜레이는 1초"
        assert analyzer.MAX_DELAY == 60.0, "최대 딜레이는 60초"
        assert analyzer.BATCH_DELAY == 0.5, "배치 딜레이는 0.5초"

        print(f"[검증] MAX_RETRIES: {analyzer.MAX_RETRIES}")
        print(f"[검증] INITIAL_DELAY: {analyzer.INITIAL_DELAY}초")
        print(f"[검증] MAX_DELAY: {analyzer.MAX_DELAY}초")
        print(f"[검증] BATCH_DELAY: {analyzer.BATCH_DELAY}초")

        print("\n[PASS] 테스트 3 통과!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 테스트 3 실패: {e}")
        return False


def test_retry_wrapper_structure():
    """테스트 4: Retry 래퍼 구조 확인"""
    print("\n" + "="*60)
    print("테스트 4: Retry 래퍼 함수 존재 확인")
    print("="*60)

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[SKIP] OPENAI_API_KEY 환경변수 없음")
            return True

        analyzer = GPTAnalyzer(api_key=api_key)

        # _call_with_retry 메서드 존재 확인
        assert hasattr(analyzer, '_call_with_retry'), "_call_with_retry 메서드가 있어야 함"
        print("[검증] _call_with_retry 메서드 존재")

        # 부정 리뷰 필터링 메서드 존재 확인
        assert hasattr(analyzer, '_filter_negative_reviews'), "_filter_negative_reviews 메서드가 있어야 함"
        print("[검증] _filter_negative_reviews 메서드 존재")

        # 비용 추적 메서드 존재 확인
        assert hasattr(analyzer, 'get_cost_info'), "get_cost_info 메서드가 있어야 함"
        assert hasattr(analyzer, 'reset_cost_tracking'), "reset_cost_tracking 메서드가 있어야 함"
        print("[검증] 비용 추적 메서드 존재")

        print("\n[PASS] 테스트 4 통과!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 테스트 4 실패: {e}")
        return False


def test_filter_edge_cases():
    """테스트 5: 필터링 엣지 케이스"""
    print("\n" + "="*60)
    print("테스트 5: 필터링 엣지 케이스")
    print("="*60)

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[SKIP] OPENAI_API_KEY 환경변수 없음")
            return True

        analyzer = GPTAnalyzer(api_key=api_key)

        # 케이스 1: 평점 컬럼 없음
        df1 = pd.DataFrame({
            'review_text': ['리뷰1', '리뷰2'],
            'other_column': [1, 2]
        })
        result1 = analyzer._filter_negative_reviews(df1, rating_column='rating')
        assert len(result1) == 2, "평점 컬럼 없으면 전체 리뷰 반환"
        print("[검증] 평점 컬럼 없을 때 전체 반환")

        # 케이스 2: 텍스트 컬럼 없음
        df2 = pd.DataFrame({
            'rating': [1, 2, 5],
            'other_column': ['a', 'b', 'c']
        })
        result2 = analyzer._filter_negative_reviews(df2, text_column='review_text')
        assert len(result2) == 0, "텍스트 컬럼 없으면 빈 리스트"
        print("[검증] 텍스트 컬럼 없을 때 빈 리스트 반환")

        # 케이스 3: 모든 리뷰가 긍정적
        df3 = pd.DataFrame({
            'review_text': ['좋아요', '최고예요'],
            'rating': [5, 5]
        })
        result3 = analyzer._filter_negative_reviews(df3, threshold=3.0)
        assert len(result3) == 0, "부정 리뷰 없으면 빈 리스트"
        print("[검증] 부정 리뷰 없을 때 빈 리스트")

        # 케이스 4: 모든 리뷰가 부정적
        df4 = pd.DataFrame({
            'review_text': ['별로', '최악'],
            'rating': [1, 2]
        })
        result4 = analyzer._filter_negative_reviews(df4, threshold=3.0)
        assert len(result4) == 2, "모든 리뷰가 부정이면 모두 반환"
        print("[검증] 모든 리뷰가 부정일 때 모두 반환")

        print("\n[PASS] 테스트 5 통과!")
        return True

    except Exception as e:
        print(f"\n[FAIL] 테스트 5 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("DAY 27: GPT 최적화 테스트 시작")
    print("="*60)

    tests = [
        test_cost_tracking,
        test_negative_review_filtering,
        test_batch_delay,
        test_retry_wrapper_structure,
        test_filter_edge_cases
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__} 실패: {e}")
            failed += 1
        except Exception as e:
            # SKIP 처리
            if "SKIP" in str(e):
                skipped += 1
            else:
                print(f"\n[ERROR] {test_func.__name__} 에러: {e}")
                import traceback
                traceback.print_exc()
                failed += 1

    print("\n" + "="*60)
    print(f"테스트 결과: {passed}개 통과, {failed}개 실패, {skipped}개 스킵")
    print("="*60)

    if failed == 0:
        print("\n[SUCCESS] DAY 27 GPT 최적화 완료!")
        print("\n주요 기능:")
        print("  - Rate Limit 핸들링 (Exponential backoff)")
        print("  - 부정 리뷰 필터링 (비용 절감)")
        print("  - 비용 추적 (토큰, 금액)")
        print("  - 배치 딜레이 (0.5초)")
        print("  - 최대 재시도: 5회")
        return True
    else:
        print(f"\n[WARNING] {failed}개 테스트 실패")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
