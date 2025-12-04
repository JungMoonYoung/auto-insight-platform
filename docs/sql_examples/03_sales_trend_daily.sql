-- ============================================================
-- 매출 트렌드 분석 SQL 쿼리 (daily)
-- 생성일: 2025-12-04 19:25:52
-- ============================================================
-- Step 1: 기간별 매출 집계
WITH period_sales AS (
SELECT
strftime('%Y-%m-%d', sales_date) AS period,
DATE(sales_date) AS sales_date,
ROUND(SUM(revenue), 2) AS total_sales,
SUM(quantity) AS total_quantity,
COUNT(DISTINCT product) AS unique_products
FROM sales
WHERE sales_date IS NOT NULL
GROUP BY strftime('%Y-%m-%d', sales_date), DATE(sales_date)
),
-- Step 2: 이동평균 및 성장률 계산
sales_with_metrics AS (
SELECT
period,
sales_date,
total_sales,
total_quantity,
unique_products,
-- 7일 이동평균 (Window Function 사용)
ROUND(AVG(total_sales) OVER (
ORDER BY sales_date
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
), 2) AS moving_avg_7d,
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
moving_avg_7d AS '7일 이동평균',
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