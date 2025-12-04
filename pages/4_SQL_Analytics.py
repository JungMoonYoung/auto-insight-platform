"""
SQL Analytics Dashboard
DAY 36: Phase 4 - SQL 역량 강화

실시간 SQL 쿼리 실행 및 분석 결과 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.db_manager import DatabaseManager
from modules.sql_query_generator import SQLQueryGenerator

# 페이지 설정
st.set_page_config(
    page_title="SQL Analytics | Auto-Insight Platform",
    page_icon="🔍",
    layout="wide"
)

# ==================== CSS 스타일 ====================
st.markdown("""
<style>
    /* 다크 테마 */
    .main {
        background: #0a0e27;
    }

    .block-container {
        padding-top: 2rem;
        background: rgba(20, 25, 45, 0.95);
        border-radius: 20px;
    }

    /* 제목 */
    h1 {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    h2, h3 {
        color: #00f2fe;
    }

    /* SQL 코드 블록 */
    .stCodeBlock {
        background: #1a1f3a !important;
        border: 1px solid #00f2fe;
        border-radius: 10px;
    }

    /* 메트릭 카드 */
    .stMetric {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }

    /* 데이터프레임 */
    .dataframe {
        background: #1a1f3a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 헤더 ====================
st.title("🔍 SQL Analytics Dashboard")
st.markdown("### 실시간 SQL 쿼리 실행 및 데이터 분석")
st.markdown("---")

# ==================== 세션 초기화 ====================
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager(db_path='data/analytics.db')

if 'sql_generator' not in st.session_state:
    st.session_state.sql_generator = SQLQueryGenerator()

db = st.session_state.db_manager
sql_gen = st.session_state.sql_generator

# ==================== 사이드바 - 쿼리 선택 ====================
st.sidebar.title("📋 SQL 쿼리 선택")

query_options = {
    "RFM 분석": "rfm_analysis",
    "RFM 세그먼트 요약": "rfm_summary",
    "일별 매출 트렌드": "sales_trend_daily",
    "월별 매출 트렌드": "sales_trend_monthly",
    "파레토 분석 (상위 상품)": "pareto_analysis",
    "감성 분석": "sentiment_analysis",
    "상위 고객 분석": "top_customers"
}

selected_query_name = st.sidebar.selectbox(
    "분석 유형 선택",
    options=list(query_options.keys())
)

selected_query_type = query_options[selected_query_name]

# ==================== 파라미터 설정 ====================
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 파라미터 설정")

# RFM 분석 파라미터
if selected_query_type in ['rfm_analysis', 'rfm_summary']:
    reference_date = st.sidebar.date_input(
        "기준일",
        value=pd.Timestamp.now()
    ).strftime('%Y-%m-%d')

    max_score = st.sidebar.slider(
        "최대 RFM 점수",
        min_value=3,
        max_value=10,
        value=5,
        help="고객을 몇 등급으로 나눌지 설정 (3-10)"
    )

# 매출 트렌드 파라미터
elif selected_query_type in ['sales_trend_daily', 'sales_trend_monthly']:
    moving_avg_days = st.sidebar.slider(
        "이동평균 기간",
        min_value=3,
        max_value=30,
        value=7,
        help="이동평균 계산 기간 (일수)"
    )

# 파레토 분석 파라미터
elif selected_query_type == 'pareto_analysis':
    top_pct = st.sidebar.slider(
        "누적 비율 (%)",
        min_value=50,
        max_value=100,
        value=80,
        help="상위 몇 %까지 표시할지 설정"
    )

# 상위 고객 파라미터
elif selected_query_type == 'top_customers':
    limit = st.sidebar.slider(
        "표시할 고객 수",
        min_value=5,
        max_value=50,
        value=10
    )

# ==================== 메인 영역 ====================

# 데이터베이스 상태 확인
col1, col2, col3 = st.columns(3)

with col1:
    try:
        transactions_count = db.get_data("SELECT COUNT(*) as cnt FROM transactions")['cnt'].iloc[0]
        st.metric("거래 데이터", f"{transactions_count:,}건")
    except:
        st.metric("거래 데이터", "0건")

with col2:
    try:
        reviews_count = db.get_data("SELECT COUNT(*) as cnt FROM reviews")['cnt'].iloc[0]
        st.metric("리뷰 데이터", f"{reviews_count:,}건")
    except:
        st.metric("리뷰 데이터", "0건")

with col3:
    try:
        sales_count = db.get_data("SELECT COUNT(*) as cnt FROM sales")['cnt'].iloc[0]
        st.metric("판매 데이터", f"{sales_count:,}건")
    except:
        st.metric("판매 데이터", "0건")

st.markdown("---")

# ==================== SQL 쿼리 생성 및 실행 ====================
st.subheader(f"📊 {selected_query_name}")

# 쿼리 생성
try:
    if selected_query_type == 'rfm_analysis':
        query = sql_gen.generate_rfm_query(reference_date=reference_date, max_score=max_score)
    elif selected_query_type == 'rfm_summary':
        query = sql_gen.generate_rfm_summary_query(reference_date=reference_date, max_score=max_score)
    elif selected_query_type == 'sales_trend_daily':
        query = sql_gen.generate_sales_trend_query(period='daily', moving_average_days=moving_avg_days)
    elif selected_query_type == 'sales_trend_monthly':
        query = sql_gen.generate_sales_trend_query(period='monthly', moving_average_days=moving_avg_days)
    elif selected_query_type == 'pareto_analysis':
        query = sql_gen.generate_pareto_query(top_pct=top_pct)
    elif selected_query_type == 'sentiment_analysis':
        query = sql_gen.generate_sentiment_query()
    elif selected_query_type == 'top_customers':
        query = sql_gen.generate_top_customers_query(limit=limit)

    # SQL 쿼리 표시 (접기/펼치기)
    with st.expander("🔍 생성된 SQL 쿼리 보기"):
        st.code(query, language='sql')

    # 쿼리 실행
    if st.button("▶️ 쿼리 실행", type="primary", use_container_width=True):
        with st.spinner("쿼리 실행 중..."):
            df = db.get_data(query)

            if len(df) == 0:
                st.warning("⚠️ 데이터가 없습니다. 먼저 데이터를 수집해주세요.")
            else:
                st.success(f"✅ {len(df):,}개의 결과를 조회했습니다.")

                # 결과 저장
                st.session_state.query_result = df
                st.session_state.query_type = selected_query_type

except Exception as e:
    st.error(f"❌ 쿼리 생성 오류: {e}")

# ==================== 결과 시각화 ====================
if 'query_result' in st.session_state and st.session_state.query_result is not None:
    df_result = st.session_state.query_result
    query_type = st.session_state.query_type

    st.markdown("---")
    st.subheader("📈 분석 결과")

    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["📊 차트", "📋 데이터 테이블", "💾 내보내기"])

    with tab1:
        # RFM 분석 시각화
        if query_type == 'rfm_analysis':
            col1, col2 = st.columns(2)

            with col1:
                # 세그먼트별 고객 수
                segment_counts = df_result['segment'].value_counts()
                fig1 = px.pie(
                    values=segment_counts.values,
                    names=segment_counts.index,
                    title='고객 세그먼트 분포',
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # RFM 점수 분포
                fig2 = go.Figure()
                fig2.add_trace(go.Box(y=df_result['r_score'], name='Recency', marker_color='#00f2fe'))
                fig2.add_trace(go.Box(y=df_result['f_score'], name='Frequency', marker_color='#4facfe'))
                fig2.add_trace(go.Box(y=df_result['m_score'], name='Monetary', marker_color='#f093fb'))
                fig2.update_layout(
                    title='RFM 점수 분포',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)

        # RFM 요약 시각화
        elif query_type == 'rfm_summary':
            col1, col2 = st.columns(2)

            with col1:
                # 세그먼트별 고객 수
                fig1 = px.bar(
                    df_result,
                    x='세그먼트',
                    y='고객 수',
                    title='세그먼트별 고객 수',
                    color='고객 수',
                    color_continuous_scale='Plasma'
                )
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # 매출 기여도
                fig2 = px.pie(
                    df_result,
                    values='총 매출',
                    names='세그먼트',
                    title='세그먼트별 매출 기여도',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig2, use_container_width=True)

        # 매출 트렌드 시각화
        elif query_type in ['sales_trend_daily', 'sales_trend_monthly']:
            # 시계열 차트
            fig = go.Figure()

            # 실제 매출
            fig.add_trace(go.Scatter(
                x=df_result.iloc[:, 0],
                y=df_result.iloc[:, 1],
                mode='lines+markers',
                name='매출',
                line=dict(color='#00f2fe', width=2),
                marker=dict(size=6)
            ))

            # 이동평균
            if len(df_result.columns) > 2:
                fig.add_trace(go.Scatter(
                    x=df_result.iloc[:, 0],
                    y=df_result.iloc[:, 2],
                    mode='lines',
                    name='이동평균',
                    line=dict(color='#f093fb', width=2, dash='dash')
                ))

            fig.update_layout(
                title='매출 트렌드',
                xaxis_title='기간',
                yaxis_title='매출',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

        # 파레토 분석 시각화
        elif query_type == 'pareto_analysis':
            fig = go.Figure()

            # 매출 막대 그래프
            fig.add_trace(go.Bar(
                x=df_result['상품명'],
                y=df_result['총 매출'],
                name='총 매출',
                marker_color='#00f2fe',
                yaxis='y'
            ))

            # 누적 비율 선 그래프
            fig.add_trace(go.Scatter(
                x=df_result['상품명'],
                y=df_result['누적 비율 (%)'],
                name='누적 비율',
                line=dict(color='#f093fb', width=3),
                yaxis='y2'
            ))

            fig.update_layout(
                title='파레토 분석 (ABC Analysis)',
                xaxis_title='상품명',
                yaxis=dict(title='총 매출', side='left'),
                yaxis2=dict(title='누적 비율 (%)', side='right', overlaying='y'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

        # 감성 분석 시각화
        elif query_type == 'sentiment_analysis':
            col1, col2 = st.columns(2)

            with col1:
                # 감성 분포 (파이 차트)
                fig1 = px.pie(
                    df_result,
                    values='리뷰 수',
                    names='감성',
                    title='감성 분포',
                    color='감성',
                    color_discrete_map={
                        'positive': '#00f2fe',
                        'neutral': '#4facfe',
                        'negative': '#f093fb'
                    }
                )
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # 감성별 리뷰 수 (막대 그래프)
                fig2 = px.bar(
                    df_result,
                    x='감성',
                    y='리뷰 수',
                    title='감성별 리뷰 수',
                    color='감성',
                    color_discrete_map={
                        'positive': '#00f2fe',
                        'neutral': '#4facfe',
                        'negative': '#f093fb'
                    }
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)

        # 상위 고객 시각화
        elif query_type == 'top_customers':
            col1, col2 = st.columns(2)

            with col1:
                # 총 구매액 (막대 그래프)
                fig1 = px.bar(
                    df_result,
                    x='고객 ID',
                    y='총 구매액',
                    title='상위 고객별 구매액',
                    color='총 구매액',
                    color_continuous_scale='Plasma'
                )
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # 매출 기여도 (파이 차트)
                fig2 = px.pie(
                    df_result,
                    values='총 구매액',
                    names='고객 ID',
                    title='매출 기여도',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        # 데이터 테이블 표시
        st.dataframe(
            df_result,
            use_container_width=True,
            height=400
        )

        # 기본 통계
        st.subheader("📊 기본 통계")
        st.write(df_result.describe())

    with tab3:
        # CSV 다운로드
        csv = df_result.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 파일로 다운로드",
            data=csv,
            file_name=f"{selected_query_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Excel 다운로드 (선택적)
        st.info("💡 Excel 다운로드는 추후 구현 예정입니다.")

else:
    st.info("👆 쿼리를 선택하고 '쿼리 실행' 버튼을 눌러주세요.")

# ==================== 푸터 ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5);'>
    <p>🔍 SQL Analytics Dashboard | DAY 36: Phase 4 - SQL 역량 강화</p>
    <p>CTE, Window Functions, Aggregate Functions를 활용한 고급 SQL 분석</p>
</div>
""", unsafe_allow_html=True)
