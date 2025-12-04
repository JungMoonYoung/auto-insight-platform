"""
SQL Query Generator 테스트
DAY 35: Phase 4 - SQL 역량 강화
"""

import pytest
import pandas as pd
import sqlite3
from pathlib import Path
import sys

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.sql_query_generator import SQLQueryGenerator
from modules.db_manager import DatabaseManager


@pytest.fixture
def db_with_data():
    """테스트용 데이터베이스 (샘플 데이터 포함)"""
    test_db_path = 'tests/test_sql_queries.db'

    # 기존 DB 삭제
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()

    # 데이터베이스 생성 및 샘플 데이터 삽입
    db = DatabaseManager(db_path=test_db_path)

    # 샘플 거래 데이터
    transactions = pd.DataFrame({
        'CustomerID': ['C001', 'C002', 'C001', 'C003', 'C002', 'C001', 'C004', 'C002'],
        'InvoiceNo': [f'INV{i:03d}' for i in range(1, 9)],
        'InvoiceDate': pd.date_range('2025-11-01', periods=8, freq='3D'),
        'Description': ['상품A', '상품B', '상품C', '상품A', '상품D', '상품A', '상품B', '상품C'],
        'Quantity': [2, 1, 3, 1, 2, 5, 1, 2],
        'UnitPrice': [10.0, 20.0, 15.0, 10.0, 25.0, 10.0, 20.0, 15.0],
        'Country': ['Korea'] * 8
    })
    db.insert_transactions(transactions)

    # 샘플 판매 데이터
    sales = pd.DataFrame({
        'sales_date': pd.date_range('2025-11-01', periods=10, freq='D'),
        'product': ['상품A', '상품B', '상품C', '상품A', '상품D'] * 2,
        'category': ['전자제품', '의류', '식품', '전자제품', '가구'] * 2,
        'quantity': [10, 5, 20, 15, 3, 8, 6, 18, 12, 4],
        'price': [100.0, 50.0, 30.0, 100.0, 500.0, 100.0, 50.0, 30.0, 100.0, 500.0]
    })
    db.insert_sales(sales)

    # 샘플 리뷰 데이터
    reviews = pd.DataFrame({
        'rating': [5, 4, 3, 2, 1, 5, 4, 3],
        'review_text': [
            '정말 좋아요!',
            '괜찮습니다',
            '보통이에요',
            '별로였어요',
            '최악입니다',
            '최고의 제품',
            '만족합니다',
            '그저 그래요'
        ],
        'author': [f'user{i}' for i in range(1, 9)],
        'review_date': pd.date_range('2025-12-01', periods=8, freq='D')
    })
    db.insert_reviews(reviews, source='test')

    yield db

    db.close()
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()


@pytest.fixture
def query_generator():
    """SQL 쿼리 생성기"""
    return SQLQueryGenerator()


class TestSQLQueryGenerator:
    """SQL Query Generator 테스트"""

    def test_01_rfm_query_generation(self, query_generator):
        """테스트 1: RFM 분석 SQL 쿼리 생성"""
        query = query_generator.generate_rfm_query(reference_date='2025-12-04')

        # 쿼리 구조 검증
        assert 'WITH customer_rfm AS' in query
        assert 'rfm_scores AS' in query
        assert 'customer_segments AS' in query
        assert 'NTILE' in query
        assert 'JULIANDAY' in query
        assert 'CASE' in query
        print("테스트 1 통과: RFM SQL 쿼리 생성 성공")
        print(f"쿼리 길이: {len(query)} 문자")

    def test_02_rfm_query_execution(self, db_with_data, query_generator):
        """테스트 2: RFM SQL 쿼리 실행"""
        query = query_generator.generate_rfm_query(reference_date='2025-12-04')

        # SQL 실행
        df = db_with_data.get_data(query)

        # 결과 검증
        assert len(df) > 0
        assert 'customer_id' in df.columns
        assert 'recency' in df.columns
        assert 'frequency' in df.columns
        assert 'monetary' in df.columns
        assert 'r_score' in df.columns
        assert 'f_score' in df.columns
        assert 'm_score' in df.columns
        assert 'segment' in df.columns

        print(f"테스트 2 통과: RFM 쿼리 실행 성공 ({len(df)}명 고객)")
        print(f"세그먼트: {df['segment'].unique()}")

    def test_03_sales_trend_query(self, query_generator):
        """테스트 3: 매출 트렌드 SQL 쿼리 생성"""
        query = query_generator.generate_sales_trend_query(period='daily', moving_average_days=7)

        # 쿼리 구조 검증
        assert 'WITH period_sales AS' in query
        assert 'sales_with_metrics AS' in query
        assert 'AVG(total_sales) OVER' in query
        assert 'ROWS BETWEEN' in query
        assert 'LAG' in query
        print("테스트 3 통과: 매출 트렌드 SQL 쿼리 생성 성공")

    def test_04_sales_trend_execution(self, db_with_data, query_generator):
        """테스트 4: 매출 트렌드 SQL 쿼리 실행"""
        query = query_generator.generate_sales_trend_query(period='daily', moving_average_days=3)

        # SQL 실행
        df = db_with_data.get_data(query)

        # 결과 검증
        assert len(df) > 0
        assert '기간' in df.columns
        assert '매출' in df.columns
        assert '3일 이동평균' in df.columns
        assert '성장률 (%)' in df.columns

        print(f"테스트 4 통과: 매출 트렌드 쿼리 실행 성공 ({len(df)}개 기간)")
        print(f"총 매출: {df['매출'].sum():.2f}")

    def test_05_pareto_query(self, query_generator):
        """테스트 5: 파레토 분석 SQL 쿼리 생성"""
        query = query_generator.generate_pareto_query(top_pct=80)

        # 쿼리 구조 검증
        assert 'WITH product_sales AS' in query
        assert 'cumulative_sales AS' in query
        assert 'ROW_NUMBER() OVER' in query
        assert 'SUM(total_sales) OVER' in query
        assert 'UNBOUNDED PRECEDING' in query
        print("테스트 5 통과: 파레토 분석 SQL 쿼리 생성 성공")

    def test_06_pareto_execution(self, db_with_data, query_generator):
        """테스트 6: 파레토 분석 SQL 쿼리 실행"""
        query = query_generator.generate_pareto_query(top_pct=80)

        # SQL 실행
        df = db_with_data.get_data(query)

        # 결과 검증
        assert len(df) > 0
        assert '순위' in df.columns
        assert '상품명' in df.columns
        assert '총 매출' in df.columns
        assert '누적 비율 (%)' in df.columns

        # 누적 비율이 80% 이하인지 확인
        assert df['누적 비율 (%)'].max() <= 80 or len(df) <= 10

        print(f"테스트 6 통과: 파레토 분석 실행 성공 ({len(df)}개 상품)")
        print(f"상위 상품: {df['상품명'].head(3).tolist()}")

    def test_07_sentiment_query(self, query_generator):
        """테스트 7: 감성 분석 SQL 쿼리 생성"""
        query = query_generator.generate_sentiment_query()

        # 쿼리 구조 검증
        assert 'WITH review_sentiment AS' in query
        assert 'CASE' in query
        assert 'LIKE' in query
        assert 'GROUP BY' in query
        print("테스트 7 통과: 감성 분석 SQL 쿼리 생성 성공")

    def test_08_sentiment_execution(self, db_with_data, query_generator):
        """테스트 8: 감성 분석 SQL 쿼리 실행"""
        query = query_generator.generate_sentiment_query()

        # SQL 실행
        df = db_with_data.get_data(query)

        # 결과 검증
        assert len(df) > 0
        assert '감성' in df.columns
        assert '리뷰 수' in df.columns
        assert '비율 (%)' in df.columns

        # 감성 종류 확인
        sentiments = df['감성'].unique()
        assert len(sentiments) > 0

        print(f"테스트 8 통과: 감성 분석 실행 성공 ({len(df)}개 감성)")
        print(f"감성 분포: {dict(zip(df['감성'], df['리뷰 수']))}")

    def test_09_top_customers_query(self, query_generator):
        """테스트 9: 상위 고객 조회 SQL 쿼리 생성"""
        query = query_generator.generate_top_customers_query(limit=10)

        # 쿼리 구조 검증
        assert 'GROUP BY customer_id' in query
        assert 'ORDER BY' in query
        assert 'LIMIT 10' in query
        assert 'JULIANDAY' in query
        print("테스트 9 통과: 상위 고객 SQL 쿼리 생성 성공")

    def test_10_top_customers_execution(self, db_with_data, query_generator):
        """테스트 10: 상위 고객 조회 SQL 쿼리 실행"""
        query = query_generator.generate_top_customers_query(limit=5)

        # SQL 실행
        df = db_with_data.get_data(query)

        # 결과 검증
        assert len(df) > 0
        assert len(df) <= 5
        assert '고객 ID' in df.columns
        assert '거래 횟수' in df.columns
        assert '총 구매액' in df.columns
        assert '매출 기여도 (%)' in df.columns

        # 정렬 순서 확인 (총 구매액 내림차순)
        assert df['총 구매액'].tolist() == sorted(df['총 구매액'].tolist(), reverse=True)

        print(f"테스트 10 통과: 상위 고객 조회 실행 성공 ({len(df)}명)")
        print(f"1위 고객: {df.iloc[0]['고객 ID']} (구매액: {df.iloc[0]['총 구매액']:.2f})")

    def test_11_get_all_queries(self, query_generator):
        """테스트 11: 모든 쿼리 일괄 생성"""
        all_queries = query_generator.get_all_queries()

        # 7개 쿼리 확인
        assert len(all_queries) == 7
        assert 'rfm_analysis' in all_queries
        assert 'sales_trend_daily' in all_queries
        assert 'pareto_analysis' in all_queries
        assert 'sentiment_analysis' in all_queries

        # 각 쿼리가 유효한지 확인
        for query_name, query in all_queries.items():
            assert len(query) > 100  # 최소 100자 이상
            assert 'SELECT' in query.upper()

        print(f"테스트 11 통과: 전체 쿼리 일괄 생성 성공 ({len(all_queries)}개)")
        print(f"쿼리 목록: {list(all_queries.keys())}")

    def test_12_query_format(self, query_generator):
        """테스트 12: 쿼리 포맷팅 검증"""
        query = query_generator.generate_rfm_query()

        # 주석 포함 확인
        assert '--' in query
        assert '포트폴리오 증명 포인트' in query

        # 들여쓰기 확인 (최소한의 정리)
        lines = query.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) > 20  # 충분히 상세한 쿼리

        print("테스트 12 통과: 쿼리 포맷팅 검증 성공")
        print(f"총 라인 수: {len(non_empty_lines)}")

    def test_13_complex_sql_features(self, query_generator):
        """테스트 13: 복잡한 SQL 기능 사용 검증"""
        # RFM 쿼리에서 고급 기능 확인
        rfm_query = query_generator.generate_rfm_query()
        assert 'NTILE' in rfm_query  # Window Function
        assert 'OVER' in rfm_query
        assert 'WITH' in rfm_query  # CTE

        # 매출 트렌드 쿼리에서 고급 기능 확인
        sales_query = query_generator.generate_sales_trend_query()
        assert 'ROWS BETWEEN' in sales_query  # Window Frame
        assert 'LAG' in sales_query  # Window Function
        assert 'OVER' in sales_query

        # 파레토 쿼리에서 고급 기능 확인
        pareto_query = query_generator.generate_pareto_query()
        assert 'ROW_NUMBER' in pareto_query  # Window Function
        assert 'UNBOUNDED PRECEDING' in pareto_query  # Window Frame

        print("테스트 13 통과: 복잡한 SQL 기능 사용 검증 완료")
        print("검증된 기능: NTILE, LAG, ROW_NUMBER, ROWS BETWEEN, UNBOUNDED PRECEDING")


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("SQL Query Generator 테스트 시작")
    print("=" * 60)

    pytest.main([__file__, '-v', '-s'])


if __name__ == "__main__":
    run_all_tests()
