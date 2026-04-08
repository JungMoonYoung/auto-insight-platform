# Auto-Insight — E-Commerce 고객 분석 자동화 플랫폼

> **SQL·RFM·NLP 자동화로 분석 프로세스를 플랫폼화할 수 있습니다.**

CSV 파일 하나만 업로드하면 RFM 고객 세분화 · 매출 분석 · 리뷰 감성 분석 · SQL 쿼리 생성까지 자동으로 수행하는 Streamlit 기반 플랫폼입니다.

---

## Links

- **Live Demo**: https://auto-insight-platform-vocgdmswtxgaxvx3sk5r9u.streamlit.app/
- **Portfolio (Notion)**: https://www.notion.so/33a404a59bef8106a7ecc2baa5c97853

---

## 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 구분 | 개인 프로젝트 |
| 기간 | 2025.08 ~ 2025.09 |
| 기여도 | 100% |
| 역할 | 주제선정, 데이터 수집 및 전처리, EDA, SQL 쿼리 최적화 및 자동화 |
| 배포 URL | https://auto-insight-platform-vocgdmswtxgaxvx3sk5r9u.streamlit.app/ |

---

## 문제 정의 & 해결 방향

### 문제 정의

실무에서 데이터 분석은 **수집 → 저장 → 분석 → 시각화 → 인사이트 도출**의 반복 과정입니다. 이 과정을 매번 수동으로 수행하면 분석가의 시간이 반복 작업에 소모되고, 비개발자는 분석 결과에 접근조차 어렵습니다.

### 해결 방향

**CSV 파일 하나를 업로드하면 RFM 분석, 매출 분석, 리뷰 감성 분석, SQL 쿼리 생성까지 자동으로 수행하는 플랫폼**을 구축하여, 분석 프로세스 자체를 자동화하는 것을 목표로 했습니다.

---

## 기술 스택

| 영역 | 스택 |
|---|---|
| Language & DB | Python, SQLite |
| Data & ML | Pandas, Scikit-learn (K-Means, TF-IDF, LDA) |
| NLP & LLM | KoNLPy, OpenAI API |
| Web & Viz | Streamlit, Plotly |

---

## 시스템 아키텍처

### System Architecture

```
사용자 입력  →  Streamlit UI  →  SQLite DB  →  분석 모듈  →  결과 출력
                                               ├─ RFM
                                               ├─ 매출
                                               └─ NLP
```

### Data Flow

```
데이터 입력 → 전처리 → 검증 → 분석 유형 자동 분기 → 시각화 → 인사이트
                                   ├─ 리뷰
                                   ├─ NLP
                                   ├─ 매출
                                   └─ RFM
```

---

## 주요 기능

### 1) SQL 쿼리 자동 생성 및 실행

- **CTE 3단계 중첩**: RFM 계산 → NTILE 분위수 → 세그먼트 분류
- **Window Functions 8종**: LAG, LEAD, SUM OVER, ROW_NUMBER 등
- **이동평균 구현**: ROWS BETWEEN으로 7일/30일 트렌드 추출
- 100,000건 데이터 → **2초 이내** 집계 및 차트 시각화

### 2) RFM 고객 세분화 (K-Means)

- Silhouette Score 기반 **최적 K 탐색** (3~8개 군집)
- VIP / 충성 / 이탈 위험 / 신규 고객 자동 분류
- 3,000명 고객 → **3초 이내** 세분화 완료

### 3) NLP 리뷰 감성 분석 (한국어)

- KoNLPy + TF-IDF 형태소 분석·키워드 추출
- **LDA 토픽 모델링**: 숨겨진 주제 5개 자동 발견
- **부정 리뷰만 GPT 전송** → API 비용 70% 절감
- 워드클라우드 + 감성 분포 히트맵 생성

### 4) GPT 마케팅 전략 자동 생성

- RFM 분석 + 매출 트렌드 통합 분석
- 고객 세그먼트별 목표 / 액션 / 메시지톤 / 예상효과 제공
- **15초 이내** 전문가 수준 인사이트 생성

---

## 비즈니스 활용 시나리오

### 1. RFM 자동 분석 시스템

- **분석과 액션 사이의 병목 제거**: 데이터 팀에 분석 요청·대기 없이 마케터가 스스로 타겟 리스트 직접 추출 가능
- **API 보고서 자동화**: 자동 생성된 보고서 결과를 시계열로 누적하여 캠페인 전후 효과를 데이터로 검증하는 정기 모니터링 체계 설립
- **고도화 확장 계획**: ML 기반 LTV 예측 모델을 결합하여 이탈 확률이 높은 고가치 고객을 선제 방어하는 **예측형 CRM으로 고도화**

### 2. 리뷰 감성 분석

- **부정 리뷰 급증 키워드 주 단위 모니터링**: 상품 QC팀에 전달하여 품질 이슈 조기 대응
- **토픽 모델링으로 카테고리 자동 분류**: "배송 지연", "품질 불량", "사이즈 불일치" 등 카테고리별 응답 매뉴얼 및 응대 자동화 구축
- **고도화 확장 계획**:
  - LLM 기반 근본 원인 추론으로 확장, 공정·배송 단계의 병목 구간까지 자동 리포팅
  - 상품 QC팀에 부정 리뷰 알림 자동 발송 시스템 구축

### 3. SQL 쿼리 작성 및 자동화

- **마케터 셀프 데이터 추출**: 쿼리 작성 없이 캠페인에 필요한 데이터 추출 가능, 분석팀 요청 대기 없이 즉시 집행
- **주간/월간 매출 리포트 자동 생성**: 직접 작성하던 정기 리포트를 자동화하여 생산성 향상
- **파레토 분석 쿼리 자동 생성**:
  - 매출 상위 20% 상품 즉시 식별 → 재고 물량 조절
  - 매출 하위 상품 식별 → 재고 정리·할인 판매로 악성 재고 해소
- **고도화 확장 계획**: 자연어 질문만으로 시뮬레이션 결과와 액션 아이템까지 제공하는 **AI 데이터 에이전트로 확장**

---

## 문제 해결 경험

### 1. GPT 비용 95% 절감 (하이브리드 감성 분석)

- **문제**: 전체 리뷰를 GPT로 분석하면 천문학적 토큰 비용 발생
- **해결**: 1차로 키워드 기반 무료 감성 분류 → 부정 리뷰만 100개 샘플링 → GPT는 심층 분석에만 선별 적용
- **결과**: 전체 비용 **95% 절감**
- **배운 점**: 비즈니스 관점에서 가장 중요한 것은 비용이므로, 비용이 있는 API는 **"전수 처리"가 아닌 "필요한 곳에만 정밀 투입"** 하는 설계가 중요하다.

### 2. 파레토 분석 조건 오류 처리

- **문제**: 조건식이 `<80`이어서 80% 도달 직전 상품에서 끊김 → 마지막 상품이 누락되는 오류
- **해결**: 조건식을 `<=`으로 수정 + 80% 미달 시 전체 반환 + 빈 데이터 시 최소 1개 보장하는 방어 로직 추가
- **배운 점**: **경계값에서 오류가 가장 많이 난다**는 것을 직접 경험 후, 경계값을 조심하고 **경계값 테스트를 하는 습관**을 들이게 되었다.

---

## 실행 방법

### Local 실행

```bash
# 1. 저장소 클론
git clone https://github.com/JungMoonYoung/auto-insight-platform.git
cd auto-insight-platform

# 2. 가상환경 및 의존성
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt

# 3. 대시보드 실행
streamlit run app.py
```

### 폴더 구조

```
auto-insight-platform/
├── app.py                      # Streamlit 메인 앱 (인사이트 / 데이터 준비 / 자동 분석 / 상세 탐색 / 내보내기)
├── pages/
│   └── 4_SQL_Analytics.py      # SQL Analytics 서브 페이지
├── modules/                    # 분석 모듈
│   ├── data_loader.py
│   ├── preprocessor.py
│   ├── rfm_analyzer.py
│   ├── sales_analyzer.py
│   ├── text_analyzer.py
│   ├── visualizer.py
│   ├── db_manager.py
│   ├── sql_query_generator.py
│   ├── gpt_analyzer.py
│   ├── insight_generator.py
│   └── report_generator.py
├── crawlers/                   # 데이터 수집 모듈
├── sample_data/                # 샘플 데이터
├── config/
├── utils/
├── tests/
├── requirements.txt
└── README.md
```

---

## 성장 포인트

> 분석을 수행하는 것과 분석이 자동으로 돌아가는 시스템을 구축하는 것은 **완전히 다른 영역**입니다. 자동화가 비즈니스에 미치는 임팩트를 직접 확인했습니다.
>
> 데이터 품질 검증 없이 분석에 진입하여 결과가 틀어진 경험 이후, **분석 파이프라인 설계 초입에서 검증 프로세스를 배치하는 것을 원칙**으로 적용하고 있습니다.

---

## Contact

- **GitHub**: [JungMoonYoung](https://github.com/JungMoonYoung)
- **Email**: kobing7122@gmail.com
- **Portfolio**: https://www.notion.so/252404a59bef802b8693d40f30b48d82
