"""
GPT Analyzer Test Script
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 환경변수 로드
load_dotenv()

print("=" * 60)
print("GPT Analyzer Test")
print("=" * 60)

# 1. 환경변수 확인
api_key = os.getenv("OPENAI_API_KEY")
print(f"\n1. API Key Load Test:")
if api_key:
    print(f"   [OK] API Key Found: {api_key[:20]}...{api_key[-4:]}")
else:
    print("   [FAIL] No API Key")
    exit(1)

# 2. GPTAnalyzer 임포트 테스트
print(f"\n2. GPTAnalyzer Import Test:")
try:
    from modules.gpt_analyzer import GPTAnalyzer
    print("   [OK] GPTAnalyzer Import Success")
except Exception as e:
    print(f"   [FAIL] Import Failed: {str(e)}")
    exit(1)

# 3. GPTAnalyzer 인스턴스 생성 테스트
print(f"\n3. GPTAnalyzer Instance Creation Test:")
try:
    gpt = GPTAnalyzer(api_key=api_key)
    print("   [OK] GPTAnalyzer Instance Created")
except Exception as e:
    print(f"   [FAIL] Instance Creation Failed: {str(e)}")
    exit(1)

# 4. 샘플 데이터 생성
print(f"\n4. Sample Data Creation:")
sample_rfm = pd.DataFrame({
    'customerid': [1, 2, 3, 4, 5],
    'Recency': [10, 20, 100, 5, 200],
    'Frequency': [10, 5, 2, 15, 1],
    'Monetary': [10000, 5000, 1000, 20000, 500]
})

sample_cluster_summary = pd.DataFrame({
    'cluster': [0, 1],
    'cluster_name': ['VIP Customer', 'Dormant Customer'],
    '고객 수': [2, 3],
    '고객 비율(%)': [40.0, 60.0],
    'Recency_평균': [7.5, 106.7],
    'Frequency_평균': [12.5, 2.7],
    'Monetary_평균': [15000, 2166.7],
    'Monetary_총합': [30000, 6500]
})

print("   [OK] Sample Data Created")
print(f"   - RFM Data: {len(sample_rfm)} rows")
print(f"   - Cluster Summary: {len(sample_cluster_summary)} clusters")

# 5. RFM 해석 테스트
print(f"\n5. RFM Analysis Test:")
print("   (Calling GPT API... may take 10-20 seconds)")
try:
    result = gpt.analyze_rfm_insights(sample_rfm, sample_cluster_summary)
    print("   [OK] RFM Analysis Success")
    print(f"\nResult Preview:")
    print("-" * 60)
    print(result[:500] + "..." if len(result) > 500 else result)
    print("-" * 60)
except Exception as e:
    print(f"   [FAIL] RFM Analysis Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("[OK] All Tests Passed!")
print("=" * 60)
