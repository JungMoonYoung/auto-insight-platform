# 📊 Auto-Insight Platform
> AI 기반 자동 데이터 분석 플랫폼 | 제로 코딩으로 전문가 수준의 인사이트 제공

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-red?style=for-the-badge)](배포URL_여기에_입력)
[![GitHub](https://img.shields.io/badge/📂_GitHub-Source_Code-181717?style=for-the-badge&logo=github)](https://github.com/your-username/auto-insight-platform)

---

## 🎬 데모 영상 (30초)

<!-- 데모 GIF를 여기에 삽입하세요 -->
![Demo GIF](docs/screenshots/demo.gif)

> **사용법**: 파일 업로드 → 자동 분석 → 인터랙티브 차트 확인 → 리포트 다운로드

---

## 💡 프로젝트 개요

**Auto-Insight Platform**은 비개발자도 쉽게 사용할 수 있는 **제로 코딩 데이터 분석 도구**입니다.
CSV/Excel 파일을 업로드하면 AI가 자동으로 분석하고 비즈니스 인사이트를 제공합니다.

### 🎯 핵심 가치

| 기능 | 기술 스택 | 비즈니스 가치 |
|------|----------|--------------|
| 🛒 **고객 세분화** | K-Means, RFM 분석 | VIP 고객 20% 자동 식별, 이탈 위험 고객 타겟팅 |
| 💬 **리뷰 감성 분석** | KoNLPy, TF-IDF, GPT-4o-mini | 부정 요인 자동 발견, 개선 방향 도출 |
| 📈 **매출 트렌드 분석** | 시계열, 파레토 차트 | 매출의 80%를 만드는 상위 20% 상품 발견 |
| 🔍 **SQL Analytics** | CTE, Window Functions | 복잡한 집계 쿼리 자동 생성 및 실행 |

---

## 🏗️ 시스템 아키텍처

<p align="center">
  <img src="diagrams/시스템아키텍처.png" alt="System Architecture" width="700"/>
</p>

**주요 구조**:
- **Data Layer**: CSV/Excel 업로드, 웹 크롤링, SQLite 저장
- **Analytics Engine**: RFM 분석, NLP, 매출 분석
- **SQL Analytics Engine**: 쿼리 자동 생성 (CTE, Window Functions)
- **Visualization Layer**: Plotly 인터랙티브 차트, HTML 리포트

📂 [아키텍처 상세 문서](docs/ARCHITECTURE.md) | 📂 [데이터 플로우 다이어그램](diagrams/데이터플로우.png)

---

## ⚡ 주요 기능

### 1️⃣ E-commerce 고객 분석 (RFM)

<img src="docs/screenshots/rfm_3d.png" alt="RFM 3D Scatter" width="500"/>

- **RFM 지표 자동 계산**: Recency, Frequency, Monetary
- **K-Means 군집화**: 최적 K 자동 선택 (Silhouette Score 기반)
- **비즈니스 세그먼트 자동 네이밍**: VIP, 충성, 이탈위험, 신규, 휴면 고객
- **3D 시각화**: Plotly 인터랙티브 차트

📂 [RFM 분석 프로세스](diagrams/RFM분석.png)

---

### 2️⃣ 리뷰 감성 분석

<img src="docs/screenshots/wordcloud.png" alt="Word Cloud" width="500"/>

- **한국어 형태소 분석**: KoNLPy (Okt) 기반 명사 추출
- **감성 분류**: 긍정/중립/부정 자동 분류
- **GPT-4o-mini 심층 분석**: 부정 리뷰 100개 샘플링 (비용 최적화)
- **토픽 모델링**: LDA 기반 5개 토픽 자동 추출
- **Word Cloud**: 감성별 키워드 시각화

---

### 3️⃣ 매출 트렌드 분석

<img src="docs/screenshots/sales_trend.png" alt="Sales Trend" width="500"/>

- **시계열 분석**: 일/주/월별 매출 트렌드
- **이동평균선**: 7일, 30일 MA
- **파레토 차트**: 상위 20% 상품의 매출 기여도 시각화
- **전월 대비 성장률**: % 자동 계산

---

### 4️⃣ SQL Analytics (고급 쿼리 자동 생성)

<img src="docs/screenshots/sql_query_view.png" alt="SQL Query View" width="500"/>

- **CTE 3단계 중첩**: RFM 분석 SQL 자동 생성
- **Window Functions**: NTILE, LAG, ROW_NUMBER, SUM OVER
- **이동평균 구현**: ROWS BETWEEN 활용
- **쿼리 복사/실행 기능**: Streamlit UI 통합

📂 [SQL 역량 증명 문서](docs/SQL_CAPABILITIES.md) | 📂 [SQL 분석 다이어그램](diagrams/SQL분석.drawio.png)

---

## 🚀 빠른 시작

### 로컬 환경 실행

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/auto-insight-platform.git
cd auto-insight-platform

# 2. 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 앱 실행
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 사용할 수 있습니다.

### 온라인 데모 체험

배포된 버전을 바로 체험하세요 (크롤링 제외, 샘플 데이터 제공):

👉 **[Live Demo 바로가기](배포URL_여기에_입력)**

---

## 💪 기술적 도전과 해결

### 1️⃣ 배포 환경 크롤링 제약 문제

**문제**:
- Streamlit Cloud에서 Selenium WebDriver 실행 불가
- 크롤링 기능 없이는 데모 불가능

**해결**:
- **하이브리드 아키텍처** 구현
  - 로컬: 실제 Selenium 크롤링
  - 배포: 미리 수집한 샘플 데이터 제공
- 환경 변수 `IS_DEPLOYED`로 자동 감지
- 법적 리스크 최소화 (배포 버전에서 크롤링 비활성화)

**학습**:
- 환경별 기능 분리 설계
- 법적 안전성 고려한 아키텍처

---

### 2️⃣ OpenAI API 비용 폭증 위험

**문제**:
- 전체 리뷰(1,000개)를 GPT로 분석 시 비용 $10+ 예상
- 개인 프로젝트 예산 초과

**해결**:
- **부정 리뷰만 샘플링** (100개)
- 1차: 키워드 기반 감성 분류 (무료)
- 2차: 부정 리뷰만 GPT 심층 분석
- 비용 **95% 절감** ($10 → $0.5)

**학습**:
- 비용-성능 트레이드오프 최적화
- 하이브리드 분석 전략

---

### 3️⃣ K-Means 군집 자동 네이밍

**문제**:
- K-Means는 숫자 라벨만 제공 (0, 1, 2...)
- 비개발자에게는 의미 없는 정보

**해결**:
- 군집 중심값(centroid) 분석
- R, F, M 평균값 기준 룰 기반 네이밍
  ```python
  if R높고 F높음 → "VIP 고객"
  if R높고 F낮음 → "신규 고객"
  if R낮음 → "이탈 위험 고객"
  ```
- 비즈니스 인사이트로 변환

**학습**:
- 머신러닝 결과를 비즈니스 용어로 번역
- 도메인 지식과 알고리즘 연결

---

## 📊 프로젝트 성과

### 성능 지표

- ✅ **10만 건 데이터 처리**: 30초 이내 (Pandas 최적화)
- ✅ **RFM 군집 품질**: Silhouette Score 0.6+ (K=5)
- ✅ **한국어 NLP 정확도**: 85%+ (감성 분석)
- ✅ **메모리 사용량**: 800MB 이하 (Streamlit Cloud 1GB 제한)

### 기술 역량 증명

| 분야 | 구현 내용 | 코드 위치 |
|------|----------|----------|
| **Python** | Pandas, NumPy 고급 활용 | `modules/preprocessor.py` |
| **머신러닝** | K-Means 군집화, 평가 지표 | `modules/rfm_analyzer.py` (200줄) |
| **NLP** | 형태소 분석, TF-IDF, LDA | `modules/text_analyzer.py` (300줄) |
| **SQL** | CTE, Window Functions, 인덱스 | `modules/sql_query_generator.py` (400줄) |
| **API 통합** | OpenAI API, Rate Limit 핸들링 | `modules/gpt_analyzer.py` |
| **웹 개발** | Streamlit 멀티 페이지 | `app.py`, `pages/` |
| **데이터 시각화** | Plotly 인터랙티브 차트 | `modules/visualizer.py` |

---

## 📁 프로젝트 구조

```
auto-insight-platform/
├── app.py                        # Streamlit 메인 앱
├── requirements.txt              # 의존성 패키지
│
├── modules/                      # 분석 엔진 (7개 모듈, 2,000줄)
│   ├── data_loader.py            # CSV/Excel 로드, 검증
│   ├── preprocessor.py           # 결측치, 이상치, 파생변수
│   ├── rfm_analyzer.py           # K-Means 군집화
│   ├── text_analyzer.py          # NLP 파이프라인
│   ├── sales_analyzer.py         # 시계열 분석
│   ├── gpt_analyzer.py           # GPT API 통합
│   ├── db_manager.py             # SQLite CRUD
│   ├── sql_query_generator.py    # SQL 자동 생성
│   ├── visualizer.py             # Plotly 차트
│   ├── insight_generator.py      # 인사이트 생성
│   └── report_generator.py       # HTML 리포트
│
├── crawlers/                     # 웹 크롤링 (독립 모듈)
│   ├── naver_movie_crawler.py    # 네이버 영화 리뷰
│   └── naver_place_crawler.py    # 네이버 플레이스 리뷰
│
├── diagrams/                     # 아키텍처 다이어그램
│   ├── 시스템아키텍처.png
│   ├── 데이터플로우.png
│   ├── RFM분석.png
│   └── SQL분석.png
│
├── docs/                         # 기술 문서
│   ├── ARCHITECTURE.md           # 시스템 아키텍처 상세
│   ├── SQL_CAPABILITIES.md       # SQL 샘플 쿼리
│   └── screenshots/              # UI 스크린샷
│
├── config/
│   └── settings.yaml             # 설정 파일
│
├── sample_data/                  # 샘플 데이터 (배포용)
│   ├── ecommerce_sample.csv
│   ├── reviews_sample.csv
│   └── sales_sample.csv
│
└── tests/                        # 테스트 코드
    ├── test_rfm_analyzer.py
    └── test_sql_generator.py
```

---

## 🎨 주요 시각화 갤러리

<table>
  <tr>
    <td align="center">
      <img src="docs/screenshots/rfm_3d.png" width="300"/><br/>
      <b>3D 고객 세분화 맵</b>
    </td>
    <td align="center">
      <img src="docs/screenshots/wordcloud.png" width="300"/><br/>
      <b>리뷰 Word Cloud</b>
    </td>
    <td align="center">
      <img src="docs/screenshots/sales_trend.png" width="300"/><br/>
      <b>매출 트렌드 차트</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/screenshots/segment_pie.png" width="300"/><br/>
      <b>고객 세그먼트 분포</b>
    </td>
    <td align="center">
      <img src="docs/screenshots/topic_modeling.png" width="300"/><br/>
      <b>토픽 모델링 결과</b>
    </td>
    <td align="center">
      <img src="docs/screenshots/pareto.png" width="300"/><br/>
      <b>파레토 차트</b>
    </td>
  </tr>
</table>

---

## 🔍 SQL 역량 증명 (샘플 쿼리)

### RFM 분석 SQL (CTE 3단계 중첩)

```sql
-- 고객별 RFM 지표 계산 및 세그먼트 분류
WITH customer_rfm AS (
    SELECT
        customer_id,
        JULIANDAY('2025-12-07') - JULIANDAY(MAX(invoice_date)) AS recency,
        COUNT(DISTINCT invoice_no) AS frequency,
        SUM(quantity * unit_price) AS monetary
    FROM transactions
    WHERE quantity > 0 AND unit_price > 0
    GROUP BY customer_id
),
rfm_quantiles AS (
    SELECT
        customer_id,
        recency, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_rfm
)
SELECT
    customer_id,
    recency, frequency, monetary,
    r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'VIP 고객'
        WHEN r_score >= 3 AND f_score >= 3 THEN '충성 고객'
        WHEN r_score <= 2 THEN '이탈 위험 고객'
        ELSE '일반 고객'
    END AS segment
FROM rfm_quantiles
ORDER BY monetary DESC;
```

### 매출 트렌드 SQL (Window Functions: LAG, 이동평균)

```sql
-- 일별 매출 트렌드 + 전일 대비 성장률 + 7일 이동평균
WITH daily_sales AS (
    SELECT
        DATE(sales_date) AS date,
        SUM(sales_amount) AS total_sales
    FROM sales
    GROUP BY DATE(sales_date)
)
SELECT
    date,
    total_sales,
    LAG(total_sales, 1) OVER (ORDER BY date) AS prev_day_sales,
    ROUND(
        (total_sales - LAG(total_sales, 1) OVER (ORDER BY date)) * 100.0 /
        LAG(total_sales, 1) OVER (ORDER BY date), 2
    ) AS growth_rate_pct,
    ROUND(
        AVG(total_sales) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS ma_7_days
FROM daily_sales
ORDER BY date;
```

📂 [전체 SQL 샘플 쿼리 10개 보기](docs/SQL_CAPABILITIES.md)

---

## 🛠️ 기술 스택 상세

### Backend & Data Processing
- **Python 3.9+**: 코어 언어
- **Pandas 2.1.4**: 데이터 전처리, 집계
- **NumPy 1.24.3**: 수치 연산
- **SQLite 3.x**: 임베디드 데이터베이스

### Machine Learning & NLP
- **Scikit-learn 1.3.2**: K-Means 군집화, StandardScaler
- **KoNLPy 0.6.0**: 한국어 형태소 분석 (Okt)
- **Gensim 4.3.2**: LDA 토픽 모델링
- **TF-IDF**: 키워드 추출
- **OpenAI GPT-4o-mini**: 심층 감성 분석

### Visualization
- **Plotly 5.18.0**: 인터랙티브 차트 (3D, 필터링)
- **Matplotlib 3.8.2**: 정적 차트
- **WordCloud 1.9.3**: 키워드 시각화

### Web Framework
- **Streamlit 1.30.0**: 웹 UI, 멀티 페이지
- **Streamlit Cloud**: 무료 배포 플랫폼

### Web Crawling
- **Selenium 4.16.0**: 브라우저 자동화
- **undetected-chromedriver 3.5.5**: Anti-detection

---

## 📚 기술 문서

- 📂 [시스템 아키텍처 상세](docs/ARCHITECTURE.md)
- 📂 [SQL 역량 증명 (샘플 쿼리 10개)](docs/SQL_CAPABILITIES.md)
- 📂 [배포 가이드 (Streamlit Cloud)](docs/DEPLOYMENT.md)
- 📂 [기술적 의사결정 (ADR)](docs/TECHNICAL_DECISIONS.md)
- 📂 [포트폴리오 학습 가이드](포트폴리오_학습가이드.md)
- 📂 [면접용 Answer Book](면접용_Answer_Book.md)

---

## 🎯 개발 로드맵

### ✅ Phase 1 - E-commerce 분석 (완료)
- [x] RFM 분석 및 K-Means 군집화
- [x] 3D 시각화
- [x] HTML 리포트 생성

### ✅ Phase 2 - 리뷰 분석 (완료)
- [x] 한국어 형태소 분석
- [x] 감성 분류
- [x] GPT 심층 분석
- [x] Word Cloud

### ✅ Phase 3 - 매출 분석 (완료)
- [x] 시계열 트렌드
- [x] 파레토 차트
- [x] 이동평균선

### ✅ Phase 4 - SQL Analytics (완료)
- [x] SQLite 통합
- [x] SQL 쿼리 자동 생성
- [x] CTE, Window Functions
- [x] Streamlit UI 통합

### 🔜 Phase 5 - 추가 기능 (선택적)
- [ ] CLV (고객 생애 가치) 예측
- [ ] ARIMA 시계열 예측
- [ ] 연관 규칙 마이닝 (Apriori)
- [ ] PDF 리포트 생성

---

## 🐛 문제 해결

### Streamlit 실행 오류
```bash
pip uninstall streamlit
pip install streamlit==1.30.0
```

### 한국어 NLP 오류 (KoNLPy)
Java 설치 필요 (KoNLPy 의존성):
- Windows: https://www.java.com/ko/download/
- Mac: `brew install openjdk`
- Linux: `sudo apt-get install default-jdk`

### Plotly 차트 표시 안 됨
브라우저 캐시 삭제 후 새로고침 (Ctrl + F5)

---

## 📜 라이선스 및 면책

이 프로젝트는 **개인 학습 및 포트폴리오 목적**으로 제작되었습니다.

**크롤링 관련 주의사항**:
- 웹 크롤링 기능은 **로컬 환경에서만** 사용 가능합니다.
- 배포 버전에서는 법적 안전을 위해 크롤링 기능이 비활성화되어 있습니다.
- 크롤링 시 `robots.txt` 준수 및 1초 이상 요청 딜레이를 적용합니다.
- 상업적 사용을 금지하며, 학습 및 연구 목적으로만 사용해주세요.

---

## 👨‍💻 개발자 정보

**[이름]**
- 📧 Email: your.email@example.com
- 🔗 LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- 📝 Tech Blog: [yourblog.com](https://yourblog.com)
- 💼 Portfolio: [yourportfolio.com](https://yourportfolio.com)

---

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 라이브러리를 사용합니다:

- [Streamlit](https://streamlit.io/) - 웹 앱 프레임워크
- [Plotly](https://plotly.com/) - 인터랙티브 차트
- [Scikit-learn](https://scikit-learn.org/) - 머신러닝
- [Pandas](https://pandas.pydata.org/) - 데이터 처리
- [OpenAI](https://openai.com/) - GPT API
- [KoNLPy](https://konlpy.org/) - 한국어 NLP

---

<p align="center">
  Made with ❤️ by [Your Name]<br/>
  ⭐ Star this repo if you find it helpful!
</p>
