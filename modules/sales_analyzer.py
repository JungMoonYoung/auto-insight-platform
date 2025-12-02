"""
Sales Analyzer Module
매출 데이터 시계열 분석 및 상품 분석
DAY 29: 기간별 집계, 이동평균, 성장률, 파레토 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SalesAnalyzer:
    """매출 데이터 분석 클래스 (DAY 29 개선: 입력 검증 강화)"""

    def __init__(self, df: pd.DataFrame,
                 date_column: str = 'date',
                 product_column: str = 'product',
                 quantity_column: str = 'quantity',
                 price_column: str = 'price',
                 sales_column: str = 'sales'):
        """
        Args:
            df: 매출 데이터프레임 (거래 단위)
            date_column: 날짜 컬럼명
            product_column: 상품 컬럼명
            quantity_column: 수량 컬럼명
            price_column: 가격 컬럼명
            sales_column: 매출 컬럼명 (없으면 자동 계산)

        Raises:
            ValueError: 입력 데이터 검증 실패 시

        Note:
            입력 데이터는 거래 단위 (1행 = 1건 거래)
            Sales = Quantity × Price로 자동 계산 (sales_column이 없을 경우)
        """
        # ========== 1단계: 입력 검증 (Critical Fix #1) ==========
        self._validate_input(df, date_column, product_column, quantity_column, price_column)

        self.df = df.copy()
        self.date_column = date_column
        self.product_column = product_column
        self.quantity_column = quantity_column
        self.price_column = price_column
        self.sales_column = sales_column

        # ========== 2단계: 매출 컬럼 처리 (Critical Fix #2) ==========
        if sales_column not in self.df.columns:
            # 필수 컬럼 존재 여부 확인
            if quantity_column not in self.df.columns or price_column not in self.df.columns:
                raise ValueError(
                    f"매출 계산 불가: '{sales_column}' 컬럼이 없고, "
                    f"'{quantity_column}' 또는 '{price_column}' 컬럼도 누락되었습니다.\n"
                    f"사용 가능한 컬럼: {list(self.df.columns)}"
                )

            # 매출 계산
            self.df[sales_column] = self.df[quantity_column] * self.df[price_column]
            logger.info(f"매출 컬럼 생성: {sales_column} = {quantity_column} × {price_column}")
        else:
            logger.info(f"기존 매출 컬럼 사용: {sales_column}")

        # ========== 3단계: 날짜 컬럼 변환 (Critical Fix #3) ==========
        original_len = len(self.df)
        self.df[date_column] = pd.to_datetime(self.df[date_column], errors='coerce')

        # 변환 실패 개수 확인
        invalid_dates = self.df[date_column].isna().sum()
        if invalid_dates > 0:
            invalid_ratio = invalid_dates / original_len * 100
            if invalid_ratio > 50:
                raise ValueError(
                    f"날짜 변환 실패: {invalid_dates}행 ({invalid_ratio:.1f}%) - "
                    f"데이터 품질이 너무 낮습니다."
                )
            logger.warning(
                f"날짜 변환 실패: {invalid_dates}행 ({invalid_ratio:.1f}%) 제거됨"
            )
            self.df = self.df.dropna(subset=[date_column])

        self.df = self.df.sort_values(date_column)
        logger.info(f"날짜 변환 완료: {len(self.df)}행 (원본: {original_len}행)")

    def _validate_input(self, df: pd.DataFrame, date_column: str,
                       product_column: str, quantity_column: str,
                       price_column: str) -> None:
        """
        입력 데이터 검증 (Critical Fix #1)

        Args:
            df: 입력 데이터프레임
            date_column, product_column, quantity_column, price_column: 컬럼명

        Raises:
            ValueError: 검증 실패 시
        """
        # 1. 빈 데이터 체크
        if df is None or df.empty:
            raise ValueError("입력 데이터가 비어있습니다. 최소 1행 이상 필요합니다.")

        # 2. 최소 행 수 체크
        if len(df) < 2:
            raise ValueError(f"데이터가 너무 적습니다: {len(df)}행 (최소 2행 필요)")

        # 3. 필수 컬럼 존재 여부 (날짜, 상품은 필수)
        required_columns = [date_column, product_column]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(
                f"필수 컬럼 누락: {missing_columns}\n"
                f"사용 가능한 컬럼: {list(df.columns)}"
            )

        # 4. 날짜 컬럼 기본 검증 (전체가 NULL이면 안 됨)
        if df[date_column].isna().all():
            raise ValueError(f"날짜 컬럼 '{date_column}'이 전부 비어있습니다.")

        # 5. 상품 컬럼 기본 검증
        if df[product_column].isna().all():
            raise ValueError(f"상품 컬럼 '{product_column}'이 전부 비어있습니다.")

        # 6. 수량/가격 컬럼 검증 (둘 다 있으면 음수 체크)
        if quantity_column in df.columns:
            negative_qty = (df[quantity_column] < 0).sum()
            if negative_qty > 0:
                logger.warning(f"음수 수량 발견: {negative_qty}행 (반품 또는 오류 데이터)")

        if price_column in df.columns:
            negative_price = (df[price_column] < 0).sum()
            if negative_price > 0:
                logger.warning(f"음수 가격 발견: {negative_price}행 (할인 또는 오류 데이터)")

        logger.info(f"입력 검증 통과: {len(df)}행, {len(df.columns)}개 컬럼")

    def aggregate_by_period(self, period: str = 'D') -> pd.DataFrame:
        """
        기간별 매출 집계 (Critical Fix #6: 컬럼명 하드코딩 제거)

        Args:
            period: 집계 기간
                'D': 일별 (daily)
                'W': 주별 (weekly)
                'M': 월별 (monthly)
                'Q': 분기별 (quarterly)
                'Y': 연별 (yearly)

        Returns:
            집계된 데이터프레임
            - date: 날짜
            - sales: 매출
            - quantity: 수량
            - transactions: 거래 건수
        """
        logger.info(f"기간별 집계 시작: {period}")

        # 날짜를 인덱스로 설정하고 리샘플링
        df_indexed = self.df.set_index(self.date_column)

        # Critical Fix #6: self.sales_column 사용
        aggregated = df_indexed.resample(period).agg({
            self.sales_column: 'sum',
            self.quantity_column: 'sum',
        }).reset_index()

        # 거래 건수 계산
        transaction_counts = df_indexed.resample(period).size().reset_index(name='transactions')
        aggregated = aggregated.merge(transaction_counts, on=self.date_column, how='left')

        # 컬럼명 정리 (표준화)
        aggregated.columns = ['date', 'sales', 'quantity', 'transactions']

        logger.info(f"집계 완료: {len(aggregated)}개 기간")
        return aggregated

    def calculate_moving_average(self, df: pd.DataFrame,
                                 column: str = 'sales',
                                 windows: List[int] = [7, 30]) -> pd.DataFrame:
        """
        이동평균선 계산

        Args:
            df: 집계된 데이터프레임 (aggregate_by_period 결과)
            column: 이동평균 계산 대상 컬럼
            windows: 이동평균 윈도우 크기 리스트 (일 단위)

        Returns:
            이동평균이 추가된 데이터프레임
            - {column}_ma_{window}: 이동평균 컬럼
        """
        logger.info(f"이동평균 계산: {column}, 윈도우={windows}")

        df_result = df.copy()

        for window in windows:
            ma_col = f'{column}_ma_{window}'
            df_result[ma_col] = df_result[column].rolling(window=window, min_periods=1).mean()
            logger.debug(f"  {ma_col} 계산 완료")

        return df_result

    def calculate_growth_rate(self, df: pd.DataFrame,
                              column: str = 'sales',
                              shift_periods: int = 1) -> pd.DataFrame:
        """
        이전 기간 대비 성장률 계산 (Critical Fix #4, #5)

        Args:
            df: 집계된 데이터프레임
            column: 성장률 계산 대상 컬럼
            shift_periods: 비교 기간 간격
                - 일별 데이터 전주 비교: shift_periods=7
                - 월별 데이터 전월 비교: shift_periods=1
                - 월별 데이터 전년 비교: shift_periods=12

        Returns:
            성장률이 추가된 데이터프레임
            - {column}_growth: 성장률 (%)
            - {column}_growth_abs: 절대 성장량

        Note:
            ZeroDivision 방어: 이전 값이 0이면 성장률 NaN 처리
        """
        logger.info(f"성장률 계산: {column}, shift={shift_periods}기간")

        df_result = df.copy()

        # 데이터 충분성 체크
        if len(df_result) <= shift_periods:
            logger.warning(
                f"데이터가 부족하여 성장률 계산 불가: {len(df_result)}행 "
                f"(최소 {shift_periods + 1}행 필요)"
            )
            df_result[f'{column}_growth'] = np.nan
            df_result[f'{column}_growth_abs'] = np.nan
            return df_result

        # 이전 기간 값
        prev_value = df_result[column].shift(shift_periods)

        # 절대 성장량
        df_result[f'{column}_growth_abs'] = df_result[column] - prev_value

        # ========== Critical Fix #4: ZeroDivision 방어 ==========
        # 성장률 계산 (이전 값이 0이면 NaN)
        with np.errstate(divide='ignore', invalid='ignore'):
            growth = np.where(
                prev_value != 0,
                (df_result[column] - prev_value) / prev_value * 100,
                np.nan  # 이전 값이 0이면 성장률 정의 불가
            )

        df_result[f'{column}_growth'] = np.round(growth, 2)

        # 무한대 제거 (혹시라도 발생한 경우)
        df_result[f'{column}_growth'] = df_result[f'{column}_growth'].replace(
            [np.inf, -np.inf], np.nan
        )

        # 성장률 통계
        valid_growth = df_result[f'{column}_growth'].dropna()
        if len(valid_growth) > 0:
            logger.info(
                f"성장률 계산 완료: 평균 {valid_growth.mean():.2f}%, "
                f"범위 [{valid_growth.min():.2f}% ~ {valid_growth.max():.2f}%]"
            )
        else:
            logger.warning("유효한 성장률 데이터 없음")

        return df_result

    def get_top_products(self, top_n: int = 20,
                        metric: str = 'sales') -> pd.DataFrame:
        """
        상품별 매출 순위 (TOP N) (Critical Fix #6)

        Args:
            top_n: 상위 N개 (자동으로 상품 수에 맞춤)
            metric: 순위 기준 ('sales', 'quantity', 'transactions')

        Returns:
            상위 N개 상품 데이터프레임
            - product: 상품명
            - sales: 총 매출
            - quantity: 총 수량
            - transactions: 거래 건수
            - avg_price: 평균 단가
        """
        logger.info(f"상품 순위 계산: TOP {top_n}, 기준={metric}")

        # 상품별 집계 (Critical Fix #6: self.sales_column 사용)
        product_agg = self.df.groupby(self.product_column).agg({
            self.sales_column: 'sum',
            self.quantity_column: 'sum',
            self.price_column: 'mean'
        }).reset_index()

        # 거래 건수
        transaction_counts = self.df.groupby(self.product_column).size().reset_index(name='transactions')
        product_agg = product_agg.merge(transaction_counts, on=self.product_column, how='left')

        # 컬럼명 정리
        product_agg.columns = ['product', 'sales', 'quantity', 'avg_price', 'transactions']

        # top_n을 실제 상품 수에 맞춤 (Critical Fix #13)
        actual_top_n = min(top_n, len(product_agg))

        # 정렬 및 상위 N개 추출
        product_agg = product_agg.sort_values(metric, ascending=False).head(actual_top_n).reset_index(drop=True)

        logger.info(f"상위 {len(product_agg)}개 상품 추출 완료 (요청: {top_n}개)")
        return product_agg

    def analyze_pareto(self, metric: str = 'sales') -> Tuple[pd.DataFrame, Dict]:
        """
        파레토 분석 (80-20 법칙) (Critical Fix #4, #6)

        Args:
            metric: 분석 기준 ('sales', 'quantity')

        Returns:
            (pareto_df, pareto_summary)
            - pareto_df: 파레토 분석 결과 데이터프레임
                - product: 상품명
                - {metric}: 메트릭 값
                - cumulative_{metric}: 누적 값
                - cumulative_pct: 누적 비율 (%)
                - rank: 순위
            - pareto_summary: 파레토 요약 통계
                - top_20_pct_products: 상위 20% 상품 수
                - top_20_pct_contribution: 상위 20% 매출 기여도 (%)
                - top_80_pct_products: 상위 80% 매출을 차지하는 상품 수
        """
        logger.info(f"파레토 분석 시작: {metric}")

        # 상품별 집계 (Critical Fix #6: sales_column 사용)
        product_agg = self.df.groupby(self.product_column).agg({
            self.sales_column: 'sum',
            self.quantity_column: 'sum'
        }).reset_index()

        product_agg.columns = ['product', 'sales', 'quantity']

        # 정렬 (내림차순)
        product_agg = product_agg.sort_values(metric, ascending=False).reset_index(drop=True)

        # ========== Critical Fix #4: ZeroDivision 방어 ==========
        total = product_agg[metric].sum()

        if total == 0:
            logger.warning("총 매출/수량이 0입니다. 파레토 분석 불가")
            return product_agg, {
                'total_products': len(product_agg),
                'total_sales': 0,
                'top_20_pct_products': 0,
                'top_20_pct_contribution': 0.0,
                'top_80_pct_products': 0,
                'top_80_pct_ratio': 0.0
            }

        # 누적 계산
        product_agg[f'cumulative_{metric}'] = product_agg[metric].cumsum()
        product_agg['cumulative_pct'] = (product_agg[f'cumulative_{metric}'] / total * 100).round(2)
        product_agg['rank'] = range(1, len(product_agg) + 1)

        # 파레토 요약 통계
        total_products = len(product_agg)
        top_20_pct_count = max(1, int(total_products * 0.2))  # 최소 1개

        # 상위 20% 상품의 기여도
        top_20_contribution = product_agg.head(top_20_pct_count)[metric].sum() / total * 100

        # 80% 매출을 차지하는 상품 수 (Critical Fix: < 80 대신 <= 80)
        top_80_products = len(product_agg[product_agg['cumulative_pct'] < 80])

        # 80% 미만으로만 하면 정확히 80% 달성 시점을 놓칠 수 있음
        # 따라서 80% 이상인 첫 번째 상품까지 포함
        if top_80_products < total_products:
            top_80_products += 1

        pareto_summary = {
            'total_products': total_products,
            'total_sales': total,
            'top_20_pct_products': top_20_pct_count,
            'top_20_pct_contribution': round(top_20_contribution, 2),
            'top_80_pct_products': top_80_products,
            'top_80_pct_ratio': round(top_80_products / total_products * 100, 2)
        }

        logger.info(f"파레토 분석 완료: 상위 20%({top_20_pct_count}개) → {top_20_contribution:.1f}% 기여")

        return product_agg, pareto_summary

    def get_summary_statistics(self) -> Dict:
        """
        전체 매출 요약 통계 (Critical Fix #6)

        Returns:
            요약 통계 딕셔너리
        """
        # Critical Fix #6: self.sales_column 사용
        summary = {
            'total_sales': self.df[self.sales_column].sum(),
            'total_quantity': self.df[self.quantity_column].sum(),
            'total_transactions': len(self.df),
            'unique_products': self.df[self.product_column].nunique(),
            'avg_transaction_value': self.df[self.sales_column].mean(),
            'date_range': {
                'start': self.df[self.date_column].min(),
                'end': self.df[self.date_column].max(),
                'days': (self.df[self.date_column].max() - self.df[self.date_column].min()).days
            }
        }

        return summary


if __name__ == "__main__":
    # 테스트 코드 (Critical Fix #11: 인코딩 문제 해결)
    import sys
    import io

    # Windows 콘솔 인코딩 설정 (Critical Fix #11)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("Sales Analyzer 테스트")
    print("=" * 60)

    # 샘플 데이터 생성
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
    products = ['노트북', '마우스', '키보드', '모니터', '헤드셋']

    data = []
    for date in dates:
        for _ in range(np.random.randint(5, 15)):  # 하루 5-15건 거래
            product = np.random.choice(products)
            quantity = np.random.randint(1, 5)
            price = {
                '노트북': 1000000,
                '마우스': 30000,
                '키보드': 50000,
                '모니터': 300000,
                '헤드셋': 80000
            }[product] * (0.9 + np.random.random() * 0.2)  # ±10% 변동

            data.append({
                'date': date,
                'product': product,
                'quantity': quantity,
                'price': price
            })

    df = pd.DataFrame(data)
    print(f"\n샘플 데이터 생성: {len(df)}건")
    print(df.head())

    # 분석기 초기화
    print("\n분석기 초기화 중...")
    analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                            quantity_column='quantity', price_column='price')

    # 1. 요약 통계
    print("\n" + "=" * 60)
    print("1. 요약 통계")
    print("=" * 60)
    summary = analyzer.get_summary_statistics()
    print(f"총 매출: {summary['total_sales']:,.0f}원")  # ₩ 대신 '원' 사용
    print(f"총 수량: {summary['total_quantity']:,}개")
    print(f"총 거래: {summary['total_transactions']:,}건")
    print(f"상품 수: {summary['unique_products']}개")
    print(f"평균 거래액: {summary['avg_transaction_value']:,.0f}원")
    print(f"기간: {summary['date_range']['start']} ~ {summary['date_range']['end']} ({summary['date_range']['days']}일)")

    # 2. 일별 집계 + 이동평균
    print("\n" + "=" * 60)
    print("2. 일별 집계 + 이동평균 (최근 5일)")
    print("=" * 60)
    daily = analyzer.aggregate_by_period('D')
    daily_ma = analyzer.calculate_moving_average(daily, 'sales', [7, 30])
    print(daily_ma.tail())

    # 3. 월별 집계 + 성장률 (Critical Fix #5: shift_periods 사용)
    print("\n" + "=" * 60)
    print("3. 월별 집계 + 성장률")
    print("=" * 60)
    monthly = analyzer.aggregate_by_period('M')
    monthly_growth = analyzer.calculate_growth_rate(monthly, 'sales', shift_periods=1)
    print(monthly_growth[['date', 'sales', 'sales_growth', 'sales_growth_abs']])

    # 4. 상품 순위 TOP 5
    print("\n" + "=" * 60)
    print("4. 상품 순위 TOP 5")
    print("=" * 60)
    top_products = analyzer.get_top_products(5, 'sales')
    print(top_products)

    # 5. 파레토 분석
    print("\n" + "=" * 60)
    print("5. 파레토 분석")
    print("=" * 60)
    pareto_df, pareto_summary = analyzer.analyze_pareto('sales')
    print("\n파레토 요약:")
    print(f"  총 상품 수: {pareto_summary['total_products']}개")
    print(f"  상위 20%({pareto_summary['top_20_pct_products']}개) → {pareto_summary['top_20_pct_contribution']}% 기여")
    print(f"  80% 매출 달성: {pareto_summary['top_80_pct_products']}개 ({pareto_summary['top_80_pct_ratio']}%)")
    print("\n파레토 상위 5개:")
    print(pareto_df.head())

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
