# 📊 Auto-Insight Platform

AI 기반 자동 데이터 분석 및 리포트 생성 시스템

## 🎯 프로젝트 소개

**Auto-Insight Platform**은 비개발자도 쉽게 사용할 수 있는 자동 데이터 분석 도구입니다.
CSV/Excel 파일을 업로드하면 AI가 자동으로 분석하고 인사이트를 제공합니다.

### 주요 기능

- 🛒 **E-commerce 분석**: RFM 분석, 고객 세분화, 구매 패턴 발견
- 📈 **매출 분석**: 시계열 트렌드, 상품별 성과, ABC 분석
- 💬 **리뷰 분석**: 감성 분석, 토픽 모델링, 키워드 추출
- 🔍 **SQL Analytics**: SQLite 기반 고급 쿼리 분석 (CTE, Window Functions)
- 📊 **인터랙티브 대시보드**: Plotly 기반 동적 차트
- 📄 **HTML 리포트 자동 생성**: 전문가 수준의 분석 리포트
- 🕷️ **웹 크롤링**: 네이버 영화/웹툰 등 데이터 자동 수집

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론 (또는 다운로드)
cd auto-insight-platform

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 사용할 수 있습니다.

### 3. 사용 방법

1. **분석 타입 선택**: E-commerce, 매출 분석, 리뷰 분석 중 선택
2. **파일 업로드**: CSV 또는 Excel 파일 업로드
3. **자동 분석**: 클릭 한 번으로 분석 완료
4. **결과 확인**: 대시보드에서 인터랙티브 차트 확인
5. **리포트 다운로드**: HTML 리포트 또는 CSV 결과 다운로드

## 📁 프로젝트 구조

```
auto-insight-platform/
│
├── app.py                      # Streamlit 메인 앱
├── requirements.txt            # 앱 의존성 패키지
├── README.md                   # 이 파일
│
├── config/
│   └── settings.yaml           # 설정 파일
│
├── modules/                    # 분석 엔진 모듈
│   ├── __init__.py
│   ├── data_loader.py          # 데이터 로드 및 검증
│   ├── preprocessor.py         # 데이터 전처리
│   ├── rfm_analyzer.py         # RFM 분석 (E-commerce)
│   ├── text_analyzer.py        # 텍스트 분석 (리뷰) - 구현 예정
│   ├── sales_analyzer.py       # 매출 분석 - 구현 예정
│   ├── visualizer.py           # 차트 생성
│   ├── insight_generator.py    # 인사이트 자동 생성
│   └── report_generator.py     # HTML 리포트 생성
│
├── crawlers/                   # 독립 크롤링 스크립트
│   ├── README.md               # 크롤러 사용 가이드
│   ├── requirements_crawler.txt
│   ├── naver_movie_crawler.py  # 네이버 영화 리뷰 크롤러
│   └── output/                 # 크롤링 결과 저장 폴더
│
├── templates/                  # HTML 템플릿
│   ├── report_template.html
│   └── styles.css
│
└── tests/                      # 테스트 코드
    └── sample_data.csv
```

## 📊 지원하는 데이터 형식

### E-commerce 데이터

**필수 컬럼:**
- `CustomerID`: 고객 ID
- `InvoiceDate`: 구매 날짜
- `Quantity`: 수량
- `UnitPrice`: 단가

**선택 컬럼:**
- `InvoiceNo`: 송장 번호
- `Description`: 상품 설명
- `Country`: 국가

### 매출 데이터

**필수 컬럼:**
- `Date`: 날짜
- `Product`: 상품명
- `Sales` 또는 `Revenue`: 매출액

### 리뷰 데이터

**필수 컬럼:**
- `Review` 또는 `Text`: 리뷰 텍스트

**선택 컬럼:**
- `Rating` 또는 `Score`: 평점
- `Date`: 작성일

## 🎨 주요 시각화

### E-commerce 분석
- 3D 고객 세분화 맵
- 군집별 RFM 평균 비교
- 고객 세그먼트 분포 (파이 차트)
- RFM 히트맵

### 매출 분석 (구현 예정)
- 시계열 매출 트렌드
- 상품별 성과 차트
- 계절성 분석

### 리뷰 분석 (구현 예정)
- 감성 분포 차트
- Word Cloud
- 토픽별 문서 분포

## 🕷️ 웹 크롤링 사용하기

데이터가 없다면 크롤러를 사용하여 수집할 수 있습니다.

```bash
# 크롤러 의존성 설치
cd crawlers
pip install -r requirements_crawler.txt

# 네이버 영화 리뷰 크롤링
python naver_movie_crawler.py --movie-id 215095 --count 500 --headless

# 결과는 crawlers/output/ 폴더에 저장됨
```

자세한 사용법은 [`crawlers/README.md`](crawlers/README.md)를 참조하세요.

## ⚙️ 설정

`config/settings.yaml` 파일에서 다양한 설정을 변경할 수 있습니다:

- 군집 수 범위 (min_clusters, max_clusters)
- 이상치 탐지 방법 (IQR, Z-score)
- 시각화 색상 스키마
- 파일 업로드 제한

## 🐛 문제 해결

### Streamlit 실행 오류

```bash
# Streamlit 재설치
pip uninstall streamlit
pip install streamlit==1.30.0
```

### 한국어 NLP 오류 (KoNLPy)

```bash
# Java 설치 필요 (KoNLPy 의존성)
# Windows: https://www.java.com/ko/download/
# Mac: brew install openjdk
# Linux: sudo apt-get install default-jdk
```

### Plotly 차트가 표시되지 않음

브라우저 캐시를 삭제하고 새로고침하세요 (Ctrl + F5).

## 📈 개발 로드맵

### Phase 1 - MVP (완료)
- [x] Streamlit 기본 UI
- [x] 파일 업로드 및 검증
- [x] RFM 분석
- [x] 기본 시각화
- [x] HTML 리포트

### Phase 2 - 리뷰 분석 (진행 중)
- [ ] KoBERT 감성 분석
- [ ] Word Cloud 생성
- [ ] 토픽 모델링 (LDA)

### Phase 3 - 고도화
- [ ] 매출 시계열 분석
- [ ] 추가 크롤러 (웹툰, 도서)
- [ ] 대시보드 템플릿 선택
- [ ] 다국어 지원

## 🤝 기여하기

이 프로젝트에 기여하고 싶으시다면:

1. 이슈를 등록하여 개선 사항 제안
2. Pull Request로 코드 기여
3. 버그 리포트 및 피드백 제공

## 🔍 SQL Analytics (Phase 4)

### SQLite 데이터베이스 통합

프로젝트에는 SQLite 데이터베이스가 통합되어 고급 SQL 쿼리로 데이터를 분석할 수 있습니다.

#### 주요 기능

1. **데이터베이스 자동 저장**
   - 크롤링 데이터를 SQLite에 자동 저장
   - CSV/Excel 업로드 데이터도 DB 저장 가능

2. **SQL 쿼리 자동 생성**
   - RFM 분석 (CTE 3단계 중첩)
   - 매출 트렌드 (Window Functions: LAG, 이동평균)
   - 파레토 분석 (누적 합계, ROW_NUMBER)
   - 감성 분석 (CASE WHEN)

3. **고급 SQL 기술**
   - ✅ CTE (Common Table Expressions)
   - ✅ Window Functions (NTILE, LAG, ROW_NUMBER, SUM OVER)
   - ✅ Window Frame (ROWS BETWEEN)
   - ✅ Date Functions (JULIANDAY)
   - ✅ Aggregate Functions
   - ✅ Subquery

#### 사용 방법

```bash
# 샘플 데이터 생성
python utils/generate_sample_data.py

# Streamlit 앱에서 SQL Analytics 페이지 접속
streamlit run app.py
# → 4_SQL_Analytics 페이지 선택
```

자세한 SQL 기능은 `docs/SQL_PORTFOLIO_GUIDE.md`를 참고하세요.

---

## 📜 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 제작되었습니다.

## 📞 문의

- 프로젝트 이슈: GitHub Issues 활용
- 크롤링 관련: `crawlers/README.md` 참조

## 🙏 감사의 말

이 프로젝트는 다음 라이브러리를 사용합니다:

- [Streamlit](https://streamlit.io/) - 웹 앱 프레임워크
- [Plotly](https://plotly.com/) - 인터랙티브 차트
- [Scikit-learn](https://scikit-learn.org/) - 머신러닝
- [Pandas](https://pandas.pydata.org/) - 데이터 처리
- [Selenium](https://www.selenium.dev/) - 웹 크롤링

---

Made with ❤️ by Auto-Insight Team
