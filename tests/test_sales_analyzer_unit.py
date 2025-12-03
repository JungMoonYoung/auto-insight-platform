"""
Unit Tests for SalesAnalyzer Module
Critical Fix: Proper unit testing with assertions and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from modules.sales_analyzer import SalesAnalyzer


class TestSalesAnalyzerInputValidation:
    """Input validation tests (Critical Fix #1)"""

    def test_empty_dataframe_raises_error(self):
        """Empty DataFrame should raise ValueError"""
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="입력 데이터가 비어있습니다"):
            SalesAnalyzer(df, date_column='date', product_column='product')

    def test_single_row_raises_error(self):
        """Single row should raise ValueError (minimum 2 rows required)"""
        df = pd.DataFrame([{
            'date': '2024-01-01',
            'product': 'A',
            'quantity': 1,
            'price': 100
        }])

        with pytest.raises(ValueError, match="데이터가 너무 적습니다"):
            SalesAnalyzer(df, date_column='date', product_column='product',
                         quantity_column='quantity', price_column='price')

    def test_missing_date_column_raises_error(self):
        """Missing date column should raise ValueError"""
        df = pd.DataFrame([
            {'product': 'A', 'quantity': 1, 'price': 100},
            {'product': 'B', 'quantity': 2, 'price': 200}
        ])

        with pytest.raises(ValueError, match="필수 컬럼 누락.*date"):
            SalesAnalyzer(df, date_column='date', product_column='product',
                         quantity_column='quantity', price_column='price')

    def test_missing_product_column_raises_error(self):
        """Missing product column should raise ValueError"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'quantity': 1, 'price': 100},
            {'date': '2024-01-02', 'quantity': 2, 'price': 200}
        ])

        with pytest.raises(ValueError, match="필수 컬럼 누락.*product"):
            SalesAnalyzer(df, date_column='date', product_column='product',
                         quantity_column='quantity', price_column='price')

    def test_all_null_dates_raises_error(self):
        """All NULL dates should raise ValueError"""
        df = pd.DataFrame([
            {'date': None, 'product': 'A', 'quantity': 1, 'price': 100},
            {'date': None, 'product': 'B', 'quantity': 2, 'price': 200}
        ])

        with pytest.raises(ValueError, match="날짜 컬럼.*전부 비어있습니다"):
            SalesAnalyzer(df, date_column='date', product_column='product',
                         quantity_column='quantity', price_column='price')

    def test_all_null_products_raises_error(self):
        """All NULL products should raise ValueError"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': None, 'quantity': 1, 'price': 100},
            {'date': '2024-01-02', 'product': None, 'quantity': 2, 'price': 200}
        ])

        with pytest.raises(ValueError, match="상품 컬럼.*전부 비어있습니다"):
            SalesAnalyzer(df, date_column='date', product_column='product',
                         quantity_column='quantity', price_column='price')

    def test_sales_column_auto_creation(self):
        """Sales column should be auto-created if missing"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 2, 'price': 100},
            {'date': '2024-01-02', 'product': 'B', 'quantity': 3, 'price': 200}
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        assert 'sales' in analyzer.df.columns
        assert analyzer.df.iloc[0]['sales'] == 200  # 2 * 100
        assert analyzer.df.iloc[1]['sales'] == 600  # 3 * 200

    def test_invalid_date_format_handling(self):
        """Invalid dates should be dropped with warning"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 1, 'price': 100},
            {'date': 'INVALID', 'product': 'B', 'quantity': 2, 'price': 200},
            {'date': '2024-01-03', 'product': 'C', 'quantity': 3, 'price': 300},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        # Invalid date row should be dropped
        assert len(analyzer.df) == 2


class TestSalesAnalyzerAggregation:
    """Aggregation logic tests (Critical Fix #6)"""

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing (3 days, 2 products)"""
        return pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 2, 'price': 100},
            {'date': '2024-01-01', 'product': 'B', 'quantity': 1, 'price': 200},
            {'date': '2024-01-02', 'product': 'A', 'quantity': 3, 'price': 100},
            {'date': '2024-01-03', 'product': 'B', 'quantity': 2, 'price': 200},
        ])

    def test_aggregate_by_period_daily(self, sample_data):
        """Daily aggregation should sum correctly"""
        analyzer = SalesAnalyzer(sample_data, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')

        # Check number of days
        assert len(daily) == 3

        # Check sales calculation (quantity * price)
        assert daily.iloc[0]['sales'] == 400  # Day 1: 2*100 + 1*200
        assert daily.iloc[1]['sales'] == 300  # Day 2: 3*100
        assert daily.iloc[2]['sales'] == 400  # Day 3: 2*200

        # Check quantity sum
        assert daily.iloc[0]['quantity'] == 3  # Day 1: 2 + 1
        assert daily.iloc[1]['quantity'] == 3  # Day 2: 3
        assert daily.iloc[2]['quantity'] == 2  # Day 3: 2

        # Check transaction count
        assert daily.iloc[0]['transactions'] == 2  # Day 1: 2 rows
        assert daily.iloc[1]['transactions'] == 1  # Day 2: 1 row
        assert daily.iloc[2]['transactions'] == 1  # Day 3: 1 row

    def test_aggregate_by_period_weekly(self, sample_data):
        """Weekly aggregation should work correctly"""
        analyzer = SalesAnalyzer(sample_data, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        weekly = analyzer.aggregate_by_period('W')

        # 3 consecutive days should be in same week
        assert len(weekly) == 1

        # Total sales: 400 + 300 + 400 = 1100
        assert weekly.iloc[0]['sales'] == 1100

        # Total quantity: 3 + 3 + 2 = 8
        assert weekly.iloc[0]['quantity'] == 8

        # Total transactions: 4
        assert weekly.iloc[0]['transactions'] == 4

    def test_aggregate_by_period_monthly(self, sample_data):
        """Monthly aggregation should work correctly"""
        analyzer = SalesAnalyzer(sample_data, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        monthly = analyzer.aggregate_by_period('M')

        # All in January 2024
        assert len(monthly) == 1
        assert monthly.iloc[0]['sales'] == 1100


class TestSalesAnalyzerMovingAverage:
    """Moving average calculation tests"""

    def test_moving_average_basic(self):
        """Moving average should calculate correctly"""
        df = pd.DataFrame([
            {'date': f'2024-01-{i:02d}', 'product': 'A', 'quantity': 1, 'price': 100}
            for i in range(1, 11)  # 10 days
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        daily_ma = analyzer.calculate_moving_average(daily, 'sales', [3])

        # Check MA column exists
        assert 'sales_ma_3' in daily_ma.columns

        # First value should be 100 (only 1 data point)
        assert daily_ma.iloc[0]['sales_ma_3'] == 100

        # Third value should be 100 (average of 100, 100, 100)
        assert daily_ma.iloc[2]['sales_ma_3'] == 100

    def test_moving_average_multiple_windows(self):
        """Multiple MA windows should work"""
        df = pd.DataFrame([
            {'date': f'2024-01-{i:02d}', 'product': 'A', 'quantity': 1, 'price': 100}
            for i in range(1, 31)  # 30 days
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        daily_ma = analyzer.calculate_moving_average(daily, 'sales', [7, 14, 30])

        assert 'sales_ma_7' in daily_ma.columns
        assert 'sales_ma_14' in daily_ma.columns
        assert 'sales_ma_30' in daily_ma.columns


class TestSalesAnalyzerGrowthRate:
    """Growth rate calculation tests (Critical Fix #4, #5)"""

    def test_growth_rate_basic(self):
        """Growth rate should calculate correctly"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 1, 'price': 100},  # 100
            {'date': '2024-01-02', 'product': 'A', 'quantity': 1, 'price': 150},  # 150 (+50%)
            {'date': '2024-01-03', 'product': 'A', 'quantity': 1, 'price': 120},  # 120 (-20%)
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        daily_growth = analyzer.calculate_growth_rate(daily, 'sales', shift_periods=1)

        # First row should be NaN (no previous data)
        assert pd.isna(daily_growth.iloc[0]['sales_growth'])

        # Second row: (150 - 100) / 100 * 100 = 50%
        assert daily_growth.iloc[1]['sales_growth'] == 50.0

        # Third row: (120 - 150) / 150 * 100 = -20%
        assert daily_growth.iloc[2]['sales_growth'] == -20.0

    def test_growth_rate_zero_division_handling(self):
        """Zero previous value should result in NaN (Critical Fix #4)"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 0, 'price': 100},  # 0
            {'date': '2024-01-02', 'product': 'A', 'quantity': 1, 'price': 100},  # 100
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        daily_growth = analyzer.calculate_growth_rate(daily, 'sales', shift_periods=1)

        # Division by zero should result in NaN
        assert pd.isna(daily_growth.iloc[1]['sales_growth'])

    def test_growth_rate_absolute_value(self):
        """Absolute growth should be calculated"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 1, 'price': 100},
            {'date': '2024-01-02', 'product': 'A', 'quantity': 1, 'price': 150},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        daily_growth = analyzer.calculate_growth_rate(daily, 'sales', shift_periods=1)

        # Absolute growth: 150 - 100 = 50
        assert daily_growth.iloc[1]['sales_growth_abs'] == 50

    def test_growth_rate_insufficient_data(self):
        """Insufficient data should result in all NaN"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 1, 'price': 100},
            {'date': '2024-01-02', 'product': 'A', 'quantity': 1, 'price': 150},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        daily = analyzer.aggregate_by_period('D')
        # Requesting shift of 7 days, but only 2 days data
        daily_growth = analyzer.calculate_growth_rate(daily, 'sales', shift_periods=7)

        # All growth values should be NaN
        assert daily_growth['sales_growth'].isna().all()


class TestSalesAnalyzerTopProducts:
    """Top products tests (Critical Fix #13)"""

    def test_get_top_products_basic(self):
        """Top products should be sorted correctly"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 10, 'price': 100},  # 1000
            {'date': '2024-01-01', 'product': 'B', 'quantity': 5, 'price': 100},   # 500
            {'date': '2024-01-01', 'product': 'C', 'quantity': 20, 'price': 100},  # 2000
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        top_products = analyzer.get_top_products(top_n=3, metric='sales')

        # Should be sorted by sales descending
        assert len(top_products) == 3
        assert top_products.iloc[0]['product'] == 'C'  # 2000
        assert top_products.iloc[1]['product'] == 'A'  # 1000
        assert top_products.iloc[2]['product'] == 'B'  # 500

    def test_get_top_products_limit(self):
        """Top N should be limited correctly (Critical Fix #13)"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': f'P{i}', 'quantity': i, 'price': 100}
            for i in range(1, 6)  # 5 products
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        # Request top 3
        top_products = analyzer.get_top_products(top_n=3, metric='sales')
        assert len(top_products) == 3

    def test_get_top_products_auto_adjust(self):
        """Top N should auto-adjust to available products (Critical Fix #13)"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 1, 'price': 100},
            {'date': '2024-01-01', 'product': 'B', 'quantity': 2, 'price': 100},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        # Request top 10, but only 2 products available
        top_products = analyzer.get_top_products(top_n=10, metric='sales')
        assert len(top_products) == 2  # Should return only 2


class TestSalesAnalyzerPareto:
    """Pareto analysis tests (Critical Fix #4)"""

    def test_pareto_basic(self):
        """Pareto analysis should calculate correctly"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 10, 'price': 100},  # 1000
            {'date': '2024-01-01', 'product': 'B', 'quantity': 5, 'price': 100},   # 500
            {'date': '2024-01-01', 'product': 'C', 'quantity': 3, 'price': 100},   # 300
            {'date': '2024-01-01', 'product': 'D', 'quantity': 1, 'price': 100},   # 100
            {'date': '2024-01-01', 'product': 'E', 'quantity': 1, 'price': 100},   # 100
        ])
        # Total: 2000

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        pareto_df, pareto_summary = analyzer.analyze_pareto('sales')

        # Check cumulative percentage
        assert pareto_df.iloc[0]['cumulative_pct'] == 50.0   # 1000/2000
        assert pareto_df.iloc[1]['cumulative_pct'] == 75.0   # 1500/2000
        assert pareto_df.iloc[-1]['cumulative_pct'] == 100.0

        # Check summary
        assert pareto_summary['total_products'] == 5
        assert pareto_summary['top_20_pct_products'] == 1  # 20% of 5 = 1

    def test_pareto_zero_total_handling(self):
        """Zero total sales should be handled (Critical Fix #4)"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 0, 'price': 100},
            {'date': '2024-01-01', 'product': 'B', 'quantity': 0, 'price': 100},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        pareto_df, pareto_summary = analyzer.analyze_pareto('sales')

        # Should not crash, return zero stats
        assert pareto_summary['total_sales'] == 0
        assert pareto_summary['top_20_pct_contribution'] == 0.0

    def test_pareto_cumulative_monotonic(self):
        """Cumulative percentage should be monotonically increasing"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': f'P{i}', 'quantity': i, 'price': 100}
            for i in range(1, 11)
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        pareto_df, _ = analyzer.analyze_pareto('sales')

        # Cumulative should always increase
        cumulative_pct = pareto_df['cumulative_pct'].values
        assert all(cumulative_pct[i] <= cumulative_pct[i+1]
                  for i in range(len(cumulative_pct)-1))


class TestSalesAnalyzerSummaryStats:
    """Summary statistics tests"""

    def test_summary_statistics(self):
        """Summary statistics should be accurate"""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'product': 'A', 'quantity': 2, 'price': 100},
            {'date': '2024-01-02', 'product': 'B', 'quantity': 3, 'price': 200},
            {'date': '2024-01-03', 'product': 'A', 'quantity': 1, 'price': 100},
        ])

        analyzer = SalesAnalyzer(df, date_column='date', product_column='product',
                                quantity_column='quantity', price_column='price')

        summary = analyzer.get_summary_statistics()

        assert summary['total_sales'] == 900  # 200 + 600 + 100
        assert summary['total_quantity'] == 6  # 2 + 3 + 1
        assert summary['total_transactions'] == 3
        assert summary['unique_products'] == 2  # A, B
        assert summary['avg_transaction_value'] == 300  # 900 / 3
        assert summary['date_range']['days'] == 2  # Jan 1 to Jan 3


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
