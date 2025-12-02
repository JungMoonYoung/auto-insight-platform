# 🚀 빠른 시작 가이드 - Phase 2 완료!

Auto-Insight Platform - 리뷰 분석 기능 추가 완료! 🎉

## ⚡ 빠른 실행 (3단계)

### 1️⃣ 패키지 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# ⚠️ KoNLPy 사용 시 Java 필요
# Windows: https://www.java.com/ko/download/
# Mac: brew install openjdk  
# Linux: sudo apt-get install default-jdk
```

### 2️⃣ 앱 실행

```bash
streamlit run app.py
```

### 3️⃣ 바로 테스트!

#### ✅ 리뷰 분석 (Phase 2 완성!)
1. **"리뷰 분석"** 선택
2. `tests/sample_reviews.csv` 업로드
3. **"분석 시작하기"** 클릭
4. 🎉 완전 작동! 감성 분석, 키워드, 토픽 확인 가능

#### E-commerce 분석 (연결 필요)
1. **"E-commerce"** 선택
2. `tests/sample_data.csv` 업로드
3. 분석 모듈 연결 필요 (아래 참조)

## 📊 Phase 2 새로운 기능

### 리뷰 분석 기능
- ✅ **자동 텍스트 전처리** (KoNLPy 형태소 분석)
- ✅ **감성 분석** (긍정/부정/중립 자동 분류)
- ✅ **키워드 추출** (TF-IDF 기반)
- ✅ **토픽 모델링** (LDA 알고리즘)
- ✅ **인터랙티브 시각화**
  - 감성 분포 차트
  - 감성별 키워드 비교
  - 단어 빈도 차트
  - 토픽 시각화
- ✅ **자동 인사이트 생성**
  - 주요 발견사항
  - 개선 액션 아이템
- ✅ **CSV 내보내기**

## 🎨 화면 미리보기

앱을 실행하면 다음을 볼 수 있습니다:

1. **메인 화면**: 3가지 분석 타입 선택 카드
2. **파일 업로드**: 드래그 앤 드롭 또는 클릭
3. **데이터 검증**: 메트릭 카드로 데이터 개요 표시
4. **분석 결과**: 탭으로 구분된 시각화
   - 📊 감성 분석
   - 🔑 키워드
   - 📚 토픽
   - 📈 데이터
5. **인사이트**: 자동 생성된 발견사항 및 제안

## 🧪 테스트 방법

### 샘플 데이터로 빠른 테스트

```bash
# 1. 앱 실행
streamlit run app.py

# 2. 브라우저에서
#    - "리뷰 분석" 선택
#    - tests/sample_reviews.csv 업로드
#    - "분석 시작하기" 클릭

# 3. 결과 확인!
```

### 크롤링한 실제 데이터로 테스트

```bash
# 1. 크롤러로 리뷰 수집
cd crawlers
pip install -r requirements_crawler.txt
python naver_movie_crawler.py --movie-id 215095 --count 100 --headless

# 2. 크롤링된 CSV를 앱에 업로드
# crawlers/output/*.csv 파일 사용
```

## 📝 개발 현황

### ✅ Phase 1 - Core MVP
- ✅ Streamlit 앱 UI (모던 디자인)
- ✅ 파일 업로드 및 검증
- ✅ 데이터 전처리 모듈
- ✅ RFM 분석 모듈
- ✅ 시각화 모듈 (Plotly)
- ✅ 인사이트 생성 모듈
- ✅ HTML 리포트 생성 모듈

### ✅ Phase 2 - 리뷰 분석 (완료!)
- ✅ `text_analyzer.py` 완전 구현
- ✅ 시각화 함수 8개 추가
- ✅ 인사이트 생성 함수 추가
- ✅ `app.py` 연결 완료
- ✅ 샘플 데이터 생성
- ✅ 완전 작동 테스트 완료

### 📝 Phase 3 - 매출 분석 (예정)
- ⬜ 시계열 트렌드 분석
- ⬜ 상품별 ABC 분석
- ⬜ 계절성 감지

## 🔧 모듈 개별 테스트

```bash
# 리뷰 분석 모듈 테스트
python modules/text_analyzer.py

# RFM 분석 모듈 테스트
python modules/rfm_analyzer.py

# 전처리 모듈 테스트
python modules/preprocessor.py
```

## 🆘 문제 해결

### KoNLPy 설치 오류

```bash
# 1. Java 설치 확인
java -version

# 2. Java 없으면 설치
# Windows: https://www.java.com/ko/download/
# Mac: brew install openjdk
# Linux: sudo apt-get install default-jdk

# 3. KoNLPy 재설치
pip uninstall konlpy
pip install konlpy
```

### "Java 없음" 오류 발생 시

KoNLPy 없이도 기본 기능은 작동합니다!
- 형태소 분석 대신 단순 공백 분리 사용
- 정확도는 낮지만 테스트 가능

### Streamlit 포트 변경

```bash
streamlit run app.py --server.port 8502
```

## 📦 파일 구조

```
auto-insight-platform/
├── app.py                       # 메인 앱 (✅ Phase 2 연결)
├── requirements.txt             # 패키지 목록 (✅ Phase 2 추가)
│
├── modules/
│   ├── text_analyzer.py         # ✅ 리뷰 분석 (350줄)
│   ├── visualizer.py            # ✅ 시각화 +250줄
│   ├── insight_generator.py     # ✅ 인사이트 +150줄
│   ├── rfm_analyzer.py          # ✅ RFM 분석
│   ├── preprocessor.py          # ✅ 전처리
│   └── report_generator.py      # ✅ 리포트
│
├── tests/
│   ├── sample_data.csv          # E-commerce 샘플
│   └── sample_reviews.csv       # ✅ 리뷰 샘플 (새로 추가)
│
├── crawlers/
│   ├── naver_movie_crawler.py   # ✅ 영화 리뷰 크롤러
│   └── output/                  # 크롤링 결과
│
└── README.md
```

## 🎯 다음 할 일

### E-commerce 분석 연결

app.py에서 E-commerce 분석 부분 연결:

```python
# app.py 분석 시작 버튼 내부 (약 300번째 줄)
if st.session_state.analysis_type == "ecommerce":
    from modules.preprocessor import DataPreprocessor
    from modules.rfm_analyzer import RFMAnalyzer
    from modules.visualizer import Visualizer
    from modules.insight_generator import InsightGenerator
    
    # 전처리
    preprocessor = DataPreprocessor(df)
    processed_df, _ = (preprocessor
                      .normalize_column_names()
                      .handle_missing_values()
                      .remove_duplicates()
                      .convert_date_columns(['InvoiceDate'])
                      .get_processed_data())
    
    # RFM 분석
    analyzer = RFMAnalyzer(processed_df)
    rfm_df = analyzer.calculate_rfm()
    analyzer.find_optimal_clusters()
    clustered_df = analyzer.perform_clustering()
    cluster_summary = analyzer.get_cluster_summary()
    
    # 시각화
    visualizer = Visualizer()
    st.plotly_chart(visualizer.plot_rfm_3d_scatter(clustered_df))
    st.plotly_chart(visualizer.plot_cluster_bar_chart(cluster_summary))
    
    # 인사이트
    generator = InsightGenerator()
    insights = generator.generate_rfm_insights(rfm_df, cluster_summary)
    # ... 결과 표시
```

## 🎉 축하합니다!

Phase 2가 완료되어 **리뷰 분석 기능을 바로 사용**할 수 있습니다!

- 📝 텍스트 분석
- 😊 감성 분류
- 🔑 키워드 추출
- 📊 시각화
- 💡 인사이트

모두 작동합니다! 🚀

---

문의사항은 GitHub Issues에 등록해주세요.
Happy Analyzing! 📊✨
