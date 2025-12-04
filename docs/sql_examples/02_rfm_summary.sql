-- ============================================================
-- RFM 세그먼트별 요약 통계
-- 생성일: 2025-12-04 19:25:52
-- 기준일: 2025-12-04
-- ============================================================
-- Step 1: 고객별 RFM 계산 (재사용)
WITH customer_rfm AS (
SELECT
customer_id,
CAST(JULIANDAY('2025-12-04') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS recency,
COUNT(*) AS frequency,
ROUND(SUM(quantity * unit_price), 2) AS monetary
FROM transactions
WHERE quantity > 0
AND unit_price > 0
AND invoice_date <= '2025-12-04'
GROUP BY customer_id
HAVING monetary > 0
),
-- Step 2: RFM 점수 계산
rfm_scores AS (
SELECT
customer_id,
recency,
frequency,
monetary,
NTILE(5) OVER (ORDER BY recency ASC) AS r_score,
NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
FROM customer_rfm
),
-- Step 3: 세그먼트 분류
customer_segments AS (
SELECT
customer_id,
recency,
frequency,
monetary,
r_score,
f_score,
m_score,
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
-- 세그먼트별 요약 통계
SELECT
segment AS '고객 세그먼트',
COUNT(*) AS '고객 수',
ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_segments), 2) AS '비율 (%)',
ROUND(AVG(recency), 1) AS '평균 Recency',
ROUND(AVG(frequency), 1) AS '평균 Frequency',
ROUND(AVG(monetary), 2) AS '평균 Monetary',
ROUND(SUM(monetary), 2) AS '총 매출',
ROUND(SUM(monetary) * 100.0 / (SELECT SUM(monetary) FROM customer_segments), 2) AS '매출 기여도 (%)'
FROM customer_segments
GROUP BY segment
ORDER BY SUM(monetary) DESC;
-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. CTE 재사용 (중복 코드 없이 깔끔한 구조)
-- 2. 서브쿼리로 전체 집계 ((SELECT COUNT(*) FROM ...))
-- 3. 백분율 계산
-- ============================================================