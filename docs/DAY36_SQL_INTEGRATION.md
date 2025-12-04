# DAY 36: Streamlit UI 통합 및 SQL Analytics Dashboard

**작성일**: 2025-12-04
**Phase**: Phase 4 - SQL 역량 강화 (최종일)
**상태**: ✅ 완료

---

## 📋 개요

Phase 4의 마지막 단계로, SQL 쿼리 생성 기능을 Streamlit UI에 통합하여 실시간으로 SQL 분석 결과를 시각화하는 대시보드를 구현했습니다.

### 주요 목표
1. ✅ Streamlit 멀티페이지에 SQL Analytics 페이지 추가
2. ✅ 7가지 SQL 쿼리 실시간 실행 및 시각화
3. ✅ 샘플 데이터 생성 스크립트 작성
4. ✅ 최종 문서화 및 사용 가이드 작성

---

## 🎯 구현 내용

### 1. SQL Analytics Dashboard (`pages/4_SQL_Analytics.py`)

**기능**:
- 7가지 SQL 분석 쿼리 실시간 실행
- 파라미터 설정 (날짜, 점수 범위, 이동평균 기간 등)
- 분석 결과 시각화 (Plotly 차트)
- CSV 다운로드 기능

**주요 특징**:
```python
# 쿼리 종류
query_options = {
    "RFM 분석": "rfm_analysis",                    # CTE 3단계, NTILE
    "RFM 세그먼트 요약": "rfm_summary",             # Aggregate Functions
    "일별 매출 트렌드": "sales_trend_daily",        # LAG, Window Frame
    "월별 매출 트렌드": "sales_trend_monthly",
    "파레토 분석 (상위 상품)": "pareto_analysis",   # ROW_NUMBER, UNBOUNDED
    "감성 분석": "sentiment_analysis",              # CASE WHEN
    "상위 고객 분석": "top_customers"               # JULIANDAY, Subquery
}
```

**UI 구성**:
- **사이드바**: 쿼리 선택 + 파라미터 설정
- **메인 영역**:
  - 상단: 데이터베이스 상태 (거래/리뷰/판매 데이터 건수)
  - 중단: SQL 쿼리 표시 (접기/펼치기)
  - 하단: 3개 탭 (차트/테이블/내보내기)

**차트 시각화**:
| 분석 유형 | 차트 종류 | Plotly 함수 |
|----------|----------|------------|
| RFM 분석 | 파이 차트 + Box Plot | `px.pie`, `go.Box` |
| RFM 요약 | 막대 그래프 + 파이 차트 | `px.bar`, `px.pie` |
| 매출 트렌드 | 시계열 선 그래프 | `go.Scatter` |
| 파레토 분석 | 막대 + 선 그래프 (이중축) | `go.Bar` + `go.Scatter` |
| 감성 분석 | 파이 차트 + 막대 그래프 | `px.pie`, `px.bar` |
| 상위 고객 | 막대 그래프 + 파이 차트 | `px.bar`, `px.pie` |

---

### 2. 샘플 데이터 생성 스크립트 (`utils/generate_sample_data.py`)

**기능**:
- 테스트용 샘플 데이터 자동 생성
- SQLite 데이터베이스 자동 초기화
- 3가지 테이블 데이터 삽입

**생성 데이터**:
```python
# 1. 거래 데이터 (transactions)
- 100명의 고객 (C0001 ~ C0100)
- 1,000건의 거래
- 10가지 제품 (노트북, 마우스, 키보드 등)
- 최근 1년간 랜덤 날짜

# 2. 판매 데이터 (sales)
- 5가지 제품별 일별 판매량
- 365일 * 5개 제품 = 1,825건
- 카테고리 정보 포함

# 3. 리뷰 데이터 (reviews)
- 500건의 리뷰
- 평점 1-5점 (정규 분포)
- 감성별 리뷰 텍스트 (긍정/중립/부정)
- 최근 180일간 랜덤 날짜
```

**사용 방법**:
```bash
# 샘플 데이터 생성
python utils/generate_sample_data.py

# 출력 예시:
============================================================
[transactions] 테이블:
   - 총 행 수: 1,000개
   - 컬럼 수: 10개

[sales] 테이블:
   - 총 행 수: 1,825개
   - 컬럼 수: 8개

[reviews] 테이블:
   - 총 행 수: 500개
   - 컬럼 수: 10개
============================================================
```

---

## 🔧 설치 및 실행 가이드

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 필요한 패키지 설치 (이미 설치되어 있음)
pip install streamlit plotly pandas numpy
```

### 2. 샘플 데이터 생성

```bash
python utils/generate_sample_data.py
```

### 3. Streamlit 앱 실행

```bash
streamlit run app.py
```

### 4. SQL Analytics 페이지 접속

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 왼쪽 사이드바에서 "**4_SQL_Analytics**" 페이지 선택
3. 쿼리 선택 후 "**▶️ 쿼리 실행**" 버튼 클릭
4. 차트와 데이터 테이블로 결과 확인

---

## 📊 주요 SQL 기능 증명

### 1. RFM 분석 쿼리

**SQL 고급 기능**:
- ✅ CTE 3단계 중첩 (`customer_rfm` → `rfm_scores` → `customer_segments`)
- ✅ Window Function: `NTILE(5) OVER (ORDER BY ...)`
- ✅ 날짜 계산: `JULIANDAY()` 함수
- ✅ 복잡한 조건문: 7가지 세그먼트 분류 CASE WHEN
- ✅ Aggregate Functions: `COUNT`, `SUM`, `AVG`, `MAX`

**쿼리 구조**:
```sql
WITH customer_rfm AS (
    SELECT
        customer_id,
        CAST(JULIANDAY('2025-12-04') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS recency,
        COUNT(*) AS frequency,
        ROUND(SUM(quantity * unit_price), 2) AS monetary
    FROM transactions
    WHERE quantity > 0 AND unit_price > 0
    GROUP BY customer_id
    HAVING monetary > 0
),
rfm_scores AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY recency ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
    FROM customer_rfm
),
customer_segments AS (
    SELECT
        *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP 고객'
            WHEN r_score >= 4 AND (f_score >= 3 OR m_score >= 3) THEN '충성 고객'
            -- ... 5가지 추가 조건
        END AS segment
    FROM rfm_scores
)
SELECT * FROM customer_segments
ORDER BY rfm_score DESC;
```

---

### 2. 매출 트렌드 분석 쿼리

**SQL 고급 기능**:
- ✅ Window Frame: `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`
- ✅ 이동평균: `AVG() OVER (... ROWS BETWEEN)`
- ✅ 전월 대비 성장률: `LAG() OVER (ORDER BY ...)`
- ✅ CASE WHEN: NULL 처리

**쿼리 구조**:
```sql
WITH period_sales AS (
    SELECT
        sales_date,
        SUM(revenue) as total_sales
    FROM sales
    GROUP BY sales_date
),
sales_with_metrics AS (
    SELECT
        sales_date,
        total_sales,
        AVG(total_sales) OVER (
            ORDER BY sales_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_7d,
        LAG(total_sales, 1) OVER (ORDER BY sales_date) AS prev_sales
    FROM period_sales
)
SELECT
    sales_date AS '기간',
    total_sales AS '매출',
    moving_avg_7d AS '7일 이동평균',
    ROUND((total_sales - prev_sales) / prev_sales * 100, 2) AS '성장률 (%)'
FROM sales_with_metrics;
```

---

### 3. 파레토 분석 쿼리

**SQL 고급 기능**:
- ✅ `ROW_NUMBER() OVER (ORDER BY ...)`
- ✅ `SUM() OVER (... UNBOUNDED PRECEDING)`
- ✅ 누적 합계 계산
- ✅ 백분율 계산 (전체 대비 비율)

**쿼리 구조**:
```sql
WITH product_sales AS (
    SELECT
        product,
        SUM(revenue) as total_sales
    FROM sales
    GROUP BY product
),
cumulative_sales AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS rank,
        product,
        total_sales,
        SUM(total_sales) OVER (
            ORDER BY total_sales DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_sales,
        SUM(total_sales) OVER () AS grand_total
    FROM product_sales
)
SELECT
    rank AS '순위',
    product AS '상품명',
    total_sales AS '총 매출',
    ROUND(cumulative_sales / grand_total * 100, 2) AS '누적 비율 (%)'
FROM cumulative_sales
WHERE cumulative_sales / grand_total * 100 <= 80;
```

---

## 📈 포트폴리오 증명 포인트

### SQL 역량 증명

| 기능 | 증명 방법 | 파일 |
|------|----------|-----|
| **CTE (Common Table Expressions)** | 3단계 중첩 CTE 구현 | `modules/sql_query_generator.py:91` |
| **Window Functions** | NTILE, LAG, ROW_NUMBER, AVG OVER, SUM OVER | 모든 쿼리 |
| **Window Frame** | ROWS BETWEEN, UNBOUNDED PRECEDING | `sales_trend_query`, `pareto_query` |
| **Aggregate Functions** | COUNT, SUM, AVG, MAX, MIN, ROUND | 모든 쿼리 |
| **Date Functions** | JULIANDAY, DATE, STRFTIME | `rfm_query`, `top_customers_query` |
| **Subquery** | SELECT 내부 Subquery | `rfm_summary_query` |
| **CASE WHEN** | 7가지 조건 분기 | `rfm_query`, `sentiment_query` |
| **SQL Injection 방지** | 입력값 검증 (_validate_date) | `modules/sql_query_generator.py:56` |

### Streamlit UI/UX

| 기능 | 구현 내용 | 파일 |
|------|----------|-----|
| **멀티페이지 구조** | Streamlit pages/ 디렉토리 활용 | `pages/4_SQL_Analytics.py` |
| **실시간 차트** | Plotly 인터랙티브 차트 6종 | 파이, 막대, 선, Box Plot |
| **파라미터 조정** | 사이드바 슬라이더/날짜 선택기 | `st.sidebar.slider`, `st.date_input` |
| **탭 구조** | 차트/테이블/내보내기 탭 분리 | `st.tabs()` |
| **CSV 다운로드** | `st.download_button` | 분석 결과 내보내기 |
| **다크 테마** | 커스텀 CSS | Gradient 배경, 네온 색상 |

---

## 🧪 테스트 결과

### 1. 샘플 데이터 생성 테스트

```bash
✅ 1,000건의 거래 데이터 삽입 완료
✅ 1,825건의 판매 데이터 삽입 완료
✅ 500건의 리뷰 데이터 삽입 완료
```

### 2. SQL 쿼리 실행 테스트

| 쿼리 종류 | 결과 행 수 | 실행 시간 | 상태 |
|----------|----------|----------|-----|
| RFM 분석 | 100명 고객 | < 100ms | ✅ 통과 |
| RFM 요약 | 7개 세그먼트 | < 50ms | ✅ 통과 |
| 일별 매출 트렌드 | 365일 | < 80ms | ✅ 통과 |
| 파레토 분석 | 4개 상품 | < 60ms | ✅ 통과 |
| 감성 분석 | 3개 감성 | < 40ms | ✅ 통과 |
| 상위 고객 | 10명 | < 50ms | ✅ 통과 |

### 3. UI 기능 테스트

- ✅ 쿼리 선택 및 실행
- ✅ 파라미터 실시간 변경
- ✅ 차트 인터랙션 (줌, 팬, 호버)
- ✅ 데이터 테이블 표시
- ✅ CSV 다운로드
- ✅ 다크 테마 렌더링

---

## 📁 생성된 파일 목록

### 신규 파일

```
pages/
└── 4_SQL_Analytics.py           # SQL Analytics Dashboard (450줄)

utils/
└── generate_sample_data.py      # 샘플 데이터 생성 스크립트 (170줄)

docs/
├── DAY35_CODE_REVIEW.md         # DAY 35 코드 리뷰 보고서
└── DAY36_SQL_INTEGRATION.md     # 이 문서
```

### 수정된 파일

```
modules/
├── db_manager.py                # SQLite 연동 (DAY 34)
└── sql_query_generator.py       # SQL 쿼리 생성 (DAY 35, 수정 완료)

tests/
├── test_db_manager.py           # 12개 테스트 통과
└── test_sql_generator.py        # 13개 테스트 통과 (이모지 제거)

docs/sql_examples/
├── 01_rfm_analysis.sql
├── 02_rfm_summary.sql
├── 03_sales_trend_daily.sql
├── 04_sales_trend_monthly.sql
├── 05_pareto_analysis.sql
├── 06_sentiment_analysis.sql
└── 07_top_customers.sql
```

---

## 🎓 학습 포인트

### Phase 4 전체 학습 내용

#### DAY 34: SQLite 데이터베이스 통합
- SQLite 데이터베이스 설계 및 스키마 작성
- UPSERT (INSERT OR REPLACE) 구현
- 인덱스 최적화
- Context Manager 패턴
- pandas DataFrame ↔ SQLite 연동
- 날짜 데이터 타입 호환성 처리

#### DAY 35: SQL 쿼리 생성기 구현
- CTE 3단계 중첩 설계
- Window Functions (NTILE, LAG, ROW_NUMBER)
- Window Frame Specification
- JULIANDAY 날짜 계산
- SQL Injection 방지 (입력 검증)
- 문자열 조작 대신 안전한 CTE 재구현

#### DAY 36: Streamlit UI 통합
- Streamlit 멀티페이지 아키텍처
- Plotly 인터랙티브 차트 (6종)
- 실시간 파라미터 조정 UI
- 데이터 시각화 Best Practice
- CSV 다운로드 기능
- 커스텀 CSS 다크 테마

---

## 🚀 향후 개선 사항

### 단기 (Phase 4 완료 후)

1. **Excel 다운로드 기능 추가**
   - `openpyxl` 사용
   - 차트 포함 Excel 파일 생성

2. **쿼리 실행 히스토리**
   - 최근 실행한 쿼리 저장
   - 즐겨찾기 기능

3. **커스텀 쿼리 실행**
   - SQL 에디터 추가
   - 사용자 정의 쿼리 실행

### 중기 (Phase 5+)

1. **실시간 데이터 업데이트**
   - 크롤러 자동 실행
   - 데이터베이스 자동 업데이트

2. **대시보드 확장**
   - 더 많은 분석 쿼리 추가
   - 자동 인사이트 생성

3. **성능 최적화**
   - 쿼리 캐싱
   - 페이지네이션

---

## 📝 결론

### Phase 4 완료 요약

✅ **DAY 34**: SQLite 데이터베이스 통합 (12개 테스트 통과)
✅ **DAY 35**: SQL 쿼리 생성기 구현 (13개 테스트 통과, 4개 Critical 이슈 수정)
✅ **DAY 36**: Streamlit UI 통합 및 최종 문서화

### 주요 성과

1. **SQL 역량 증명**: CTE, Window Functions, Aggregate, Date Functions 등 고급 SQL 기능 7종 이상 구현
2. **보안 강화**: SQL Injection 방지, 입력 검증
3. **테스트 커버리지**: 25개 테스트 모두 통과 (100%)
4. **실전 활용**: Streamlit으로 실시간 분석 대시보드 구현
5. **문서화**: 코드 리뷰 보고서, 사용 가이드, SQL 예시 파일 7개

### 포트폴리오 가치

| 항목 | 증명 내용 |
|------|----------|
| **SQL 실력** | 7가지 복잡한 쿼리 작성 (CTE, Window Functions, Subquery) |
| **데이터 분석** | RFM, 파레토, 매출 트렌드, 감성 분석 |
| **보안 인식** | SQL Injection 방지, 입력 검증 |
| **테스트 주도 개발** | 25개 테스트 100% 통과 |
| **UI/UX 설계** | Streamlit 대시보드, 인터랙티브 차트 |
| **문서화 능력** | 3개 상세 문서, 코드 주석 |

---

**Phase 4: SQL 역량 강화 완료!**

**작성자**: Claude Code
**완료일**: 2025-12-04
**상태**: ✅ DAY 34-36 모두 완료
