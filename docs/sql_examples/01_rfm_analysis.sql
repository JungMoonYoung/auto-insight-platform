-- ============================================================
-- RFM 분석 SQL 쿼리 (자동 생성)
-- 생성일: 2025-12-04 19:25:52
-- 기준일: 2025-12-04
-- ============================================================
-- Step 1: 고객별 RFM 지표 계산
WITH customer_rfm AS (
SELECT
customer_id,
-- Recency: 마지막 구매일로부터 경과 일수 (낮을수록 좋음)
CAST(JULIANDAY('2025-12-04') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS recency,
-- Frequency: 총 거래 건수 (높을수록 좋음)
COUNT(*) AS frequency,
-- Monetary: 총 매출액 (높을수록 좋음)
ROUND(SUM(quantity * unit_price), 2) AS monetary
FROM transactions
WHERE quantity > 0
AND unit_price > 0
AND invoice_date <= '2025-12-04'
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
NTILE(5) OVER (ORDER BY recency ASC) AS r_score,
-- F 점수: Frequency 높을수록 높은 점수
NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
-- M 점수: Monetary 높을수록 높은 점수
NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
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