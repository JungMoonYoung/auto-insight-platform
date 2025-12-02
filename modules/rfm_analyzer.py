"""
RFM Analyzer Module
E-commerce 고객 세분화를 위한 RFM 분석
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from datetime import datetime, timedelta
from typing import Tuple, Dict


class RFMAnalyzer:
    """RFM 분석 및 K-Means 군집화"""
    
    def __init__(self, df: pd.DataFrame, 
                 customer_col: str = 'CustomerID',
                 date_col: str = 'InvoiceDate',
                 amount_col: str = None,
                 quantity_col: str = 'Quantity',
                 price_col: str = 'UnitPrice'):
        """
        Args:
            df: 거래 데이터프레임
            customer_col: 고객 ID 컬럼명
            date_col: 날짜 컬럼명
            amount_col: 금액 컬럼명 (None이면 Quantity * UnitPrice 계산)
            quantity_col: 수량 컬럼명
            price_col: 단가 컬럼명
        """
        self.df = df.copy()
        self.customer_col = customer_col
        self.date_col = date_col
        self.amount_col = amount_col
        self.quantity_col = quantity_col
        self.price_col = price_col
        
        # 날짜 컬럼 변환
        if self.df[date_col].dtype != 'datetime64[ns]':
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col])
            except Exception as e:
                raise ValueError(f"'{date_col}' 컬럼을 날짜 형식으로 변환할 수 없습니다: {str(e)}")
        
        # 금액 컬럼 생성
        if amount_col is None:
            if quantity_col in self.df.columns and price_col in self.df.columns:
                # 기존 totalamount 컬럼이 있으면 경고
                if 'totalamount' in self.df.columns:
                    import warnings
                    warnings.warn("기존 'totalamount' 컬럼이 덮어씌워집니다. 명시적으로 amount_col을 지정하세요.")
                self.df['totalamount'] = self.df[quantity_col] * self.df[price_col]
                self.amount_col = 'totalamount'
            else:
                raise ValueError(f"금액 컬럼이 없으며, {quantity_col}와 {price_col}도 없습니다.")
        
        self.rfm_df = None
        self.clustered_df = None
        self.optimal_k = None
        self.cluster_names = {}
    
    def calculate_rfm(self, reference_date: datetime = None) -> pd.DataFrame:
        """
        RFM 지표 계산
        
        Args:
            reference_date: 기준일 (None이면 최근 날짜 + 1일)
        
        Returns:
            pd.DataFrame: RFM 데이터프레임
        """
        if reference_date is None:
            reference_date = self.df[self.date_col].max() + timedelta(days=1)
        
        # 고객별 RFM 계산
        rfm = self.df.groupby(self.customer_col).agg({
            self.date_col: lambda x: (reference_date - x.max()).days,  # Recency
            self.customer_col: 'count',  # Frequency (거래 건수)
            self.amount_col: 'sum'  # Monetary
        })
        
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        rfm = rfm.reset_index()

        # 이상치 처리 (음수 금액 제거)
        rfm = rfm[rfm['Monetary'] > 0]

        # 빈 데이터셋 검증
        if len(rfm) == 0:
            raise ValueError("유효한 거래 데이터가 없습니다. 모든 Monetary 값이 0 이하입니다.")

        self.rfm_df = rfm
        return rfm
    
    def find_optimal_clusters(self, min_k: int = 3, max_k: int = 8) -> Tuple[int, Dict]:
        """
        Elbow Method와 Silhouette Score로 최적 군집 수 찾기

        Args:
            min_k: 최소 군집 수
            max_k: 최대 군집 수

        Returns:
            (int, dict): (최적 K, 평가 메트릭)
        """
        if self.rfm_df is None:
            raise ValueError("먼저 calculate_rfm()을 실행하세요.")

        # 파라미터 검증
        if min_k > max_k:
            raise ValueError(f"min_k({min_k})는 max_k({max_k})보다 작거나 같아야 합니다.")

        n_samples = len(self.rfm_df)
        if min_k > n_samples:
            raise ValueError(f"최소 군집 수({min_k})가 고객 수({n_samples})보다 많습니다. min_k를 {n_samples} 이하로 설정하세요.")

        if max_k > n_samples:
            import warnings
            warnings.warn(f"최대 군집 수({max_k})가 고객 수({n_samples})보다 많습니다. max_k를 {n_samples}으로 조정합니다.")
            max_k = n_samples

        # RFM 데이터 스케일링
        rfm_scaled = self._scale_rfm()

        # 다양한 K값 시도
        inertias = []
        silhouette_scores = []
        k_range = range(min_k, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(rfm_scaled)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(rfm_scaled, labels))
        
        # Silhouette Score가 가장 높은 K 선택
        optimal_idx = np.argmax(silhouette_scores)
        self.optimal_k = list(k_range)[optimal_idx]
        
        metrics = {
            'k_range': list(k_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'optimal_k': self.optimal_k
        }
        
        return self.optimal_k, metrics
    
    def _scale_rfm(self) -> np.ndarray:
        """RFM 데이터 스케일링 (로그 변환 + 표준화)"""
        rfm_log = self.rfm_df[['Recency', 'Frequency', 'Monetary']].copy()
        
        # 로그 변환 (0 방지를 위해 +1)
        rfm_log['Recency'] = np.log1p(rfm_log['Recency'])
        rfm_log['Frequency'] = np.log1p(rfm_log['Frequency'])
        rfm_log['Monetary'] = np.log1p(rfm_log['Monetary'])
        
        # 표준화
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm_log)
        
        return rfm_scaled
    
    def perform_clustering(self, k: int = None) -> pd.DataFrame:
        """
        K-Means 군집화 수행
        
        Args:
            k: 군집 수 (None이면 optimal_k 사용)
        
        Returns:
            pd.DataFrame: 군집 레이블이 추가된 RFM 데이터
        """
        if self.rfm_df is None:
            raise ValueError("먼저 calculate_rfm()을 실행하세요.")
        
        if k is None:
            if self.optimal_k is None:
                self.find_optimal_clusters()
            k = self.optimal_k
        
        # 스케일링
        rfm_scaled = self._scale_rfm()
        
        # K-Means 실행
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        self.rfm_df['cluster'] = kmeans.fit_predict(rfm_scaled)

        # 군집별 평균 RFM 계산
        cluster_summary = self.rfm_df.groupby('cluster')[['Recency', 'Frequency', 'Monetary']].mean()

        # 군집 이름 자동 부여
        self.cluster_names = self._assign_cluster_names(cluster_summary)
        self.rfm_df['cluster_name'] = self.rfm_df['cluster'].map(self.cluster_names)

        self.clustered_df = self.rfm_df
        return self.rfm_df
    
    def _assign_cluster_names(self, cluster_summary: pd.DataFrame) -> Dict[int, str]:
        """
        군집별 특성에 따라 이름 자동 부여
        
        Args:
            cluster_summary: 군집별 평균 RFM
        
        Returns:
            dict: {군집 번호: 군집 이름}
        """
        names = {}
        
        for cluster_id in cluster_summary.index:
            r = cluster_summary.loc[cluster_id, 'Recency']
            f = cluster_summary.loc[cluster_id, 'Frequency']
            m = cluster_summary.loc[cluster_id, 'Monetary']
            
            # R은 낮을수록 좋음 (최근 구매)
            # F, M은 높을수록 좋음
            r_rank = 'High' if r < cluster_summary['Recency'].median() else 'Low'
            f_rank = 'High' if f > cluster_summary['Frequency'].median() else 'Low'
            m_rank = 'High' if m > cluster_summary['Monetary'].median() else 'Low'
            
            # 이름 결정 로직
            if r_rank == 'High' and f_rank == 'High' and m_rank == 'High':
                name = "💎 VIP 고객"
            elif r_rank == 'High' and (f_rank == 'High' or m_rank == 'High'):
                name = "⭐ 충성 고객"
            elif r_rank == 'Low' and f_rank == 'High' and m_rank == 'High':
                name = "⚠️ 이탈 위험 고객"
            elif r_rank == 'High' and f_rank == 'Low':
                name = "🌱 신규 고객"
            elif r_rank == 'Low' and f_rank == 'Low':
                name = "💤 휴면 고객"
            else:
                name = f"🔍 기타 고객 (Cluster {cluster_id})"
            
            names[cluster_id] = name
        
        return names
    
    def get_cluster_summary(self) -> pd.DataFrame:
        """군집별 통계 요약"""
        if self.clustered_df is None:
            raise ValueError("먼저 perform_clustering()을 실행하세요.")

        summary = self.clustered_df.groupby(['cluster', 'cluster_name']).agg({
            self.customer_col: 'count',
            'Recency': ['mean', 'median'],
            'Frequency': ['mean', 'median'],
            'Monetary': ['mean', 'median', 'sum']
        }).round(2)

        summary.columns = ['고객 수', 'Recency_평균', 'Recency_중앙값',
                          'Frequency_평균', 'Frequency_중앙값',
                          'Monetary_평균', 'Monetary_중앙값', 'Monetary_총합']

        # 고객 비율 추가
        summary['고객 비율(%)'] = (summary['고객 수'] / summary['고객 수'].sum() * 100).round(2)

        return summary.reset_index()
    
    def get_customer_segment(self, customer_id) -> Dict:
        """특정 고객의 세그먼트 정보 조회"""
        if self.clustered_df is None:
            raise ValueError("먼저 perform_clustering()을 실행하세요.")

        customer_data = self.clustered_df[self.clustered_df[self.customer_col] == customer_id]

        if len(customer_data) == 0:
            return None

        row = customer_data.iloc[0]

        return {
            'customer_id': customer_id,
            'cluster': int(row['cluster']),
            'cluster_name': row['cluster_name'],
            'recency': int(row['Recency']),
            'frequency': int(row['Frequency']),
            'monetary': float(row['Monetary'])
        }


if __name__ == "__main__":
    # 테스트 코드
    print("RFMAnalyzer 모듈 테스트")
    
    # 샘플 데이터 생성
    np.random.seed(42)
    n_customers = 100
    n_transactions = 500
    
    sample_df = pd.DataFrame({
        'CustomerID': np.random.randint(1, n_customers + 1, n_transactions),
        'InvoiceDate': pd.date_range('2024-01-01', periods=n_transactions, freq='H'),
        'Quantity': np.random.randint(1, 10, n_transactions),
        'UnitPrice': np.random.uniform(10, 100, n_transactions)
    })
    
    # RFM 분석
    analyzer = RFMAnalyzer(sample_df)
    
    print("\n1. RFM 계산")
    rfm = analyzer.calculate_rfm()
    print(rfm.head())
    
    print("\n2. 최적 군집 수 찾기")
    optimal_k, metrics = analyzer.find_optimal_clusters()
    print(f"최적 군집 수: {optimal_k}")
    print(f"Silhouette Scores: {metrics['silhouette_scores']}")
    
    print("\n3. 군집화 수행")
    clustered = analyzer.perform_clustering()
    print(clustered.head())
    
    print("\n4. 군집 요약")
    summary = analyzer.get_cluster_summary()
    print(summary)
    
    print("\n5. 특정 고객 조회")
    customer_info = analyzer.get_customer_segment(1)
    if customer_info:
        print(f"고객 ID: {customer_info['customer_id']}")
        print(f"세그먼트: {customer_info['cluster_name']}")
        print(f"RFM: R={customer_info['recency']}, F={customer_info['frequency']}, M={customer_info['monetary']:.2f}")
