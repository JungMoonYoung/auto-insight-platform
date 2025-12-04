-- ============================================================
-- 파레토 분석 SQL 쿼리 (상위 80% 매출 제품)
-- 생성일: 2025-12-04 19:25:52
-- ============================================================
-- Step 1: 상품별 총 매출 계산
WITH product_sales AS (
SELECT
product,
category,
ROUND(SUM(revenue), 2) AS total_sales,
SUM(quantity) AS total_quantity
FROM sales
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
-- Step 3: 상위 80% 매출 제품만 필터링
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
WHERE cumulative_pct <= 80
OR sales_rank <= 10  -- 또는 상위 10개 상품
ORDER BY sales_rank;
-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. Window Functions: SUM OVER, ROW_NUMBER
-- 2. ROWS BETWEEN UNBOUNDED PRECEDING (누적 합계)
-- 3. 백분율 계산
-- 4. 복잡한 필터링 조건 (WHERE ... OR)
-- ============================================================