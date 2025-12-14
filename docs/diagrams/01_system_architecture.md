# System Architecture Diagram

```mermaid
graph TB
    subgraph User["사용자 인터페이스"]
        UI[Streamlit Web App]
        style UI fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph DataInput["데이터 입력 계층"]
        Upload[파일 업로드<br/>CSV/Excel]
        Crawler[웹 크롤러<br/>Selenium]
        style Upload fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Crawler fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph Processing["데이터 처리 계층"]
        Loader[Data Loader]
        Preprocessor[Preprocessor]
        style Loader fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Preprocessor fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph Analysis["분석 엔진"]
        RFM[RFM Analyzer]
        Text[Text Analyzer]
        Sales[Sales Analyzer]
        style RFM fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Text fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Sales fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph Output["출력 계층"]
        Viz[Visualizer<br/>Plotly]
        Insight[Insight Generator]
        Report[Report Generator]
        style Viz fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Insight fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Report fill:#4A6DDF,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph Storage["저장소"]
        DB[(SQLite Database)]
        style DB fill:#5AB7A0,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    subgraph External["외부 서비스"]
        GPT[OpenAI GPT API]
        Cloud[Streamlit Cloud]
        style GPT fill:#FF9BC6,stroke:#9CA3AF,stroke-width:2px,color:#fff
        style Cloud fill:#FF9BC6,stroke:#9CA3AF,stroke-width:2px,color:#fff
    end

    UI -->|파일| Upload
    UI -->|크롤링 요청| Crawler
    Upload --> Loader
    Crawler --> Loader
    Crawler -->|저장| DB

    Loader --> Preprocessor
    Preprocessor --> RFM
    Preprocessor --> Text
    Preprocessor --> Sales

    RFM --> Viz
    Text --> Viz
    Sales --> Viz
    Text -->|부정 리뷰| GPT
    GPT --> Insight

    Viz --> UI
    Insight --> UI
    Viz --> Report
    Insight --> Report
    Report -->|HTML/CSV| UI

    RFM -.->|조회| DB
    Text -.->|조회| DB
    Sales -.->|조회| DB
    UI -.->|배포| Cloud
```

## 주요 구성 요소

### 사용자 인터페이스
- **Streamlit Web App**: 멀티페이지 구조의 대화형 웹 인터페이스

### 데이터 입력 계층
- **파일 업로드**: CSV/Excel 파일 지원 (최대 100MB)
- **웹 크롤러**: Selenium 기반 네이버 크롤링 (로컬 환경)

### 데이터 처리 계층
- **Data Loader**: 파일 인코딩 감지 및 데이터 로딩
- **Preprocessor**: 결측치, 이상치, 파생변수 처리

### 분석 엔진
- **RFM Analyzer**: K-Means 군집화 기반 고객 세분화
- **Text Analyzer**: 키워드 추출, 감성 분석, 토픽 모델링
- **Sales Analyzer**: 시계열 분석, 상품 순위, 파레토 분석

### 출력 계층
- **Visualizer**: Plotly 인터랙티브 차트 생성
- **Insight Generator**: 핵심 발견사항 및 액션 아이템 생성
- **Report Generator**: HTML/CSV 리포트 다운로드

### 저장소
- **SQLite Database**: 크롤링 데이터 및 분석 결과 저장

### 외부 서비스
- **OpenAI GPT API**: 부정 리뷰 심층 분석
- **Streamlit Cloud**: 무료 호스팅 플랫폼
