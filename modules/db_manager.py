"""
DatabaseManager Module
SQLite 데이터베이스 관리 클래스

DAY 34: Phase 4 - SQL 역량 강화
크롤링 데이터 및 분석 데이터를 SQLite에 저장하고 관리
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite 데이터베이스 관리 클래스"""

    def __init__(self, db_path: str = 'data/analytics.db'):
        """
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._create_tables()
        logger.info(f"DatabaseManager initialized: {self.db_path}")

    def _connect(self):
        """데이터베이스 연결"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능
            logger.info("Database connection established")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """테이블 스키마 생성"""
        cursor = self.conn.cursor()

        # ========== 1. reviews 테이블 (크롤링 데이터) ==========
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,  -- 'naver_place', 'naver_movie' 등
            place_id TEXT,         -- 플레이스 ID (naver_place용)
            movie_id TEXT,         -- 영화 ID (naver_movie용)
            rating REAL,           -- 평점 (1-10)
            review_text TEXT,      -- 리뷰 내용
            author TEXT,           -- 작성자
            review_date DATE,      -- 리뷰 작성일
            image_count INTEGER DEFAULT 0,  -- 첨부 이미지 개수
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- DB 삽입 시간
            UNIQUE(source, author, review_text, review_date)  -- 중복 방지 (핵심 필드만)
        )
        """)

        # ========== 2. transactions 테이블 (E-commerce 데이터) ==========
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            invoice_no TEXT,
            invoice_date DATE NOT NULL,
            product TEXT,
            description TEXT,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(customer_id, invoice_no, product, invoice_date)  -- 중복 방지
        )
        """)

        # ========== 3. sales 테이블 (판매 데이터) ==========
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sales_date DATE NOT NULL,
            product TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            revenue REAL,  -- quantity * price
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sales_date, product)  -- 일별 상품별 중복 방지
        )
        """)

        self.conn.commit()
        logger.info("Tables created successfully")

        # 인덱스 생성 (성능 최적화)
        self._create_indexes()

    def _create_indexes(self):
        """인덱스 생성 (쿼리 성능 최적화)"""
        cursor = self.conn.cursor()

        # reviews 테이블 인덱스
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_date
        ON reviews(review_date)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_source
        ON reviews(source)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_rating
        ON reviews(rating)
        """)

        # transactions 테이블 인덱스
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_customer
        ON transactions(customer_id)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_date
        ON transactions(invoice_date)
        """)

        # sales 테이블 인덱스
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_date
        ON sales(sales_date)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_product
        ON sales(product)
        """)

        self.conn.commit()
        logger.info("Indexes created successfully")

    # ==================== CRUD 함수 ====================

    def insert_reviews(self, df: pd.DataFrame, source: str) -> int:
        """
        리뷰 데이터 삽입 (UPSERT)

        Args:
            df: 리뷰 데이터프레임
            source: 데이터 소스 ('naver_place', 'naver_movie' 등)

        Returns:
            int: 삽입된 행 수

        Expected columns:
            - rating: 평점
            - review_text or review or text: 리뷰 내용
            - author: 작성자 (선택)
            - review_date or date: 작성일 (선택)
            - place_id: 플레이스 ID (naver_place의 경우)
            - movie_id: 영화 ID (naver_movie의 경우)
        """
        df = df.copy()
        df['source'] = source

        # 컬럼명 정규화
        column_mapping = {
            'review': 'review_text',
            'text': 'review_text',
            'date': 'review_date',
            'score': 'rating'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 필수 컬럼 확인
        required_cols = ['review_text']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # 선택 컬럼 기본값 설정
        if 'rating' not in df.columns:
            df['rating'] = None
        if 'author' not in df.columns:
            df['author'] = 'Unknown'
        if 'review_date' not in df.columns:
            df['review_date'] = datetime.now().date()
        if 'image_count' not in df.columns:
            df['image_count'] = 0
        if 'place_id' not in df.columns:
            df['place_id'] = None
        if 'movie_id' not in df.columns:
            df['movie_id'] = None

        # 데이터 타입 변환 (SQLite 호환을 위해 문자열로 변환)
        if df['review_date'].dtype == 'object':
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')

        # Timestamp를 문자열로 변환 (SQLite 호환)
        df['review_date'] = df['review_date'].dt.strftime('%Y-%m-%d').where(df['review_date'].notna(), None)

        # 필요한 컬럼만 선택
        insert_cols = ['source', 'place_id', 'movie_id', 'rating',
                      'review_text', 'author', 'review_date', 'image_count']
        df_insert = df[insert_cols]

        # INSERT OR REPLACE 실행
        cursor = self.conn.cursor()
        inserted_count = 0

        for _, row in df_insert.iterrows():
            try:
                cursor.execute("""
                INSERT OR REPLACE INTO reviews
                (source, place_id, movie_id, rating, review_text, author, review_date, image_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(row))
                inserted_count += 1
            except sqlite3.Error as e:
                logger.warning(f"Failed to insert review: {e}")

        self.conn.commit()
        logger.info(f"Inserted {inserted_count} reviews from {source}")
        return inserted_count

    def insert_transactions(self, df: pd.DataFrame) -> int:
        """
        E-commerce 거래 데이터 삽입 (UPSERT)

        Args:
            df: 거래 데이터프레임

        Returns:
            int: 삽입된 행 수

        Expected columns:
            - customer_id or CustomerID: 고객 ID
            - invoice_date or InvoiceDate: 구매 날짜
            - quantity or Quantity: 수량
            - unit_price or UnitPrice: 단가
            - invoice_no or InvoiceNo: 송장 번호 (선택)
            - product or Description: 상품명 (선택)
        """
        df = df.copy()

        # 컬럼명 정규화
        column_mapping = {
            'CustomerID': 'customer_id',
            'InvoiceNo': 'invoice_no',
            'InvoiceDate': 'invoice_date',
            'Description': 'product',
            'Quantity': 'quantity',
            'UnitPrice': 'unit_price',
            'Country': 'country'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 필수 컬럼 확인
        required_cols = ['customer_id', 'invoice_date', 'quantity', 'unit_price']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # 선택 컬럼 기본값
        if 'invoice_no' not in df.columns:
            df['invoice_no'] = None
        if 'product' not in df.columns:
            df['product'] = 'Unknown'
        if 'description' not in df.columns:
            df['description'] = None
        if 'country' not in df.columns:
            df['country'] = None

        # 데이터 타입 변환 (SQLite 호환을 위해 문자열로 변환)
        if df['invoice_date'].dtype == 'object':
            df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')

        # Timestamp를 문자열로 변환 (SQLite 호환)
        df['invoice_date'] = df['invoice_date'].dt.strftime('%Y-%m-%d').where(df['invoice_date'].notna(), None)

        # 필요한 컬럼만 선택
        insert_cols = ['customer_id', 'invoice_no', 'invoice_date', 'product',
                      'description', 'quantity', 'unit_price', 'country']
        df_insert = df[insert_cols]

        # INSERT OR REPLACE 실행
        cursor = self.conn.cursor()
        inserted_count = 0

        for _, row in df_insert.iterrows():
            try:
                cursor.execute("""
                INSERT OR REPLACE INTO transactions
                (customer_id, invoice_no, invoice_date, product, description, quantity, unit_price, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(row))
                inserted_count += 1
            except sqlite3.Error as e:
                logger.warning(f"Failed to insert transaction: {e}")

        self.conn.commit()
        logger.info(f"Inserted {inserted_count} transactions")
        return inserted_count

    def insert_sales(self, df: pd.DataFrame) -> int:
        """
        판매 데이터 삽입 (UPSERT)

        Args:
            df: 판매 데이터프레임

        Returns:
            int: 삽입된 행 수

        Expected columns:
            - sales_date or date: 판매 날짜
            - product: 상품명
            - quantity: 수량
            - price: 가격
            - category: 카테고리 (선택)
        """
        df = df.copy()

        # 컬럼명 정규화
        column_mapping = {
            'date': 'sales_date',
            'Date': 'sales_date'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 필수 컬럼 확인
        required_cols = ['sales_date', 'product', 'quantity', 'price']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # revenue 계산
        df['revenue'] = df['quantity'] * df['price']

        # 선택 컬럼 기본값
        if 'category' not in df.columns:
            df['category'] = None

        # 데이터 타입 변환 (SQLite 호환을 위해 문자열로 변환)
        if df['sales_date'].dtype == 'object':
            df['sales_date'] = pd.to_datetime(df['sales_date'], errors='coerce')

        # Timestamp를 문자열로 변환 (SQLite 호환)
        df['sales_date'] = df['sales_date'].dt.strftime('%Y-%m-%d').where(df['sales_date'].notna(), None)

        # 필요한 컬럼만 선택
        insert_cols = ['sales_date', 'product', 'category', 'quantity', 'price', 'revenue']
        df_insert = df[insert_cols]

        # INSERT OR REPLACE 실행
        cursor = self.conn.cursor()
        inserted_count = 0

        for _, row in df_insert.iterrows():
            try:
                cursor.execute("""
                INSERT OR REPLACE INTO sales
                (sales_date, product, category, quantity, price, revenue)
                VALUES (?, ?, ?, ?, ?, ?)
                """, tuple(row))
                inserted_count += 1
            except sqlite3.Error as e:
                logger.warning(f"Failed to insert sales record: {e}")

        self.conn.commit()
        logger.info(f"Inserted {inserted_count} sales records")
        return inserted_count

    def get_data(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        SQL 쿼리 실행 및 DataFrame 반환

        Args:
            query: SQL SELECT 쿼리
            params: 쿼리 파라미터 (선택)

        Returns:
            pd.DataFrame: 쿼리 결과
        """
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            raise

    def delete_old_data(self, table: str, date_column: str, days: int) -> int:
        """
        특정 기간 이전 데이터 삭제

        Args:
            table: 테이블명 ('reviews', 'transactions', 'sales')
            date_column: 날짜 컬럼명
            days: 삭제할 기준 (N일 이전 데이터)

        Returns:
            int: 삭제된 행 수
        """
        cursor = self.conn.cursor()
        query = f"""
        DELETE FROM {table}
        WHERE {date_column} < date('now', '-{days} days')
        """
        cursor.execute(query)
        deleted_count = cursor.rowcount
        self.conn.commit()
        logger.info(f"Deleted {deleted_count} rows from {table}")
        return deleted_count

    def get_table_info(self, table: str) -> Dict[str, Any]:
        """
        테이블 정보 조회

        Args:
            table: 테이블명

        Returns:
            dict: 테이블 정보 (행 수, 컬럼 정보 등)
        """
        cursor = self.conn.cursor()

        # 행 수 조회
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]

        # 컬럼 정보 조회
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()

        return {
            'table_name': table,
            'row_count': row_count,
            'columns': [
                {
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'primary_key': bool(col[5])
                }
                for col in columns
            ]
        }

    def execute_query(self, query: str, params: tuple = ()) -> int:
        """
        일반 SQL 쿼리 실행 (INSERT, UPDATE, DELETE 등)

        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터

        Returns:
            int: 영향받은 행 수
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        affected_rows = cursor.rowcount
        self.conn.commit()
        return affected_rows

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def __del__(self):
        """소멸자"""
        self.close()
