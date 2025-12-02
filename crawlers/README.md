# 🕷️ 웹 크롤러 가이드

이 폴더에는 다양한 웹사이트에서 데이터를 수집하는 독립 크롤링 스크립트가 포함되어 있습니다.

## 📋 설치 방법

크롤러를 사용하기 전에 필요한 패키지를 설치하세요:

```bash
pip install -r requirements_crawler.txt
```

## 🎬 네이버 영화 리뷰 크롤러

### 사용법

```bash
python naver_movie_crawler.py --movie-id [영화ID] --count [리뷰개수] --headless
```

### 파라미터

- `--movie-id`: 네이버 영화 ID (필수)
  - 영화 페이지 URL에서 확인 가능
  - 예: `https://movie.naver.com/movie/bi/mi/basic.nhn?code=215095`
  - 이 경우 영화 ID는 `215095`

- `--count`: 수집할 리뷰 개수 (기본: 100)
- `--output`: 출력 CSV 파일명 (선택, 미지정 시 자동 생성)
- `--delay`: 요청 간 지연 시간 초 단위 (기본: 1.0)
- `--headless`: 브라우저를 보이지 않게 실행

### 예시

```bash
# 영화 ID 215095의 리뷰 500개 수집
python naver_movie_crawler.py --movie-id 215095 --count 500 --headless

# 특정 파일명으로 저장
python naver_movie_crawler.py --movie-id 215095 --count 1000 --output my_reviews.csv --headless
```

### 출력 데이터 형식

수집된 CSV 파일은 다음 컬럼을 포함합니다:

| 컬럼명 | 설명 |
|--------|------|
| movie_id | 영화 ID |
| author | 작성자 |
| score | 평점 (1-10) |
| review | 리뷰 텍스트 |
| date | 작성일 |
| likes | 공감 수 |
| crawled_at | 크롤링 시각 |

## 📚 네이버 웹툰 댓글 크롤러

*(구현 예정)*

```bash
python naver_webtoon_crawler.py --webtoon-id [웹툰ID] --count [댓글개수]
```

## 📖 교보문고 도서 리뷰 크롤러

*(구현 예정)*

```bash
python kyobo_book_crawler.py --book-id [도서ID] --count [리뷰개수]
```

## ⚖️ 크롤링 윤리 가이드라인

웹 크롤링 시 다음 사항을 준수하세요:

### ✅ 반드시 지켜야 할 사항

1. **robots.txt 준수**: 각 웹사이트의 크롤링 정책을 확인하세요
2. **요청 제한**: 서버에 부하를 주지 않도록 요청 간 지연을 두세요 (최소 1초)
3. **User-Agent 설정**: 크롤러임을 명시하는 User-Agent를 사용하세요
4. **개인정보 보호**: 수집한 데이터에서 개인정보(이메일, 전화번호 등)는 마스킹하세요
5. **이용약관 확인**: 각 사이트의 이용약관을 확인하고 위반하지 마세요

### ❌ 금지 사항

- 상업적 재배포 금지
- 대규모 자동 크롤링 금지
- 서버에 과도한 부하를 주는 행위
- 저작권이 있는 콘텐츠의 무단 복제

### 📜 법적 책임

- 이 크롤러는 **개인 연구 및 학습 목적**으로만 사용하세요
- 크롤링으로 인한 법적 문제는 사용자 본인의 책임입니다
- 각 웹사이트의 이용약관과 저작권법을 준수하세요

## 🔧 문제 해결

### Chrome Driver 오류

```bash
# Chrome Driver가 자동으로 설치되지 않는 경우
pip install --upgrade webdriver-manager
```

### 인코딩 오류

```bash
# Windows에서 한글이 깨지는 경우
# CSV 저장 시 encoding='utf-8-sig' 사용 (코드에 이미 적용됨)
```

### 요소를 찾을 수 없는 오류

- 웹사이트 구조가 변경되었을 수 있습니다
- 크롤러 코드의 CSS Selector를 업데이트해야 합니다

## 📁 출력 파일 위치

기본적으로 수집된 데이터는 `crawlers/output/` 폴더에 저장됩니다.

```
crawlers/
└── output/
    ├── naver_movie_215095_20241123_143022.csv
    ├── naver_webtoon_12345_20241123_150000.csv
    └── ...
```

## 🚀 메인 앱에서 사용하기

1. 크롤러를 실행하여 CSV 파일 생성
2. Streamlit 앱 실행: `streamlit run app.py`
3. "리뷰 분석" 선택
4. 생성된 CSV 파일 업로드
5. 자동 분석 실행!

## 💡 팁

- **대량 수집**: 1,000개 이상 수집 시 중간에 저장되도록 코드 수정 권장
- **에러 처리**: 네트워크 오류 발생 시 자동으로 재시도하도록 개선 가능
- **병렬 처리**: 여러 영화/웹툰을 동시에 크롤링하려면 멀티프로세싱 사용

## 📞 문의

크롤러 관련 문제가 있다면 이슈를 등록해주세요.
