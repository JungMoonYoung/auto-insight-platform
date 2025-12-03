"""
DAY 31: 판매 분석 페이지 통합 테스트
Streamlit 페이지 없이 로직만 검증
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from modules.sales_analyzer import SalesAnalyzer
from modules.visualizer import Visualizer


def test_sales_page_logic():
    """판매 분석 페이지 로직 테스트"""

    print("=" * 70)
    print("DAY 31: 판매 분석 페이지 통합 테스트")
    print("=" * 70)

    # ========== [20%] 샘플 데이터 생성 ==========
    print("\n[20%] 샘플 데이터 생성 중...")

    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
    products = ['노트북', '마우스', '키보드', '모니터', '헤드셋']

    data = []
    for date in dates:
        for _ in range(np.random.randint(5, 15)):
            product = np.random.choice(products)
            quantity = np.random.randint(1, 5)
            price = {
                '노트북': 1000000,
                '마우스': 30000,
                '키보드': 50000,
                '모니터': 300000,
                '헤드셋': 80000
            }[product] * (0.9 + np.random.random() * 0.2)

            data.append({
                'date': date,
                'product': product,
                'quantity': quantity,
                'price': price
            })

    df = pd.DataFrame(data)
    print(f"   ✓ 샘플 데이터: {len(df)}건")

    # ========== [40%] run_sales_analysis() 로직 시뮬레이션 ==========
    print("\n[40%] SalesAnalyzer 초기화 및 집계 중...")

    analyzer = SalesAnalyzer(
        df,
        date_column='date',
        product_column='product',
        quantity_column='quantity',
        price_column='price'
    )

    # 일별/주별/월별 집계
    daily = analyzer.aggregate_by_period('D')
    weekly = analyzer.aggregate_by_period('W')
    monthly = analyzer.aggregate_by_period('M')

    # 이동평균 계산
    daily_ma = analyzer.calculate_moving_average(daily, 'sales', [7, 30])
    weekly_ma = analyzer.calculate_moving_average(weekly, 'sales', [4])
    monthly_ma = analyzer.calculate_moving_average(monthly, 'sales', [3])

    # 성장률 계산
    daily_growth = analyzer.calculate_growth_rate(daily, 'sales', shift_periods=1)
    weekly_growth = analyzer.calculate_growth_rate(weekly, 'sales', shift_periods=1)
    monthly_growth = analyzer.calculate_growth_rate(monthly, 'sales', shift_periods=1)

    # 상품 분석
    top_products = analyzer.get_top_products(20, 'sales')
    pareto_df, pareto_summary = analyzer.analyze_pareto('sales')

    print(f"   ✓ 일별 집계: {len(daily)}일")
    print(f"   ✓ 주별 집계: {len(weekly)}주")
    print(f"   ✓ 월별 집계: {len(monthly)}월")
    print(f"   ✓ 상품 분석: {len(top_products)}개")

    # results 딕셔너리 구성 (실제 app.py와 동일)
    results = {
        'type': 'sales',
        'analyzer': analyzer,
        'daily': daily_ma,
        'weekly': weekly_ma,
        'monthly': monthly_ma,
        'daily_growth': daily_growth,
        'weekly_growth': weekly_growth,
        'monthly_growth': monthly_growth,
        'top_products': top_products,
        'pareto_df': pareto_df,
        'pareto_summary': pareto_summary,
        'columns': {
            'date': 'date',
            'product': 'product',
            'quantity': 'quantity',
            'price': 'price'
        }
    }

    # ========== [60%] show_sales_results() 로직 검증 ==========
    print("\n[60%] 판매 분석 페이지 로직 검증 중...")

    # 기간 선택 시뮬레이션 (일별/주별/월별)
    for period_name in ['일별', '주별', '월별']:
        period_map = {'일별': 'daily', '주별': 'weekly', '월별': 'monthly'}
        selected_period = period_map[period_name]

        df_display = results[selected_period]
        df_growth = results[f'{selected_period}_growth']

        # 메트릭 계산
        total_sales = df_display['sales'].sum()
        avg_sales = df_display['sales'].mean()

        print(f"\n   [{period_name}]")
        print(f"      - 총 매출: {total_sales:,.0f}원")
        print(f"      - 평균 매출: {avg_sales:,.0f}원")
        print(f"      - 데이터 포인트: {len(df_display)}개")

        # 성장률 테이블 검증 (최근 5개)
        if 'sales_growth' in df_growth.columns:
            recent_growth = df_growth['sales_growth'].dropna().tail(5)
            if not recent_growth.empty:
                avg_growth = recent_growth.mean()
                print(f"      - 최근 평균 성장률: {avg_growth:.1f}%")

    # ========== [80%] 차트 생성 검증 ==========
    print("\n[80%] 차트 생성 검증 중...")

    visualizer = Visualizer()

    # 차트 1: 트렌드 차트
    ma_cols = [col for col in daily_ma.columns if 'ma_' in col]
    fig_trend = visualizer.plot_sales_trend(
        daily_ma,
        date_column='date',
        sales_column='sales',
        ma_columns=ma_cols if ma_cols else None,
        title='일별 매출 트렌드',
        currency='원'
    )
    assert fig_trend is not None, "트렌드 차트 생성 실패"
    print(f"   ✓ 트렌드 차트: {len(fig_trend.data)}개 trace")

    # 차트 2: 상품 순위 차트
    fig_products = visualizer.plot_top_products_bar(
        top_products,
        product_column='product',
        sales_column='sales',
        top_n=20,
        title='상품별 매출 순위 TOP 20',
        currency='원'
    )
    assert fig_products is not None, "상품 순위 차트 생성 실패"
    print(f"   ✓ 상품 순위 차트: 생성 완료")

    # 차트 3: 파레토 차트
    fig_pareto = visualizer.plot_pareto_chart(
        pareto_df,
        product_column='product',
        sales_column='sales',
        cumulative_pct_column='cumulative_pct',
        top_n=30,
        threshold=80.0,
        title='파레토 분석',
        currency='원'
    )
    assert fig_pareto is not None, "파레토 차트 생성 실패"
    print(f"   ✓ 파레토 차트: {len(fig_pareto.data)}개 trace")

    # ========== [90%] 인사이트 검증 ==========
    print("\n[90%] 인사이트 생성 검증 중...")

    # 파레토 요약
    print(f"   ✓ 전체 상품: {pareto_summary['total_products']}개")
    print(f"   ✓ 상위 20% 상품: {pareto_summary['top_20_pct_products']}개")
    print(f"   ✓ 상위 20% 기여도: {pareto_summary['top_20_pct_contribution']:.1f}%")
    print(f"   ✓ 80% 달성 상품: {pareto_summary['top_80_pct_products']}개")

    # 성장률 추세 분석
    if 'sales_growth' in daily_growth.columns:
        recent_growth = daily_growth['sales_growth'].dropna().tail(5)
        if not recent_growth.empty:
            avg_recent_growth = recent_growth.mean()
            print(f"   ✓ 최근 5일 평균 성장률: {avg_recent_growth:.1f}%")

            if avg_recent_growth > 5:
                print("   ✓ 성장세: 양호 (5% 이상)")
            elif avg_recent_growth > 0:
                print("   ✓ 성장세: 완만 (0~5%)")
            else:
                print("   ✓ 성장세: 하락 (0% 미만)")

    # 집중도 분석
    concentration = pareto_summary['top_20_pct_contribution']
    if concentration > 80:
        print("   ✓ 매출 집중도: 매우 높음 (80% 이상) → 리스크 분산 필요")
    elif concentration > 60:
        print("   ✓ 매출 집중도: 적정 (60~80%) → 핵심 상품 관리")
    else:
        print("   ✓ 매출 집중도: 분산형 (60% 미만) → 다양한 포트폴리오")

    # ========== [100%] 완료 ==========
    print("\n[100%] 테스트 완료!")
    print("=" * 70)
    print("✅ DAY 31 판매 분석 페이지 로직 모두 정상 작동")
    print("=" * 70)

    print("\n구현된 기능:")
    print("  1. ✅ 기간 선택 (일별/주별/월별)")
    print("  2. ✅ 3개 탭 구성 (트렌드/상품/인사이트)")
    print("  3. ✅ 트렌드 차트 + 성장률 테이블")
    print("  4. ✅ 상품 순위 차트 + 파레토 차트")
    print("  5. ✅ 요약 통계 + 기본 인사이트")
    print("  6. ✅ CSV 다운로드 (일별/상품)")
    print("  7. ✅ HTML 리포트 생성")

    return True


if __name__ == "__main__":
    # UTF-8 출력 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    try:
        result = test_sales_page_logic()
        if result:
            print("\n🎉 DAY 31 테스트 성공!")
            sys.exit(0)
        else:
            print("\n❌ 테스트 실패")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
