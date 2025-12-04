-- ============================================================
-- 감성 분석 SQL 쿼리 (키워드 기반)
-- 생성일: 2025-12-04 19:25:52
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
WHEN rating >= 8 THEN 'positive'
WHEN rating >= 5 THEN 'neutral'
WHEN rating < 5 THEN 'negative'
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
WHEN rating >= 8 OR review_text LIKE '%좋%' OR review_text LIKE '%최고%' THEN 'positive'
WHEN rating <= 3 OR review_text LIKE '%나쁘%' OR review_text LIKE '%최악%' THEN 'negative'
ELSE 'neutral'
END AS final_sentiment
FROM reviews
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
WHEN 'positive' THEN 1
WHEN 'neutral' THEN 2
WHEN 'negative' THEN 3
ELSE 4
END;
-- ============================================================
-- 포트폴리오 증명 포인트:
-- 1. CASE WHEN (복잡한 조건부 로직)
-- 2. LIKE (텍스트 패턴 매칭)
-- 3. 서브쿼리로 전체 집계
-- 4. ORDER BY CASE (커스텀 정렬)
-- ============================================================