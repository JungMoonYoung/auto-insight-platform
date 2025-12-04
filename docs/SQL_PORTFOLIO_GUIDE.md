# SQL 역량 포트폴리오 가이드

이 문서는 `auto-insight-platform` 프로젝트에서 구현한 **SQL 역량**을 면접관에게 보여주기 위한 가이드입니다.

---

## 🎯 빠른 시작

### 1. 샘플 데이터 생성
```bash
python utils/generate_sample_data.py
```

### 2. Streamlit 앱 실행
```bash
streamlit run app.py
```

### 3. SQL Analytics 페이지 접속
- 브라우저에서 `http://localhost:8501` 접속
- 왼쪽 사이드바에서 "**4_SQL_Analytics**" 선택
- 7가지 SQL 쿼리 실시간 실행 및 시각화

---

## 📊 구현된 SQL 기능 (포트폴리오 증명)

### 1. CTE (Common Table Expressions) - 3단계 중첩

**파일**: `modules/sql_query_generator.py`
**함수**: `generate_rfm_query()` (91줄)

```sql
WITH customer_rfm AS (
    -- Step 1: 고객별 RFM 지표 계산
    SELECT customer_id, recency, frequency, monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    -- Step 2: NTILE로 점수 계산
    SELECT *, NTILE(5) OVER (ORDER BY ...) AS r_score
    FROM customer_rfm
),
customer_segments AS (
    -- Step 3: 세그먼트 분류
    SELECT *, CASE WHEN ... THEN 'VIP 고객' END AS segment
    FROM rfm_scores
)
SELECT * FROM customer_segments;
```

**증명 포인트**: 복잡한 비즈니스 로직을 단계별로 분리하여 가독성 향상

---

### 2. Window Functions - 5가지 함수 사용

#### NTILE (분위수 분할)
```sql
NTILE(5) OVER (ORDER BY frequency DESC) AS f_score
```

#### LAG (이전 행 참조)
```sql
LAG(total_sales, 1) OVER (ORDER BY sales_date) AS prev_sales
```

#### ROW_NUMBER (순위 계산)
```sql
ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS rank
```

#### AVG + Window Frame (이동평균)
```sql
AVG(total_sales) OVER (
    ORDER BY sales_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS moving_avg_7d
```

#### SUM + UNBOUNDED (누적 합계)
```sql
SUM(total_sales) OVER (
    ORDER BY total_sales DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) AS cumulative_sales
```

**증명 포인트**: Window Function의 다양한 활용법 이해

---

### 3. 날짜 함수 (JULIANDAY)

```sql
CAST(JULIANDAY('2025-12-04') - JULIANDAY(MAX(invoice_date)) AS INTEGER) AS recency
```

**증명 포인트**: SQLite 특화 날짜 계산 함수 활용

---

### 4. 복잡한 조건문 (CASE WHEN) - 7가지 분기

```sql
CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP 고객'
    WHEN r_score >= 4 AND (f_score >= 3 OR m_score >= 3) THEN '충성 고객'
    WHEN r_score >= 3 AND f_score >= 3 THEN '잠재 우수 고객'
    WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN '이탈 위험 고객'
    WHEN r_score <= 2 AND f_score <= 2 THEN '휴면 고객'
    WHEN f_score <= 2 AND m_score <= 2 THEN '신규/일회성 고객'
    ELSE '일반 고객'
END AS segment
```

**증명 포인트**: 복잡한 비즈니스 규칙을 SQL로 표현

---

### 5. Subquery (서브쿼리)

```sql
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_segments), 2) AS percentage
FROM customer_segments
GROUP BY segment;
```

**증명 포인트**: 전체 집계값을 서브쿼리로 계산하여 백분율 산출

---

### 6. Aggregate Functions (집계 함수)

| 함수 | 사용 예시 | 쿼리 |
|------|----------|-----|
| `COUNT()` | 고객 수 집계 | RFM 요약 |
| `SUM()` | 총 매출 계산 | 모든 쿼리 |
| `AVG()` | 평균 RFM 점수 | RFM 요약 |
| `MAX()` | 최근 구매일 | RFM 분석 |
| `ROUND()` | 소수점 반올림 | 모든 쿼리 |

---

### 7. SQL Injection 방지 (보안)

**파일**: `modules/sql_query_generator.py`
**함수**: `_validate_date()` (56줄)

```python
def _validate_date(self, date_str: str) -> str:
    """
    날짜 형식 검증 (SQL Injection 방지)
    """
    # 1. 정규식 검증
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValueError(f"Invalid date format: {date_str}")

    # 2. 실제 날짜인지 확인
    datetime.strptime(date_str, '%Y-%m-%d')

    return date_str
```

**증명 포인트**: 입력값 검증으로 SQL Injection 공격 방지

---

## 🧪 테스트 결과

### 자동화 테스트 (pytest)

```bash
# DB Manager 테스트
pytest tests/test_db_manager.py -v
# 결과: 12/12 통과 ✅

# SQL Generator 테스트
pytest tests/test_sql_generator.py -v
# 결과: 13/13 통과 ✅
```

### 테스트 커버리지

| 모듈 | 테스트 수 | 통과율 | 주요 테스트 |
|------|----------|--------|-----------|
| `db_manager.py` | 12개 | 100% | CRUD, UPSERT, Context Manager |
| `sql_query_generator.py` | 13개 | 100% | 쿼리 생성, 실행, SQL 기능 검증 |

---

## 📁 코드 위치 (면접 시 참고)

### 핵심 파일

```
modules/
├── db_manager.py              # SQLite 데이터베이스 관리 (400줄)
└── sql_query_generator.py     # SQL 쿼리 생성 (540줄)

pages/
└── 4_SQL_Analytics.py         # Streamlit 대시보드 (450줄)

tests/
├── test_db_manager.py         # DB 테스트 (270줄)
└── test_sql_generator.py      # SQL 테스트 (316줄)

docs/sql_examples/
├── 01_rfm_analysis.sql        # RFM 분석 쿼리 (82줄)
├── 02_rfm_summary.sql         # RFM 요약 쿼리 (71줄)
├── 03_sales_trend_daily.sql   # 일별 매출 트렌드 (62줄)
├── 04_sales_trend_monthly.sql # 월별 매출 트렌드 (62줄)
├── 05_pareto_analysis.sql     # 파레토 분석 (58줄)
├── 06_sentiment_analysis.sql  # 감성 분석 (46줄)
└── 07_top_customers.sql       # 상위 고객 분석 (48줄)
```

### 문서

```
docs/
├── DAY34_DB_INTEGRATION.md    # (DAY 34 문서는 없음, 코드만 있음)
├── DAY35_CODE_REVIEW.md       # 코드 리뷰 보고서
├── DAY36_SQL_INTEGRATION.md   # 최종 통합 문서
└── SQL_PORTFOLIO_GUIDE.md     # 이 문서
```

---

## 💡 면접 대응 가이드

### Q1: "SQL에서 Window Function을 사용해본 적이 있나요?"

**A**: 네, 이 프로젝트에서 5가지 Window Function을 사용했습니다.

1. **NTILE**: RFM 분석에서 고객을 5등급으로 분류
2. **LAG**: 매출 트렌드에서 전월 대비 성장률 계산
3. **ROW_NUMBER**: 파레토 분석에서 상품 순위 계산
4. **AVG + Window Frame**: 7일 이동평균 계산
5. **SUM + UNBOUNDED**: 누적 매출 비율 계산

`docs/sql_examples/` 폴더에 실제 쿼리가 있으며, `tests/test_sql_generator.py`에서 실행 결과를 확인할 수 있습니다.

---

### Q2: "CTE를 사용해본 적이 있나요?"

**A**: 네, RFM 분석 쿼리에서 3단계 CTE를 중첩하여 사용했습니다.

```
customer_rfm (기본 지표 계산)
  ↓
rfm_scores (점수 계산)
  ↓
customer_segments (세그먼트 분류)
```

`modules/sql_query_generator.py:91` 함수에서 구현했으며, 코드 가독성과 유지보수성을 높이기 위해 단계별로 분리했습니다.

---

### Q3: "SQL Injection을 방지하기 위해 어떤 조치를 취했나요?"

**A**: 모든 사용자 입력값에 대해 검증 로직을 구현했습니다.

1. **정규식 검증**: `^\d{4}-\d{2}-\d{2}$` 패턴으로 날짜 형식 확인
2. **타입 검증**: `datetime.strptime()`으로 실제 날짜인지 확인
3. **범위 검증**: `max_score`는 1-10 사이 값만 허용

`modules/sql_query_generator.py:56` `_validate_date()` 함수에서 확인할 수 있습니다.

DAY 35 코드 리뷰에서 이 문제를 발견하고 수정했으며, 수정 전후 내용은 `docs/DAY35_CODE_REVIEW.md`에 기록되어 있습니다.

---

### Q4: "복잡한 비즈니스 로직을 SQL로 어떻게 표현했나요?"

**A**: RFM 분석의 고객 세그먼트 분류에서 7가지 조건을 CASE WHEN으로 구현했습니다.

```sql
CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'VIP 고객'
    WHEN r_score >= 4 AND (f_score >= 3 OR m_score >= 3) THEN '충성 고객'
    -- ... 5가지 추가 조건
    ELSE '일반 고객'
END
```

각 조건은 마케팅 전략에 따라 다른 세그먼트로 분류되며, SQL로 직접 구현하여 Python 코드 없이도 분석이 가능합니다.

---

### Q5: "이 SQL 쿼리들을 실제 대시보드에 어떻게 적용했나요?"

**A**: Streamlit 대시보드 (`pages/4_SQL_Analytics.py`)를 구현하여 실시간으로 쿼리를 실행하고 결과를 시각화했습니다.

- **파라미터 조정**: 사이드바에서 날짜, 점수 범위, 이동평균 기간 등을 실시간으로 변경
- **쿼리 실행**: 버튼 클릭으로 SQL 쿼리 실행
- **시각화**: Plotly로 6가지 차트 타입 구현 (파이, 막대, 선, Box Plot 등)
- **데이터 내보내기**: CSV 다운로드 기능

실제로 작동하는 모습은 `streamlit run app.py` 명령어로 확인할 수 있습니다.

---

## 📊 SQL 기능 요약표

| SQL 기능 | 사용 여부 | 증명 위치 |
|---------|---------|----------|
| SELECT, FROM, WHERE | ✅ | 모든 쿼리 |
| GROUP BY, HAVING | ✅ | RFM 분석, 감성 분석 |
| ORDER BY, LIMIT | ✅ | 상위 고객 조회 |
| JOIN | ❌ (단일 테이블 분석) | - |
| Subquery | ✅ | RFM 요약 (백분율 계산) |
| CTE (WITH) | ✅ | RFM 분석 (3단계 중첩) |
| CASE WHEN | ✅ | RFM 세그먼트, 감성 분석 |
| Window Functions | ✅ | 5가지 (NTILE, LAG, ROW_NUMBER, AVG, SUM) |
| Window Frame | ✅ | ROWS BETWEEN, UNBOUNDED |
| Aggregate Functions | ✅ | COUNT, SUM, AVG, MAX, ROUND |
| Date Functions | ✅ | JULIANDAY, DATE, STRFTIME |

---

## 🚀 데모 시나리오

면접관에게 실제로 보여줄 때 추천하는 순서:

1. **샘플 데이터 생성** (30초)
   ```bash
   python utils/generate_sample_data.py
   ```

2. **Streamlit 앱 실행** (10초)
   ```bash
   streamlit run app.py
   ```

3. **RFM 분석 시연** (2분)
   - SQL Analytics 페이지 접속
   - "RFM 분석" 선택
   - 기준일, 최대 점수 조정
   - 쿼리 실행
   - 생성된 SQL 쿼리 보기 (CTE 3단계 설명)
   - 차트 확인 (세그먼트 분포, RFM 점수 Box Plot)

4. **매출 트렌드 시연** (1분)
   - "일별 매출 트렌드" 선택
   - 이동평균 기간 조정 (3일 → 7일 → 30일)
   - LAG 함수로 성장률 계산 설명

5. **파레토 분석 시연** (1분)
   - "파레토 분석" 선택
   - 누적 비율 80% 설정
   - 상위 20% 제품이 전체 매출의 80% 차지하는 것 시각화

6. **코드 구조 설명** (2분)
   - `modules/sql_query_generator.py` 파일 열기
   - `_validate_date()` 함수 (SQL Injection 방지) 설명
   - `generate_rfm_query()` 함수 (CTE 3단계) 설명

**총 소요 시간**: 약 7분

---

## 📞 추가 질문 대응

### "왜 SQLite를 사용했나요?"

- **경량**: 서버 없이 파일 기반 데이터베이스
- **통합**: Python sqlite3 모듈로 간단히 연동
- **포트폴리오**: 설치 없이 데모 가능
- **Window Functions 지원**: SQLite 3.25+ 버전

### "실무에서는 어떤 DB를 사용할 건가요?"

- **PostgreSQL**: Window Functions, CTE 모두 지원
- **MySQL 8.0+**: Window Functions 지원
- 이 프로젝트의 SQL 쿼리는 약간의 수정으로 모든 RDBMS에서 실행 가능

### "쿼리 성능 최적화는 어떻게 했나요?"

- **인덱스**: `db_manager.py:103` 7개 인덱스 생성
- **HAVING 절**: 불필요한 행 사전 제거
- **CTE**: 중간 결과 재사용

---

## ✅ 체크리스트 (면접 전 확인)

- [ ] 샘플 데이터 생성 완료 (`python utils/generate_sample_data.py`)
- [ ] Streamlit 앱 정상 실행 확인 (`streamlit run app.py`)
- [ ] SQL Analytics 페이지 접속 확인
- [ ] 7가지 쿼리 모두 실행 테스트
- [ ] pytest 테스트 25개 모두 통과 확인
- [ ] `docs/sql_examples/` 폴더 7개 파일 확인
- [ ] 코드 리뷰 문서 숙지 (`docs/DAY35_CODE_REVIEW.md`)
- [ ] 이 가이드 숙지

---

**작성일**: 2025-12-04
**버전**: 1.0
**상태**: ✅ Phase 4 완료
