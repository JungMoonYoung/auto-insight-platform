"""
예시 SQL 쿼리 저장 스크립트
DAY 35: Phase 4
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.sql_query_generator import SQLQueryGenerator


def save_all_example_queries():
    """모든 예시 SQL 쿼리를 파일로 저장"""
    generator = SQLQueryGenerator()
    output_dir = 'docs/sql_examples'

    # 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 모든 쿼리 생성 및 저장
    queries = {
        '01_rfm_analysis': generator.generate_rfm_query(),
        '02_rfm_summary': generator.generate_rfm_summary_query(),
        '03_sales_trend_daily': generator.generate_sales_trend_query(period='daily'),
        '04_sales_trend_monthly': generator.generate_sales_trend_query(period='monthly'),
        '05_pareto_analysis': generator.generate_pareto_query(),
        '06_sentiment_analysis': generator.generate_sentiment_query(),
        '07_top_customers': generator.generate_top_customers_query(),
    }

    saved_files = []
    for query_name, query in queries.items():
        file_path = generator.save_query_to_file(query_name, query, output_dir)
        saved_files.append(file_path)
        print(f"Saved: {query_name}.sql")

    print(f"\nTotal {len(queries)} SQL queries saved")
    print(f"Location: {output_dir}/")


if __name__ == "__main__":
    save_all_example_queries()
