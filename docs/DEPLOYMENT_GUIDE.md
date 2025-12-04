# 🚀 Streamlit Cloud 배포 가이드

Auto-Insight Platform을 Streamlit Cloud에 배포하는 완벽 가이드입니다.

## 📋 배포 전 체크리스트

배포하기 전에 다음 사항을 확인하세요:

- [x] 모든 기능이 로컬에서 정상 작동
- [x] `requirements.txt` 최적화 완료 (Selenium 제외)
- [x] `.streamlit/config.toml` 설정 완료
- [x] `utils/environment.py` 환경 감지 시스템 구현
- [x] SQLite 데이터베이스 샘플 데이터 생성 가능
- [x] `.gitignore`에 민감 정보 제외 설정

## 🔧 1단계: GitHub 저장소 준비

### 1.1 저장소 생성 (처음 배포하는 경우)

```bash
# GitHub에서 새 저장소 생성 후
git init
git add .
git commit -m "Initial commit: Auto-Insight Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/auto-insight-platform.git
git push -u origin main
```

### 1.2 코드 푸시 (저장소가 이미 있는 경우)

```bash
# 최신 변경사항 커밋
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 1.3 .gitignore 확인

다음 파일들이 제외되었는지 확인:

```
# .gitignore
.env
.streamlit/secrets.toml
data/analytics.db
*.pyc
__pycache__/
venv/
crawlers/output/
```

## ☁️ 2단계: Streamlit Cloud 배포

### 2.1 Streamlit Cloud 접속

1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 버튼 클릭

### 2.2 앱 설정

**Repository 설정:**
- Repository: `YOUR_USERNAME/auto-insight-platform`
- Branch: `main`
- Main file path: `app.py`

**Advanced settings (선택):**
- Python version: `3.10` (권장)
- App URL: `your-custom-name` (원하는 URL 지정)

### 2.3 Secrets 설정

배포 전에 **반드시** Secrets를 설정해야 합니다.

1. "Advanced settings" 클릭
2. "Secrets" 탭 선택
3. 다음 내용 입력:

```toml
# .streamlit/secrets.toml (Streamlit Cloud용)

# ========================================
# 배포 환경 설정
# ========================================
deployed = true  # 크롤링 비활성화

# ========================================
# API Keys
# ========================================
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"

# ========================================
# 데이터베이스 설정 (선택)
# ========================================
# SQLite는 기본적으로 data/analytics.db 사용
# Supabase 연동 시 아래 추가:
# SUPABASE_URL = "https://your-project.supabase.co"
# SUPABASE_KEY = "your-anon-key-here"

# ========================================
# 크롤링 설정 (로컬 전용)
# ========================================
# 배포 환경에서는 크롤링 자동 비활성화됨
```

**중요:** OpenAI API Key는 필수입니다!

### 2.4 배포 시작

1. "Deploy!" 버튼 클릭
2. 빌드 로그 확인 (5-10분 소요)
3. 배포 완료 시 자동으로 앱 실행

## 🔍 3단계: 배포 확인

### 3.1 환경 감지 테스트

앱이 실행되면 사이드바 하단에서 환경 정보 확인:

```
Environment: DEPLOYED
Crawling: Disabled
Database: SQLite (data/analytics.db)
```

**확인 사항:**
- Environment가 `DEPLOYED`인지
- Crawling이 `Disabled`인지
- 크롤링 관련 UI가 숨겨졌는지

### 3.2 기능별 테스트

#### ✅ 파일 업로드 테스트
1. "E-commerce Analysis" 페이지 접속
2. 샘플 CSV 파일 업로드
3. RFM 분석 실행 확인

#### ✅ SQL Analytics 테스트
1. "SQL Analytics" 페이지 접속
2. "샘플 데이터 생성" 버튼 클릭
3. 각 쿼리 실행 및 시각화 확인

#### ✅ 리포트 생성 테스트
1. 분석 완료 후 "HTML 리포트 다운로드" 클릭
2. 파일이 정상 다운로드되는지 확인

### 3.3 성능 확인

Streamlit Cloud 무료 티어 제한:
- **RAM**: 1GB
- **CPU**: 1 core
- **실행 시간**: 요청당 최대 10분

큰 데이터셋(10,000+ 행)은 처리 시간이 길어질 수 있습니다.

## 🐛 4단계: 문제 해결

### 문제 1: ModuleNotFoundError

**증상:**
```
ModuleNotFoundError: No module named 'XXX'
```

**해결:**
```bash
# requirements.txt에 패키지 추가
echo "missing-package==1.0.0" >> requirements.txt
git commit -am "Add missing dependency"
git push
```

Streamlit Cloud가 자동으로 재배포합니다.

### 문제 2: 크롤링 기능이 보임

**증상:** 배포 환경에서도 크롤링 UI가 표시됨

**해결:**
1. Streamlit Cloud Secrets에 `deployed = true` 확인
2. 앱 재시작: "Manage app" → "Reboot app"
3. 캐시 클리어: "Settings" → "Clear cache"

**디버깅:**
```python
# app.py에 임시 디버그 코드 추가
import streamlit as st
from utils.environment import Environment

st.write("DEBUG:", Environment.get_environment_info())
```

### 문제 3: OpenAI API 에러

**증상:**
```
AuthenticationError: Incorrect API key
```

**해결:**
1. Streamlit Cloud Secrets에서 `OPENAI_API_KEY` 확인
2. OpenAI 대시보드에서 API Key 유효성 확인
3. 앱 재시작

### 문제 4: 데이터베이스 초기화 실패

**증상:**
```
No such table: transactions
```

**해결:**
1. "SQL Analytics" 페이지에서 "샘플 데이터 생성" 클릭
2. 데이터베이스가 자동으로 초기화됨
3. 또는 로컬에서 생성한 `data/analytics.db`를 Git에 포함:

```bash
# .gitignore에서 제외
# data/analytics.db  # 주석 처리

# 로컬에서 샘플 데이터 생성
python utils/generate_sample_data.py

# Git에 추가
git add data/analytics.db
git commit -m "Add pre-populated database"
git push
```

### 문제 5: 메모리 부족 (MemoryError)

**증상:**
```
MemoryError: Unable to allocate array
```

**해결:**
1. 대용량 데이터 처리 시 청크 단위로 분할
2. 캐싱 최적화:

```python
# modules/data_loader.py
@st.cache_data(max_entries=3)  # 캐시 엔트리 제한
def load_data(file):
    # 대용량 파일은 샘플링
    df = pd.read_csv(file)
    if len(df) > 50000:
        return df.sample(50000)
    return df
```

3. 또는 Streamlit Cloud 유료 플랜 업그레이드 (4GB RAM)

### 문제 6: 느린 로딩 속도

**해결:**
1. 필요한 라이브러리만 import:

```python
# app.py 상단
import streamlit as st
# 페이지별로 lazy import
if page == "SQL Analytics":
    from modules.db_manager import DatabaseManager
```

2. 캐싱 적극 활용:

```python
@st.cache_resource
def get_db_connection():
    return DatabaseManager()
```

## 🔄 5단계: 업데이트 배포

코드 변경 후 배포 방법:

```bash
# 1. 변경사항 커밋
git add .
git commit -m "Update: Add new feature"

# 2. 푸시
git push origin main

# 3. Streamlit Cloud가 자동 재배포 (1-2분 소요)
```

**강제 재배포:**
1. Streamlit Cloud 대시보드 접속
2. "Manage app" 클릭
3. "Reboot app" 버튼 클릭

## 📊 6단계: 모니터링

### 6.1 로그 확인

Streamlit Cloud 대시보드에서:
- "Manage app" → "Logs" 탭
- 실시간 로그 스트림 확인
- 에러 발생 시 스택 트레이스 확인

### 6.2 사용량 모니터링

**무료 티어 제한:**
- 1개 프라이빗 앱
- 무제한 퍼블릭 앱
- Community 서버 (공유 리소스)

**유료 티어 (추후 고려):**
- Starter: $20/월 (4GB RAM, 2 cores)
- Team: $250/월 (8GB RAM, 4 cores)

## 🎯 7단계: 최적화 팁

### 7.1 성능 최적화

```python
# 1. Session State 활용
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# 2. 불필요한 재실행 방지
@st.cache_data(ttl=3600)  # 1시간 캐시
def expensive_computation(data):
    return analyze(data)

# 3. 프로그레스 바 표시
with st.spinner('분석 중...'):
    result = analyze_data(df)
```

### 7.2 사용자 경험 개선

```python
# 1. 에러 핸들링
try:
    result = analyze_data(df)
except Exception as e:
    st.error(f"분석 실패: {str(e)}")
    st.stop()

# 2. 도움말 추가
st.info("💡 팁: CSV 파일 업로드 시 인코딩은 UTF-8을 권장합니다.")

# 3. 로딩 상태 표시
if st.button("분석 시작"):
    with st.status("분석 진행 중...", expanded=True) as status:
        st.write("데이터 로드 중...")
        df = load_data()
        st.write("전처리 중...")
        df = preprocess(df)
        st.write("분석 중...")
        result = analyze(df)
        status.update(label="분석 완료!", state="complete")
```

### 7.3 보안 강화

```python
# 1. 파일 크기 제한
if uploaded_file.size > 100 * 1024 * 1024:  # 100MB
    st.error("파일 크기는 100MB 이하여야 합니다.")
    st.stop()

# 2. 파일 타입 검증
if not uploaded_file.name.endswith(('.csv', '.xlsx')):
    st.error("CSV 또는 Excel 파일만 업로드 가능합니다.")
    st.stop()

# 3. SQL Injection 방지 (이미 구현됨)
# modules/db_manager.py에서 parameterized queries 사용
```

## 🌐 8단계: 커스텀 도메인 (선택)

Streamlit Cloud 유료 플랜에서 지원:

1. 도메인 구매 (예: yourdomain.com)
2. DNS 설정:
   ```
   CNAME record: app.yourdomain.com → your-app.streamlit.app
   ```
3. Streamlit Cloud에서 커스텀 도메인 추가

## 📚 추가 리소스

- **Streamlit 공식 문서**: https://docs.streamlit.io/streamlit-cloud
- **배포 FAQ**: https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app
- **Community Forum**: https://discuss.streamlit.io

## ✅ 최종 체크리스트

배포 완료 후 확인:

- [ ] 앱이 정상적으로 로드됨
- [ ] Environment: DEPLOYED로 표시됨
- [ ] 크롤링 UI가 숨겨짐
- [ ] 파일 업로드가 작동함
- [ ] RFM 분석이 실행됨
- [ ] SQL Analytics가 작동함
- [ ] HTML 리포트 다운로드가 작동함
- [ ] 샘플 데이터 생성이 작동함
- [ ] 에러 로그가 없음

## 🎉 배포 완료!

축하합니다! Auto-Insight Platform이 성공적으로 배포되었습니다.

**다음 단계:**
1. 팀원/친구와 공유하여 피드백 받기
2. 포트폴리오에 프로젝트 URL 추가
3. LinkedIn/GitHub에 프로젝트 공유
4. 사용자 피드백 기반 기능 개선

**앱 URL 예시:**
- 기본: `https://your-app-name.streamlit.app`
- 커스텀: `https://app.yourdomain.com` (유료 플랜)

---

문제가 발생하면 [GitHub Issues](https://github.com/YOUR_USERNAME/auto-insight-platform/issues)에서 질문해주세요!
