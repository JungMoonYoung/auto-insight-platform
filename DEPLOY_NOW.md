# 🚀 지금 바로 배포하기 - Streamlit Cloud

**소요 시간:** 약 10분
**난이도:** ⭐ 쉬움

---

## 📋 배포 전 최종 체크리스트

### ✅ 준비된 항목들

- [x] GitHub 저장소: `https://github.com/JungMoonYoung/auto-insight-platform`
- [x] 최신 코드 푸시 완료 (커밋 d4058f1)
- [x] requirements.txt 최적화 완료
- [x] .streamlit/config.toml 설정 완료
- [x] .gitignore로 secrets.toml 보호됨
- [x] 민감 정보 제거 확인 완료

### 🔑 필요한 것

- [ ] GitHub 계정 (이미 있음)
- [ ] OpenAI API Key (GPT 인사이트용 - 선택사항)

---

## 🎯 STEP 1: Streamlit Cloud 가입/로그인

### 1-1. Streamlit Cloud 접속

브라우저에서 다음 URL로 이동:
```
https://share.streamlit.io
```

### 1-2. GitHub 계정으로 로그인

1. 우측 상단 **"Sign in"** 클릭
2. **"Continue with GitHub"** 선택
3. GitHub 계정으로 로그인
4. Streamlit의 GitHub 접근 권한 승인

---

## 🎯 STEP 2: 새 앱 생성

### 2-1. New app 버튼 클릭

대시보드에서 우측 상단의 **"New app"** 버튼 클릭

### 2-2. 배포 설정 입력

다음 정보를 정확히 입력:

| 항목 | 입력값 |
|------|--------|
| **Repository** | `JungMoonYoung/auto-insight-platform` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL (subdomain)** | 원하는 이름 입력 (예: `auto-insight-platform`) |

**예시:**
```
Repository: JungMoonYoung/auto-insight-platform
Branch: main
Main file path: app.py
App URL: https://auto-insight-platform.streamlit.app
```

### 2-3. Advanced Settings (선택사항)

**"Advanced settings"** 클릭 후:
- **Python version:** `3.9` (권장)
- 나머지는 기본값 유지

---

## 🎯 STEP 3: Secrets 설정 (중요!)

### 3-1. Deploy 전 Secrets 설정

**"Advanced settings"** 섹션에서 아래로 스크롤하여 **"Secrets"** 찾기

### 3-2. Secrets 내용 입력

다음 내용을 **그대로** 복사하여 붙여넣기:

```toml
# OpenAI API Key (GPT 인사이트 기능용)
OPENAI_API_KEY = "실제-API-키-입력"

# 배포 플래그 (크롤링 비활성화)
deployed = true
```

**⚠️ 중요:**
- `OPENAI_API_KEY`에 실제 OpenAI API 키를 입력하세요
- API 키가 없다면 임시로 `"sk-dummy-key-for-testing"` 입력 가능
  (GPT 인사이트 기능만 작동 안 함, 나머지는 정상 작동)

### 3-3. OpenAI API Key 발급 방법 (선택사항)

1. https://platform.openai.com/api-keys 접속
2. **"Create new secret key"** 클릭
3. 이름 입력 (예: "auto-insight-platform")
4. 키 복사 (예: `sk-proj-...`)
5. Streamlit Secrets에 붙여넣기

---

## 🎯 STEP 4: 배포 실행!

### 4-1. Deploy 버튼 클릭

모든 설정을 확인한 후 **"Deploy!"** 버튼 클릭

### 4-2. 배포 로그 모니터링

배포가 시작되면 **실시간 로그**가 표시됩니다:

```
[1/4] 📦 Installing dependencies from requirements.txt
      ✓ streamlit
      ✓ pandas
      ✓ numpy
      ...

[2/4] 🔨 Building Python environment

[3/4] 📥 Installing system packages

[4/4] 🚀 Starting Streamlit app
```

**예상 소요 시간:** 5-10분

### 4-3. 완료 확인

로그 마지막에 다음 메시지가 표시되면 성공:

```
🎉 Your app is live!
🌐 https://your-app-name.streamlit.app
```

---

## 🎯 STEP 5: 배포 후 검증

### 5-1. 앱 URL 접속

배포가 완료되면 자동으로 앱이 열립니다.
또는 직접 URL 접속:
```
https://your-app-name.streamlit.app
```

### 5-2. 기능 테스트

다음 기능들이 정상 작동하는지 확인:

#### ✅ 기본 기능
- [ ] 앱이 정상적으로 로드됨
- [ ] 다크 테마가 적용됨
- [ ] 사이드바가 표시됨

#### ✅ 데이터 업로드
- [ ] "데이터 업로드" 탭 클릭
- [ ] CSV 파일 업로드 버튼 표시
- [ ] 샘플 데이터 다운로드 버튼 작동

#### ✅ RFM 분석
1. 샘플 데이터 다운로드
2. 다운로드한 파일 업로드
3. "RFM 분석" 메뉴 선택
4. 컬럼 자동 매핑 확인
5. "분석 시작" 클릭
6. 결과 확인:
   - [ ] 3D 산점도 표시됨
   - [ ] 고객 세그먼트 테이블 표시됨
   - [ ] 다운로드 버튼 작동함

#### ✅ 판매 분석
- [ ] "판매 분석" 메뉴 선택
- [ ] 기간 선택 (일별/주별/월별) 작동
- [ ] 트렌드 차트 표시됨
- [ ] 상품 순위 차트 표시됨
- [ ] 파레토 차트 표시됨

#### ⚠️ 비활성화된 기능
- [ ] 크롤링 버튼이 **보이지 않음** (정상)
  - `deployed=true`일 때 자동 숨김

---

## 🎯 STEP 6: 문제 해결

### 문제 1: 앱이 시작되지 않음

**증상:**
```
ModuleNotFoundError: No module named 'xxx'
```

**해결:**
1. Streamlit Cloud 대시보드로 이동
2. 앱 선택 → **"Reboot app"** 클릭
3. 로그 확인

### 문제 2: KoNLPy 설치 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement konlpy
```

**해결:**
- 정상입니다! KoNLPy는 조건부 설치로 설정됨
- Linux(Streamlit Cloud)에서는 설치 생략됨
- 텍스트 분석은 fallback 로직으로 작동

### 문제 3: Secrets 로드 실패

**증상:**
```
KeyError: 'OPENAI_API_KEY'
```

**해결:**
1. 앱 Settings → **"Secrets"** 클릭
2. 내용 확인:
   ```toml
   OPENAI_API_KEY = "sk-..."
   deployed = true
   ```
3. **"Save"** 클릭
4. 앱이 자동으로 재시작됨

---

## 🎉 배포 완료!

### 배포 후 할 일

1. **URL 공유**
   ```
   https://your-app-name.streamlit.app
   ```

2. **README.md에 배포 URL 추가**
   ```markdown
   ## 🌐 Live Demo

   Try it now: https://your-app-name.streamlit.app
   ```

3. **GitHub README 배지 추가 (선택사항)**
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
   ```

---

## 📊 배포 후 관리

### 앱 업데이트 방법

GitHub에 푸시하면 **자동으로 재배포**됩니다:

```bash
# 코드 수정 후
git add .
git commit -m "Update feature"
git push origin main

# 2-3분 후 자동으로 앱이 업데이트됨
```

### 앱 설정 변경

Streamlit Cloud 대시보드에서:
- **Settings → General:** 앱 이름, URL 변경
- **Settings → Secrets:** API 키 업데이트
- **Settings → Advanced:** Python 버전, 리소스 설정

### 로그 확인

- **Dashboard → 앱 선택 → "Logs"** 탭
- 실시간 에러 및 경고 확인

---

## 🔗 유용한 링크

| 항목 | URL |
|------|-----|
| **Streamlit Cloud Dashboard** | https://share.streamlit.io |
| **배포된 앱** | https://your-app-name.streamlit.app |
| **GitHub 저장소** | https://github.com/JungMoonYoung/auto-insight-platform |
| **Streamlit 문서** | https://docs.streamlit.io |
| **OpenAI API Keys** | https://platform.openai.com/api-keys |

---

## 📞 도움이 필요하신가요?

- **Streamlit 커뮤니티:** https://discuss.streamlit.io
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues
- **문서:** `DEPLOYMENT.md` 참조

---

**🎊 축하합니다! 배포가 완료되었습니다!**

이제 전 세계 누구나 당신의 Auto-Insight Platform을 사용할 수 있습니다!

---

**작성일:** 2025-02-09 (DAY 32)
**문서 버전:** 1.0
