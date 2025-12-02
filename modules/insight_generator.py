"""
Insight Generator Module
분석 결과로부터 비즈니스 인사이트 자동 생성
"""

import pandas as pd
from typing import List, Dict


class InsightGenerator:
    """자동 인사이트 및 액션 아이템 생성"""
    
    @staticmethod
    def generate_rfm_insights(rfm_df: pd.DataFrame, cluster_summary: pd.DataFrame) -> Dict[str, List[str]]:
        """
        RFM 분석 결과로부터 인사이트 생성
        
        Args:
            rfm_df: RFM 데이터프레임
            cluster_summary: 군집 요약 데이터
        
        Returns:
            dict: {'key_findings': [...], 'action_items': [...]}
        """
        key_findings = []
        action_items = []
        
        total_customers = len(rfm_df)
        
        # 1. 군집별 비율 분석
        for _, row in cluster_summary.iterrows():
            cluster_name = row['cluster_name']
            customer_count = row['고객 수']
            customer_pct = row['고객 비율(%)']
            
            if customer_pct > 30:
                key_findings.append(
                    f"📊 전체 고객의 {customer_pct:.1f}% ({customer_count}명)가 '{cluster_name}' 그룹에 속합니다."
                )
        
        # 2. VIP/충성 고객 분석
        vip_clusters = cluster_summary[cluster_summary['cluster_name'].str.contains('VIP|충성')]
        if not vip_clusters.empty:
            vip_total = vip_clusters['고객 수'].sum()
            vip_revenue = vip_clusters['Monetary_총합'].sum()
            total_revenue = cluster_summary['Monetary_총합'].sum()
            vip_revenue_pct = (vip_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            key_findings.append(
                f"💎 VIP/충성 고객 {vip_total}명이 전체 매출의 {vip_revenue_pct:.1f}%를 차지하고 있습니다."
            )
            
            action_items.append(
                f"💡 VIP/충성 고객에게 프리미엄 멤버십 혜택을 제공하여 로열티를 강화하세요."
            )
        
        # 3. 이탈 위험 고객 분석
        churn_clusters = cluster_summary[cluster_summary['cluster_name'].str.contains('이탈|휴면')]
        if not churn_clusters.empty:
            churn_total = churn_clusters['고객 수'].sum()
            churn_pct = (churn_total / total_customers * 100)
            
            if churn_pct > 20:
                key_findings.append(
                    f"⚠️  이탈 위험/휴면 고객이 {churn_total}명 ({churn_pct:.1f}%)으로 주의가 필요합니다."
                )
                
                action_items.append(
                    f"🎯 이탈 위험 고객에게 재참여 캠페인(할인 쿠폰, 개인화 이메일)을 실행하세요."
                )
        
        # 4. 신규 고객 분석
        new_clusters = cluster_summary[cluster_summary['cluster_name'].str.contains('신규')]
        if not new_clusters.empty:
            new_total = new_clusters['고객 수'].sum()
            new_pct = (new_total / total_customers * 100)
            
            key_findings.append(
                f"🌱 신규 고객이 {new_total}명 ({new_pct:.1f}%)으로, 온보딩이 중요한 시점입니다."
            )
            
            action_items.append(
                f"📧 신규 고객에게 환영 메시지와 첫 구매 인센티브를 제공하여 재구매를 유도하세요."
            )
        
        # 5. Recency 분석
        avg_recency = rfm_df['Recency'].mean()
        if avg_recency > 90:
            key_findings.append(
                f"📉 평균 최근 구매일이 {avg_recency:.0f}일 전으로, 전반적인 활성도가 낮습니다."
            )
            action_items.append(
                f"🚀 전체 고객 대상 리마케팅 캠페인을 통해 브랜드 인지도를 높이세요."
            )
        
        # 6. Frequency 분석
        avg_frequency = rfm_df['Frequency'].mean()
        if avg_frequency < 3:
            key_findings.append(
                f"🔄 평균 구매 빈도가 {avg_frequency:.1f}회로 낮습니다. 재구매율 향상이 필요합니다."
            )
            action_items.append(
                f"💳 구독 서비스 또는 로열티 프로그램 도입을 고려하세요."
            )
        
        # 7. Monetary 분석
        total_revenue = rfm_df['Monetary'].sum()
        avg_monetary = rfm_df['Monetary'].mean()
        
        key_findings.append(
            f"💰 총 매출액은 {total_revenue:,.0f}원이며, 고객 평균 구매액은 {avg_monetary:,.0f}원입니다."
        )
        
        # 상위 20% 고객의 매출 기여도
        top_20_pct_threshold = rfm_df['Monetary'].quantile(0.8)
        top_20_pct_customers = rfm_df[rfm_df['Monetary'] >= top_20_pct_threshold]
        top_20_pct_revenue = top_20_pct_customers['Monetary'].sum()
        top_20_pct_contribution = (top_20_pct_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        if top_20_pct_contribution > 60:
            key_findings.append(
                f"📈 상위 20% 고객이 전체 매출의 {top_20_pct_contribution:.1f}%를 차지합니다 (파레토 법칙)."
            )
            action_items.append(
                f"🎁 상위 고객 맞춤형 보상 프로그램을 강화하여 이탈을 방지하세요."
            )
        
        return {
            'key_findings': key_findings,
            'action_items': action_items
        }
    
    @staticmethod
    def generate_text_analysis_insights(df: pd.DataFrame, 
                                        sentiment_summary: Dict,
                                        keywords: Dict) -> Dict[str, List[str]]:
        """
        텍스트(리뷰) 분석 결과로부터 인사이트 생성
        
        Args:
            df: 리뷰 데이터프레임 (sentiment 컬럼 포함)
            sentiment_summary: 감성 분석 요약 통계
            keywords: 키워드 딕셔너리
        
        Returns:
            dict: {'key_findings': [...], 'action_items': [...]}
        """
        key_findings = []
        action_items = []
        
        total = sentiment_summary.get('total_reviews', 0)
        pos_ratio = sentiment_summary.get('positive_ratio', 0)
        neg_ratio = sentiment_summary.get('negative_ratio', 0)
        neu_ratio = sentiment_summary.get('neutral_ratio', 0)
        
        # 1. 전체 감성 평가
        if pos_ratio > 60:
            key_findings.append(
                f"😊 긍정적인 반응이 {pos_ratio:.1f}%로 매우 높습니다. 전반적으로 만족도가 높습니다."
            )
            action_items.append(
                f"✅ 현재의 강점을 유지하면서 긍정 요소를 마케팅에 적극 활용하세요."
            )
        elif pos_ratio < 30:
            key_findings.append(
                f"😟 긍정 반응이 {pos_ratio:.1f}%에 불과합니다. 개선이 시급합니다."
            )
            action_items.append(
                f"🚨 고객 불만사항을 즉시 파악하고 개선 계획을 수립하세요."
            )
        else:
            key_findings.append(
                f"😐 긍정 반응이 {pos_ratio:.1f}%로 보통 수준입니다."
            )
        
        # 2. 부정 리뷰 분석
        if neg_ratio > 30:
            key_findings.append(
                f"⚠️  부정 리뷰가 {neg_ratio:.1f}%로 높은 편입니다. 주의가 필요합니다."
            )
            
            # 부정 키워드 분석
            if 'negative' in keywords and keywords['negative']:
                top_neg_keywords = [kw[0] for kw in keywords['negative'][:3]]
                key_findings.append(
                    f"🔍 주요 불만 키워드: {', '.join(top_neg_keywords)}"
                )
                action_items.append(
                    f"📋 '{', '.join(top_neg_keywords)}' 관련 이슈를 우선적으로 해결하세요."
                )
        
        # 3. 긍정 요소 강화
        if 'positive' in keywords and keywords['positive']:
            top_pos_keywords = [kw[0] for kw in keywords['positive'][:3]]
            key_findings.append(
                f"💎 고객이 특히 좋아하는 점: {', '.join(top_pos_keywords)}"
            )
            action_items.append(
                f"📢 '{', '.join(top_pos_keywords)}' 같은 강점을 홍보 포인트로 활용하세요."
            )
        
        # 4. 중립 리뷰 분석
        if neu_ratio > 40:
            key_findings.append(
                f"🤔 중립 의견이 {neu_ratio:.1f}%로 많습니다. 명확한 차별점이 부족할 수 있습니다."
            )
            action_items.append(
                f"🎯 중립 고객을 만족 고객으로 전환할 수 있는 차별화 전략이 필요합니다."
            )
        
        # 5. 리뷰 개수 평가
        if total < 50:
            key_findings.append(
                f"📊 리뷰 개수({total}개)가 적어 통계적 신뢰도가 낮을 수 있습니다."
            )
            action_items.append(
                f"💬 더 많은 고객 리뷰를 수집하여 정확한 분석을 진행하세요."
            )
        elif total > 500:
            key_findings.append(
                f"📊 충분한 리뷰({total:,}개)로 신뢰도 높은 분석 결과입니다."
            )
        
        # 6. 감성 점수 추세 (시간별 데이터가 있는 경우)
        if 'date' in df.columns or 'Date' in df.columns:
            try:
                date_col = 'date' if 'date' in df.columns else 'Date'
                df[date_col] = pd.to_datetime(df[date_col])
                df_sorted = df.sort_values(date_col)
                
                # 최근 30% vs 초기 30% 비교
                recent_30 = df_sorted.tail(int(len(df) * 0.3))
                early_30 = df_sorted.head(int(len(df) * 0.3))
                
                recent_pos = (recent_30['sentiment'] == 'positive').sum() / len(recent_30) * 100
                early_pos = (early_30['sentiment'] == 'positive').sum() / len(early_30) * 100
                
                diff = recent_pos - early_pos
                
                if diff > 10:
                    key_findings.append(
                        f"📈 최근 긍정 리뷰가 {diff:.1f}%p 증가했습니다. 개선 효과가 나타나고 있습니다!"
                    )
                elif diff < -10:
                    key_findings.append(
                        f"📉 최근 긍정 리뷰가 {abs(diff):.1f}%p 감소했습니다. 원인 파악이 필요합니다."
                    )
                    action_items.append(
                        f"🔍 최근 변경사항(제품/서비스 개선, 가격 등)을 검토하세요."
                    )
            except:
                pass
        
        # 7. 키워드 다양성 분석
        if 'all' in keywords:
            unique_keywords = len(keywords['all'])
            if unique_keywords < 10:
                key_findings.append(
                    f"💭 언급되는 키워드가 제한적입니다. 다양한 측면의 피드백이 부족할 수 있습니다."
                )
        
        return {
            'key_findings': key_findings,
            'action_items': action_items
        }

    @staticmethod
    def generate_executive_summary(insights: Dict, cluster_summary: pd.DataFrame) -> str:
        """
        경영진용 한 페이지 요약 생성
        
        Args:
            insights: generate_rfm_insights의 결과
            cluster_summary: 군집 요약 데이터
        
        Returns:
            str: 요약 텍스트
        """
        summary = "## 📋 Executive Summary\n\n"
        
        # 핵심 지표
        total_customers = cluster_summary['고객 수'].sum()
        total_revenue = cluster_summary['Monetary_총합'].sum()
        
        summary += f"**분석 대상**: {total_customers:,}명의 고객\n"
        summary += f"**총 매출액**: {total_revenue:,.0f}원\n"
        summary += f"**고객 세그먼트**: {len(cluster_summary)}개 그룹\n\n"
        
        # 주요 발견사항 (상위 3개)
        summary += "### 🔍 주요 발견사항\n"
        for i, finding in enumerate(insights['key_findings'][:3], 1):
            summary += f"{i}. {finding}\n"
        
        summary += "\n### 💡 권장 액션 아이템\n"
        for i, action in enumerate(insights['action_items'][:3], 1):
            summary += f"{i}. {action}\n"
        
        return summary


if __name__ == "__main__":
    # 테스트 코드
    print("InsightGenerator 모듈 테스트")
    
    # 샘플 데이터
    sample_rfm = pd.DataFrame({
        'CustomerID': range(1, 101),
        'Recency': [30] * 50 + [120] * 50,
        'Frequency': [10] * 30 + [2] * 70,
        'Monetary': [10000] * 30 + [1000] * 70,
        'cluster': [0] * 30 + [1] * 20 + [2] * 50,
        'cluster_name': ['💎 VIP 고객'] * 30 + ['⚠️ 이탈 위험 고객'] * 20 + ['🌱 신규 고객'] * 50
    })

    sample_summary = pd.DataFrame({
        'cluster': [0, 1, 2],
        'cluster_name': ['💎 VIP 고객', '⚠️ 이탈 위험 고객', '🌱 신규 고객'],
        '고객 수': [30, 20, 50],
        '고객 비율(%)': [30.0, 20.0, 50.0],
        'Recency_평균': [30, 120, 25],
        'Frequency_평균': [10, 2, 2],
        'Monetary_평균': [10000, 1000, 1000],
        'Monetary_총합': [300000, 20000, 50000]
    })
    
    generator = InsightGenerator()
    insights = generator.generate_rfm_insights(sample_rfm, sample_summary)
    
    print("\n=== 주요 발견사항 ===")
    for finding in insights['key_findings']:
        print(finding)
    
    print("\n=== 액션 아이템 ===")
    for action in insights['action_items']:
        print(action)
    
    print("\n=== Executive Summary ===")
    summary = generator.generate_executive_summary(insights, sample_summary)
    print(summary)
