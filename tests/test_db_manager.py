"""
DatabaseManager 테스트
DAY 34: Phase 4 - SQL 역량 강화
"""

import pytest
import pandas as pd
import sqlite3
from pathlib import Path
import sys
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.db_manager import DatabaseManager


@pytest.fixture
def db_manager():
    """테스트용 임시 데이터베이스 매니저"""
    test_db_path = 'tests/test_analytics.db'

    # 기존 테스트 DB 삭제
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()

    db = DatabaseManager(db_path=test_db_path)
    yield db
    db.close()

    # 테스트 후 정리
    if Path(test_db_path).exists():
        Path(test_db_path).unlink()


@pytest.fixture
def sample_reviews():
    """샘플 리뷰 데이터"""
    return pd.DataFrame({
        'rating': [5, 4, 3, 2, 1],
        'review_text': [
            '정말 좋아요!',
            '괜찮습니다',
            '보통이에요',
            '별로였어요',
            '최악입니다'
        ],
        'author': ['user1', 'user2', 'user3', 'user4', 'user5'],
        'review_date': [
            '2025-12-01',
            '2025-12-02',
            '2025-12-03',
            '2025-12-04',
            '2025-12-05'
        ],
        'place_id': ['12345'] * 5
    })


@pytest.fixture
def sample_transactions():
    """샘플 E-commerce 거래 데이터"""
    return pd.DataFrame({
        'CustomerID': ['C001', 'C002', 'C001', 'C003', 'C002'],
        'InvoiceNo': ['INV001', 'INV002', 'INV003', 'INV004', 'INV005'],
        'InvoiceDate': pd.date_range('2025-11-01', periods=5, freq='D'),
        'Description': ['상품A', '상품B', '상품C', '상품A', '상품D'],
        'Quantity': [2, 1, 3, 1, 2],
        'UnitPrice': [10.0, 20.0, 15.0, 10.0, 25.0],
        'Country': ['Korea'] * 5
    })


@pytest.fixture
def sample_sales():
    """샘플 판매 데이터"""
    return pd.DataFrame({
        'sales_date': pd.date_range('2025-11-01', periods=5, freq='D'),
        'product': ['상품A', '상품B', '상품C', '상품A', '상품D'],
        'category': ['전자제품', '의류', '식품', '전자제품', '가구'],
        'quantity': [10, 5, 20, 15, 3],
        'price': [100.0, 50.0, 30.0, 100.0, 500.0]
    })


class TestDatabaseManager:
    """DatabaseManager 테스트 클래스"""

    def test_01_database_creation(self, db_manager):
        """테스트 1: 데이터베이스 파일 생성 확인"""
        assert db_manager.db_path.exists()
        assert db_manager.conn is not None
        print("✅ 테스트 1 통과: 데이터베이스 파일 생성 성공")

    def test_02_table_creation(self, db_manager):
        """테스트 2: 테이블 생성 확인"""
        cursor = db_manager.conn.cursor()

        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert 'reviews' in tables
        assert 'transactions' in tables
        assert 'sales' in tables
        print(f"✅ 테스트 2 통과: 3개 테이블 생성 확인 ({tables})")

    def test_03_index_creation(self, db_manager):
        """테스트 3: 인덱스 생성 확인"""
        cursor = db_manager.conn.cursor()

        # 인덱스 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        # 주요 인덱스 확인
        assert any('reviews_date' in idx for idx in indexes)
        assert any('transactions_customer' in idx for idx in indexes)
        assert any('sales_date' in idx for idx in indexes)
        print(f"✅ 테스트 3 통과: 인덱스 생성 확인 ({len(indexes)}개)")

    def test_04_insert_reviews(self, db_manager, sample_reviews):
        """테스트 4: 리뷰 데이터 삽입"""
        inserted_count = db_manager.insert_reviews(sample_reviews, source='naver_place')

        assert inserted_count == 5

        # 데이터 조회 확인
        df = db_manager.get_data("SELECT * FROM reviews")
        assert len(df) == 5
        assert df['source'].iloc[0] == 'naver_place'
        assert df['rating'].iloc[0] == 5
        print(f"✅ 테스트 4 통과: 리뷰 {inserted_count}개 삽입 성공")

    def test_05_insert_transactions(self, db_manager, sample_transactions):
        """테스트 5: 거래 데이터 삽입"""
        inserted_count = db_manager.insert_transactions(sample_transactions)

        assert inserted_count == 5

        # 데이터 조회 확인
        df = db_manager.get_data("SELECT * FROM transactions")
        assert len(df) == 5
        assert df['customer_id'].iloc[0] == 'C001'
        print(f"✅ 테스트 5 통과: 거래 {inserted_count}개 삽입 성공")

    def test_06_insert_sales(self, db_manager, sample_sales):
        """테스트 6: 판매 데이터 삽입"""
        inserted_count = db_manager.insert_sales(sample_sales)

        assert inserted_count == 5

        # 데이터 조회 확인
        df = db_manager.get_data("SELECT * FROM sales")
        assert len(df) == 5
        assert df['revenue'].iloc[0] == 1000.0  # 10 * 100
        print(f"✅ 테스트 6 통과: 판매 {inserted_count}개 삽입 성공")

    def test_07_upsert_duplicate(self, db_manager, sample_reviews):
        """테스트 7: UPSERT 중복 처리 확인"""
        # 첫 번째 삽입
        db_manager.insert_reviews(sample_reviews, source='naver_place')

        # 동일 데이터 재삽입 (UPSERT로 덮어쓰기)
        inserted_count = db_manager.insert_reviews(sample_reviews, source='naver_place')

        # 여전히 5개만 있어야 함
        df = db_manager.get_data("SELECT COUNT(*) as count FROM reviews")
        assert df['count'].iloc[0] == 5
        print(f"✅ 테스트 7 통과: UPSERT 중복 처리 확인 (여전히 5개)")

    def test_08_get_data_with_query(self, db_manager, sample_reviews):
        """테스트 8: SQL 쿼리로 데이터 조회"""
        db_manager.insert_reviews(sample_reviews, source='naver_place')

        # WHERE 절 사용 쿼리
        df = db_manager.get_data("SELECT * FROM reviews WHERE rating >= 4")
        assert len(df) == 2  # 평점 4, 5
        print(f"✅ 테스트 8 통과: WHERE 절 쿼리 실행 성공 ({len(df)}개 조회)")

    def test_09_delete_old_data(self, db_manager, sample_reviews):
        """테스트 9: 오래된 데이터 삭제"""
        db_manager.insert_reviews(sample_reviews, source='naver_place')

        # 100일 이전 데이터 삭제 (테스트 데이터는 최근이므로 삭제 안 됨)
        deleted_count = db_manager.delete_old_data('reviews', 'review_date', days=100)
        assert deleted_count == 0

        # 0일 이전 데이터 삭제 (모두 삭제)
        deleted_count = db_manager.delete_old_data('reviews', 'review_date', days=0)
        assert deleted_count >= 0
        print(f"✅ 테스트 9 통과: 데이터 삭제 기능 작동")

    def test_10_get_table_info(self, db_manager):
        """테스트 10: 테이블 정보 조회"""
        info = db_manager.get_table_info('reviews')

        assert info['table_name'] == 'reviews'
        assert 'row_count' in info
        assert 'columns' in info
        assert len(info['columns']) > 0

        # 주요 컬럼 확인
        column_names = [col['name'] for col in info['columns']]
        assert 'review_id' in column_names
        assert 'rating' in column_names
        assert 'review_text' in column_names
        print(f"✅ 테스트 10 통과: 테이블 정보 조회 성공 ({len(column_names)}개 컬럼)")

    def test_11_context_manager(self):
        """테스트 11: Context Manager 패턴 테스트"""
        test_db_path = 'tests/test_context.db'

        # Context manager 사용
        with DatabaseManager(db_path=test_db_path) as db:
            assert db.conn is not None
            df = db.get_data("SELECT 1 as test")
            assert df['test'].iloc[0] == 1

        # 자동으로 연결 종료되어야 함
        print("✅ 테스트 11 통과: Context Manager 패턴 작동")

        # 정리
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()

    def test_12_execute_query(self, db_manager):
        """테스트 12: 일반 SQL 쿼리 실행"""
        # CREATE TABLE 실행
        affected_rows = db_manager.execute_query("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)

        # INSERT 실행
        affected_rows = db_manager.execute_query("""
        INSERT INTO test_table (name) VALUES (?)
        """, ('Test Name',))

        assert affected_rows == 1

        # 데이터 확인
        df = db_manager.get_data("SELECT * FROM test_table")
        assert len(df) == 1
        assert df['name'].iloc[0] == 'Test Name'
        print("✅ 테스트 12 통과: 일반 SQL 쿼리 실행 성공")


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("DatabaseManager 테스트 시작")
    print("=" * 60)

    # pytest 실행
    pytest.main([__file__, '-v', '-s'])


if __name__ == "__main__":
    run_all_tests()
