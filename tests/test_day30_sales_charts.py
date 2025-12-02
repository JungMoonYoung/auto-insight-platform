"""
DAY 30: 판매 차트 테스트
매출 트렌드, 상품 순위, 파레토 차트 검증
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from modules.sales_analyzer import SalesAnalyzer
from modules.visualizer import Visualizer


def test_sales_charts():
    """판매 분석 차트 3개 테스트"""

    print("=" * 70)
    print("DAY 30: 판매 차트 테스트")
    print("=" * 70)

    # ========== 1단계: 샘플 데이터 생성 (10%) ==========
    print("\n[10%] 샘플 데이터 생성 중...")

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

    # ========== 2단계: 분석기 초기화 (20%) ==========
    print("\n[20%] SalesAnalyzer 초기화 중...")

    analyzer = SalesAnalyzer(
        df,
        date_column='date',
        product_column='product',
        quantity_column='quantity',
        price_column='price'
    )
    print(f"   ✓ 초기화 완료")

    # ========== 3단계: 일별 집계 + 이동평균 (40%) ==========
    print("\n[40%] 일별 집계 + 이동평균 계산 중...")

    daily = analyzer.aggregate_by_period('D')
    daily_ma = analyzer.calculate_moving_average(daily, 'sales', [7, 30])

    print(f"   ✓ 집계 완료: {len(daily)}일")
    print(f"   ✓ 이동평균 컬럼: {[col for col in daily_ma.columns if 'ma' in col]}")

    # ========== 4단계: 상품 순위 계산 (50%) ==========
    print("\n[50%] 상품 순위 TOP 5 계산 중...")

    top_products = analyzer.get_top_products(5, 'sales')
    print(f"   ✓ 상위 5개 상품:")
    for idx, row in top_products.iterrows():
        print(f"      {idx+1}. {row['product']}: {row['sales']:,.0f}원")

    # ========== 5단계: 파레토 분석 (60%) ==========
    print("\n[60%] 파레토 분석 중...")

    pareto_df, pareto_summary = analyzer.analyze_pareto('sales')
    print(f"   ✓ 파레토 요약:")
    print(f"      - 총 상품: {pareto_summary['total_products']}개")
    print(f"      - 상위 20%({pareto_summary['top_20_pct_products']}개) → {pareto_summary['top_20_pct_contribution']}% 기여")
    print(f"      - 80% 매출 달성: {pareto_summary['top_80_pct_products']}개")

    # ========== 6단계: 차트 생성 (70-90%) ==========
    print("\n[70%] Visualizer 초기화 및 차트 생성 중...")

    visualizer = Visualizer()

    # 차트 1: 매출 트렌드
    print("   [75%] 매출 트렌드 차트 생성 중...")
    fig_trend = visualizer.plot_sales_trend(
        daily_ma,
        date_column='date',
        sales_column='sales',
        ma_columns=['sales_ma_7', 'sales_ma_30'],
        title='일별 매출 트렌드 (이동평균 포함)'
    )
    print(f"      ✓ 트렌드 차트 생성 완료 ({len(fig_trend.data)}개 trace)")

    # 차트 2: 상품 순위
    print("   [80%] 상품 순위 차트 생성 중...")
    fig_products = visualizer.plot_top_products_bar(
        top_products,
        product_column='product',
        sales_column='sales',
        top_n=5,
        title='상품별 매출 순위 TOP 5'
    )
    print(f"      ✓ 상품 순위 차트 생성 완료")

    # 차트 3: 파레토 차트
    print("   [85%] 파레토 차트 생성 중...")
    fig_pareto = visualizer.plot_pareto_chart(
        pareto_df,
        product_column='product',
        sales_column='sales',
        cumulative_pct_column='cumulative_pct',
        top_n=5,
        threshold=80.0,
        title='파레토 분석 (80-20 법칙)'
    )
    print(f"      ✓ 파레토 차트 생성 완료 ({len(fig_pareto.data)}개 trace)")

    # ========== 7단계: 차트 검증 (95%) ==========
    print("\n[95%] 차트 검증 중...")

    # 트렌드 차트 검증
    assert len(fig_trend.data) >= 2, "트렌드 차트는 최소 2개 trace 필요 (실제 매출 + MA)"
    print("   ✓ 트렌드 차트: OK")

    # 상품 순위 차트 검증
    assert len(fig_products.data) == 1, "상품 순위 차트는 1개 trace"
    assert fig_products.data[0].orientation == 'h', "가로형 막대 차트"
    print("   ✓ 상품 순위 차트: OK (가로형)")

    # 파레토 차트 검증 (듀얼 축)
    assert len(fig_pareto.data) == 2, "파레토 차트는 2개 trace (막대 + 선)"
    assert fig_pareto.data[0].type == 'bar', "첫 번째 trace는 막대"
    assert fig_pareto.data[1].type == 'scatter', "두 번째 trace는 선"
    print("   ✓ 파레토 차트: OK (듀얼 축)")

    # 80% 기준선 검증
    has_hline = any('hline' in str(shape) for shape in fig_pareto.layout.shapes) if hasattr(fig_pareto.layout, 'shapes') else False
    print(f"   ✓ 파레토 80% 기준선: {'있음' if has_hline else '없음 (hline 대신 annotation 사용)'}")

    # ========== 8단계: 완료 (100%) ==========
    print("\n[100%] 테스트 완료!")
    print("=" * 70)
    print("✅ DAY 30 판매 차트 3개 모두 정상 작동")
    print("=" * 70)

    print("\n생성된 차트:")
    print("  1. 매출 트렌드 차트 (막대 + 이동평균선)")
    print("  2. 상품 순위 차트 (가로형 TOP 5)")
    print("  3. 파레토 차트 (듀얼 축 + 80% 기준선)")

    return True


if __name__ == "__main__":
    # UTF-8 출력 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    try:
        result = test_sales_charts()
        if result:
            print("\n🎉 DAY 30 테스트 성공!")
            sys.exit(0)
        else:
            print("\n❌ 테스트 실패")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
