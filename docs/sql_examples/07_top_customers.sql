-- ============================================================
-- 상위 20명 고객 조회
-- 생성일: 2025-12-04 19:25:52
-- ============================================================
SELECT
customer_id AS '고객 ID',
COUNT(*) AS '거래 횟수',
ROUND(SUM(quantity * unit_price), 2) AS '총 구매액',
ROUND(AVG(quantity * unit_price), 2) AS '평균 구매액',
ROUND(SUM(quantity * unit_price) * 100.0 / (
SELECT SUM(quantity * unit_price) FROM transactions
), 2) AS '매출 기여도 (%)',
MIN(invoice_date) AS '첫 구매일',
MAX(invoice_date) AS '최근 구매일',
CAST(JULIANDAY('now') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS '마지막 구매 경과일'
FROM transactions
WHERE quantity > 0 AND unit_price > 0
GROUP BY customer_id
ORDER BY SUM(quantity * unit_price) DESC
LIMIT 20;
-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)
-- 2. 서브쿼리로 전체 매출 계산
-- 3. ORDER BY, LIMIT
-- 4. JULIANDAY로 날짜 계산
-- ============================================================