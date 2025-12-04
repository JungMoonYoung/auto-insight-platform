# Auto-Insight Platform 개발 계획서
## 날짜별 개발 일정 (DAY 1 ~ DAY 33)

**계획 수립일**: 2025-01-27
**전체 기간**: 33일 (약 7주)
**완료된 작업**: DAY 1-18 (55%)
**남은 작업**: DAY 19-33 (45%)
**최종 데드라인**: 2개월 후 (여유 5주)

---

## 📊 전체 진행 현황

```
전체 진행률: 55% (18/33 DAY)

✅ DAY 1-18:   완료 (RFM 분석, 텍스트 분석, 시각화)
🔄 DAY 19-28:  진행 예정 (UI 통합, 자동화)
📦 DAY 29-33:  진행 예정 (판매 분석, 배포)
```

---

## 📋 Phase 1: 분석 엔진 구축 (DAY 1-18) - 완료 ✅

---

## Week 1-2: 핵심 모듈 구현 (DAY 1-10)

### DAY 1 (완료 ✅) - 프로젝트 기반 구조 설정

**목표**: 프로젝트 초기 설정 및 데이터 로더 구현

**구현 내용**:
- 프로젝트 폴더 구조 생성 (modules/, crawlers/, config/, utils/)
- requirements.txt 작성 (Streamlit, pandas, scikit-learn, KoNLPy 등 52개 패키지)
- .gitignore 설정 (Python 표준, 환경변수, 가상환경 제외)
- config/settings.yaml 작성 (RFM, 텍스트 분석, 전처리 파라미터 정의)
- modules/data_loader.py 클래스 뼈대 작성

**산출물**:
- 프로젝트 폴더 구조 완성
- requirements.txt (52개 패키지)
- config/settings.yaml (분석 파라미터 설정)
- modules/data_loader.py (기본 구조)

**특이사항**:
- 가상환경 생성 및 패키지 설치 완료
- Git 저장소 초기화

---

### DAY 2 (완료 ✅) - 데이터 로더 완성 및 전처리 시작

**목표**: 파일 로드 기능 완성 및 전처리 모듈 구현

**구현 내용**:
- modules/data_loader.py 완성 (158줄)
  - CSV/Excel 파일 로드 기능
  - 한글 인코딩 자동 감지 (chardet 라이브러리)
  - 폴백 인코딩 순서: utf-8 → cp949 → euc-kr → latin1
  - 데이터 품질 리포트 함수 (행/열 수, 결측치, 고유값 비율)
  - 날짜 컬럼 자동 감지
- modules/preprocessor.py 구현 시작 (200줄)
  - 결측치 처리 (auto 전략: 숫자형=median, 범주형=mode)
  - 결측치 50% 이상 시 경고 메시지
  - 메소드 체이닝 패턴 적용

**산출물**:
- modules/data_loader.py (완성, 158줄)
- modules/preprocessor.py (기본 기능, 200줄)

**특이사항**:
- 한글 인코딩 문제 해결 (cp949, euc-kr 지원)
- 파일 로드 테스트 성공 (샘플 CSV 파일)

---

### DAY 3 (완료 ✅) - 전처리 모듈 완성 및 RFM 설계

**목표**: 전처리 고도화 및 RFM 분석 시작

**구현 내용**:
- modules/preprocessor.py 완성 (276줄)
  - 이상치 처리 (IQR 방식: Winsorization으로 경계값에 클리핑)
  - Z-score 방식 옵션 (이상치 제거)
  - 중복 제거 함수
  - 날짜 파생 변수 생성 (year, month, day, dayofweek, is_weekend, season)
- modules/rfm_analyzer.py 클래스 설계 및 기본 구조 작성
  - RFM 계산 로직 설계
  - 필수 컬럼 검증 (CustomerID, InvoiceDate, Quantity, UnitPrice)

**산출물**:
- modules/preprocessor.py (완성, 276줄)
- modules/rfm_analyzer.py (기본 구조, 100줄)

**특이사항**:
- 전처리 체이닝 패턴 적용 (method chaining)
- IQR 방식 이상치 처리 (제거 대신 클리핑으로 데이터 보존)

---

### DAY 4 (완료 ✅) - RFM 계산 로직 구현

**목표**: RFM 지표 계산 및 데이터 변환

**구현 내용**:
- modules/rfm_analyzer.py RFM 계산 함수 완성
  - Recency: (기준일 - 마지막 구매일).days
  - Frequency: 고객별 거래 건수
  - Monetary: 고객별 총 매출액 (Quantity × UnitPrice)
  - 기준일 자동 설정 (미지정 시 데이터 최신 날짜 사용)
- 데이터 스케일링 준비
  - Log 변환 (np.log1p) 적용 준비
  - StandardScaler 적용 준비
- 테스트 데이터로 RFM 계산 검증

**산출물**:
- modules/rfm_analyzer.py (RFM 계산 완성, 200줄)

**특이사항**:
- RFM 계산 정확도 확인 (수동 계산과 비교)
- Recency는 낮을수록 좋음, Frequency/Monetary는 높을수록 좋음

---

### DAY 5 (완료 ✅) - RFM 군집화 구현 (1/2)

**목표**: K-Means 군집화 기본 구현

**구현 내용**:
- K-Means 군집화 로직 구현
  - Log 변환: np.log1p(RFM values)
  - StandardScaler로 정규화
  - scikit-learn KMeans 적용
- 최적 K 탐색 로직 (Elbow Method + Silhouette Score)
  - K 범위: 3~8 (설정 가능)
  - 각 K에 대해 Silhouette Score 계산
  - 최고 점수 K 자동 선택
- 군집별 평균 RFM 계산 함수

**산출물**:
- modules/rfm_analyzer.py (군집화 추가, 280줄)

**특이사항**:
- Log 변환으로 왜곡 분포 정규화
- Silhouette Score로 최적 K 자동 선택 (주관성 배제)

---

### DAY 6 (완료 ✅) - RFM 군집 네이밍 및 검색 기능

**목표**: RFM 분석 모듈 완성

**구현 내용**:
- modules/rfm_analyzer.py 완성 (304줄)
  - 군집 자동 네이밍 로직
    - R 낮음 + F/M 높음 → "💎 VIP 고객"
    - R 낮음 + F/M 중간 → "⭐ 충성 고객"
    - R 높음 + F/M 낮음 → "⚠️ 이탈 위험 고객"
    - R 중간 + F/M 중간 → "🔄 일반 고객"
    - 기타 → "🆕 신규 고객"
  - 고객 검색 기능 (CustomerID로 군집 및 RFM 조회)
  - 군집별 통계 요약 (평균 RFM, 고객 수, 비율)
- 전체 RFM 분석 파이프라인 테스트 성공

**산출물**:
- modules/rfm_analyzer.py (완성, 304줄)

**특이사항**:
- 비즈니스 의미 있는 군집명 자동 부여
- 이모지 사용으로 시각적 구분 강화

---

### DAY 7 (완료 ✅) - 텍스트 분석 기반 구조

**목표**: 한국어 NLP 설정 및 전처리 구현

**구현 내용**:
- modules/text_analyzer.py 클래스 설계 및 기본 구조 (150줄)
  - KoNLPy 설치 및 Okt 형태소 분석기 설정
  - 한글 불용어 리스트 정의 (100개)
  - 텍스트 전처리 함수 구현
    - 소문자 변환
    - 특수문자 제거 (한글, 영문, 숫자만 유지)
    - 형태소 분석 (명사 추출)
    - 불용어 제거
    - 최소 길이 2자 이상 토큰만 유지
- 전처리 파이프라인 테스트

**산출물**:
- modules/text_analyzer.py (기본 구조, 150줄)

**특이사항**:
- KoNLPy 설치 시간 소요 (Java JDK 의존성)
- Okt 선택 이유: 빠르고 정확도 높음

---

### DAY 8 (완료 ✅) - 키워드 기반 감성 분석

**목표**: 감성 분석 구현 (키워드 기반)

**구현 내용**:
- modules/text_analyzer.py 감성 분석 추가 (250줄)
  - 방법 1: 평점 기반 감성 분류
    - 평점 >= 8: 긍정 (positive)
    - 평점 >= 5: 중립 (neutral)
    - 평점 < 5: 부정 (negative)
  - 방법 2: 키워드 기반 감성 분류
    - 긍정 키워드: "좋다", "훌륭", "최고", "만족" 등 50개
    - 부정 키워드: "나쁘다", "별로", "최악", "실망" 등 50개
    - 키워드 매칭 개수로 감성 판단
  - 두 방법 결합 (평점 70%, 키워드 30%)
- 감성별 리뷰 분류 함수

**산출물**:
- modules/text_analyzer.py (감성 분석 추가, 250줄)

**특이사항**:
- 딥러닝 모델 대신 키워드 기반 (속도 빠름, 비용 없음)
- GPT 분석은 부정 리뷰만 따로 처리 예정

---

### DAY 9 (완료 ✅) - TF-IDF 키워드 추출

**목표**: 키워드 추출 및 토픽 모델링 준비

**구현 내용**:
- modules/text_analyzer.py TF-IDF 구현 (300줄)
  - scikit-learn TfidfVectorizer 사용
  - 감성별 키워드 추출 (긍정/중립/부정 각각 Top 20)
  - n-gram 범위: 1~2 (단어 및 2단어 조합)
  - 최소 문서 빈도: 2 (너무 드문 단어 제외)
- 단어 빈도수 계산 함수 (Counter 사용)
- 워드 클라우드 데이터 준비

**산출물**:
- modules/text_analyzer.py (TF-IDF 추가, 300줄)

**특이사항**:
- TF-IDF로 중요도 기반 키워드 추출
- 감성별 분리로 인사이트 명확화

---

### DAY 10 (완료 ✅) - LDA 토픽 모델링

**목표**: 텍스트 분석 모듈 완성

**구현 내용**:
- modules/text_analyzer.py LDA 토픽 모델링 완성 (361줄)
  - Gensim LDA 모델 사용
  - CountVectorizer로 문서-단어 행렬 생성
  - 토픽 개수: 5개 (설정 가능)
  - 각 토픽당 상위 10개 단어 추출
  - 토픽 일관성 점수 계산 (Coherence Score)
- 전체 텍스트 분석 파이프라인 완성
  - 전처리 → 감성 분석 → 키워드 추출 → 토픽 모델링

**산출물**:
- modules/text_analyzer.py (완성, 361줄)

**특이사항**:
- LDA로 숨겨진 토픽 자동 발견
- 토픽 레이블 자동 생성 (상위 3단어 조합)

---

## Week 3: 시각화 및 크롤링 (DAY 11-15)

### DAY 11 (완료 ✅) - 시각화 모듈 기반 구조

**목표**: Plotly 시각화 기본 설정

**구현 내용**:
- modules/visualizer.py 클래스 설계 (150줄)
  - Plotly 테마 설정 (plotly_white)
  - 한글 폰트 설정 (Malgun Gothic)
  - 차트 기본 레이아웃 템플릿
- RFM 3D Scatter Plot 구현
  - x축: Recency, y축: Frequency, z축: Monetary
  - 색상: 군집별 구분
  - 호버 정보: CustomerID, RFM 값, 군집명
  - 인터랙티브 회전 가능

**산출물**:
- modules/visualizer.py (기본 구조, 150줄)

**특이사항**:
- Plotly 선택 이유: 인터랙티브, HTML 임베딩 가능
- 3D 시각화로 RFM 관계 직관적 표현

---

### DAY 12 (완료 ✅) - RFM 시각화 완성

**목표**: RFM 관련 차트 구현 완료

**구현 내용**:
- modules/visualizer.py RFM 차트 추가 (300줄)
  - 군집별 Bar Chart (3개 서브플롯)
    - 평균 Recency (낮을수록 좋음)
    - 평균 Frequency (높을수록 좋음)
    - 평균 Monetary (높을수록 좋음)
  - 군집별 Pie Chart
    - 고객 수 비율
    - 매출 비율
    - 거래 건수 비율
  - 군집별 박스플롯 (RFM 분포)
- 차트 스타일 일관성 유지

**산출물**:
- modules/visualizer.py (RFM 차트 완성, 300줄)

**특이사항**:
- 서브플롯으로 여러 차트 한 화면에 표시
- 색상 팔레트 일관성 유지

---

### DAY 13 (완료 ✅) - 텍스트 분석 시각화 및 크롤러 시작

**목표**: 워드 클라우드 및 감성 차트, 크롤러 기본 구조

**구림 내용**:
- modules/visualizer.py 텍스트 차트 추가 (500줄 추정)
  - 워드 클라우드 (한글 폰트 설정)
  - 감성 분포 Pie Chart
  - 감성별 키워드 Bar Chart (Top 15)
  - 시간별 리뷰 개수 Line Chart
- crawlers/naver_movie_crawler.py 기본 구조 작성
  - Selenium WebDriver 설정
  - ChromeDriverManager로 자동 드라이버 설치
  - headless 모드 옵션

**산출물**:
- modules/visualizer.py (텍스트 차트 추가, 500줄 추정)
- crawlers/naver_movie_crawler.py (기본 구조, 100줄)

**특이사항**:
- 워드 클라우드 한글 깨짐 방지 (NanumGothic 폰트)
- Selenium 설정 시 user-agent 스푸핑

---

### DAY 14 (완료 ✅) - 네이버 영화 크롤러 구현

**목표**: 영화 리뷰 크롤링 로직 완성

**구현 내용**:
- crawlers/naver_movie_crawler.py 크롤링 로직 구현 (300줄)
  - 영화 ID로 리뷰 페이지 접근
  - 리뷰 데이터 추출 (평점, 텍스트, 작성자, 날짜)
  - 페이지네이션 처리 (더보기 버튼 클릭)
  - 배치 단위 크롤링 (50개씩)
  - 진행률 표시 (tqdm 프로그레스 바)
  - 에러 핸들링 (요소 없을 때, 타임아웃)
  - 딜레이 설정 (1초) - 서버 부하 방지
- CSV 저장 기능

**산출물**:
- crawlers/naver_movie_crawler.py (완성, 300줄)

**특이사항**:
- undetected-chromedriver 사용 (봇 탐지 회피)
- 명시적 대기 (WebDriverWait) 사용

---

### DAY 15 (완료 ✅) - 네이버 플레이스 크롤러 구현

**목표**: 플레이스 리뷰 크롤링 완성 및 CLI 테스트

**구현 내용**:
- crawlers/naver_place_crawler.py 구현 (18KB, 약 400줄)
  - 플레이스 ID로 리뷰 페이지 접근
  - iframe 전환 처리
  - 리뷰 데이터 추출 (별점, 텍스트, 날짜, 이미지 개수)
  - 스크롤 기반 로딩 처리
  - 배치 크롤링 및 에러 핸들링
  - CSV 저장
- 두 크롤러 CLI 테스트 성공
  - 영화 리뷰 100개 수집 성공
  - 플레이스 리뷰 100개 수집 성공

**산출물**:
- crawlers/naver_place_crawler.py (완성, 400줄)
- 테스트 데이터 (영화 리뷰 100개, 플레이스 리뷰 100개)

**특이사항**:
- iframe 전환 처리 필요 (네이버 플레이스 구조)
- 동적 로딩 처리 (스크롤 이벤트)

---

## Week 4: UI 및 리포트 (DAY 16-18)

### DAY 16 (완료 ✅) - Streamlit UI 기본 구현

**목표**: 파일 업로드 및 기본 UI 구성

**구현 내용**:
- app.py 작성 (단일 페이지 구조, 약 500줄)
  - Streamlit 기본 레이아웃
  - 사이드바: 분석 타입 선택 (E-commerce, 리뷰, 판매)
  - 파일 업로드 위젯 (CSV/Excel)
  - 업로드 파일 미리보기
  - 데이터 품질 리포트 표시
- modules/data_loader.py 통합
- 세션 상태 관리 (st.session_state)
  - 업로드 데이터 저장
  - 분석 결과 저장

**산출물**:
- app.py (기본 UI, 500줄)

**특이사항**:
- 단일 페이지 구조 (나중에 멀티 페이지로 전환 필요)
- 세션 상태로 데이터 유지

---

### DAY 17 (완료 ✅) - 분석 워크플로우 연결 (1/2)

**목표**: RFM 및 텍스트 분석 UI 통합

**구현 내용**:
- app.py 분석 실행 로직 추가 (약 1000줄)
  - E-commerce 분석 버튼 및 파이프라인
    - 전처리 → RFM 계산 → 군집화 → 시각화
  - RFM 분석 결과 탭 구성
    - 군집 요약 테이블
    - 3D Scatter Plot
    - 군집별 Bar Chart
    - 고객 검색 기능
  - 리뷰 분석 버튼 및 파이프라인
    - 전처리 → 감성 분석 → 키워드 추출 → 토픽 모델링 → 시각화
  - 리뷰 분석 결과 탭 구성
    - 감성 분포 Pie Chart
    - 워드 클라우드
    - 키워드 Bar Chart
- modules/insight_generator.py 기본 구조 작성 (14KB)
  - 인사이트 자동 생성 로직 설계
  - 액션 아이템 추천 구조

**산출물**:
- app.py (분석 연결, 1000줄)
- modules/insight_generator.py (기본 구조, 14KB)

**특이사항**:
- 탭 구조로 결과 정리
- 차트 인터랙티브 기능 작동

---

### DAY 18 (완료 ✅) - 리포트 생성 및 통합 테스트

**목표**: HTML 리포트 생성 및 전체 통합

**구현 내용**:
- modules/report_generator.py 구현 (10.6KB, 약 350줄)
  - HTML 템플릿 설계
  - CSS 스타일 (그라데이션 헤더, 카드 레이아웃)
  - Plotly 차트를 HTML로 변환
  - 인사이트 및 액션 아이템 포맷팅
  - 데이터 개요 테이블
  - 다운로드 기능 (st.download_button)
- modules/insight_generator.py 부분 구현
  - RFM 인사이트 생성 (VIP 비율, 이탈 위험 비율)
  - 텍스트 인사이트 생성 (부정 비율, 주요 키워드)
- app.py에 리포트 다운로드 기능 통합
- modules/gpt_analyzer.py 기본 구조 작성 (100줄)
  - OpenAI API 클라이언트 설정
  - 배치 처리 로직
  - JSON 응답 파싱
- 전체 워크플로우 통합 테스트
  - 파일 업로드 → E-commerce 분석 → 리포트 다운로드 성공
  - 파일 업로드 → 리뷰 분석 → 리포트 다운로드 성공
- 버그 수정 (인코딩, 차트 렌더링)

**산출물**:
- modules/report_generator.py (완성, 350줄)
- modules/insight_generator.py (부분 구현, 14KB)
- modules/gpt_analyzer.py (기본 구조, 100줄)
- app.py (리포트 통합, 약 2000줄 추정)

**특이사항**:
- HTML 리포트 디자인 기본적 (개선 필요)
- GPT 분석은 아직 UI 통합 안 됨 (구조만 작성)
- 판매 분석 모듈은 거의 비어있음 (sales_analyzer.py 1.7KB)

---

## 📊 Phase 1 완료 요약 (DAY 1-18)

### ✅ 완성된 모듈 (100%)
1. **modules/data_loader.py** (158줄) - 파일 로드, 인코딩 감지, 품질 리포트
2. **modules/preprocessor.py** (276줄) - 결측치, 이상치, 중복, 날짜 파생 변수
3. **modules/rfm_analyzer.py** (304줄) - RFM 계산, K-Means 군집화, 자동 네이밍
4. **modules/text_analyzer.py** (361줄) - KoNLPy, 감성 분석, TF-IDF, LDA
5. **config/settings.yaml** - 분석 파라미터 설정

### ⚠️ 부분 완성된 모듈 (30-50%)
6. **modules/visualizer.py** (500줄 추정) - RFM 및 텍스트 차트 (판매 차트 미구현)
7. **modules/report_generator.py** (350줄) - HTML 리포트 기본 (템플릿 개선 필요)
8. **modules/insight_generator.py** (14KB) - 인사이트 생성 구조 (완성도 40%)
9. **modules/gpt_analyzer.py** (100줄) - GPT 구조만 (최적화 및 UI 통합 필요)
10. **app.py** (2000줄 추정) - 단일 페이지 UI (멀티 페이지 전환 필요)

### ✅ 완성된 크롤러 (CLI 독립 실행)
11. **crawlers/naver_movie_crawler.py** (300줄) - Selenium 기반 영화 리뷰 크롤링
12. **crawlers/naver_place_crawler.py** (400줄) - iframe 전환, 플레이스 리뷰 크롤링

### ❌ 미구현 모듈
13. **modules/sales_analyzer.py** (1.7KB, 거의 비어있음) - 판매 분석 재구현 필요
14. **utils/session_manager.py** (없음) - 세션 관리 유틸리티 필요
15. **utils/environment.py** (없음) - 로컬/배포 환경 감지 필요
16. **utils/column_mapper.py** (없음) - 컬럼 자동 매핑 필요
17. **utils/progress_tracker.py** (없음) - 프로그레스 시스템 필요
18. **utils/api_key_manager.py** (없음) - API 키 관리 필요

### 🎯 달성한 기능
- ✅ CSV/Excel 파일 업로드 및 미리보기
- ✅ 한글 인코딩 자동 감지
- ✅ 데이터 전처리 (결측치, 이상치, 중복)
- ✅ RFM 분석 (K-Means 군집화, 자동 네이밍)
- ✅ 텍스트 분석 (KoNLPy, 키워드 기반 감성, TF-IDF, LDA)
- ✅ 인터랙티브 차트 (Plotly 3D, Bar, Pie, WordCloud)
- ✅ HTML 리포트 다운로드
- ✅ 독립 CLI 크롤러 (영화, 플레이스)

### ⚠️ 남은 과제
- ❌ 멀티 페이지 구조 (4개 페이지 분리)
- ❌ 크롤링 Streamlit 통합 및 하이브리드 구조
- ❌ 컬럼 자동 매핑 (FuzzyWuzzy + 데이터 추론)
- ❌ 프로그레스 추적 시스템
- ❌ GPT 최적화 (부정 리뷰만, Rate Limit 핸들링)
- ❌ 판매 분석 재구현 (시계열, 파레토)
- ❌ 상세 탐색 페이지 (필터링, 검색)
- ❌ Streamlit Cloud 배포
- ❌ 문서화 및 스크린샷

---

## 📅 Phase 2 시작: UI 통합 및 자동화 (DAY 19-33)

---

## Week 5: UI 통합 및 크롤링 하이브리드 (DAY 19-23)

### DAY 19 (2025-01-27) - 샘플 데이터 수집 + 설계

**목표**: 배포용 샘플 데이터 준비 및 멀티 페이지 구조 설계

**오전 작업 (4시간)**:
- 로컬에서 네이버 영화 리뷰 500개 크롤링
- 네이버 플레이스 리뷰 500개 크롤링
- E-commerce 샘플 데이터 1,000건 생성
- 판매 데이터 샘플 1,000건 생성
- sample_data/ 폴더 생성 및 4개 파일 저장

**오후 작업 (4시간)**:
- 현재 app.py 백업
- 멀티 페이지 구조 설계 (4개 페이지: 시작하기, 자동 분석, 상세 탐색, 내보내기)
- 세션 상태 관리 설계 (페이지 간 데이터 공유 구조)
- 각 페이지 함수 시그니처 정의

**체크리스트**:
- [ ] 샘플 데이터 4개 파일 생성 완료
- [ ] app.py 백업 완료
- [ ] 멀티 페이지 설계 문서 작성
- [ ] Git 커밋: "feat: Add sample datasets"

**산출물**:
- sample_data/naver_movie_reviews.csv
- sample_data/naver_place_reviews.csv
- sample_data/ecommerce_sample.csv
- sample_data/sales_sample.csv
- app.py.backup_before_multipage
- docs/multipage_design.md

---

### DAY 20 (2025-01-28) - 멀티 페이지 구현 (1/2)

**목표**: 세션 관리자 및 기본 페이지 구조 구현

**오전 작업 (4시간)**:
- utils/session_manager.py 작성 (세션 초기화, 데이터 저장/조회 함수)
- 페이지 1 구현: 시작하기 (파일 업로드 탭)
- 페이지 2 기본 구조: 자동 분석 (데이터 없을 때 경고 표시)

**오후 작업 (4시간)**:
- 페이지 3 기본 구조: 상세 탐색 (분석 결과 없을 때 경고)
- 페이지 4 기본 구조: 내보내기 (CSV 다운로드 버튼)
- app.py 메인 라우팅 (sidebar.radio로 4개 페이지 전환)

**체크리스트**:
- [ ] session_manager.py 작성 완료
- [ ] 4개 페이지 함수 생성
- [ ] sidebar.radio로 페이지 전환 작동
- [ ] 파일 업로드 테스트 성공

**산출물**:
- utils/session_manager.py (200줄)
- app.py 리팩토링 (500줄)
- 4개 페이지 함수

---

### DAY 21 (2025-01-29) - 크롤링 하이브리드 구현 (1/3)

**목표**: 환경 감지 및 배포 버전 크롤링 UI

**오전 작업 (4시간)**:
- utils/environment.py 작성 (로컬/배포 환경 자동 감지)
- .env.example 작성 (로컬 환경변수 템플릿)
- .streamlit/secrets.toml.example 작성 (배포 환경 시크릿 템플릿)
- 환경 감지 테스트

**오후 작업 (4시간)**:
- 배포 버전 크롤링 UI 구현 (샘플 데이터 선택 드롭다운)
- 시뮬레이션 프로그레스 바 추가
- 4개 샘플 데이터 로드 기능 구현
- 데이터 미리보기 표시

**체크리스트**:
- [ ] 환경 감지 로직 작동 확인
- [ ] 배포 버전 샘플 데이터 로드 성공
- [ ] 시뮬레이션 프로그레스 바 표시
- [ ] 법적 안내 메시지 표시

**산출물**:
- utils/environment.py (100줄)
- 크롤링 UI (배포 버전, 150줄)
- .env.example
- .streamlit/secrets.toml.example

---

### DAY 22 (2025-01-30) - 크롤링 하이브리드 구현 (2/3)

**목표**: 로컬 버전 실제 크롤링 UI 구현

**전일 작업 (8시간)**:
- 로컬 버전 크롤링 UI 구현 (네이버 영화 리뷰)
- 크롤링 소스 선택 드롭다운 (영화/플레이스)
- 영화 ID 입력 필드
- 수집 개수 슬라이더 (100~1000개)
- 실제 크롤링 실행 로직 연결
- 배치 단위 크롤링 + 진행률 실시간 업데이트
- 에러 핸들링 (영화 ID 검증, 네트워크 오류 처리)
- 크롤링 완료 후 세션에 데이터 저장

**체크리스트**:
- [ ] 로컬 크롤링 UI 구현 완료
- [ ] 네이버 영화 크롤링 테스트 성공 (100개)
- [ ] 진행률 프로그레스 바 작동
- [ ] 에러 메시지 명확하게 표시

**산출물**:
- 크롤링 UI (로컬 버전, 200줄)

---

### DAY 23 (2025-01-31) - 크롤링 하이브리드 구현 (3/3) + 통합

**목표**: 크롤링 후 자동 분석 연결 및 통합 테스트

**오전 작업 (4시간)**:
- 크롤링 완료 후 자동 페이지 전환 로직
- 자동 분석 페이지 개선 (데이터 타입 표시)
- 분석 시작 버튼 추가
- 데이터 타입별 분석 함수 연결 (E-commerce/리뷰/판매)

**오후 작업 (4시간)**:
- 로컬 환경 전체 워크플로우 테스트
- 배포 환경 시뮬레이션 테스트
- 버그 수정
- Git 커밋

**체크리스트**:
- [ ] 크롤링 → 분석 자동 전환 작동
- [ ] 로컬: 파일 업로드 → 분석 성공
- [ ] 로컬: 크롤링 → 분석 성공
- [ ] 배포 모드: 샘플 데이터 → 분석 성공
- [ ] Git 커밋: "feat: Implement hybrid crawling"

**주간 산출물**:
- ✅ 샘플 데이터 4개
- ✅ 멀티 페이지 구조 (4개)
- ✅ 하이브리드 크롤링 시스템
- ✅ 자동 분석 연결

---

## Week 2: 자동화 강화 (DAY 24-28)

### DAY 24 (완료 ✅) - 컬럼 자동 매핑 (1/3)

**목표**: 컬럼 자동 매핑 기반 구조 및 유사도 매칭

**오전 작업 (4시간)**:
- FuzzyWuzzy 라이브러리 설치 (python-Levenshtein은 선택적)
- utils/column_mapper.py 클래스 뼈대 작성
- 표준 컬럼 정의 (E-commerce, 리뷰, 판매 각각)
- 데이터 타입 자동 감지 함수 설계

**오후 작업 (4시간)**:
- 컬럼명 유사도 매칭 로직 구현
- 컬럼명 정규화 (소문자, 언더스코어 제거)
- FuzzyWuzzy로 유사도 계산
- 테스트 케이스 6개 작성 및 검증 (영어, 한글, 언더스코어, 리뷰, 누락, 판매)

**체크리스트**:
- [x] ColumnMapper 클래스 뼈대 완성
- [x] 유사도 매칭 함수 작동
- [x] 한글 컬럼명 테스트 통과
- [x] 테스트 케이스 6개 모두 통과

**산출물**:
- utils/column_mapper.py (290줄, 기본 매핑 구현)
- tests/test_column_mapper.py (231줄, 6개 테스트 케이스)
- requirements.txt (fuzzywuzzy 추가)

---

### DAY 25 (완료 ✅) - 컬럼 자동 매핑 (2/3)

**목표**: 데이터 샘플 분석 로직 구현

**작업 내용**:
- 컬럼 데이터 통계 분석 함수 (데이터 타입, 고유값 비율, 결측치 비율)
- 날짜 컬럼 자동 감지 (파싱 시도, 샘플 10개 중 70% 이상 날짜 형식)
- 숫자형 컬럼 범위 분석 (min, max, mean)
- 컬럼 타입 추론 로직 (ID는 고유값 90% 이상, 평점은 0-10 범위 등)
- 각 타입별 신뢰도 점수 계산 (0-100 점수)
- 테스트 케이스 5개 작성 및 검증 (ID, 날짜, 숫자, 평점, 텍스트)

**체크리스트**:
- [x] 데이터 샘플 분석 함수 완성 (analyze_column_data)
- [x] 컬럼 타입 추론 로직 작동 (infer_column_type)
- [x] ID, 날짜, 평점, 텍스트 각각 추론 테스트
- [x] 신뢰도 점수 검증 (5개 테스트 모두 통과)

**산출물**:
- utils/column_mapper.py (분석 로직 추가, 385줄 총 +95줄)
- tests/test_column_analysis.py (202줄, 5개 테스트 케이스)

---

### DAY 26 (완료 ✅) - 컬럼 자동 매핑 (3/3)

**목표**: 하이브리드 매핑 시스템 완성

**작업 내용**:
- 하이브리드 매핑 함수 구현 (컬럼명 유사도 60% + 데이터 추론 40%)
- 종합 점수 계산 로직
  - 각 표준 컬럼별로 모든 사용자 컬럼과 매칭
  - 컬럼명 점수 × 0.6 + 데이터 타입 점수 × 0.4
  - 임계값 50점 이상만 매핑
- 신뢰도 레벨 분류 (high ≥80, medium ≥65, low <65)
- 매핑 적용 함수 (DataFrame 컬럼명 자동 변경)
- 3가지 데이터 타입 테스트 (E-commerce, Review, Sales)

**체크리스트**:
- [x] 하이브리드 매핑 함수 완성
- [x] 종합 점수 계산 로직 구현
- [x] 신뢰도 레벨 분류 함수
- [x] 매핑 적용 함수 (apply_mapping)
- [x] 테스트 6개 모두 통과

**산출물**:
- utils/column_mapper.py (668줄, +168줄 추가)
- tests/test_hybrid_mapping.py (270줄, 6개 테스트)

**특이사항**:
- 하이브리드 매핑은 컬럼명만 사용하는 것보다 더 많은 컬럼 매핑 (테스트 3 검증)
- 애매한 컬럼명도 데이터 타입으로 구분 가능 (value1=날짜, value2=숫자)
- UI 통합은 DAY 27 이후 별도 진행 예정

---

### DAY 27 (완료 ✅) - 프로그레스 시스템 + GPT 최적화

**목표**: 단계별 프로그레스 표시 및 GPT Rate Limit 핸들링

**작업 내용**:
- utils/progress_tracker.py 구현 (230줄)
  - ProgressTracker 기본 클래스 (5단계 시스템)
  - RFMProgressTracker, TextProgressTracker 전문 클래스
  - 콜백 패턴으로 진행 상황 업데이트
  - 커스텀 단계 지원
  - start(), next_step(), complete(), error() 메서드
- modules/gpt_analyzer.py GPT 최적화 (수정)
  - Rate Limit 핸들링 (Exponential backoff with retry)
  - _call_with_retry() 메서드: 최대 5회 재시도, 1초 → 60초 지수 증가
  - 부정 리뷰 필터링 함수 _filter_negative_reviews() 추가
  - 비용 추적 (토큰, 금액 계산)
  - get_cost_info(), reset_cost_tracking() 메서드 추가
  - 배치 간 딜레이 (0.5초)
  - 모든 GPT 메서드에 retry 래퍼 적용 (8개 메서드)

**체크리스트**:
- [x] ProgressTracker 클래스 작동
- [x] 5단계 분석 프로그레스 로직
- [x] GPT 부정 리뷰 필터링 로직
- [x] Rate Limit 에러 처리 (Exponential backoff)
- [x] 비용 추적 기능
- [x] 테스트 작성 및 통과 (5개 테스트)

**산출물**:
- utils/progress_tracker.py (230줄, 3개 클래스)
- modules/gpt_analyzer.py (수정, +200줄)
- tests/test_day27_gpt_optimization.py (300줄, 5개 테스트)

**특이사항**:
- OpenAI API 키 없어도 테스트 통과 (SKIP 처리)
- 비용 추적은 gpt-4o-mini 가격 하드코딩 (추후 개선 필요)
- filter_negative 파라미터 구현했지만 미사용 (코드 리뷰에서 지적)

---

### DAY 28 (완료 ✅) - API 키 관리 + 통합 테스트

**목표**: API 키 관리 및 GPT 옵션 UI 통합

**작업 내용**:
- utils/api_key_manager.py 구현 (210줄)
  - `get_openai_api_key()`: Streamlit Secrets > 환경변수 > .env 순서로 로드
  - `mask_api_key()`: 보안을 위한 API 키 마스킹 (sk-proj-...xyz)
  - `validate_api_key()`: 형식 검증 (sk- 시작, 20자 이상)
  - `estimate_cost()`: 토큰 기반 비용 추정
  - `get_api_key_status()`: API 키 상태 확인 (available, source, valid)
- app.py: GPT 옵션 UI 추가
  - 리뷰 분석 페이지에 GPT 고급 분석 섹션 추가
  - API 키 자동 감지 및 상태 표시
  - GPT 사용 체크박스 + 예상 비용 표시
  - API 키 없을 때 설정 방법 안내 (Expander)
- run_review_analysis() GPT 통합
  - `use_gpt` 파라미터 추가
  - 부정 리뷰 필터링 + GPT 감성 분석
  - 비용 정보 표시 (토큰, 금액)
  - 6단계 프로그레스 바 (GPT 포함 시)

**체크리스트**:
- [x] API 키 자동 감지 작동 (3개 소스 지원)
- [x] GPT 옵션 체크박스 표시
- [x] 예상 비용 실시간 계산
- [x] Streamlit 앱 실행 테스트 성공

**산출물**:
- utils/api_key_manager.py (210줄, 신규)
- app.py (수정, +70줄)

**특이사항**:
- API 키 우선순위: Streamlit Secrets (배포) > 환경변수 > .env
- GPT 분석은 부정 리뷰만 필터링하여 비용 절감
- 예상 비용: 100개 리뷰 × 100 토큰 ≈ $0.0015 (gpt-4o-mini)

**Week 2 최종 산출물**:
- ✅ 컬럼 자동 매핑 시스템 (하이브리드)
- ✅ 프로그레스 추적 시스템 (5-6단계)
- ✅ GPT 최적화 (Rate Limit + 비용 추적)
- ✅ API 키 관리 (자동 감지 + 검증)

---

## Week 3: 판매 분석 + 배포 (DAY 29-33)

### DAY 29 (2025-02-06) - 판매 분석 (1/3)

**목표**: 판매 분석 엔진 구현

**오전 작업 (4시간)**:
- modules/sales_analyzer.py 재구현
- 기간별 집계 함수 (일별, 주별, 월별)
- 이동평균선 계산 (7일, 30일)
- 전월 대비 성장률 계산
- 상품별 매출 순위 TOP 20

**오후 작업 (4시간)**:
- 파레토 분석 함수 (누적 매출 비율)
- 거래 단위 데이터 전처리 (Quantity × UnitPrice → Sales)
- 일별/상품별 집계
- 테스트 데이터로 검증

**체크리스트**:
- [ ] SalesAnalyzer 클래스 완성
- [ ] 기간별 집계 작동
- [ ] 이동평균선 계산 정확
- [ ] 파레토 분석 결과 확인

**산출물**:
- modules/sales_analyzer.py (재구현, 400줄)

---

### DAY 30 (2025-02-07) - 판매 분석 (2/3)

**목표**: 판매 분석 시각화

**전일 작업 (8시간)**:
- modules/visualizer.py에 판매 차트 추가
- 매출 트렌드 라인 차트 (실제 매출 + 이동평균선)
- 상품 순위 막대 차트 (가로형, TOP 20)
- 파레토 차트 (듀얼 축: 매출 막대 + 누적 비율 선)
- 80% 기준선 표시
- 3개 차트 테스트

**체크리스트**:
- [ ] 매출 트렌드 차트 표시
- [ ] 상품 순위 차트 표시
- [ ] 파레토 차트 듀얼 축 작동
- [ ] 인터랙티브 기능 확인

**산출물**:
- modules/visualizer.py (판매 차트 추가, +300줄)

---

### DAY 31 (2025-02-08) - 판매 분석 (3/3) + 상세 탐색

**목표**: 판매 분석 페이지 완성 및 필터링 기능

**오전 작업 (4시간)**:
- 판매 분석 페이지 구현 (3개 탭: 트렌드, 상품, 인사이트)
- 기간 선택 라디오 버튼 (일별/주별/월별)
- 집계 및 차트 표시
- 성장률 테이블 표시
- 파레토 80% 달성 상품 개수 표시

**오후 작업 (4시간)**:
- 상세 탐색 페이지 필터링 기능 추가
- E-commerce: 군집 선택 멀티셀렉트
- 리뷰: 감성 필터 (긍정/중립/부정)
- 고객 ID 검색 기능 연결
- 필터링된 데이터 테이블 표시

**체크리스트**:
- [ ] 판매 분석 3개 탭 작동
- [ ] 기간 선택 기능
- [ ] 필터링 UI 작동
- [ ] 검색 기능 연결

**산출물**:
- 판매 분석 페이지 (+200줄)
- 상세 탐색 페이지 기본 구현 (+150줄)

---

### DAY 32 (2025-02-09) - Streamlit Cloud 배포

**목표**: 배포 준비 및 실제 배포

**오전 작업 (4시간)**:
- requirements.txt 최적화 (불필요한 패키지 제거, 버전 고정)
- .streamlit/config.toml 작성 (테마 설정, 업로드 제한)
- .streamlit/secrets.toml 로컬 테스트용 작성
- .gitignore 업데이트 (secrets.toml, .env 제외)
- 민감 정보 제거 확인

**오후 작업 (4시간)**:
- GitHub 저장소 최종 푸시
- Streamlit Cloud 가입 및 앱 생성
- GitHub 저장소 연결
- Secrets 설정 (OPENAI_API_KEY, deployed=true)
- 배포 실행
- 배포 후 전체 기능 테스트

**체크리스트**:
- [ ] requirements.txt 최적화 완료
- [ ] .streamlit/ 설정 파일 작성
- [ ] GitHub 푸시 성공
- [ ] Streamlit Cloud 배포 성공
- [ ] 배포 URL 접속 가능
- [ ] 샘플 데이터 로드 → 분석 성공
- [ ] 크롤링 버튼 비활성화 확인

**산출물**:
- requirements.txt (최적화)
- .streamlit/config.toml
- .streamlit/secrets.toml.example
- Streamlit Cloud 배포 URL

---

### DAY 33 (2025-02-10) - 문서화 + 최종 점검

**목표**: README 작성 및 프로젝트 완료

**오전 작업 (4시간)**:
- README.md 대폭 업데이트
- 프로젝트 소개 및 주요 기능
- 빠른 시작 가이드 (배포/로컬)
- 기술 스택 나열
- 프로젝트 구조 트리

**오후 작업 (4시간)**:
- 스크린샷 5-7장 제작 (홈, 업로드, RFM 분석, 감성 분석, 판매 트렌드, 리포트)
- screenshots/ 폴더에 저장
- 최종 점검 체크리스트 (기능, UI/UX, 보안, 문서)
- 모든 항목 테스트
- Git 최종 커밋
- 배포 URL 최종 확인

**체크리스트**:
- [ ] README 작성 완료
- [ ] 스크린샷 7장 제작
- [ ] 파일 업로드 → 분석 → 다운로드 전체 테스트
- [ ] 크롤링 (로컬) → 분석 테스트
- [ ] 샘플 데이터 (배포) → 분석 테스트
- [ ] API 키 노출 확인 (없어야 함)
- [ ] Git 최종 커밋: "docs: Finalize README and screenshots"

**산출물**:
- README.md (완성, 300줄)
- screenshots/ (7장)
- 프로젝트 완료

---

## 🎉 프로젝트 완료 체크리스트

### 핵심 기능
- [ ] 파일 업로드 (CSV/Excel)
- [ ] 샘플 데이터 로드 (배포)
- [ ] 웹 크롤링 (로컬)
- [ ] 컬럼 자동 매핑
- [ ] E-commerce RFM 분석
- [ ] 리뷰 감성 분석 (키워드 + GPT)
- [ ] 판매 시계열 분석
- [ ] 인터랙티브 차트 10+개
- [ ] CSV/HTML 리포트 다운로드

### UI/UX
- [ ] 멀티 페이지 4개 (시작하기, 자동 분석, 상세 탐색, 내보내기)
- [ ] 단계별 프로그레스 바
- [ ] 에러 메시지 명확
- [ ] 필터링 및 검색 기능
- [ ] 모바일 반응형

### 보안 및 법적
- [ ] 배포 버전 크롤링 비활성화
- [ ] API 키 Streamlit Secrets 관리
- [ ] .env 파일 Git 제외
- [ ] 면책 조항 표시
- [ ] 샘플 데이터 개인정보 없음

### 문서
- [ ] README.md (사용 가이드)
- [ ] SRS_최종확정본.md
- [ ] 현재진행상황.md
- [ ] PLAN.md
- [ ] 스크린샷 5-7장
- [ ] 코드 주석 충분

### 배포
- [ ] GitHub 저장소 공개
- [ ] Streamlit Cloud 배포 성공
- [ ] 배포 URL 접속 가능
- [ ] 전체 기능 작동

---

## 📊 최종 산출물

**코드**:
- app.py (멀티 페이지 라우팅)
- modules/ (8개 모듈: 분석 엔진)
- utils/ (4개 유틸리티: 세션, 매핑, 프로그레스, API)
- crawlers/ (하이브리드 크롤러)
- sample_data/ (4개 샘플 파일)

**문서**:
- README.md (사용 가이드)
- SRS_최종확정본.md (요구사항 명세)
- 현재진행상황.md (진행 추적)
- PLAN.md (개발 계획)

**배포**:
- Streamlit Cloud URL
- GitHub 저장소
- 스크린샷 5-7장

---

## 📅 일정 요약

| 주차 | 기간 | 주요 작업 | 목표 |
|------|------|----------|------|
| Week 1 | DAY 19-23 | UI 통합, 크롤링 하이브리드 | 멀티 페이지 완성 |
| Week 2 | DAY 24-28 | 자동 매핑, 프로그레스, GPT | 자동화 강화 |
| Week 3 | DAY 29-33 | 판매 분석, 배포, 문서화 | 프로젝트 완료 |

**총 개발 기간**: 15일
**데드라인까지**: 여유 5주
**예상 성공률**: 95%

---

## 📌 선택적 개선 (Phase 4)

프로젝트 완료 후 추가 가능:

### 우선순위 1 (UX 개선)
- **파일 업로드 시 자동 분석 타입 감지**
  - 현재: 샘플 데이터만 자동 감지 (파일명 기반)
  - 개선: 업로드 파일도 컬럼명 분석으로 자동 감지
  - 구현 방법:
    - `SessionManager.save_data()`에서 컬럼 분석
    - `CustomerID`, `InvoiceDate` 있으면 → `ecommerce`
    - `review`, `rating` 있으면 → `review`
    - `sales_date`, `product` 있으면 → `sales`
  - 예상 시간: 2시간
  - 파일: `app.py` (178-182줄), `utils/session_manager.py`

### 우선순위 2 (기능 추가)
- PDF 리포트 생성
- 판매 분석 Level 2 (계절성 분해)
- CLV 예측
- 추가 크롤링 소스
- 사용자 인증

---

## 🔥 Phase 4: SQL 역량 강화 (DAY 34-36) - 포트폴리오 차별화

**목표**: 데이터베이스 통합 및 SQL 쿼리 생성 기능 추가로 포트폴리오 경쟁력 향상

**추가 기간**: 3일 (약 18시간)
**완료 후 효과**: SQL 기본/중급/고급 역량 모두 증명 가능

---

### DAY 34 (Phase 4 시작) - SQLite 데이터베이스 통합 (1/3)

**목표**: 크롤링 데이터 → SQLite 저장 파이프라인 구축

**오전 작업 (4시간)**:
- modules/db_manager.py 신규 생성 (300줄)
  - DatabaseManager 클래스 설계
  - SQLite 연결 관리 (context manager 패턴)
  - 테이블 스키마 설계 및 생성
    - `reviews` 테이블 (review_id, source, place_id, rating, review_text, author, review_date, image_count)
    - `transactions` 테이블 (transaction_id, customer_id, invoice_date, quantity, unit_price, product)
    - `sales` 테이블 (sales_id, sales_date, product, category, quantity, price)
  - 인덱스 생성 (review_date, customer_id, sales_date 등)
  - 테이블 스키마 검증 함수

**오후 작업 (4시간)**:
- CRUD 함수 구현
  - `insert_reviews()` - 크롤링 데이터 삽입 (UPSERT 로직)
  - `insert_transactions()` - E-commerce 데이터 삽입
  - `insert_sales()` - 판매 데이터 삽입
  - `get_data()` - SELECT 쿼리 실행 및 DataFrame 반환
  - `delete_old_data()` - 특정 기간 이전 데이터 삭제
- 크롤러 수정
  - naver_place_crawler.py에 SQLite 저장 옵션 추가
  - CSV + SQLite 병행 저장 (--save-db 플래그)
- 테스트 작성 및 검증

**체크리스트**:
- [ ] DatabaseManager 클래스 완성
- [ ] 3개 테이블 스키마 생성 작동
- [ ] UPSERT 로직 테스트 (중복 데이터 처리)
- [ ] 인덱스 성능 확인 (EXPLAIN QUERY PLAN)
- [ ] 크롤러 → SQLite 저장 성공

**산출물**:
- modules/db_manager.py (300줄)
- data/reviews.db (SQLite 파일)
- tests/test_db_manager.py (150줄)

**포트폴리오 증명 가능한 SQL 역량**:
- ✅ CREATE TABLE (스키마 설계)
- ✅ PRIMARY KEY, AUTOINCREMENT
- ✅ CREATE INDEX (성능 최적화)
- ✅ INSERT OR REPLACE (UPSERT)
- ✅ 데이터 타입 선택 (TEXT, INTEGER, REAL, DATE, TIMESTAMP)

---

### DAY 35 - SQL 쿼리 생성기 구현 (2/3)

**목표**: 분석 로직을 SQL 쿼리로 자동 변환하는 생성기 구현

**오전 작업 (4시간)**:
- modules/sql_query_generator.py 신규 생성 (500줄)
  - SQLQueryGenerator 클래스 설계
  - `generate_rfm_query()` - RFM 분석 SQL 생성
    - CTE 3단계: (1) 고객별 RFM 계산, (2) NTILE 분위수, (3) 세그먼트 분류
    - Window Functions 활용 (NTILE, ROW_NUMBER)
    - CASE WHEN으로 비즈니스 로직 구현
    - 주석 자동 생성 (-- 단계 설명)
  - `generate_sales_trend_query()` - 매출 트렌드 SQL 생성
    - 일별/주별/월별 집계 (DATE, strftime)
    - 7일/30일 이동평균 (Window Functions: ROWS BETWEEN)
    - 전월 대비 성장률 (LAG, LEAD)
  - `generate_pareto_query()` - 파레토 분석 SQL 생성
    - 상품별 매출 합계
    - 누적 매출 계산 (SUM() OVER)
    - 상위 80% 매출 제품 필터링

**오후 작업 (4시간)**:
- `generate_sentiment_query()` - 감성 분석 SQL 생성
  - CASE WHEN으로 평점 기반 감성 분류
  - LIKE 연산자로 키워드 매칭
  - 감성별 집계 및 백분율 계산
- `generate_top_customers_query()` - 상위 고객 조회 SQL
  - ORDER BY, LIMIT
  - 매출 기여도 계산
- 쿼리 포맷팅 및 하이라이팅
  - SQL 예쁘게 정렬 (sqlparse 라이브러리)
  - 주석 자동 추가
- 테스트: 생성된 SQL을 실제 SQLite에서 실행하여 결과 검증

**체크리스트**:
- [ ] RFM SQL 쿼리 생성 작동
- [ ] 생성된 SQL이 실제 DB에서 실행 성공
- [ ] Window Functions 정확히 구현
- [ ] 매출 트렌드 SQL 작동
- [ ] 파레토 분석 SQL 작동
- [ ] 쿼리 주석 자동 생성

**산출물**:
- modules/sql_query_generator.py (500줄)
- tests/test_sql_generator.py (200줄)
- 예시 쿼리 파일 5개 (docs/sql_examples/*.sql)

**포트폴리오 증명 가능한 SQL 역량**:
- ✅ CTE (WITH 절) - 복잡한 쿼리 분해
- ✅ Window Functions (NTILE, ROW_NUMBER, RANK, LAG, LEAD)
- ✅ ROWS BETWEEN (이동평균)
- ✅ SUM() OVER (누적 합계)
- ✅ CASE WHEN (비즈니스 로직)
- ✅ GROUP BY, HAVING
- ✅ 서브쿼리 중첩
- ✅ JOIN (필요 시)
- ✅ 날짜 함수 (DATE, strftime, JULIANDAY)

---

### DAY 36 - Streamlit UI 통합 및 문서화 (3/3)

**목표**: SQL 쿼리 생성 기능을 UI에 통합하고 포트폴리오 문서 작성

**오전 작업 (4시간)**:
- app.py 수정: SQL 쿼리 보기 기능 추가
  - 각 분석 결과 페이지에 "📊 SQL 쿼리 보기" Expander 추가
  - RFM 분석 결과 → RFM SQL 쿼리 표시
  - 매출 분석 결과 → 매출 트렌드 SQL 쿼리 표시
  - 감성 분석 결과 → 감성 분류 SQL 쿼리 표시
  - st.code(sql_query, language='sql') 코드 하이라이팅
  - "📋 쿼리 복사" 버튼 추가 (클립보드 복사)
  - "▶️ 쿼리 실행" 버튼 추가 (SQLite에서 실행 후 결과 표시)
- 데이터 소스 토글 기능
  - "데이터 소스 선택" 라디오 버튼 (CSV vs SQLite)
  - SQLite 선택 시 → SQL 쿼리로 데이터 로드
  - CSV 선택 시 → 기존 pandas 방식

**오후 작업 (4시간)**:
- 문서화 및 포트폴리오 자료 작성
  - docs/SQL_CAPABILITIES.md 신규 작성
    - 프로젝트에서 사용한 SQL 기술 목록
    - 각 쿼리 예시 및 설명
    - 복잡한 쿼리 3개 강조 (RFM, 파레토, 이동평균)
  - README.md 업데이트
    - "SQL 데이터베이스 통합" 섹션 추가
    - SQLite 사용법 가이드
    - SQL 쿼리 생성 기능 소개
  - 스크린샷 3장 추가
    - SQL 쿼리 보기 화면
    - SQLite 테이블 스키마 (DB Browser)
    - 쿼리 실행 결과 화면
- 최종 통합 테스트
  - 크롤링 → SQLite 저장 → SQL 쿼리로 분석 → 시각화 전체 파이프라인
  - CSV 업로드 → SQLite 저장 → SQL 쿼리 생성 테스트
  - 배포 환경에서 SQLite 작동 확인

**체크리스트**:
- [ ] "SQL 쿼리 보기" 버튼 모든 분석 페이지에 추가
- [ ] 코드 하이라이팅 작동
- [ ] 쿼리 복사 버튼 작동
- [ ] 쿼리 실행 버튼 작동 (결과 표시)
- [ ] SQL_CAPABILITIES.md 작성 완료
- [ ] README.md 업데이트 완료
- [ ] 스크린샷 3장 추가
- [ ] 전체 파이프라인 테스트 성공

**산출물**:
- app.py (SQL UI 통합, +150줄)
- docs/SQL_CAPABILITIES.md (포트폴리오용 문서, 400줄)
- README.md (SQL 섹션 추가, +100줄)
- screenshots/sql_query_view.png (3장)

---

## 🎯 Phase 4 완료 후 포트폴리오 효과

### ✅ 면접 시 강조 가능한 포인트

1. **"저는 pandas뿐만 아니라 SQL로도 동일한 분석을 구현할 수 있습니다"**
   - RFM 분석을 SQL CTE + Window Functions로 구현
   - 이동평균, 파레토 분석 등 복잡한 비즈니스 로직을 SQL로 표현

2. **"ETL 파이프라인 경험이 있습니다"**
   - 크롤링 (Extract) → SQLite 저장 (Transform & Load) → 분석 (Query)
   - 실무에서 많이 사용하는 데이터 파이프라인 구조

3. **"성능 최적화를 고려합니다"**
   - 인덱스 설계 (review_date, customer_id)
   - EXPLAIN QUERY PLAN으로 쿼리 성능 분석
   - Window Functions 활용으로 서브쿼리 최소화

4. **"복잡한 SQL 쿼리를 작성할 수 있습니다"**
   - CTE 3단계 중첩
   - Window Functions (NTILE, ROW_NUMBER, LAG, SUM OVER)
   - 동적 날짜 처리 (JULIANDAY, strftime)

### 📊 증명 가능한 SQL 역량 전체 목록

#### 기본 SQL (DDL, DML)
- ✅ CREATE TABLE (스키마 설계)
- ✅ INSERT, UPDATE, DELETE
- ✅ INSERT OR REPLACE (UPSERT)
- ✅ CREATE INDEX
- ✅ PRIMARY KEY, FOREIGN KEY
- ✅ 데이터 타입 선택

#### 중급 SQL (집계, 조인)
- ✅ SELECT, WHERE, ORDER BY, LIMIT
- ✅ GROUP BY, HAVING
- ✅ COUNT, SUM, AVG, MAX, MIN
- ✅ DISTINCT
- ✅ LIKE, BETWEEN, IN
- ✅ 날짜 함수 (DATE, strftime, JULIANDAY)
- ✅ CASE WHEN (조건부 로직)

#### 고급 SQL (서브쿼리, CTE, Window Functions)
- ✅ CTE (WITH 절) - 복잡한 쿼리 분해
- ✅ 서브쿼리 (스칼라, 인라인 뷰)
- ✅ Window Functions:
  - ✅ NTILE (분위수)
  - ✅ ROW_NUMBER, RANK, DENSE_RANK
  - ✅ LAG, LEAD (이전/다음 행)
  - ✅ SUM() OVER (누적 합계)
  - ✅ AVG() OVER (이동평균)
  - ✅ ROWS BETWEEN (범위 지정)
- ✅ 복잡한 JOIN (필요 시)
- ✅ 쿼리 최적화 (EXPLAIN QUERY PLAN)

### 📈 예상 투자 시간 대비 효과

| 항목 | 투자 시간 | 포트폴리오 임팩트 |
|------|----------|------------------|
| SQLite 통합 | 8시간 | ⭐⭐⭐⭐ (기본 CRUD 증명) |
| SQL 쿼리 생성기 | 8시간 | ⭐⭐⭐⭐⭐ (고급 쿼리 증명) |
| UI 통합 + 문서화 | 8시간 | ⭐⭐⭐⭐⭐ (시각적 증명) |
| **총합** | **24시간 (3일)** | **⭐⭐⭐⭐⭐** |

**ROI 분석**: 3일 투자로 SQL 기본/중급/고급 역량 모두 증명 가능 → 백엔드/데이터 엔지니어 포지션 경쟁력 대폭 상승

---

## 📋 Phase 4 최종 체크리스트

### 기능 완성도
- [ ] SQLite 데이터베이스 3개 테이블 생성
- [ ] 크롤링 데이터 → SQLite 자동 저장
- [ ] RFM 분석 SQL 쿼리 생성 작동
- [ ] 매출 분석 SQL 쿼리 생성 작동
- [ ] 감성 분석 SQL 쿼리 생성 작동
- [ ] Streamlit UI에 "SQL 쿼리 보기" 버튼 추가
- [ ] 쿼리 복사/실행 기능 작동

### 문서화
- [ ] docs/SQL_CAPABILITIES.md 작성
- [ ] README.md SQL 섹션 추가
- [ ] 스크린샷 3장 추가
- [ ] 예시 SQL 쿼리 5개 저장

### 테스트
- [ ] 크롤링 → SQLite → SQL 분석 파이프라인 성공
- [ ] CSV 업로드 → SQLite 변환 성공
- [ ] 생성된 SQL 쿼리 실행 성공
- [ ] 배포 환경에서 SQLite 작동 확인

### 포트폴리오
- [ ] SQL 역량 증명 자료 준비 (쿼리 예시)
- [ ] 면접 시 설명 가능한 복잡한 쿼리 3개 선정
- [ ] GitHub README에 SQL 기능 강조
- [ ] 이력서에 "SQL 쿼리 생성 자동화" 추가 가능

---

**작성**: Claude (AI Assistant)
**실행**: 사용자
**목표 완료일**: 2025-02-10 (DAY 33) → 2025-02-13 (DAY 36, Phase 4 포함)
