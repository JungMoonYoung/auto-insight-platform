"""
SQL Query Generator Module
분석 로직을 SQL 쿼리로 자동 변환

DAY 35: Phase 4 - SQL 역량 강화
복잡한 SQL 쿼리 작성 능력 증명 (CTE, Window Functions, 집계 등)
"""

from typing import Optional, Dict, List
from datetime import datetime, date
import re


class SQLQueryGenerator:
    """SQL 쿼리 자동 생성기"""

    def __init__(self, table_prefix: str = ''):
        """
        Args:
            table_prefix: 테이블 이름 접두사 (스키마명 등)
        """
        self.table_prefix = table_prefix

    def _validate_date(self, date_str: str) -> str:
        """
        날짜 형식 검증 (SQL Injection 방지)

        Args:
            date_str: 날짜 문자열 (YYYY-MM-DD)

        Returns:
            str: 검증된 날짜 문자열

        Raises:
            ValueError: 잘못된 날짜 형식
        """
        # YYYY-MM-DD 형식 검증
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")

        # 실제 날짜로 파싱 가능한지 확인
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date: {date_str}. {str(e)}")

        return date_str

    def _format_query(self, query: str) -> str:
        """
        SQL 쿼리 포맷팅 (들여쓰기 정리 및 주석 제거)

        Args:
            query: 원본 SQL 쿼리

        Returns:
            str: 포맷팅된 SQL 쿼리 (주석 제거됨)
        """
        lines = query.strip().split('\n')
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            # 주석 라인 제거 (-- 로 시작하는 라인)
            if stripped.startswith('--'):
                continue
            # 빈 줄 제거
            if not stripped:
                continue
            formatted_lines.append(stripped)

        return '\n'.join(formatted_lines)

    # ==================== RFM 분석 SQL ====================

    def generate_rfm_query(
        self,
        reference_date: Optional[str] = None,
        max_score: int = 5
    ) -> str:
        """
        RFM 분석 SQL 쿼리 생성 (CTE + Window Functions 사용)

        Args:
            reference_date: 기준일 (YYYY-MM-DD), None이면 현재 날짜
            max_score: 최대 RFM 점수 (기본: 5, 1~10 범위)

        Returns:
            str: RFM 분석 SQL 쿼리

        Raises:
            ValueError: 잘못된 날짜 형식 또는 max_score 범위

        SQL 역량 증명:
            - CTE (WITH 절) 3단계
            - Window Functions (NTILE)
            - JULIANDAY (날짜 계산)
            - CASE WHEN (세그먼트 분류)
            - GROUP BY, Aggregate Functions
        """
        if reference_date is None:
            reference_date = datetime.now().strftime('%Y-%m-%d')
        else:
            reference_date = self._validate_date(reference_date)  # 검증 추가

        # max_score 범위 검증
        if not 1 <= max_score <= 10:
            raise ValueError(f"max_score must be between 1 and 10, got {max_score}")

        query = f"""
-- ============================================================
-- RFM 분석 SQL 쿼리 (자동 생성)
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- 기준일: {reference_date}
-- ============================================================

-- Step 1: 고객별 RFM 지표 계산
WITH customer_rfm AS (
    SELECT
        customer_id,
        -- Recency: 마지막 구매일로부터 경과 일수 (낮을수록 좋음)
        CAST(JULIANDAY('{reference_date}') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS recency,
        -- Frequency: 총 거래 건수 (높을수록 좋음)
        COUNT(*) AS frequency,
        -- Monetary: 총 매출액 (높을수록 좋음)
        ROUND(SUM(quantity * unit_price), 2) AS monetary
    FROM {self.table_prefix}transactions
    WHERE quantity > 0
      AND unit_price > 0
      AND invoice_date <= '{reference_date}'
    GROUP BY customer_id
    HAVING monetary > 0  -- 유효한 거래만
),

-- Step 2: RFM 점수 계산 (NTILE로 분위수 분할)
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        -- R 점수: Recency 낮을수록 높은 점수 (역순 정렬)
        NTILE({max_score}) OVER (ORDER BY recency ASC) AS r_score,
        -- F 점수: Frequency 높을수록 높은 점수
        NTILE({max_score}) OVER (ORDER BY frequency DESC) AS f_score,
        -- M 점수: Monetary 높을수록 높은 점수
        NTILE({max_score}) OVER (ORDER BY monetary DESC) AS m_score
    FROM customer_rfm
),

-- Step 3: 고객 세그먼트 분류
customer_segments AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        -- 종합 RFM 점수 (평균)
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_score,
        -- 고객 세그먼트 자동 분류
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP 고객'
            WHEN r_score >= 4 AND (f_score >= 3 OR m_score >= 3) THEN '충성 고객'
            WHEN r_score >= 3 AND f_score >= 3 THEN '잠재 우수 고객'
            WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN '이탈 위험 고객'
            WHEN r_score <= 2 AND f_score <= 2 THEN '휴면 고객'
            WHEN f_score <= 2 AND m_score <= 2 THEN '신규/일회성 고객'
            ELSE '일반 고객'
        END AS segment
    FROM rfm_scores
)

-- 최종 결과 조회
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    rfm_score,
    segment
FROM customer_segments
ORDER BY rfm_score DESC, monetary DESC;

-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. CTE 3단계 중첩 (customer_rfm → rfm_scores → customer_segments)
-- 2. Window Functions (NTILE) 사용
-- 3. JULIANDAY로 날짜 계산
-- 4. CASE WHEN으로 복잡한 비즈니스 로직 구현
-- 5. GROUP BY, HAVING, Aggregate Functions
-- ============================================================
"""
        return self._format_query(query)

    # ==================== 매출 분석 SQL ====================

    def generate_sales_trend_query(
        self,
        period: str = 'daily',
        moving_average_days: int = 7
    ) -> str:
        """
        매출 트렌드 분석 SQL 쿼리 (이동평균 포함)

        Args:
            period: 집계 기간 ('daily', 'weekly', 'monthly')
            moving_average_days: 이동평균 기간 (일)

        Returns:
            str: 매출 트렌드 SQL 쿼리

        SQL 역량 증명:
            - Window Functions (AVG OVER, LAG)
            - ROWS BETWEEN (이동평균)
            - 날짜 함수 (DATE, strftime)
            - 전월 대비 성장률 계산
        """
        # 기간별 날짜 포맷
        date_formats = {
            'daily': '%Y-%m-%d',
            'weekly': '%Y-W%W',
            'monthly': '%Y-%m'
        }
        date_format = date_formats.get(period, '%Y-%m-%d')

        query = f"""
-- ============================================================
-- 매출 트렌드 분석 SQL 쿼리 ({period})
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================

-- Step 1: 기간별 매출 집계
WITH period_sales AS (
    SELECT
        strftime('{date_format}', sales_date) AS period,
        DATE(sales_date) AS sales_date,
        ROUND(SUM(revenue), 2) AS total_sales,
        SUM(quantity) AS total_quantity,
        COUNT(DISTINCT product) AS unique_products
    FROM {self.table_prefix}sales
    WHERE sales_date IS NOT NULL
    GROUP BY strftime('{date_format}', sales_date), DATE(sales_date)
),

-- Step 2: 이동평균 및 성장률 계산
sales_with_metrics AS (
    SELECT
        period,
        sales_date,
        total_sales,
        total_quantity,
        unique_products,
        -- {moving_average_days}일 이동평균 (Window Function 사용)
        ROUND(AVG(total_sales) OVER (
            ORDER BY sales_date
            ROWS BETWEEN {moving_average_days - 1} PRECEDING AND CURRENT ROW
        ), 2) AS moving_avg_{moving_average_days}d,
        -- 전 기간 대비 성장률 (LAG 사용)
        LAG(total_sales, 1) OVER (ORDER BY sales_date) AS prev_sales,
        ROUND(
            (total_sales - LAG(total_sales, 1) OVER (ORDER BY sales_date)) * 100.0 /
            NULLIF(LAG(total_sales, 1) OVER (ORDER BY sales_date), 0),
            2
        ) AS growth_rate_pct
    FROM period_sales
)

-- 최종 결과
SELECT
    period AS '기간',
    sales_date AS '날짜',
    total_sales AS '매출',
    moving_avg_{moving_average_days}d AS '{moving_average_days}일 이동평균',
    prev_sales AS '이전 기간 매출',
    growth_rate_pct AS '성장률 (%)',
    total_quantity AS '판매 수량',
    unique_products AS '상품 종류'
FROM sales_with_metrics
ORDER BY sales_date DESC;

-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. Window Functions: AVG OVER, LAG
-- 2. ROWS BETWEEN (이동평균 계산)
-- 3. 날짜 함수 (strftime, DATE)
-- 4. 성장률 계산 (전 기간 대비)
-- 5. NULLIF로 0 나누기 방지
-- ============================================================
"""
        return self._format_query(query)

    def generate_pareto_query(self, top_pct: int = 80) -> str:
        """
        파레토 분석 SQL 쿼리 (상위 N% 제품)

        Args:
            top_pct: 누적 매출 비율 (기본: 80%)

        Returns:
            str: 파레토 분석 SQL

        SQL 역량 증명:
            - Window Functions (SUM OVER, ROW_NUMBER)
            - 누적 합계 계산
            - 백분율 계산
        """
        query = f"""
-- ============================================================
-- 파레토 분석 SQL 쿼리 (상위 {top_pct}% 매출 제품)
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================

-- Step 1: 상품별 총 매출 계산
WITH product_sales AS (
    SELECT
        product,
        category,
        ROUND(SUM(revenue), 2) AS total_sales,
        SUM(quantity) AS total_quantity
    FROM {self.table_prefix}sales
    GROUP BY product, category
),

-- Step 2: 누적 매출 및 백분율 계산
cumulative_sales AS (
    SELECT
        product,
        category,
        total_sales,
        total_quantity,
        -- 순위 (매출 높은 순)
        ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS sales_rank,
        -- 누적 매출 (Window Function 사용)
        ROUND(SUM(total_sales) OVER (
            ORDER BY total_sales DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS cumulative_sales,
        -- 전체 매출 대비 비율
        ROUND(total_sales * 100.0 / SUM(total_sales) OVER (), 2) AS sales_pct,
        -- 누적 매출 비율
        ROUND(SUM(total_sales) OVER (
            ORDER BY total_sales DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) * 100.0 / SUM(total_sales) OVER (), 2) AS cumulative_pct
    FROM product_sales
)

-- Step 3: 상위 {top_pct}% 매출 제품만 필터링
SELECT
    sales_rank AS '순위',
    product AS '상품명',
    category AS '카테고리',
    total_sales AS '총 매출',
    total_quantity AS '판매 수량',
    sales_pct AS '매출 비율 (%)',
    cumulative_sales AS '누적 매출',
    cumulative_pct AS '누적 비율 (%)'
FROM cumulative_sales
WHERE cumulative_pct <= {top_pct}
   OR sales_rank <= 10  -- 또는 상위 10개 상품
ORDER BY sales_rank;

-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. Window Functions: SUM OVER, ROW_NUMBER
-- 2. ROWS BETWEEN UNBOUNDED PRECEDING (누적 합계)
-- 3. 백분율 계산
-- 4. 복잡한 필터링 조건 (WHERE ... OR)
-- ============================================================
"""
        return self._format_query(query)

    # ==================== 감성 분석 SQL ====================

    def generate_sentiment_query(self) -> str:
        """
        감성 분석 SQL 쿼리 (키워드 기반)

        Returns:
            str: 감성 분석 SQL

        SQL 역량 증명:
            - CASE WHEN (조건부 로직)
            - LIKE (텍스트 패턴 매칭)
            - GROUP BY, COUNT
        """
        query = f"""
-- ============================================================
-- 감성 분석 SQL 쿼리 (키워드 기반)
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================

-- Step 1: 리뷰별 감성 분류
WITH review_sentiment AS (
    SELECT
        review_id,
        source,
        rating,
        review_text,
        review_date,
        -- 평점 기반 감성 분류
        CASE
            WHEN rating >= 8 THEN '긍정'
            WHEN rating >= 5 THEN '중립'
            WHEN rating < 5 THEN '부정'
            ELSE 'unknown'
        END AS sentiment_by_rating,
        -- 키워드 기반 감성 점수
        CASE
            WHEN review_text LIKE '%좋%' OR review_text LIKE '%최고%'
                 OR review_text LIKE '%훌륭%' OR review_text LIKE '%만족%' THEN 1
            WHEN review_text LIKE '%나쁘%' OR review_text LIKE '%별로%'
                 OR review_text LIKE '%최악%' OR review_text LIKE '%실망%' THEN -1
            ELSE 0
        END AS keyword_score,
        -- 최종 감성 (평점 + 키워드 결합)
        CASE
            WHEN rating >= 8 OR review_text LIKE '%좋%' OR review_text LIKE '%최고%' THEN '긍정'
            WHEN rating <= 3 OR review_text LIKE '%나쁘%' OR review_text LIKE '%최악%' THEN '부정'
            ELSE '중립'
        END AS final_sentiment
    FROM {self.table_prefix}reviews
    WHERE review_text IS NOT NULL
)

-- Step 2: 감성별 통계
SELECT
    final_sentiment AS '감성',
    COUNT(*) AS '리뷰 수',
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM review_sentiment), 2) AS '비율 (%)',
    ROUND(AVG(rating), 2) AS '평균 평점',
    MIN(review_date) AS '최초 리뷰 날짜',
    MAX(review_date) AS '최근 리뷰 날짜'
FROM review_sentiment
GROUP BY final_sentiment
ORDER BY
    CASE final_sentiment
        WHEN '긍정' THEN 1
        WHEN '중립' THEN 2
        WHEN '부정' THEN 3
        ELSE 4
    END;

-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. CASE WHEN (복잡한 조건부 로직)
-- 2. LIKE (텍스트 패턴 매칭)
-- 3. 서브쿼리로 전체 집계
-- 4. ORDER BY CASE (커스텀 정렬)
-- ============================================================
"""
        return self._format_query(query)

    # ==================== 상위 고객 조회 SQL ====================

    def generate_top_customers_query(self, limit: int = 20) -> str:
        """
        상위 고객 조회 SQL 쿼리

        Args:
            limit: 조회할 고객 수 (기본: 20)

        Returns:
            str: 상위 고객 SQL

        SQL 역량 증명:
            - JOIN
            - ORDER BY, LIMIT
            - 매출 기여도 계산
        """
        query = f"""
-- ============================================================
-- 상위 {limit}명 고객 조회
-- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================================

SELECT
    customer_id AS '고객 ID',
    COUNT(*) AS '거래 횟수',
    ROUND(SUM(quantity * unit_price), 2) AS '총 구매액',
    ROUND(AVG(quantity * unit_price), 2) AS '평균 구매액',
    ROUND(SUM(quantity * unit_price) * 100.0 / (
        SELECT SUM(quantity * unit_price) FROM {self.table_prefix}transactions
    ), 2) AS '매출 기여도 (%)',
    MIN(invoice_date) AS '첫 구매일',
    MAX(invoice_date) AS '최근 구매일',
    CAST(JULIANDAY('now') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS '마지막 구매 경과일'
FROM {self.table_prefix}transactions
WHERE quantity > 0 AND unit_price > 0
GROUP BY customer_id
ORDER BY SUM(quantity * unit_price) DESC
LIMIT {limit};

-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)
-- 2. 서브쿼리로 전체 매출 계산
-- 3. ORDER BY, LIMIT
-- 4. JULIANDAY로 날짜 계산
-- ============================================================
"""
        return self._format_query(query)

    # ==================== 유틸리티 함수 ====================

    def get_all_queries(self) -> Dict[str, str]:
        """
        모든 SQL 쿼리 반환 (딕셔너리)

        Returns:
            dict: {'쿼리명': 'SQL 쿼리'} 형태
        """
        return {
            'rfm_analysis': self.generate_rfm_query(),
            'sales_trend_daily': self.generate_sales_trend_query(period='daily'),
            'sales_trend_monthly': self.generate_sales_trend_query(period='monthly'),
            'pareto_analysis': self.generate_pareto_query(),
            'sentiment_analysis': self.generate_sentiment_query(),
            'top_customers': self.generate_top_customers_query()
        }

    def save_query_to_file(self, query_name: str, query: str, output_dir: str = 'docs/sql_examples'):
        """
        SQL 쿼리를 파일로 저장

        Args:
            query_name: 쿼리 이름
            query: SQL 쿼리 내용
            output_dir: 출력 디렉토리
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / f"{query_name}.sql"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(query)

        return str(file_path)
