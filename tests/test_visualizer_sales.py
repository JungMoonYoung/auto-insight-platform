"""
Unit Tests for Visualizer Module (Sales Charts)
Testing plot_sales_trend, plot_top_products_bar, plot_pareto_chart
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from modules.visualizer import Visualizer


class TestVisualizerSalesTrend:
    """Sales trend chart tests"""

    @pytest.fixture
    def visualizer(self):
        """Visualizer instance"""
        return Visualizer()

    @pytest.fixture
    def sample_trend_data(self):
        """Sample aggregated data with MA columns"""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        return pd.DataFrame({
            'date': dates,
            'sales': [100, 150, 120, 180, 200, 160, 140, 190, 210, 220],
            'sales_ma_3': [100, 125, 123.33, 150, 166.67, 180, 166.67, 163.33, 180, 186.67],
            'sales_ma_7': [100, 125, 123.33, 137.5, 150, 151.67, 150, 160, 167.14, 172.86]
        })

    def test_sales_trend_basic(self, visualizer, sample_trend_data):
        """Basic trend chart should render correctly"""
        fig = visualizer.plot_sales_trend(
            sample_trend_data,
            date_column='date',
            sales_column='sales',
            ma_columns=['sales_ma_3', 'sales_ma_7'],
            title='Test Sales Trend'
        )

        # Chart should be created
        assert fig is not None

        # Should have 3 traces (1 bar + 2 MA lines)
        assert len(fig.data) == 3

        # First trace should be bar (actual sales)
        assert fig.data[0].type == 'bar'
        assert len(fig.data[0].y) == 10

        # Second and third traces should be scatter (MA lines)
        assert fig.data[1].type == 'scatter'
        assert fig.data[2].type == 'scatter'

        # Title should match
        assert 'Test Sales Trend' in fig.layout.title.text

    def test_sales_trend_without_ma(self, visualizer, sample_trend_data):
        """Trend chart without MA should work"""
        fig = visualizer.plot_sales_trend(
            sample_trend_data,
            date_column='date',
            sales_column='sales',
            ma_columns=None
        )

        # Should have only 1 trace (bar chart)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'

    def test_sales_trend_empty_dataframe_raises_error(self, visualizer):
        """Empty DataFrame should raise ValueError"""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="데이터프레임이 비어있습니다"):
            visualizer.plot_sales_trend(df, date_column='date', sales_column='sales')

    def test_sales_trend_insufficient_data_raises_error(self, visualizer):
        """Less than 2 data points should raise ValueError"""
        df = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-01')],
            'sales': [100]
        })

        with pytest.raises(ValueError, match="최소 2개 이상의 데이터 포인트가 필요"):
            visualizer.plot_sales_trend(df, date_column='date', sales_column='sales')

    def test_sales_trend_missing_column_raises_error(self, visualizer, sample_trend_data):
        """Missing required column should raise ValueError"""
        with pytest.raises(ValueError, match="필수 컬럼 누락.*wrong_column"):
            visualizer.plot_sales_trend(
                sample_trend_data,
                date_column='wrong_column',
                sales_column='sales'
            )

    def test_sales_trend_missing_ma_column_raises_error(self, visualizer, sample_trend_data):
        """Missing MA column should raise ValueError"""
        with pytest.raises(ValueError, match="이동평균 컬럼 누락.*sales_ma_999"):
            visualizer.plot_sales_trend(
                sample_trend_data,
                date_column='date',
                sales_column='sales',
                ma_columns=['sales_ma_999']
            )

    def test_sales_trend_custom_currency(self, visualizer, sample_trend_data):
        """Custom currency should be reflected in hover template"""
        fig = visualizer.plot_sales_trend(
            sample_trend_data,
            date_column='date',
            sales_column='sales',
            currency='USD'
        )

        # Check hover template contains USD
        assert 'USD' in fig.data[0].hovertemplate

    def test_sales_trend_data_accuracy(self, visualizer, sample_trend_data):
        """Chart data should match input data"""
        fig = visualizer.plot_sales_trend(
            sample_trend_data,
            date_column='date',
            sales_column='sales',
            ma_columns=['sales_ma_3']
        )

        # Bar chart values should match sales column
        assert list(fig.data[0].y) == list(sample_trend_data['sales'])

        # MA line values should match MA column
        np.testing.assert_array_almost_equal(
            fig.data[1].y,
            sample_trend_data['sales_ma_3'],
            decimal=2
        )


class TestVisualizerTopProductsBar:
    """Top products bar chart tests"""

    @pytest.fixture
    def visualizer(self):
        return Visualizer()

    @pytest.fixture
    def sample_products_data(self):
        """Sample top products data (already sorted)"""
        return pd.DataFrame({
            'product': [f'Product {chr(65+i)}' for i in range(10)],
            'sales': [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100],
            'quantity': [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        })

    def test_top_products_basic(self, visualizer, sample_products_data):
        """Basic top products chart should render correctly"""
        fig = visualizer.plot_top_products_bar(
            sample_products_data,
            product_column='product',
            sales_column='sales',
            top_n=10
        )

        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
        assert fig.data[0].orientation == 'h'

        # Should display all 10 products
        assert len(fig.data[0].y) == 10

    def test_top_products_limit(self, visualizer, sample_products_data):
        """Top N limit should work correctly"""
        fig = visualizer.plot_top_products_bar(
            sample_products_data,
            product_column='product',
            sales_column='sales',
            top_n=5
        )

        # Should display only top 5
        assert len(fig.data[0].y) == 5

    def test_top_products_auto_title(self, visualizer, sample_products_data):
        """Auto-generated title should include top N"""
        fig = visualizer.plot_top_products_bar(
            sample_products_data,
            product_column='product',
            sales_column='sales',
            top_n=5,
            title=None  # Auto-generate
        )

        # Title should mention TOP 5
        assert 'TOP 5' in fig.layout.title.text

    def test_top_products_custom_title(self, visualizer, sample_products_data):
        """Custom title should be used"""
        fig = visualizer.plot_top_products_bar(
            sample_products_data,
            product_column='product',
            sales_column='sales',
            title='Custom Title'
        )

        assert 'Custom Title' in fig.layout.title.text

    def test_top_products_empty_dataframe_raises_error(self, visualizer):
        """Empty DataFrame should raise ValueError"""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="데이터프레임이 비어있습니다"):
            visualizer.plot_top_products_bar(df, product_column='product', sales_column='sales')

    def test_top_products_missing_column_raises_error(self, visualizer, sample_products_data):
        """Missing required column should raise ValueError"""
        with pytest.raises(ValueError, match="필수 컬럼 누락.*wrong_column"):
            visualizer.plot_top_products_bar(
                sample_products_data,
                product_column='wrong_column',
                sales_column='sales'
            )

    def test_top_products_data_accuracy(self, visualizer, sample_products_data):
        """Chart data should match input data (reversed order)"""
        fig = visualizer.plot_top_products_bar(
            sample_products_data,
            product_column='product',
            sales_column='sales',
            top_n=10
        )

        # Horizontal bar chart displays bottom to top, so data is reversed
        # First y value should be last product (due to iloc[::-1])
        assert fig.data[0].y[0] == 'Product J'
        assert fig.data[0].y[-1] == 'Product A'

        # X values should match sales (reversed)
        assert fig.data[0].x[0] == 100
        assert fig.data[0].x[-1] == 1000

    def test_top_products_height_calculation(self, visualizer):
        """Chart height should scale with number of products"""
        # Test with 5 products
        df_small = pd.DataFrame({
            'product': ['A', 'B', 'C', 'D', 'E'],
            'sales': [100, 90, 80, 70, 60]
        })

        fig_small = visualizer.plot_top_products_bar(
            df_small,
            product_column='product',
            sales_column='sales',
            top_n=5
        )

        # 5 products * 25px = 125px, but minimum is 400px
        assert fig_small.layout.height == 400

        # Test with 50 products (should hit max height limit)
        df_large = pd.DataFrame({
            'product': [f'P{i}' for i in range(50)],
            'sales': list(range(50, 0, -1))
        })

        fig_large = visualizer.plot_top_products_bar(
            df_large,
            product_column='product',
            sales_column='sales',
            top_n=50,
            max_height=1200
        )

        # 50 * 25 = 1250px, but max is 1200px
        assert fig_large.layout.height == 1200


class TestVisualizerParetoChart:
    """Pareto chart tests"""

    @pytest.fixture
    def visualizer(self):
        return Visualizer()

    @pytest.fixture
    def sample_pareto_data(self):
        """Sample pareto analysis result"""
        return pd.DataFrame({
            'product': ['A', 'B', 'C', 'D', 'E'],
            'sales': [500, 300, 150, 40, 10],  # Total: 1000
            'cumulative_sales': [500, 800, 950, 990, 1000],
            'cumulative_pct': [50.0, 80.0, 95.0, 99.0, 100.0],
            'rank': [1, 2, 3, 4, 5]
        })

    def test_pareto_basic(self, visualizer, sample_pareto_data):
        """Basic pareto chart should render correctly"""
        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct',
            threshold=80.0
        )

        assert fig is not None

        # Should have 2 traces (bar + cumulative line)
        # Threshold is added via add_hline, not as a trace
        assert len(fig.data) == 2

        # First trace: bar chart (sales)
        assert fig.data[0].type == 'bar'

        # Second trace: scatter line (cumulative %)
        assert fig.data[1].type == 'scatter'
        assert fig.data[1].mode == 'lines+markers'

    def test_pareto_empty_dataframe_raises_error(self, visualizer):
        """Empty DataFrame should raise ValueError"""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="데이터프레임이 비어있습니다"):
            visualizer.plot_pareto_chart(
                df,
                product_column='product',
                sales_column='sales',
                cumulative_pct_column='cumulative_pct'
            )

    def test_pareto_single_product_raises_error(self, visualizer):
        """Single product should raise ValueError"""
        df = pd.DataFrame({
            'product': ['A'],
            'sales': [100],
            'cumulative_pct': [100.0]
        })

        with pytest.raises(ValueError, match="최소 2개 이상의 상품이 필요"):
            visualizer.plot_pareto_chart(
                df,
                product_column='product',
                sales_column='sales',
                cumulative_pct_column='cumulative_pct'
            )

    def test_pareto_missing_column_raises_error(self, visualizer, sample_pareto_data):
        """Missing required column should raise ValueError"""
        with pytest.raises(ValueError, match="필수 컬럼 누락.*wrong_column"):
            visualizer.plot_pareto_chart(
                sample_pareto_data,
                product_column='wrong_column',
                sales_column='sales',
                cumulative_pct_column='cumulative_pct'
            )

    def test_pareto_top_n_limit(self, visualizer, sample_pareto_data):
        """Top N limit should work"""
        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct',
            top_n=3
        )

        # Bar chart should show only top 3 products
        assert len(fig.data[0].x) == 3

    def test_pareto_cumulative_accuracy(self, visualizer, sample_pareto_data):
        """Cumulative percentage should be accurate"""
        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct',
            threshold=80.0
        )

        # Cumulative line values should match input
        cumulative_values = list(fig.data[1].y)
        expected_values = list(sample_pareto_data['cumulative_pct'])

        assert cumulative_values == expected_values

    def test_pareto_threshold_line(self, visualizer, sample_pareto_data):
        """Threshold line should be added via shapes"""
        threshold = 80.0

        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct',
            threshold=threshold
        )

        # Threshold is added via shapes (horizontal line)
        assert len(fig.layout.shapes) > 0
        threshold_shape = fig.layout.shapes[0]
        assert threshold_shape.y0 == threshold
        assert threshold_shape.y1 == threshold

    def test_pareto_dual_axis_configuration(self, visualizer, sample_pareto_data):
        """Dual axis should be configured correctly"""
        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct'
        )

        # Should have secondary y-axis configuration
        assert hasattr(fig.layout, 'yaxis2')

        # Primary axis: sales
        # Secondary axis: percentage (range is dynamic, starts at 0)
        assert fig.layout.yaxis2.range[0] == 0
        assert fig.layout.yaxis2.range[1] <= 110  # Max with 5% buffer

    def test_pareto_custom_threshold(self, visualizer, sample_pareto_data):
        """Custom threshold should be used"""
        custom_threshold = 70.0

        fig = visualizer.plot_pareto_chart(
            sample_pareto_data,
            product_column='product',
            sales_column='sales',
            cumulative_pct_column='cumulative_pct',
            threshold=custom_threshold
        )

        # Threshold line should be at 70% (via shapes)
        assert len(fig.layout.shapes) > 0
        threshold_shape = fig.layout.shapes[0]
        assert threshold_shape.y0 == custom_threshold
        assert threshold_shape.y1 == custom_threshold


class TestVisualizerEdgeCases:
    """Edge case tests for all sales visualizations"""

    @pytest.fixture
    def visualizer(self):
        return Visualizer()

    def test_large_dataset_performance(self, visualizer):
        """Large dataset should render without error"""
        # 1000 days of data
        dates = pd.date_range('2020-01-01', periods=1000, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'sales': np.random.randint(1000, 10000, size=1000)
        })

        fig = visualizer.plot_sales_trend(
            df,
            date_column='date',
            sales_column='sales'
        )

        assert fig is not None
        assert len(fig.data[0].y) == 1000

    def test_zero_sales_handling(self, visualizer):
        """Zero sales should be handled correctly"""
        df = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'sales': [0, 0, 0],
            'cumulative_pct': [0, 0, 0]
        })

        # Should not crash
        fig = visualizer.plot_top_products_bar(
            df,
            product_column='product',
            sales_column='sales'
        )

        assert fig is not None

    def test_special_characters_in_product_names(self, visualizer):
        """Special characters in product names should be handled"""
        df = pd.DataFrame({
            'product': ['Product <A>', 'Product "B"', "Product 'C'", 'Product & D'],
            'sales': [100, 90, 80, 70]
        })

        fig = visualizer.plot_top_products_bar(
            df,
            product_column='product',
            sales_column='sales'
        )

        # Should render without error
        assert fig is not None
        assert len(fig.data[0].y) == 4


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
