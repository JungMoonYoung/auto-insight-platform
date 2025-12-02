"""
Auto-Insight Platform - Multi-Page Version
AI 기반 자동 데이터 분석 및 리포트 생성 시스템

DAY 20: 멀티 페이지 구조로 전환 (4개 페이지)
"""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import os
from dotenv import load_dotenv

# 유틸리티 모듈
from utils.session_manager import SessionManager
from utils.environment import Environment

# 모듈
from modules.data_loader import DataLoader
from modules.preprocessor import DataPreprocessor
from modules.rfm_analyzer import RFMAnalyzer
from modules.text_analyzer import TextAnalyzer
from modules.visualizer import Visualizer
from modules.report_generator import HTMLReportGenerator
from modules.insight_generator import InsightGenerator

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Auto-Insight Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS 스타일 ====================
def load_custom_css():
    """커스텀 CSS 로드"""
    st.markdown("""
    <style>
        /* 메인 배경 - 다크 */
        .main {
            background: #0a0e27;
            background-image:
                radial-gradient(at 47% 33%, hsl(240, 70%, 15%) 0, transparent 59%),
                radial-gradient(at 82% 65%, hsl(260, 50%, 20%) 0, transparent 55%);
            background-attachment: fixed;
        }

        /* 컨텐츠 영역 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            background: rgba(20, 25, 45, 0.95);
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            margin: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* 제목 스타일 */
        h1 {
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3em !important;
            text-align: center;
            margin-bottom: 1rem;
        }

        h2 {
            color: #00f2fe;
            font-weight: 700;
            border-left: 5px solid #00f2fe;
            padding-left: 15px;
            margin-top: 2rem;
        }

        /* 텍스트 색상 */
        p, label, .stMarkdown {
            color: rgba(255, 255, 255, 0.9) !important;
        }

        /* 버튼 스타일 */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }

        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


# ==================== 페이지 함수들 ====================

def page_start():
    """페이지 1: 시작하기 (데이터 업로드 & 크롤링)"""
    st.title("🏠 시작하기")
    st.markdown("### 분석할 데이터를 준비하세요")

    # 탭 생성
    tabs = st.tabs(["📁 파일 업로드", "🌐 웹 크롤링", "📦 샘플 데이터"])

    # Tab 1: 파일 업로드
    with tabs[0]:
        render_file_upload()

    # Tab 2: 웹 크롤링
    with tabs[1]:
        render_crawling_ui()

    # Tab 3: 샘플 데이터
    with tabs[2]:
        render_sample_data()

    # 하단: 데이터 정보 표시
    if SessionManager.has_data():
        st.markdown("---")
        show_data_info()


def render_file_upload():
    """파일 업로드 UI"""
    st.markdown("#### 📁 CSV 또는 Excel 파일 업로드")

    uploaded_file = st.file_uploader(
        "파일 선택",
        type=['csv', 'xlsx', 'xls'],
        key="file_uploader"
    )

    if uploaded_file is not None:
        try:
            with st.spinner("📂 파일을 읽는 중..."):
                # 파일 로드 (Streamlit UploadedFile 객체는 pandas로 직접 읽기)
                if uploaded_file.name.endswith('.csv'):
                    # CSV 파일: 인코딩 자동 감지
                    try:
                        df = pd.read_csv(uploaded_file, encoding='utf-8')
                    except UnicodeDecodeError:
                        uploaded_file.seek(0)  # 파일 포인터 리셋
                        df = pd.read_csv(uploaded_file, encoding='cp949')
                else:
                    # Excel 파일
                    df = pd.read_excel(uploaded_file)

                # 세션에 저장
                SessionManager.save_data(
                    data=df,
                    source='upload',
                    file_name=uploaded_file.name
                )

                st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")

                # 미리보기
                st.markdown("##### 📋 데이터 미리보기 (상위 5행)")
                st.dataframe(df.head(), use_container_width=True)

                # 데이터 품질 리포트
                with st.expander("📊 데이터 품질 리포트"):
                    quality_report = DataLoader.get_data_quality_report(df)

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("총 행 수", f"{quality_report['total_rows']:,}")
                    col2.metric("총 컬럼 수", f"{quality_report['total_columns']:,}")
                    col3.metric("결측치", f"{quality_report['total_missing']:,}")
                    col4.metric("중복 행", f"{quality_report['duplicate_rows']:,}")

                    st.markdown("**컬럼별 정보**")
                    st.dataframe(quality_report['column_info'], use_container_width=True)

                st.info("💡 '자동 분석' 페이지로 이동하여 분석을 시작하세요!")

        except Exception as e:
            st.error(f"❌ 파일 로드 실패: {str(e)}")
    else:
        st.info("📤 CSV 또는 Excel 파일을 업로드하세요")


def render_crawling_ui():
    """크롤링 UI (환경별 분기)"""
    st.markdown("#### 🌐 웹 크롤링")

    if Environment.is_local():
        # 로컬 환경: 실제 크롤링
        st.info("💻 로컬 환경: 실제 크롤링 기능 사용 가능")

        # 크롤링 소스 선택
        crawl_source = st.selectbox(
            "크롤링 소스 선택",
            ["네이버 영화 리뷰", "네이버 플레이스 리뷰"],
            key="crawl_source"
        )

        if crawl_source == "네이버 영화 리뷰":
            render_movie_crawling()
        else:
            render_place_crawling()

    else:
        # 배포 환경: 크롤링 비활성화
        st.warning("☁️ 배포 환경: 크롤링 기능이 비활성화되었습니다.")
        st.info("💡 '샘플 데이터' 탭에서 미리 수집된 데이터를 사용하세요.")


def render_movie_crawling():
    """네이버 영화 크롤링 UI"""
    st.markdown("##### 🎬 네이버 영화 리뷰 크롤링")

    col1, col2 = st.columns([3, 1])

    with col1:
        movie_url = st.text_input(
            "영화 URL 또는 ID",
            placeholder="https://movie.naver.com/movie/bi/mi/basic.nhn?code=215095",
            key="movie_url"
        )

    with col2:
        max_reviews = st.number_input(
            "수집할 리뷰 수",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            key="max_reviews_movie"
        )

    if st.button("🚀 크롤링 시작", key="start_movie_crawl", use_container_width=True):
        if not movie_url:
            st.error("❌ URL 또는 영화 ID를 입력하세요")
            return

        try:
            # URL에서 영화 ID 추출
            import re

            if 'code=' in movie_url:
                match = re.search(r'code=(\d+)', movie_url)
                movie_id = match.group(1) if match else None
            elif movie_url.isdigit():
                movie_id = movie_url
            else:
                st.error("❌ 올바른 URL 또는 영화 ID를 입력하세요")
                return

            if not movie_id:
                st.error("❌ URL에서 영화 ID를 찾을 수 없습니다")
                return

            st.info(f"🎬 영화 ID: {movie_id}")

            with st.spinner(f"🤖 네이버 영화에서 {max_reviews}개 리뷰를 크롤링하는 중..."):
                # 버그 #36 수정: 크롤러 import 실패 처리
                try:
                    import sys
                    crawler_path = Path(__file__).parent / 'crawlers'
                    if str(crawler_path) not in sys.path:
                        sys.path.insert(0, str(crawler_path))

                    from naver_movie_crawler import NaverMovieCrawler
                except ImportError as e:
                    st.error(f"❌ 크롤러 모듈을 찾을 수 없습니다: {str(e)}")
                    st.info("💡 crawlers/ 폴더와 naver_movie_crawler.py 파일을 확인하세요.")
                    st.info("💡 또는 `pip install selenium webdriver-manager` 명령으로 의존성을 설치하세요.")
                    return
                except Exception as e:
                    st.error(f"❌ 크롤러 로드 중 오류 발생: {str(e)}")
                    return

                # 크롤링 실행
                crawler = NaverMovieCrawler(headless=True, delay=0.5)

                try:
                    df = crawler.crawl_reviews(movie_id, max_reviews=max_reviews)

                    if df is not None and len(df) > 0:
                        # 컬럼명 매핑
                        df_mapped = df.rename(columns={
                            'review': 'text',
                            'score': 'rating'
                        })

                        # 세션에 저장
                        SessionManager.save_data(
                            data=df_mapped,
                            data_type='review',
                            source='crawl_movie',
                            file_name=f'movie_{movie_id}_reviews.csv'
                        )

                        st.success(f"✅ 크롤링 완료! {len(df)}개 리뷰 수집")
                        st.balloons()
                        # 버그 #35 수정: 세션 상태 저장 완료 대기
                        import time
                        time.sleep(0.1)
                        st.rerun()
                    else:
                        st.error("❌ 리뷰를 수집하지 못했습니다")

                finally:
                    crawler.close()

        except Exception as e:
            st.error(f"❌ 크롤링 오류: {str(e)}")
            st.exception(e)


def render_place_crawling():
    """네이버 플레이스 크롤링 UI"""
    st.markdown("##### 🏪 네이버 플레이스 리뷰 크롤링")

    col1, col2 = st.columns([3, 1])

    with col1:
        place_url = st.text_input(
            "플레이스 URL 또는 ID",
            placeholder="https://m.place.naver.com/restaurant/1234567890/review",
            key="place_url"
        )

    with col2:
        max_reviews = st.number_input(
            "수집할 리뷰 수",
            min_value=10,
            max_value=500,
            value=100,
            step=10,
            key="max_reviews_place"
        )

    if st.button("🚀 크롤링 시작", key="start_place_crawl", use_container_width=True):
        if not place_url:
            st.error("❌ URL 또는 플레이스 ID를 입력하세요")
            return

        try:
            # URL에서 플레이스 ID 추출
            import re

            patterns = [
                r'place\.naver\.com/[^/]+/(\d+)',
                r'pcmap\.place\.naver\.com/[^/]+/(\d+)',
                r'map\.naver\.com/[^/]+/place/(\d+)',
                r'/place/(\d+)',
                r'(\d{10,})',
            ]

            place_id = None
            for pattern in patterns:
                match = re.search(pattern, place_url)
                if match:
                    place_id = match.group(1)
                    break

            if not place_id and place_url.isdigit():
                place_id = place_url

            if not place_id:
                st.error("❌ 올바른 URL 또는 플레이스 ID를 입력하세요")
                return

            st.info(f"🏪 플레이스 ID: {place_id}")

            with st.spinner(f"🤖 네이버 플레이스에서 {max_reviews}개 리뷰를 크롤링하는 중..."):
                # 버그 #36 수정: 크롤러 import 실패 처리
                try:
                    import sys
                    crawler_path = Path(__file__).parent / 'crawlers'
                    if str(crawler_path) not in sys.path:
                        sys.path.insert(0, str(crawler_path))

                    from naver_place_crawler import NaverPlaceCrawler
                except ImportError as e:
                    st.error(f"❌ 크롤러 모듈을 찾을 수 없습니다: {str(e)}")
                    st.info("💡 crawlers/ 폴더와 naver_place_crawler.py 파일을 확인하세요.")
                    st.info("💡 또는 `pip install selenium webdriver-manager` 명령으로 의존성을 설치하세요.")
                    return
                except Exception as e:
                    st.error(f"❌ 크롤러 로드 중 오류 발생: {str(e)}")
                    return

                # 크롤링 실행
                crawler = NaverPlaceCrawler(headless=True, delay=0.5)

                try:
                    df = crawler.crawl_reviews(place_id, max_reviews=max_reviews)

                    if df is not None and len(df) > 0:
                        # 컬럼명 매핑
                        df_mapped = df.rename(columns={
                            'review': 'text',
                            'rating': 'rating'
                        })

                        # 세션에 저장
                        SessionManager.save_data(
                            data=df_mapped,
                            data_type='review',
                            source='crawl_place',
                            file_name=f'place_{place_id}_reviews.csv'
                        )

                        st.success(f"✅ 크롤링 완료! {len(df)}개 리뷰 수집")
                        st.balloons()
                        # 버그 #35 수정: 세션 상태 저장 완료 대기
                        import time
                        time.sleep(0.1)
                        st.rerun()
                    else:
                        st.error("❌ 리뷰를 수집하지 못했습니다")

                finally:
                    crawler.close()

        except Exception as e:
            st.error(f"❌ 크롤링 오류: {str(e)}")
            st.exception(e)


def render_sample_data():
    """샘플 데이터 로드 UI"""
    st.markdown("#### 📦 샘플 데이터")

    if Environment.is_deployed():
        st.info("☁️ 배포 환경: 샘플 데이터를 사용하여 플랫폼을 체험하세요")

    # 샘플 데이터 목록
    sample_files = Environment.list_sample_data()

    if not sample_files:
        st.warning("⚠️ 샘플 데이터가 없습니다. sample_data/ 폴더를 확인하세요.")
        return

    # 샘플 데이터 설명
    sample_descriptions = {
        'ecommerce_sample.csv': '🛒 E-commerce 거래 데이터 (RFM 분석용)',
        'naver_movie_reviews.csv': '🎬 네이버 영화 리뷰 데이터',
        'naver_place_reviews.csv': '📍 네이버 플레이스 리뷰 데이터',
        'sales_sample.csv': '📊 판매 데이터 (시계열 분석용)'
    }

    # 선택 UI
    selected_file = st.selectbox(
        "샘플 데이터 선택",
        sample_files,
        format_func=lambda x: sample_descriptions.get(x, x),
        key="sample_file"
    )

    if st.button("📂 샘플 데이터 로드", key="load_sample"):
        try:
            with st.spinner(f"📂 {selected_file} 로드 중..."):
                sample_path = os.path.join(Environment.get_sample_data_path(), selected_file)

                # DataLoader.load_file()을 사용하여 CSV/Excel 자동 처리
                df = DataLoader.load_file(sample_path)

                # 데이터 타입 자동 감지
                if 'ecommerce' in selected_file:
                    data_type = 'ecommerce'
                elif 'movie' in selected_file or 'place' in selected_file:
                    data_type = 'review'
                elif 'sales' in selected_file:
                    data_type = 'sales'
                else:
                    data_type = None

                # 세션에 저장
                SessionManager.save_data(
                    data=df,
                    data_type=data_type,
                    source='sample',
                    file_name=selected_file
                )

                st.success(f"✅ 샘플 데이터 로드 성공: {selected_file}")
                # 버그 #35 수정: 세션 상태 저장 완료 대기
                import time
                time.sleep(0.1)
                st.rerun()

        except Exception as e:
            st.error(f"❌ 샘플 데이터 로드 실패: {str(e)}")


def show_data_info():
    """데이터 정보 표시"""
    info = SessionManager.get_data_info()

    st.success("✅ 데이터 준비 완료")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("파일명", info['file_name'] or 'N/A')
    col2.metric("데이터 소스", info['source'] or 'N/A')
    col3.metric("행 수", f"{info['rows']:,}")
    col4.metric("컬럼 수", f"{info['columns']:,}")

    if info['data_type']:
        type_emoji = {
            'ecommerce': '🛒',
            'review': '💬',
            'sales': '📊'
        }
        st.info(f"{type_emoji.get(info['data_type'], '📄')} 감지된 데이터 타입: **{info['data_type']}**")


def page_auto_analysis():
    """페이지 2: 자동 분석"""
    st.title("🤖 자동 분석")

    # 데이터 체크
    if not SessionManager.has_data():
        st.warning("⚠️ 먼저 '시작하기' 페이지에서 데이터를 준비하세요")
        st.info("💡 왼쪽 사이드바에서 '🏠 시작하기' 페이지로 이동하세요")
        return

    st.markdown("### 📊 데이터 개요")
    show_data_info()

    st.markdown("---")
    st.markdown("### 🔧 분석 설정")

    # 분석 타입 선택 (자동 감지 or 수동 선택)
    detected_type = SessionManager.get_data_type()

    if detected_type:
        type_names = {
            'ecommerce': 'E-commerce (RFM 분석)',
            'review': '리뷰 분석 (감성 분석, 키워드 추출)',
            'sales': '판매 분석 (시계열 분석)'
        }
        st.success(f"✅ 자동 감지: **{type_names.get(detected_type)}**")
        analysis_type = detected_type
    else:
        analysis_type = st.radio(
            "분석 타입 선택",
            ['ecommerce', 'review', 'sales'],
            format_func=lambda x: {
                'ecommerce': '🛒 E-commerce (RFM 분석)',
                'review': '💬 리뷰 분석 (감성 분석)',
                'sales': '📊 판매 분석 (시계열 분석)'
            }[x],
            horizontal=True
        )

    SessionManager.set_analysis_type(analysis_type)

    # GPT 옵션 (리뷰 분석일 때만 표시)
    use_gpt = False
    if analysis_type == 'review':
        st.markdown("---")
        st.markdown("### 🤖 GPT 고급 분석 (선택)")

        # API 키 상태 확인
        from utils.api_key_manager import APIKeyManager
        api_status = APIKeyManager.get_api_key_status()

        if api_status['available'] and api_status['valid']:
            st.success(f"✅ API 키 감지됨 (소스: {api_status['source']})")

            col1, col2 = st.columns([3, 1])
            with col1:
                use_gpt = st.checkbox(
                    "GPT로 고급 감성 분석 수행 (부정 리뷰 중심)",
                    value=False,
                    help="GPT를 사용하여 더 정확한 감성 분석을 수행합니다. (비용 발생)"
                )
            with col2:
                if use_gpt:
                    # 예상 비용 표시
                    data = SessionManager.get_data()
                    est_reviews = min(len(data), 100)  # 최대 100개
                    est_tokens = est_reviews * 100  # 리뷰당 약 100 토큰
                    est_cost = APIKeyManager.estimate_cost(est_tokens, 'gpt-4o-mini')
                    st.info(f"예상: ~${est_cost:.4f}")

        else:
            st.warning("⚠️ OpenAI API 키가 없습니다")
            with st.expander("📖 API 키 설정 방법"):
                st.markdown("""
**API 키를 얻는 방법:**
1. [OpenAI Platform](https://platform.openai.com/api-keys)에 접속
2. API 키 생성
3. 다음 중 한 가지 방법으로 설정:

**방법 1: 환경변수 (권장)**
```bash
export OPENAI_API_KEY='sk-...'
```

**방법 2: .env 파일**
```
OPENAI_API_KEY=sk-...
```

**방법 3: Streamlit Secrets (배포용)**
`.streamlit/secrets.toml` 파일 생성:
```toml
OPENAI_API_KEY = "sk-..."
```
                """)

    st.markdown("---")

    # 분석 실행
    if st.button("🚀 분석 시작", type="primary", use_container_width=True):
        run_analysis(analysis_type, use_gpt=use_gpt)

    # 결과 표시
    if SessionManager.has_results():
        st.markdown("---")
        st.markdown("### 📈 분석 결과")
        show_analysis_results(analysis_type)


def run_analysis(analysis_type: str, use_gpt: bool = False):
    """분석 실행"""
    import time

    data = SessionManager.get_data()

    if analysis_type == 'ecommerce':
        run_ecommerce_analysis(data)
    elif analysis_type == 'review':
        run_review_analysis(data, use_gpt=use_gpt)
    elif analysis_type == 'sales':
        run_sales_analysis(data)


def run_ecommerce_analysis(df: pd.DataFrame):
    """E-commerce RFM 분석 실행"""
    import time

    try:
        # 필수 컬럼 확인
        required_cols = ['customerid', 'invoicedate', 'quantity', 'unitprice']
        df_cols_lower = [col.lower() for col in df.columns]

        missing_cols = [col for col in required_cols if col not in df_cols_lower]

        if missing_cols:
            st.error(f"❌ 필수 컬럼이 없습니다: {', '.join(missing_cols)}")
            st.info("💡 필요한 컬럼: CustomerID, InvoiceDate, Quantity, UnitPrice")
            return

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. 전처리
        status_text.text("1/5 데이터 전처리 중...")
        progress_bar.progress(20)
        preprocessor = DataPreprocessor(df)
        processed_df, logs = (preprocessor
                             .normalize_column_names()
                             .handle_missing_values(strategy='drop')
                             .remove_duplicates()
                             .convert_date_columns(['invoicedate'])
                             .get_processed_data())

        # 2. RFM 분석
        status_text.text("2/5 RFM 분석 중...")
        progress_bar.progress(40)
        rfm_analyzer = RFMAnalyzer(
            processed_df,
            customer_col='customerid',
            date_col='invoicedate',
            amount_col=None,
            quantity_col='quantity',
            price_col='unitprice'
        )
        rfm_df = rfm_analyzer.calculate_rfm()

        # 3. 군집화
        status_text.text("3/5 고객 세분화 중...")
        progress_bar.progress(60)
        optimal_k, metrics = rfm_analyzer.find_optimal_clusters()
        clustered_df = rfm_analyzer.perform_clustering()
        cluster_summary = rfm_analyzer.get_cluster_summary()

        # 4. 시각화 준비
        status_text.text("4/5 시각화 생성 중...")
        progress_bar.progress(80)

        # 5. 결과 저장
        results = {
            'type': 'ecommerce',
            'rfm_df': rfm_df,
            'clustered_df': clustered_df,
            'cluster_summary': cluster_summary,
            'optimal_k': optimal_k,
            'metrics': metrics,
            'analyzer': rfm_analyzer
        }

        SessionManager.save_results(results)

        # 완료
        progress_bar.progress(100)
        status_text.text("✅ 분석 완료!")
        # 버그 #35 수정: UI 업데이트 및 세션 상태 저장 완료 대기
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        st.success("🎉 E-commerce 분석이 완료되었습니다!")
        st.balloons()
        st.rerun()

    except Exception as e:
        # 버그 #45 수정: 분석 실패 시 부분 결과 삭제
        SessionManager.clear_analysis()
        st.error(f"❌ 분석 중 오류 발생: {str(e)}")
        st.exception(e)


def run_review_analysis(df: pd.DataFrame, use_gpt: bool = False):
    """리뷰 감성 분석 실행"""
    import time

    try:
        # 텍스트 컬럼 찾기
        text_col = None
        rating_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'review' in col_lower or 'text' in col_lower or 'comment' in col_lower:
                text_col = col
            if 'rating' in col_lower or 'score' in col_lower or 'point' in col_lower:
                rating_col = col

        if not text_col:
            st.error("❌ 리뷰 텍스트 컬럼을 찾을 수 없습니다.")
            st.info("💡 필요한 컬럼: review, text, comment 중 하나")
            return

        st.info(f"📝 텍스트 컬럼: **{text_col}**" + (f" | 평점 컬럼: **{rating_col}**" if rating_col else ""))

        # Progress bar
        total_steps = 6 if use_gpt else 5
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. 텍스트 분석기 초기화
        status_text.text(f"1/{total_steps} 텍스트 분석기 초기화 중...")
        progress_bar.progress(int(100 / total_steps * 1))
        analyzer = TextAnalyzer(df, text_column=text_col, rating_column=rating_col)

        # 2. 전처리
        status_text.text(f"2/{total_steps} 텍스트 전처리 중...")
        progress_bar.progress(int(100 / total_steps * 2))
        analyzer.preprocess_text()

        # 3. 감성 분석
        status_text.text(f"3/{total_steps} 감성 분석 중...")
        progress_bar.progress(int(100 / total_steps * 3))
        analyzer.analyze_sentiment_simple()

        # 4. 키워드 추출
        status_text.text(f"4/{total_steps} 키워드 추출 중...")
        progress_bar.progress(int(100 / total_steps * 4))
        keywords = analyzer.extract_keywords(top_n=20)

        # 5. GPT 고급 분석 (선택)
        gpt_results = None
        if use_gpt:
            status_text.text(f"5/{total_steps} GPT로 고급 감성 분석 중... (부정 리뷰 우선)")
            progress_bar.progress(int(100 / total_steps * 5))

            try:
                from modules.gpt_analyzer import GPTAnalyzer
                from utils.api_key_manager import get_api_key

                api_key = get_api_key()
                if api_key:
                    gpt = GPTAnalyzer(api_key=api_key)

                    # 부정 리뷰 필터링 + 분석
                    gpt_sentiment = gpt.analyze_sentiment_batch(
                        reviews=[],  # 빈 리스트 (DataFrame에서 직접 필터링)
                        max_reviews=100,
                        filter_negative=True,
                        df=analyzer.df,
                        rating_column=rating_col if rating_col else 'rating',
                        text_column=text_col
                    )

                    # 비용 정보
                    cost_info = gpt.get_cost_info()

                    gpt_results = {
                        'sentiment': gpt_sentiment,
                        'cost': cost_info
                    }

                    st.success(f"✅ GPT 분석 완료! (비용: ${cost_info['total_cost']:.4f}, 토큰: {cost_info['total_tokens']:,})")
                else:
                    st.warning("⚠️ API 키를 찾을 수 없어 GPT 분석을 건너뜁니다.")

            except Exception as e:
                st.warning(f"⚠️ GPT 분석 중 오류 발생: {str(e)}")
                import traceback
                traceback.print_exc()

        # 6. 결과 저장
        results = {
            'type': 'review',
            'analyzer': analyzer,
            'text_col': text_col,
            'rating_col': rating_col,
            'keywords': keywords,
            'gpt_results': gpt_results,
            'use_gpt': use_gpt
        }

        SessionManager.save_results(results)

        # 완료
        progress_bar.progress(100)
        status_text.text("✅ 분석 완료!")
        # 버그 #35 수정: UI 업데이트 및 세션 상태 저장 완료 대기
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        st.success("🎉 리뷰 분석이 완료되었습니다!")
        st.balloons()
        st.rerun()

    except Exception as e:
        # 버그 #45 수정: 분석 실패 시 부분 결과 삭제
        SessionManager.clear_analysis()
        st.error(f"❌ 분석 중 오류 발생: {str(e)}")
        st.exception(e)


def run_sales_analysis(df: pd.DataFrame):
    """판매 분석 실행"""
    st.info("🚧 판매 분석 기능은 DAY 29-31에 구현 예정입니다.")


def show_analysis_results(analysis_type: str):
    """분석 결과 표시"""
    results = SessionManager.get_results()

    if results.get('type') == 'ecommerce':
        show_ecommerce_results(results)
    elif results.get('type') == 'review':
        show_review_results(results)
    elif results.get('type') == 'sales':
        show_sales_results(results)


def show_ecommerce_results(results: dict):
    """E-commerce 분석 결과 표시"""
    clustered_df = results['clustered_df']
    cluster_summary = results['cluster_summary']
    optimal_k = results['optimal_k']

    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 고객 수", f"{len(clustered_df):,}")
    with col2:
        st.metric("군집 개수", optimal_k)
    with col3:
        # 버그 #37 수정: cluster_name 컬럼 존재 확인
        if 'cluster_name' in clustered_df.columns:
            vip_count = len(clustered_df[clustered_df['cluster_name'].str.contains('VIP|충성', na=False)])
        else:
            vip_count = 0
        st.metric("VIP/충성 고객", f"{vip_count:,}")
    with col4:
        # 버그 #37 수정: cluster_name 컬럼 존재 확인
        if 'cluster_name' in clustered_df.columns:
            risk_count = len(clustered_df[clustered_df['cluster_name'].str.contains('이탈|휴면', na=False)])
        else:
            risk_count = 0
        st.metric("이탈 위험", f"{risk_count:,}")

    st.markdown("---")

    # 시각화
    visualizer = Visualizer()
    tab1, tab2, tab3 = st.tabs(["📊 RFM 히트맵", "📈 고객 분포", "📋 데이터"])

    with tab1:
        st.markdown("### RFM 히트맵")
        fig_heatmap = visualizer.plot_rfm_heatmap(cluster_summary)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("### 군집별 지표")
        fig_bar = visualizer.plot_cluster_bar_chart(cluster_summary)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.markdown("### 고객 가치 피라미드")
        fig_pyramid = visualizer.plot_customer_value_pyramid(cluster_summary)
        st.plotly_chart(fig_pyramid, use_container_width=True)

        st.markdown("### 군집별 고객 분포")
        fig_pie = visualizer.plot_cluster_distribution_pie(cluster_summary)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        st.markdown("### 군집별 상세 통계")
        st.dataframe(cluster_summary, use_container_width=True)

        st.markdown("### 고객 세분화 데이터")
        # 대소문자 구분 없이 존재하는 컬럼만 표시
        display_cols = []
        for check_col in ['customerid']:
            if check_col in clustered_df.columns:
                display_cols.append(check_col)

        # RFM 컬럼 찾기 (대소문자 무관)
        for col in clustered_df.columns:
            col_lower = col.lower()
            if col_lower in ['recency', 'frequency', 'monetary'] and col not in display_cols:
                display_cols.append(col)

        # cluster 관련 컬럼
        for check_col in ['cluster', 'cluster_name']:
            if check_col in clustered_df.columns and check_col not in display_cols:
                display_cols.append(check_col)

        st.dataframe(
            clustered_df[display_cols] if display_cols else clustered_df,
            use_container_width=True
        )

    # 인사이트
    st.markdown("---")
    st.markdown("### 💡 인사이트")

    generator = InsightGenerator()
    insights = generator.generate_rfm_insights(results['rfm_df'], cluster_summary)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**주요 발견사항**")
        for finding in insights['key_findings']:
            st.info(finding)

    with col2:
        st.markdown("**액션 아이템**")
        for action in insights['action_items']:
            st.warning(action)


def show_review_results(results: dict):
    """리뷰 분석 결과 표시"""
    analyzer = results['analyzer']
    text_col = results['text_col']

    # 감성 분포
    sentiment_counts = analyzer.df['sentiment'].value_counts()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 리뷰 수", f"{len(analyzer.df):,}")
    with col2:
        positive_pct = (sentiment_counts.get('positive', 0) / len(analyzer.df) * 100)
        st.metric("긍정 비율", f"{positive_pct:.1f}%")
    with col3:
        negative_pct = (sentiment_counts.get('negative', 0) / len(analyzer.df) * 100)
        st.metric("부정 비율", f"{negative_pct:.1f}%")

    st.markdown("---")

    # 시각화
    visualizer = Visualizer()
    tab1, tab2, tab3 = st.tabs(["📊 감성 분석", "☁️ 워드 클라우드", "📋 데이터"])

    with tab1:
        st.markdown("### 감성 분포")
        fig_sentiment = visualizer.plot_sentiment_distribution(analyzer.df)
        st.plotly_chart(fig_sentiment, use_container_width=True)

        st.markdown("### 감성별 키워드 (Top 15)")
        keywords = results.get('keywords', {})
        if keywords:
            fig_keywords = visualizer.plot_keywords_comparison(keywords)
            st.plotly_chart(fig_keywords, use_container_width=True)
        else:
            st.info("키워드 데이터가 없습니다.")

    with tab2:
        st.markdown("### 전체 워드 클라우드")
        try:
            # 단어 빈도 계산
            from collections import Counter
            all_words = []
            if hasattr(analyzer, 'processed_texts') and analyzer.processed_texts:
                for tokens in analyzer.processed_texts:
                    if tokens:
                        all_words.extend(tokens.split())

            if all_words:
                word_freq = Counter(all_words).most_common(50)
                wordcloud_fig = visualizer.plot_word_cloud_data(word_freq, top_n=50)
                st.plotly_chart(wordcloud_fig, use_container_width=True)
            else:
                st.info("워드 클라우드를 생성할 데이터가 없습니다.")
        except Exception as e:
            st.error(f"워드 클라우드 생성 실패: {str(e)}")

    with tab3:
        st.markdown("### 리뷰 데이터")
        display_cols = [text_col, 'sentiment']
        if 'rating' in analyzer.df.columns:
            display_cols.insert(1, 'rating')
        st.dataframe(analyzer.df[display_cols], use_container_width=True)


def show_sales_results(results: dict):
    """판매 분석 결과 표시"""
    st.info("🚧 판매 분석 결과 표시 기능은 DAY 29-31에 구현 예정입니다.")


def page_explore():
    """페이지 3: 상세 탐색"""
    st.title("🔍 상세 탐색")

    # 결과 체크
    if not SessionManager.has_results():
        st.warning("⚠️ 먼저 '자동 분석' 페이지에서 분석을 실행하세요")
        st.info("💡 왼쪽 사이드바에서 '🤖 자동 분석' 페이지로 이동하세요")
        return

    results = SessionManager.get_results()
    analysis_type = results.get('type')

    st.markdown("### 🔧 필터링 및 검색")

    if analysis_type == 'ecommerce':
        render_ecommerce_filters(results)
    elif analysis_type == 'review':
        render_review_filters(results)
    elif analysis_type == 'sales':
        st.info("🚧 판매 분석 필터링은 DAY 29-31에 추가됩니다")


def render_ecommerce_filters(results: dict):
    """E-commerce 필터링 UI"""
    clustered_df = results.get('clustered_df')
    rfm_df = results.get('rfm_df')
    cluster_summary = results.get('cluster_summary')

    # RFM 데이터 우선 사용 (Recency, Frequency, Monetary 컬럼 포함)
    if rfm_df is not None and not rfm_df.empty:
        display_df = rfm_df
    elif clustered_df is not None and not clustered_df.empty:
        display_df = clustered_df
    else:
        st.error("❌ 분석 결과 데이터를 찾을 수 없습니다.")
        return

    # 사이드바 필터
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 필터 옵션")

        # 군집 선택 (cluster_name이 있는 경우만)
        if 'cluster_name' in display_df.columns:
            all_clusters = sorted(display_df['cluster_name'].unique())
            selected_clusters = st.multiselect(
                "군집 선택",
                options=all_clusters,
                default=all_clusters,
                key="cluster_filter"
            )
        else:
            selected_clusters = None

        # RFM 범위 슬라이더
        st.markdown("**Recency 범위 (일)**")
        # 버그 #34 수정: min == max 체크
        # 대소문자 구분 없이 컬럼 찾기
        recency_col = None
        for col in display_df.columns:
            if col.lower() == 'recency':
                recency_col = col
                break

        if recency_col is None:
            st.warning("⚠️ Recency 데이터가 없습니다.")
            r_min, r_max = 0, 0
        else:
            r_min_val = int(display_df[recency_col].min())
            r_max_val = int(display_df[recency_col].max())
            if r_min_val < r_max_val:
                r_min, r_max = st.slider(
                    "Recency",
                    min_value=r_min_val,
                    max_value=r_max_val,
                    value=(r_min_val, r_max_val),
                    key="r_range",
                    label_visibility="collapsed"
                )
            else:
                st.info(f"모든 고객의 Recency: {r_min_val}일")
                r_min, r_max = r_min_val, r_max_val

        st.markdown("**Frequency 범위 (건)**")
        # 버그 #34 수정: min == max 체크
        frequency_col = None
        for col in display_df.columns:
            if col.lower() == 'frequency':
                frequency_col = col
                break

        if frequency_col is None:
            st.warning("⚠️ Frequency 데이터가 없습니다.")
            f_min, f_max = 0, 0
        else:
            f_min_val = int(display_df[frequency_col].min())
            f_max_val = int(display_df[frequency_col].max())
            if f_min_val < f_max_val:
                f_min, f_max = st.slider(
                    "Frequency",
                    min_value=f_min_val,
                    max_value=f_max_val,
                    value=(f_min_val, f_max_val),
                    key="f_range",
                    label_visibility="collapsed"
                )
            else:
                st.info(f"모든 고객의 Frequency: {f_min_val}건")
                f_min, f_max = f_min_val, f_max_val

        st.markdown("**Monetary 범위 (원)**")
        # 버그 #34 수정: min == max 체크
        monetary_col = None
        for col in display_df.columns:
            if col.lower() == 'monetary':
                monetary_col = col
                break

        if monetary_col is None:
            st.warning("⚠️ Monetary 데이터가 없습니다.")
            m_min, m_max = 0, 0
        else:
            m_min_val = float(display_df[monetary_col].min())
            m_max_val = float(display_df[monetary_col].max())
            if m_min_val < m_max_val:
                m_min, m_max = st.slider(
                    "Monetary",
                    min_value=m_min_val,
                    max_value=m_max_val,
                    value=(m_min_val, m_max_val),
                    key="m_range",
                    label_visibility="collapsed"
                )
            else:
                st.info(f"모든 고객의 Monetary: ₩{m_min_val:,.0f}")
                m_min, m_max = m_min_val, m_max_val

    # 필터 적용 (버그 #38 수정: .copy() 추가)
    # RFM 컬럼이 모두 있는지 확인 (대소문자 무관)
    if recency_col is None or frequency_col is None or monetary_col is None:
        st.error("❌ RFM 데이터가 없습니다. 분석을 다시 실행해주세요.")
        filtered_df = display_df.copy()
    elif selected_clusters is not None and 'cluster_name' in display_df.columns:
        # 군집 + RFM 필터링
        filtered_df = display_df[
            (display_df['cluster_name'].isin(selected_clusters)) &
            (display_df[recency_col].between(r_min, r_max)) &
            (display_df[frequency_col].between(f_min, f_max)) &
            (display_df[monetary_col].between(m_min, m_max))
        ].copy()
    else:
        # RFM만 필터링
        filtered_df = display_df[
            (display_df[recency_col].between(r_min, r_max)) &
            (display_df[frequency_col].between(f_min, f_max)) &
            (display_df[monetary_col].between(m_min, m_max))
        ].copy()

    # 검색
    search_query = st.text_input(
        "🔍 고객 ID 검색",
        placeholder="고객 ID 입력...",
        key="customer_search"
    )

    if search_query:
        # 버그 #39 수정: regex 이스케이핑 추가
        import re
        escaped_query = re.escape(search_query)
        filtered_df = filtered_df[
            filtered_df['customerid'].astype(str).str.contains(escaped_query, case=False, na=False)
        ]

    # 결과 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("필터링된 고객 수", f"{len(filtered_df):,}")

    # 버그 #32, #33 수정: ZeroDivisionError와 빈 DataFrame 체크
    if len(display_df) > 0:
        ratio = len(filtered_df) / len(display_df) * 100
        col2.metric("전체 대비 비율", f"{ratio:.1f}%")
    else:
        col2.metric("전체 대비 비율", "N/A")

    if len(filtered_df) > 0 and monetary_col and monetary_col in filtered_df.columns:
        col3.metric("총 매출액", f"₩{filtered_df[monetary_col].sum():,.0f}")
    else:
        col3.metric("총 매출액", "₩0")

    st.markdown("---")

    # 빈 결과 처리
    if len(filtered_df) == 0:
        st.warning("⚠️ 필터 조건에 맞는 고객이 없습니다. 필터 조건을 완화해 보세요.")
    else:
        # 데이터 테이블 - 존재하는 컬럼만 표시
        display_cols = []
        for col in ['customerid']:
            if col in filtered_df.columns:
                display_cols.append(col)

        if recency_col and recency_col in filtered_df.columns:
            display_cols.append(recency_col)
        if frequency_col and frequency_col in filtered_df.columns:
            display_cols.append(frequency_col)
        if monetary_col and monetary_col in filtered_df.columns:
            display_cols.append(monetary_col)

        if 'cluster_name' in filtered_df.columns:
            display_cols.append('cluster_name')
        elif 'cluster' in filtered_df.columns:
            display_cols.append('cluster')

        st.dataframe(
            filtered_df[display_cols] if display_cols else filtered_df,
            use_container_width=True,
            height=400
        )

        # CSV 다운로드
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 필터링된 데이터 CSV 다운로드",
            data=csv,
            file_name=f"filtered_customers_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def render_review_filters(results: dict):
    """리뷰 필터링 UI"""
    analyzer = results['analyzer']
    text_col = results['text_col']

    # 사이드바 필터
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 필터 옵션")

        # 감성 필터
        all_sentiments = sorted(analyzer.df['sentiment'].unique())
        selected_sentiments = st.multiselect(
            "감성 선택",
            options=all_sentiments,
            default=all_sentiments,
            key="sentiment_filter"
        )

        # 평점 범위 (있을 경우)
        if 'rating' in analyzer.df.columns:
            st.markdown("**평점 범위**")
            # 버그 #34 수정: min == max 체크
            rating_min_val = float(analyzer.df['rating'].min())
            rating_max_val = float(analyzer.df['rating'].max())
            if rating_min_val < rating_max_val:
                rating_min, rating_max = st.slider(
                    "Rating",
                    min_value=rating_min_val,
                    max_value=rating_max_val,
                    value=(rating_min_val, rating_max_val),
                    key="rating_range",
                    label_visibility="collapsed"
                )
            else:
                st.info(f"모든 리뷰의 평점: {rating_min_val:.1f}")
                rating_min, rating_max = rating_min_val, rating_max_val

    # 필터 적용 (버그 #38 수정: .copy() 추가)
    filtered_df = analyzer.df[analyzer.df['sentiment'].isin(selected_sentiments)].copy()

    if 'rating' in analyzer.df.columns:
        filtered_df = filtered_df[filtered_df['rating'].between(rating_min, rating_max)]

    # 검색
    search_query = st.text_input(
        "🔍 키워드 검색",
        placeholder="리뷰 내용 검색...",
        key="review_search"
    )

    if search_query:
        # 버그 #39 수정: regex 이스케이핑 추가
        import re
        escaped_query = re.escape(search_query)
        filtered_df = filtered_df[
            filtered_df[text_col].astype(str).str.contains(escaped_query, case=False, na=False)
        ]

    # 결과 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("필터링된 리뷰 수", f"{len(filtered_df):,}")

    # 버그 #32, #33 수정: ZeroDivisionError와 빈 DataFrame 체크
    if len(analyzer.df) > 0:
        ratio = len(filtered_df) / len(analyzer.df) * 100
        col2.metric("전체 대비 비율", f"{ratio:.1f}%")
    else:
        col2.metric("전체 대비 비율", "N/A")

    if 'rating' in analyzer.df.columns:
        if len(filtered_df) > 0:
            avg_rating = filtered_df['rating'].mean()
            col3.metric("평균 평점", f"{avg_rating:.2f}")
        else:
            col3.metric("평균 평점", "N/A")

    st.markdown("---")

    # 빈 결과 처리
    if len(filtered_df) == 0:
        st.warning("⚠️ 필터 조건에 맞는 리뷰가 없습니다. 필터 조건을 완화해 보세요.")
    else:
        # 데이터 테이블
        display_cols = [text_col, 'sentiment']
        if 'rating' in analyzer.df.columns:
            display_cols.insert(1, 'rating')

        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            height=400
        )

        # CSV 다운로드
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 필터링된 리뷰 CSV 다운로드",
            data=csv,
            file_name=f"filtered_reviews_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def page_export():
    """페이지 4: 내보내기"""
    st.title("📥 내보내기")

    # 결과 체크
    if not SessionManager.has_results():
        st.warning("⚠️ 먼저 '자동 분석' 페이지에서 분석을 실행하세요")
        st.info("💡 왼쪽 사이드바에서 '🤖 자동 분석' 페이지로 이동하세요")
        return

    results = SessionManager.get_results()
    analysis_type = results.get('type')

    st.markdown("### 📦 다운로드 옵션")

    col1, col2 = st.columns(2)

    # CSV 다운로드
    with col1:
        st.markdown("#### 📄 CSV 다운로드")

        if analysis_type == 'ecommerce':
            # E-commerce: 고객 세분화 데이터
            clustered_df = results['clustered_df']
            csv = clustered_df.to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="📊 고객 세분화 CSV 다운로드",
                data=csv,
                file_name=f"rfm_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.info(f"총 {len(clustered_df):,}개 고객 데이터")

        elif analysis_type == 'review':
            # 리뷰: 감성 분석 결과
            analyzer = results['analyzer']
            text_col = results['text_col']

            display_cols = [text_col, 'sentiment']
            if 'rating' in analyzer.df.columns:
                display_cols.insert(1, 'rating')

            csv = analyzer.df[display_cols].to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="💬 리뷰 감성 분석 CSV 다운로드",
                data=csv,
                file_name=f"review_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.info(f"총 {len(analyzer.df):,}개 리뷰")

        elif analysis_type == 'sales':
            st.info("🚧 판매 분석 CSV는 DAY 29-31에 추가됩니다")

    # HTML 리포트
    with col2:
        st.markdown("#### 📊 HTML 리포트")

        if st.button("📑 리포트 생성", use_container_width=True):
            with st.spinner("📊 HTML 리포트를 생성하는 중..."):
                try:
                    generator = HTMLReportGenerator()

                    if analysis_type == 'ecommerce':
                        # E-commerce 리포트
                        # 간단한 리포트 생성 (메서드 미구현으로 임시 처리)
                        from modules.insight_generator import InsightGenerator
                        insight_gen = InsightGenerator()
                        insights = insight_gen.generate_rfm_insights(
                            results['rfm_df'],
                            results['cluster_summary']
                        )

                        html_report = generator.generate_report(
                            analysis_type='ecommerce',
                            data_info={
                                'rows': len(results['clustered_df']),
                                'columns': len(results['clustered_df'].columns),
                                'customers': len(results['clustered_df'])
                            },
                            insights=insights,
                            charts=[]
                        )

                        st.download_button(
                            label="📥 E-commerce 리포트 다운로드",
                            data=html_report,
                            file_name=f"ecommerce_report_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                            mime="text/html",
                            use_container_width=True
                        )

                        st.success("✅ 리포트 생성 완료!")

                    elif analysis_type == 'review':
                        # 리뷰 리포트
                        analyzer = results['analyzer']
                        sentiment_counts = analyzer.df['sentiment'].value_counts().to_dict()

                        # 간단한 인사이트 생성
                        total = len(analyzer.df)
                        positive_pct = (sentiment_counts.get('positive', 0) / total * 100) if total > 0 else 0
                        negative_pct = (sentiment_counts.get('negative', 0) / total * 100) if total > 0 else 0

                        insights = {
                            'key_findings': [
                                f"총 {total:,}개의 리뷰를 분석했습니다.",
                                f"긍정 리뷰 비율: {positive_pct:.1f}%",
                                f"부정 리뷰 비율: {negative_pct:.1f}%"
                            ],
                            'action_items': [
                                "긍정 리뷰의 키워드를 마케팅에 활용하세요.",
                                "부정 리뷰의 문제점을 개선하세요."
                            ]
                        }

                        html_report = generator.generate_report(
                            analysis_type='review',
                            data_info={
                                'rows': len(analyzer.df),
                                'columns': len(analyzer.df.columns)
                            },
                            insights=insights,
                            charts=[]
                        )

                        st.download_button(
                            label="📥 리뷰 분석 리포트 다운로드",
                            data=html_report,
                            file_name=f"review_report_{pd.Timestamp.now().strftime('%Y%m%d')}.html",
                            mime="text/html",
                            use_container_width=True
                        )

                        st.success("✅ 리포트 생성 완료!")

                    elif analysis_type == 'sales':
                        st.info("🚧 판매 분석 리포트는 DAY 29-31에 추가됩니다")

                except Exception as e:
                    st.error(f"❌ 리포트 생성 실패: {str(e)}")
                    st.exception(e)


# ==================== 메인 ====================

def main():
    """메인 함수"""
    # CSS 로드
    load_custom_css()

    # 세션 초기화
    SessionManager.init_session()

    # 사이드바: 네비게이션
    with st.sidebar:
        st.markdown("## 📊 Auto-Insight")
        st.markdown("---")

        # 페이지 선택
        page = st.radio(
            "메뉴",
            ["🏠 시작하기", "🤖 자동 분석", "🔍 상세 탐색", "📥 내보내기"],
            key="page_selector"
        )

        SessionManager.set_current_page(page)

        st.markdown("---")

        # 새로 시작하기 버튼
        if st.button("🔄 새로 시작하기", use_container_width=True):
            SessionManager.clear_all()
            st.rerun()

        # 환경 정보 (디버깅용)
        if st.checkbox("🔧 환경 정보 표시", key="show_env"):
            Environment.show_environment_info()

    # 페이지 라우팅
    if page == "🏠 시작하기":
        page_start()
    elif page == "🤖 자동 분석":
        page_auto_analysis()
    elif page == "🔍 상세 탐색":
        page_explore()
    elif page == "📥 내보내기":
        page_export()


if __name__ == "__main__":
    main()
