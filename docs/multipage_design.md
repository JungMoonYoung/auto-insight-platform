# 멀티 페이지 구조 설계 문서

**작성일**: 2025-01-27
**작성자**: Claude AI Assistant
**목적**: 단일 파일 app.py를 4개 페이지로 분리하여 사용성 개선

---

## 📋 현재 구조 (Before)

**파일**: `app.py` (1553줄)
**구조**: 단일 파일, 조건부 렌더링

```
if analysis_type is None:
    # Step 1: 분석 타입 선택 UI
elif data is None:
    # Step 2: 데이터 업로드 UI
else:
    # Step 3: 데이터 검증 및 분석 결과
```

**문제점**:
- 파일 크기 과대 (1553줄)
- 상태 관리 복잡
- 코드 가독성 저하
- 유지보수 어려움

---

## 🎯 목표 구조 (After)

**파일**: `app.py` (메인 라우팅만, 200줄 예상)
**구조**: 4개 페이지 함수 분리

```
sidebar.radio() → 페이지 선택
│
├── 📄 page_start()        # 시작하기 (파일 업로드 & 크롤링)
├── 🔍 page_analysis()     # 자동 분석 (분석 실행 & 결과)
├── 🔎 page_explore()      # 상세 탐색 (필터링 & 검색)
└── 📥 page_export()       # 내보내기 (CSV, HTML 리포트)
```

---

## 📊 페이지 구조 상세 설계

### 페이지 1: 시작하기 (`page_start()`)

**목적**: 데이터 수집
**위치**: 최상단 (첫 화면)

**UI 구성**:
```
1. 헤더
   - 제목: "📂 데이터 준비"
   - 설명: "분석할 데이터를 업로드하거나 크롤링하세요"

2. 탭 구조
   ├── Tab 1: 파일 업로드
   │   - CSV/Excel 파일 업로더
   │   - 파일 미리보기 (10행)
   │   - 데이터 정보 (행/열 수, 결측치)
   │
   ├── Tab 2: 네이버 영화 리뷰 크롤링
   │   - 영화 ID 입력 필드
   │   - 수집 개수 슬라이더 (100~1000)
   │   - 크롤링 시작 버튼
   │   - 진행률 표시
   │
   └── Tab 3: 네이버 플레이스 리뷰 크롤링
       - 플레이스 ID 입력 필드
       - 수집 개수 슬라이더
       - 크롤링 시작 버튼
       - 진행률 표시

3. 하단 버튼
   - "다음 단계: 분석하기 →" (데이터 있을 때만 활성화)
```

**세션 상태 저장**:
- `st.session_state['data']`: 업로드/크롤링된 DataFrame
- `st.session_state['data_source']`: 'file' | 'crawling_movie' | 'crawling_place'
- `st.session_state['file_name']`: 파일명 (파일 업로드 시)

---

### 페이지 2: 자동 분석 (`page_analysis()`)

**목적**: 원클릭 자동 분석 실행 및 결과 표시
**전제조건**: 페이지 1에서 데이터 로드 완료

**UI 구성**:
```
1. 헤더
   - 제목: "🔍 자동 분석"
   - 데이터 요약 (행/열/소스)

2. 데이터 타입 자동 감지 (또는 수동 선택)
   - 라디오 버튼: E-commerce | 리뷰 분석 | 판매 분석
   - 자동 감지 결과 표시 (신뢰도 %)

3. 컬럼 매핑 (자동 → 수동 수정 가능)
   - 테이블 형식:
     | 필수 컬럼 | 감지된 컬럼 | 신뢰도 | 수정 |
     |-----------|-------------|--------|------|
     | CustomerID | customer_id | 95%    | 드롭다운 |
   - "매핑 확인" 버튼

4. 분석 실행
   - "✨ 분석 시작" 버튼 (Primary)
   - 5단계 프로그레스 바:
     ① 데이터 전처리 (20%)
     ② 분석 실행 (40-60%)
     ③ 시각화 생성 (80%)
     ④ 인사이트 생성 (90%)
     ⑤ 완료 (100%)

5. 결과 표시 (분석 완료 후)
   - 탭 구조:
     ├── 📊 주요 지표 (메트릭 카드 4-6개)
     ├── 📈 시각화 (차트 3-5개)
     ├── 💡 인사이트 (발견사항 + 액션 아이템)
     └── 🤖 AI 심층 분석 (GPT 4개 버튼)
```

**세션 상태 저장**:
- `st.session_state['analysis_type']`: 'ecommerce' | 'review' | 'sales'
- `st.session_state['column_mapping']`: Dict (표준 컬럼 → 실제 컬럼)
- `st.session_state['analysis_results']`: Dict (분석 결과 전체)
- `st.session_state['analysis_complete']`: Boolean

---

### 페이지 3: 상세 탐색 (`page_explore()`)

**목적**: 필터링, 검색, 세부 데이터 탐색
**전제조건**: 페이지 2에서 분석 완료

**UI 구성**:
```
1. 헤더
   - 제목: "🔎 상세 탐색"

2. 필터링 패널 (Sidebar 또는 Expander)
   E-commerce:
   - 군집 선택 (멀티셀렉트)
   - RFM 범위 슬라이더
   - 날짜 범위 선택

   리뷰 분석:
   - 감성 필터 (긍정/중립/부정)
   - 평점 범위
   - 키워드 검색

   판매 분석:
   - 카테고리 선택
   - 기간 선택
   - 매출 범위

3. 검색 기능
   - 고객 ID 검색 (E-commerce)
   - 상품명 검색 (판매)
   - 리뷰 텍스트 검색

4. 결과 테이블
   - 필터링된 데이터 표시
   - 정렬 가능
   - 페이지네이션 (100행씩)

5. 상세 차트 (선택적)
   - 필터링된 데이터 기준 차트 재생성
```

---

### 페이지 4: 내보내기 (`page_export()`)

**목적**: 분석 결과 다운로드 및 공유
**전제조건**: 페이지 2에서 분석 완료

**UI 구성**:
```
1. 헤더
   - 제목: "📥 결과 내보내기"

2. 내보내기 옵션
   ├── CSV 다운로드
   │   - 전처리된 데이터
   │   - 분석 결과 (RFM 점수, 감성 등)
   │   - 다운로드 버튼
   │
   ├── HTML 리포트
   │   - 체크박스: 포함할 섹션 선택
   │     □ 주요 지표
   │     □ 시각화 차트
   │     □ 인사이트
   │     □ AI 분석 (GPT)
   │   - "리포트 생성" 버튼
   │   - 생성된 리포트 미리보기
   │   - 다운로드 버튼
   │
   └── 공유 옵션 (추후 구현)
       - URL 생성
       - 이메일 전송
```

---

## 🔄 세션 상태 관리 설계

### 핵심 원칙
1. **데이터는 한 번만 저장** (중복 방지)
2. **페이지 간 데이터 공유** (session_state 활용)
3. **상태 초기화 기능** (새로 시작하기 버튼)

### 세션 상태 구조 (`utils/session_manager.py`)

```python
# 필수 상태
st.session_state['initialized']: Boolean  # 앱 초기화 여부
st.session_state['current_page']: str     # 현재 페이지명

# 데이터 관련
st.session_state['data']: pd.DataFrame    # 원본 데이터
st.session_state['data_source']: str      # 데이터 소스
st.session_state['file_name']: str        # 파일명

# 분석 관련
st.session_state['analysis_type']: str         # 분석 타입
st.session_state['column_mapping']: Dict       # 컬럼 매핑
st.session_state['analysis_complete']: Boolean # 분석 완료 여부
st.session_state['analysis_results']: Dict     # 분석 결과

# 분석 결과 상세 (타입별)
# E-commerce
st.session_state['rfm_df']: pd.DataFrame
st.session_state['cluster_summary']: pd.DataFrame
st.session_state['clustered_df']: pd.DataFrame

# 리뷰
st.session_state['review_analyzer']: TextAnalyzer
st.session_state['review_sentiment_summary']: Dict
st.session_state['review_keywords']: Dict
st.session_state['review_topics']: Dict

# 판매
st.session_state['sales_analyzer']: SalesAnalyzer
st.session_state['sales_trends']: pd.DataFrame
```

### 상태 관리 함수

```python
def init_session_state():
    """앱 시작 시 세션 초기화"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = 'start'
        st.session_state.data = None
        # ...

def clear_session_state():
    """모든 세션 상태 초기화 (새로 시작하기)"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def has_data() -> bool:
    """데이터 로드 여부 확인"""
    return st.session_state.get('data') is not None

def has_analysis() -> bool:
    """분석 완료 여부 확인"""
    return st.session_state.get('analysis_complete', False)
```

---

## 🚀 구현 순서 (DAY 20)

### 오전 작업 (4시간)
1. **utils/session_manager.py 작성** (1시간)
   - 세션 초기화 함수
   - 상태 저장/조회 헬퍼 함수
   - 상태 검증 함수

2. **페이지 1 구현** (3시간)
   - `page_start()` 함수 작성
   - 파일 업로드 탭
   - 데이터 미리보기
   - 크롤링 UI (기본 구조만, 실제 연결은 DAY 21-23)

### 오후 작업 (4시간)
3. **페이지 2-4 기본 구조** (2시간)
   - `page_analysis()` 빈 함수 (경고 메시지만)
   - `page_explore()` 빈 함수
   - `page_export()` 빈 함수

4. **app.py 메인 라우팅** (2시간)
   - sidebar.radio() 구현
   - 페이지 전환 로직
   - 세션 초기화
   - 각 페이지 함수 호출

---

## ✅ 성공 기준

**DAY 20 완료 시**:
- [ ] `utils/session_manager.py` 작성 완료
- [ ] sidebar에서 4개 페이지 전환 작동
- [ ] 페이지 1에서 파일 업로드 가능
- [ ] 업로드한 데이터가 session_state에 저장
- [ ] 페이지 2-4는 "준비 중" 메시지 표시
- [ ] "새로 시작하기" 버튼으로 상태 초기화

---

## 📌 추후 개선사항 (Phase 3)

- 페이지 간 애니메이션 효과
- 브레드크럼프 네비게이션
- 페이지 전환 시 확인 다이얼로그 (데이터 손실 방지)
- URL 파라미터로 페이지 상태 저장 (공유 가능)

---

**다음 문서**: `크롤링_하이브리드_설계.md` (DAY 21)
