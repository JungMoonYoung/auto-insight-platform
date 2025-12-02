"""
Visualizer Module
데이터 시각화 및 차트 생성
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List


class Visualizer:
    """인터랙티브 차트 생성"""
    
    def __init__(self, color_scheme: List[str] = None):
        """
        Args:
            color_scheme: 사용할 색상 리스트
        """
        self.color_scheme = color_scheme or [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    # ===== RFM 시각화 =====
    
    def plot_rfm_3d_scatter(self, rfm_df: pd.DataFrame) -> go.Figure:
        """
        RFM 3D Scatter Plot

        Args:
            rfm_df: RFM 데이터프레임 (cluster, cluster_name 컬럼 필요)

        Returns:
            plotly.graph_objects.Figure
        """
        fig = px.scatter_3d(
            rfm_df,
            x='Recency',
            y='Frequency',
            z='Monetary',
            color='cluster_name',
            hover_data=['customerid'] if 'customerid' in rfm_df.columns else None,
            title='고객 세분화 3D 시각화 (RFM)',
            labels={
                'Recency': '최근성 (일)',
                'Frequency': '구매 빈도',
                'Monetary': '구매 금액',
                'cluster_name': '고객 세그먼트'
            },
            color_discrete_sequence=self.color_scheme
        )
        
        fig.update_traces(marker=dict(size=5, opacity=0.7))
        fig.update_layout(
            scene=dict(
                xaxis_title='Recency (낮을수록 좋음)',
                yaxis_title='Frequency (높을수록 좋음)',
                zaxis_title='Monetary (높을수록 좋음)'
            ),
            height=700
        )
        
        return fig
    
    def plot_cluster_bar_chart(self, cluster_summary: pd.DataFrame) -> go.Figure:
        """
        군집별 평균 RFM 막대 차트
        
        Args:
            cluster_summary: 군집 요약 데이터
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('평균 Recency', '평균 Frequency', '평균 Monetary')
        )
        
        # Recency (낮을수록 좋음 - 역순 색상)
        fig.add_trace(
            go.Bar(
                x=cluster_summary['cluster_name'],
                y=cluster_summary['Recency_평균'],
                name='Recency',
                marker_color='lightcoral'
            ),
            row=1, col=1
        )
        
        # Frequency
        fig.add_trace(
            go.Bar(
                x=cluster_summary['cluster_name'],
                y=cluster_summary['Frequency_평균'],
                name='Frequency',
                marker_color='lightblue'
            ),
            row=1, col=2
        )
        
        # Monetary
        fig.add_trace(
            go.Bar(
                x=cluster_summary['cluster_name'],
                y=cluster_summary['Monetary_평균'],
                name='Monetary',
                marker_color='lightgreen'
            ),
            row=1, col=3
        )
        
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(
            title_text="군집별 평균 RFM 비교",
            showlegend=False,
            height=500
        )
        
        return fig
    
    def plot_cluster_distribution_pie(self, cluster_summary: pd.DataFrame) -> go.Figure:
        """
        군집별 고객 수 분포 파이 차트
        
        Args:
            cluster_summary: 군집 요약 데이터
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = px.pie(
            cluster_summary,
            values='고객 수',
            names='cluster_name',
            title='고객 세그먼트별 분포',
            color_discrete_sequence=self.color_scheme,
            hole=0.4  # 도넛 차트
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>고객 수: %{value}<br>비율: %{percent}<extra></extra>'
        )
        
        return fig
    
    def plot_rfm_heatmap(self, cluster_summary: pd.DataFrame) -> go.Figure:
        """
        군집별 RFM 히트맵
        
        Args:
            cluster_summary: 군집 요약 데이터
        
        Returns:
            plotly.graph_objects.Figure
        """
        # 정규화를 위한 데이터 준비
        heatmap_data = cluster_summary[['cluster_name', 'Recency_평균', 'Frequency_평균', 'Monetary_평균']].copy()
        
        # 0-1 스케일링 (Recency는 역순)
        # ZeroDivisionError 방지
        r_range = heatmap_data['Recency_평균'].max() - heatmap_data['Recency_평균'].min()
        f_range = heatmap_data['Frequency_평균'].max() - heatmap_data['Frequency_평균'].min()
        m_range = heatmap_data['Monetary_평균'].max() - heatmap_data['Monetary_평균'].min()

        if r_range > 0:
            heatmap_data['Recency_평균'] = 1 - (heatmap_data['Recency_평균'] - heatmap_data['Recency_평균'].min()) / r_range
        else:
            heatmap_data['Recency_평균'] = 0.5

        if f_range > 0:
            heatmap_data['Frequency_평균'] = (heatmap_data['Frequency_평균'] - heatmap_data['Frequency_평균'].min()) / f_range
        else:
            heatmap_data['Frequency_평균'] = 0.5

        if m_range > 0:
            heatmap_data['Monetary_평균'] = (heatmap_data['Monetary_평균'] - heatmap_data['Monetary_평균'].min()) / m_range
        else:
            heatmap_data['Monetary_평균'] = 0.5
        
        # 히트맵 생성
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data[['Recency_평균', 'Frequency_평균', 'Monetary_평균']].values,
            x=['Recency<br>(최근성)', 'Frequency<br>(빈도)', 'Monetary<br>(금액)'],
            y=heatmap_data['cluster_name'],
            colorscale='RdYlGn',
            text=heatmap_data[['Recency_평균', 'Frequency_평균', 'Monetary_평균']].values.round(2),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="점수")
        ))
        
        fig.update_layout(
            title='군집별 RFM 프로파일 (정규화)',
            xaxis_title='RFM 지표',
            yaxis_title='고객 세그먼트',
            height=400
        )

        return fig

    def plot_customer_value_pyramid(self, cluster_summary: pd.DataFrame) -> go.Figure:
        """
        고객 가치 피라미드 차트

        Args:
            cluster_summary: 군집 요약 데이터

        Returns:
            plotly.graph_objects.Figure
        """
        # 매출 기여도 기준으로 정렬 (내림차순)
        pyramid_data = cluster_summary.copy()
        pyramid_data = pyramid_data.sort_values('Monetary_총합', ascending=False)

        # 누적 비율 계산
        total_revenue = pyramid_data['Monetary_총합'].sum()
        total_customers = pyramid_data['고객 수'].sum()
        pyramid_data['매출_비율'] = (pyramid_data['Monetary_총합'] / total_revenue * 100).round(1)
        pyramid_data['고객_누적비율'] = (pyramid_data['고객 수'].cumsum() / total_customers * 100).round(1)

        # 피라미드 단계 정의
        pyramid_data['단계'] = range(len(pyramid_data), 0, -1)

        # Funnel 차트 생성
        fig = go.Figure()

        # 배경색 설정 (상위일수록 진한 색)
        colors = ['#FFD700', '#FFA500', '#FF6B6B', '#4ECDC4', '#95E1D3'][:len(pyramid_data)]

        for idx, row in pyramid_data.iterrows():
            fig.add_trace(go.Funnel(
                name=row['cluster_name'],
                y=[row['cluster_name']],
                x=[row['Monetary_총합']],
                textinfo="label+value+percent total",
                texttemplate="<b>%{label}</b><br>매출: ₩%{value:,.0f}<br>비율: %{percentTotal:.1%}<br>고객 수: " + str(int(row['고객 수'])) + "명",
                marker=dict(
                    color=colors[pyramid_data.index.get_loc(idx)],
                    line=dict(width=2, color='white')
                ),
                connector=dict(line=dict(width=2, color='lightgray'))
            ))

        fig.update_layout(
            title={
                'text': '💎 고객 가치 피라미드<br><sub>상위 고객일수록 높은 매출 기여도</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=600,
            showlegend=False,
            margin=dict(l=150, r=150)
        )

        return fig

    def plot_elbow_curve(self, metrics: Dict) -> go.Figure:
        """
        Elbow Method 그래프
        
        Args:
            metrics: find_optimal_clusters에서 반환된 메트릭
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('SSE (Elbow Method)', 'Silhouette Score')
        )
        
        # SSE
        fig.add_trace(
            go.Scatter(
                x=metrics['k_range'],
                y=metrics['inertias'],
                mode='lines+markers',
                name='SSE',
                line=dict(color='blue', width=2),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Silhouette Score
        fig.add_trace(
            go.Scatter(
                x=metrics['k_range'],
                y=metrics['silhouette_scores'],
                mode='lines+markers',
                name='Silhouette',
                line=dict(color='green', width=2),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # 최적 K 표시
        optimal_k = metrics['optimal_k']
        optimal_idx = metrics['k_range'].index(optimal_k)
        
        fig.add_trace(
            go.Scatter(
                x=[optimal_k],
                y=[metrics['silhouette_scores'][optimal_idx]],
                mode='markers',
                marker=dict(color='red', size=15, symbol='star'),
                name=f'최적 K={optimal_k}',
                showlegend=True
            ),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="군집 수 (K)", row=1, col=1)
        fig.update_xaxes(title_text="군집 수 (K)", row=1, col=2)
        fig.update_yaxes(title_text="SSE", row=1, col=1)
        fig.update_yaxes(title_text="Silhouette Score", row=1, col=2)
        
        fig.update_layout(
            title_text="최적 군집 수 결정",
            height=400,
            showlegend=True
        )
        
        return fig
    
    # ===== 텍스트 분석 시각화 =====
    
    def plot_sentiment_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        감성 분포 차트 (파이 + 바 차트)
        
        Args:
            df: sentiment 컬럼이 있는 데이터프레임
        
        Returns:
            plotly.graph_objects.Figure
        """
        sentiment_counts = df['sentiment'].value_counts()
        
        # 색상 매핑
        colors = {
            'positive': '#43e97b',
            'neutral': '#4facfe',
            'negative': '#f5576c'
        }
        
        sentiment_colors = [colors.get(s, '#999') for s in sentiment_counts.index]
        
        # 한글 레이블
        labels_kr = {
            'positive': '긍정',
            'neutral': '중립',
            'negative': '부정'
        }
        labels = [labels_kr.get(s, s) for s in sentiment_counts.index]
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'bar'}]],
            subplot_titles=('감성 분포 비율', '감성별 리뷰 개수'),
            horizontal_spacing=0.1
        )
        
        # 파이 차트
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=sentiment_counts.values,
                marker=dict(colors=sentiment_colors),
                hole=0.4,
                textinfo='percent+label',
                textfont=dict(size=14),  # 글자 크기 증가
                hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 바 차트
        fig.add_trace(
            go.Bar(
                x=labels,
                y=sentiment_counts.values,
                marker=dict(color=sentiment_colors),
                text=sentiment_counts.values,
                textposition='auto',
                textfont=dict(size=14),  # 글자 크기 증가
                hovertemplate='<b>%{x}</b><br>개수: %{y}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="감성 분석 결과",
            showlegend=False,
            height=550,  # 높이 증가
            font=dict(size=13)  # 전체 폰트 크기 증가
        )
        
        # X축 글자 크기
        fig.update_xaxes(tickfont=dict(size=13), row=1, col=2)
        fig.update_yaxes(tickfont=dict(size=13), row=1, col=2)
        
        return fig
    
    def plot_sentiment_score_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        감성 점수 히스토그램
        
        Args:
            df: sentiment_score 컬럼이 있는 데이터프레임
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df['sentiment_score'],
            nbinsx=20,
            marker=dict(
                color=df['sentiment_score'],
                colorscale='RdYlGn',
                line=dict(color='white', width=1)
            ),
            hovertemplate='점수 범위: %{x}<br>개수: %{y}<extra></extra>'
        ))
        
        # 평균선 추가
        mean_score = df['sentiment_score'].mean()
        fig.add_vline(
            x=mean_score,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"평균: {mean_score:.2f}",
            annotation_position="top",
            annotation_font=dict(size=13)
        )
        
        fig.update_layout(
            title='감성 점수 분포',
            xaxis_title='감성 점수 (0: 부정 ~ 1: 긍정)',
            yaxis_title='리뷰 개수',
            showlegend=False,
            height=450,  # 높이 증가
            font=dict(size=13),
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12))
        )
        
        return fig
    
    def plot_keyword_bar_chart(self, keywords: dict, sentiment: str = None) -> go.Figure:
        """
        키워드 바 차트
        
        Args:
            keywords: extract_keywords 결과
            sentiment: 특정 감성 선택 (None이면 전체)
        
        Returns:
            plotly.graph_objects.Figure
        """
        if sentiment and sentiment in keywords:
            data = keywords[sentiment]
            title = f'{sentiment.upper()} 주요 키워드'
        elif 'all' in keywords:
            data = keywords['all']
            title = '전체 주요 키워드'
        else:
            # 첫 번째 키 사용
            key = list(keywords.keys())[0]
            data = keywords[key]
            title = f'{key.upper()} 주요 키워드'
        
        if not data or len(data) == 0:
            # 빈 차트
            fig = go.Figure()
            fig.add_annotation(
                text="키워드 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            fig.update_layout(height=400)
            return fig

        # 데이터 개수에 맞게 슬라이싱
        top_n = min(15, len(data))
        words = [item[0] for item in data[:top_n]]
        scores = [item[1] for item in data[:top_n]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=words[::-1],  # 역순으로 표시 (상위가 위로)
            x=scores[::-1],
            orientation='h',
            marker=dict(
                color=scores[::-1],
                colorscale='Viridis',
                showscale=False
            ),
            text=[f'{s:.3f}' for s in scores[::-1]],
            textposition='auto',
            width=0.7,  # 바 너비 조정
            hovertemplate='<b>%{y}</b><br>TF-IDF: %{x:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='TF-IDF 점수',
            yaxis_title='키워드',
            height=600,  # 높이 증가
            showlegend=False,
            yaxis=dict(
                tickfont=dict(size=13),  # Y축 글자 크기 증가
                automargin=True
            ),
            margin=dict(l=150)  # 왼쪽 여백 증가
        )
        
        return fig
    
    def plot_keywords_comparison(self, keywords: dict) -> go.Figure:
        """
        감성별 키워드 비교 (긍정 vs 부정)
        
        Args:
            keywords: 감성별 키워드 딕셔너리
        
        Returns:
            plotly.graph_objects.Figure
        """
        if 'positive' not in keywords or 'negative' not in keywords:
            fig = go.Figure()
            fig.add_annotation(
                text="감성별 키워드 데이터가 부족합니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=400)
            return fig

        # 데이터가 비어있거나 10개 미만일 수 있음
        pos_data = keywords['positive']
        neg_data = keywords['negative']

        if len(pos_data) == 0 or len(neg_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="키워드 데이터가 비어있습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=400)
            return fig

        pos_top_n = min(10, len(pos_data))
        neg_top_n = min(10, len(neg_data))

        pos_words = [item[0] for item in pos_data[:pos_top_n]]
        pos_scores = [item[1] for item in pos_data[:pos_top_n]]

        neg_words = [item[0] for item in neg_data[:neg_top_n]]
        neg_scores = [item[1] for item in neg_data[:neg_top_n]]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('긍정 키워드', '부정 키워드'),
            horizontal_spacing=0.15
        )
        
        # 긍정 키워드
        fig.add_trace(
            go.Bar(
                y=pos_words[::-1],
                x=pos_scores[::-1],
                orientation='h',
                marker=dict(color='#43e97b'),
                name='긍정',
                width=0.6,  # 바 너비 조정 (기본값보다 얇게)
                hovertemplate='<b>%{y}</b><br>점수: %{x:.4f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 부정 키워드
        fig.add_trace(
            go.Bar(
                y=neg_words[::-1],
                x=neg_scores[::-1],
                orientation='h',
                marker=dict(color='#f5576c'),
                name='부정',
                width=0.6,  # 바 너비 조정 (기본값보다 얇게)
                hovertemplate='<b>%{y}</b><br>점수: %{x:.4f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="긍정 vs 부정 주요 키워드 비교",
            showlegend=False,
            height=600,  # 높이 증가
            bargap=0.3  # 바 사이 간격
        )
        
        # Y축 글자 크기 증가
        fig.update_yaxes(tickfont=dict(size=12))
        
        return fig
    
    def plot_topic_words(self, topics: dict) -> go.Figure:
        """
        토픽별 주요 단어 히트맵
        
        Args:
            topics: extract_topics 결과
        
        Returns:
            plotly.graph_objects.Figure
        """
        if not topics:
            fig = go.Figure()
            fig.add_annotation(
                text="토픽 데이터가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # 토픽별 단어를 행렬로 변환
        topic_names = list(topics.keys())
        max_words = max(len(words) for words in topics.values())
        
        # 각 토픽을 텍스트로 표시
        fig = go.Figure()
        
        for i, (topic_name, words) in enumerate(topics.items()):
            fig.add_trace(go.Bar(
                name=topic_name,
                x=words[:8],  # 상위 8개 단어
                y=[1] * len(words[:8]),
                text=words[:8],
                textposition='inside',
                textfont=dict(size=13),  # 글자 크기 증가
                hovertemplate='<b>%{text}</b><extra></extra>',
                marker=dict(color=self.color_scheme[i % len(self.color_scheme)])
            ))
        
        fig.update_layout(
            title='토픽별 주요 단어',
            xaxis_title='단어',
            yaxis_title='',
            yaxis=dict(visible=False),
            height=450,  # 높이 증가
            barmode='stack',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)  # 범례 글자 크기
            ),
            xaxis=dict(
                tickfont=dict(size=13),  # X축 글자 크기 증가
                tickangle=-45,
                automargin=True
            ),
            font=dict(size=12),
            margin=dict(b=100)  # 하단 여백
        )
        
        return fig
    
    def plot_word_cloud_data(self, word_freq: list, top_n: int = 50) -> go.Figure:
        """
        워드 클라우드 데이터를 바 차트로 시각화 (실제 워드클라우드는 별도 라이브러리 필요)
        
        Args:
            word_freq: (단어, 빈도수) 튜플 리스트
            top_n: 표시할 단어 개수
        
        Returns:
            plotly.graph_objects.Figure
        """
        data = word_freq[:top_n]
        words = [item[0] for item in data[:20]]  # 상위 20개만 차트로
        freqs = [item[1] for item in data[:20]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=words,
            y=freqs,
            marker=dict(
                color=freqs,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="빈도")
            ),
            text=freqs,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>빈도: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'상위 {len(words)}개 단어 빈도',
            xaxis_title='단어',
            yaxis_title='빈도수',
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=14),  # 글자 크기 증가
                automargin=True  # 자동 여백 조정
            ),
            height=600,  # 높이 증가 (500 → 600)
            margin=dict(b=150),  # 하단 여백 증가
            showlegend=False
        )
        
        return fig
    
    def plot_histogram(self, df: pd.DataFrame, column: str, bins: int = 30) -> go.Figure:
        """
        히스토그램
        
        Args:
            df: 데이터프레임
            column: 컬럼명
            bins: 구간 수
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = px.histogram(
            df,
            x=column,
            nbins=bins,
            title=f'{column} 분포',
            labels={column: column},
            color_discrete_sequence=['steelblue']
        )
        
        fig.update_layout(
            xaxis_title=column,
            yaxis_title='빈도',
            showlegend=False
        )
        
        return fig
    
    def plot_boxplot(self, df: pd.DataFrame, columns: List[str]) -> go.Figure:
        """
        박스플롯 (여러 컬럼)
        
        Args:
            df: 데이터프레임
            columns: 컬럼 리스트
        
        Returns:
            plotly.graph_objects.Figure
        """
        fig = go.Figure()
        
        for col in columns:
            fig.add_trace(go.Box(
                y=df[col],
                name=col,
                boxmean='sd'  # 평균과 표준편차 표시
            ))
        
        fig.update_layout(
            title='데이터 분포 (박스플롯)',
            yaxis_title='값',
            showlegend=True
        )
        
        return fig
    
    def plot_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """
        상관관계 히트맵
        
        Args:
            df: 데이터프레임
        
        Returns:
            plotly.graph_objects.Figure
        """
        # 숫자형 컬럼만 선택
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="상관계수")
        ))
        
        fig.update_layout(
            title='변수 간 상관관계',
            xaxis_title='',
            yaxis_title='',
            height=600
        )
        
        return fig

    # ===== DAY 30: 판매 분석 시각화 =====

    def plot_sales_trend(self, df: pd.DataFrame,
                         date_column: str = 'date',
                         sales_column: str = 'sales',
                         ma_columns: List[str] = None,
                         title: str = '매출 트렌드 분석',
                         currency: str = '원') -> go.Figure:
        """
        매출 트렌드 라인 차트 (실제 매출 + 이동평균선) (Critical Fix)

        Args:
            df: 집계된 데이터프레임 (aggregate_by_period 결과)
            date_column: 날짜 컬럼명
            sales_column: 매출 컬럼명
            ma_columns: 이동평균 컬럼명 리스트 (예: ['sales_ma_7', 'sales_ma_30'])
            title: 차트 제목
            currency: 통화 기호 (기본: '원')

        Returns:
            plotly.graph_objects.Figure

        Raises:
            ValueError: 입력 검증 실패 시
        """
        # ========== Critical Fix #1: 입력 검증 ==========
        if df is None or df.empty:
            raise ValueError("데이터프레임이 비어있습니다.")

        if len(df) < 2:
            raise ValueError(f"트렌드 분석을 위해 최소 2개 이상의 데이터 포인트가 필요합니다. 현재: {len(df)}개")

        # 필수 컬럼 검증
        required_cols = [date_column, sales_column]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼 누락: {missing_cols}. 사용 가능한 컬럼: {list(df.columns)}")

        # ma_columns 검증
        if ma_columns:
            missing_ma_cols = [col for col in ma_columns if col not in df.columns]
            if missing_ma_cols:
                raise ValueError(f"이동평균 컬럼 누락: {missing_ma_cols}. 사용 가능한 컬럼: {list(df.columns)}")

        fig = go.Figure()

        # 실제 매출 (막대 차트) - Critical Fix #7: 통화 파라미터화
        fig.add_trace(go.Bar(
            x=df[date_column],
            y=df[sales_column],
            name='실제 매출',
            marker_color='lightblue',
            opacity=0.6,
            hovertemplate=f'%{{x|%Y-%m-%d}}<br>매출: %{{y:,.0f}}{currency}<extra></extra>'
        ))

        # ========== Critical Fix #2, #5: 색상 동적 생성 + MA 파싱 개선 ==========
        if ma_columns:
            # 색맹 친화적 색상 (빨강-녹색 대신 파랑-주황)
            base_colors = ['#d62728', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']

            for i, ma_col in enumerate(ma_columns):
                # 이동평균 윈도우 추출 (정규식 사용)
                import re
                match = re.search(r'_(\d+)$', ma_col)
                if match:
                    window = match.group(1)
                    label = f'이동평균 ({window}기간)'
                else:
                    # 패턴 불일치 시 컬럼명 그대로 사용
                    label = ma_col

                color = base_colors[i % len(base_colors)]

                fig.add_trace(go.Scatter(
                    x=df[date_column],
                    y=df[ma_col],
                    name=label,
                    line=dict(color=color, width=2),
                    mode='lines',
                    hovertemplate=f'%{{x|%Y-%m-%d}}<br>MA: %{{y:,.0f}}{currency}<extra></extra>'
                ))

        fig.update_layout(
            title=title,
            xaxis_title='날짜',
            yaxis_title=f'매출 ({currency})',
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def plot_top_products_bar(self, df: pd.DataFrame,
                              product_column: str = 'product',
                              sales_column: str = 'sales',
                              top_n: int = 20,
                              title: str = None,
                              currency: str = '원',
                              max_height: int = 1200) -> go.Figure:
        """
        상품 순위 막대 차트 (가로형, TOP N) (Critical Fix)

        Args:
            df: get_top_products() 결과 데이터프레임 (정렬 필수)
            product_column: 상품명 컬럼
            sales_column: 매출 컬럼
            top_n: 표시할 상품 개수
            title: 차트 제목 (None이면 자동 생성)
            currency: 통화 기호 (기본: '원')
            max_height: 최대 높이 제한 (기본: 1200px)

        Returns:
            plotly.graph_objects.Figure

        Raises:
            ValueError: 입력 검증 실패 시
        """
        # ========== Critical Fix #1: 입력 검증 ==========
        if df is None or df.empty:
            raise ValueError("데이터프레임이 비어있습니다.")

        # 필수 컬럼 검증
        required_cols = [product_column, sales_column]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼 누락: {missing_cols}. 사용 가능한 컬럼: {list(df.columns)}")

        # 상위 N개만 추출
        actual_top_n = min(top_n, len(df))
        df_top = df.head(actual_top_n).copy()

        if len(df_top) == 0:
            raise ValueError("표시할 데이터가 없습니다.")

        # ========== Critical Fix #10: 제목 자동 생성 ==========
        if title is None:
            title = f'상품별 매출 순위 TOP {actual_top_n}'

        # 역순으로 정렬 (가로 막대 차트는 아래에서 위로 표시)
        df_top = df_top.iloc[::-1]

        # ========== Critical Fix #3: 색상 범위 체크 + 안전한 색상 생성 ==========
        # HSL 색상 공간 사용 (더 안전하고 접근성 좋음)
        def generate_safe_color(index: int, total: int) -> str:
            """안전한 색상 생성 (음수 방지)"""
            # Hue: 0 (빨강) -> 30 (주황) 그라데이션
            hue = 10 + (index / max(total - 1, 1)) * 20
            saturation = 70  # 채도
            lightness = 40 + (index / max(total - 1, 1)) * 20  # 밝기 (상위일수록 어두움)
            return f'hsl({hue:.0f}, {saturation}%, {lightness}%)'

        colors = [generate_safe_color(i, len(df_top)) for i in range(len(df_top))]

        # ========== Critical Fix #9: 벡터화로 성능 개선 ==========
        text_labels = [f'{x:,.0f}{currency}' for x in df_top[sales_column]]

        fig = go.Figure(go.Bar(
            x=df_top[sales_column],
            y=df_top[product_column],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            ),
            text=text_labels,
            textposition='outside',
            hovertemplate=f'<b>%{{y}}</b><br>매출: %{{x:,.0f}}{currency}<extra></extra>'
        ))

        # ========== Critical Fix #4: 최대 높이 제한 ==========
        calculated_height = len(df_top) * 25
        final_height = max(400, min(calculated_height, max_height))

        # ========== Critical Fix #11: 동적 마진 계산 ==========
        max_product_name_length = df_top[product_column].astype(str).str.len().max()
        left_margin = min(150 + max_product_name_length * 3, 300)  # 최대 300px

        fig.update_layout(
            title=title,
            xaxis_title=f'매출 ({currency})',
            yaxis_title='',
            height=final_height,
            margin=dict(l=left_margin),
            showlegend=False
        )

        return fig

    def plot_pareto_chart(self, pareto_df: pd.DataFrame,
                          product_column: str = 'product',
                          sales_column: str = 'sales',
                          cumulative_pct_column: str = 'cumulative_pct',
                          top_n: int = 30,
                          threshold: float = 80.0,
                          title: str = '파레토 분석 (80-20 법칙)',
                          currency: str = '원') -> go.Figure:
        """
        파레토 차트 (듀얼 축: 매출 막대 + 누적 비율 선) (Critical Fix)

        Args:
            pareto_df: analyze_pareto() 결과 데이터프레임
            product_column: 상품명 컬럼
            sales_column: 매출 컬럼
            cumulative_pct_column: 누적 비율(%) 컬럼
            top_n: 표시할 상품 개수
            threshold: 파레토 기준선 (기본 80%)
            title: 차트 제목
            currency: 통화 기호 (기본: '원')

        Returns:
            plotly.graph_objects.Figure (듀얼 축)

        Raises:
            ValueError: 입력 검증 실패 시
        """
        # ========== Critical Fix #1: 입력 검증 ==========
        if pareto_df is None or pareto_df.empty:
            raise ValueError("데이터프레임이 비어있습니다.")

        # 필수 컬럼 검증
        required_cols = [product_column, sales_column, cumulative_pct_column]
        missing_cols = [col for col in required_cols if col not in pareto_df.columns]
        if missing_cols:
            raise ValueError(
                f"필수 컬럼 누락: {missing_cols}. "
                f"사용 가능한 컬럼: {list(pareto_df.columns)}"
            )

        # ========== Critical Fix #13: 엣지 케이스 체크 ==========
        if len(pareto_df) == 1:
            raise ValueError("파레토 분석은 최소 2개 이상의 상품이 필요합니다.")

        # 상위 N개만 표시
        actual_top_n = min(top_n, len(pareto_df))
        df_plot = pareto_df.head(actual_top_n).copy()

        # 듀얼 축 차트 생성
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 1차 축: 매출 막대 차트 (Critical Fix #7: 통화 파라미터화)
        fig.add_trace(
            go.Bar(
                x=df_plot[product_column],
                y=df_plot[sales_column],
                name='매출',
                marker_color='steelblue',
                hovertemplate=f'<b>%{{x}}</b><br>매출: %{{y:,.0f}}{currency}<extra></extra>'
            ),
            secondary_y=False
        )

        # 2차 축: 누적 비율 선 차트 (Critical Fix #12: 색맹 친화적 색상)
        fig.add_trace(
            go.Scatter(
                x=df_plot[product_column],
                y=df_plot[cumulative_pct_column],
                name='누적 비율',
                line=dict(color='#d62728', width=3),  # 빨강 대신 주황-빨강
                mode='lines+markers',
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>누적: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )

        # ========== Critical Fix #6: Y축 범위 동적 계산 ==========
        # 최대 누적 비율 + 5% 여유
        max_cumulative = df_plot[cumulative_pct_column].max()
        y_range_max = min(max_cumulative * 1.05, 100)  # 100% 초과 방지

        # 80% 기준선 (파레토 법칙)
        if threshold <= y_range_max:  # 기준선이 범위 내에 있을 때만 표시
            fig.add_hline(
                y=threshold,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"{threshold}% 기준선",
                annotation_position="right",
                secondary_y=True
            )

        # 레이아웃 설정
        fig.update_xaxes(
            title_text="상품",
            tickangle=-45
        )
        fig.update_yaxes(
            title_text=f"매출 ({currency})",
            secondary_y=False
        )
        fig.update_yaxes(
            title_text="누적 비율 (%)",
            range=[0, y_range_max],  # 동적 범위
            secondary_y=True
        )

        fig.update_layout(
            title=title,
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig


if __name__ == "__main__":
    # 테스트 코드
    print("Visualizer 모듈 테스트")
    
    # 샘플 데이터 생성
    sample_cluster_summary = pd.DataFrame({
        'cluster': [0, 1, 2, 3],
        'cluster_name': ['💎 VIP 고객', '⭐ 충성 고객', '🌱 신규 고객', '💤 휴면 고객'],
        '고객 수': [50, 100, 150, 70],
        'Recency_평균': [5, 10, 3, 60],
        'Frequency_평균': [20, 15, 3, 5],
        'Monetary_평균': [5000, 3000, 500, 2000]
    })
    
    visualizer = Visualizer()
    
    print("\n파이 차트 생성 중...")
    fig_pie = visualizer.plot_cluster_distribution_pie(sample_cluster_summary)
    # fig_pie.show()  # 주석 처리 (테스트 환경에서는 표시 안 됨)
    
    print("OK 시각화 모듈 테스트 완료")
