"""
GPT API Analyzer Module
OpenAI GPT를 사용한 고급 텍스트 분석
DAY 27: 부정 리뷰 필터링 + Rate Limit 핸들링 추가
"""

import pandas as pd
import json
import time
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

try:
    import openai
    from openai import RateLimitError, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("WARNING openai 패키지가 설치되지 않았습니다. pip install openai")


class GPTAnalyzer:
    """GPT를 활용한 고급 리뷰 분석"""

    # Rate Limit 설정
    MAX_RETRIES = 5
    INITIAL_DELAY = 1.0  # 초
    MAX_DELAY = 60.0  # 최대 60초
    BATCH_DELAY = 0.5  # 배치 간 딜레이

    # 모델별 가격 (2025년 1월 기준, USD per 1M tokens)
    # 출처: https://openai.com/pricing
    PRICING = {
        'gpt-4o-mini': {'input': 0.15, 'output': 0.6},
        'gpt-4o': {'input': 2.50, 'output': 10.0},
        'gpt-4-turbo': {'input': 10.0, 'output': 30.0},
        'gpt-4': {'input': 30.0, 'output': 60.0},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
    }

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Args:
            api_key: OpenAI API 키 (None이면 환경변수에서 가져옴)
            model: 사용할 모델 (gpt-4o-mini 권장 - 저렴하고 빠름)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지를 설치하세요: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. api_key 파라미터나 OPENAI_API_KEY 환경변수를 설정하세요.")

        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        self.total_tokens = 0
        self.total_cost = 0.0

        # 모델별 가격 설정
        if model in self.PRICING:
            self.input_price = self.PRICING[model]['input']
            self.output_price = self.PRICING[model]['output']
            logger.info(f"Model: {model} (${self.input_price}/M input, ${self.output_price}/M output)")
        else:
            # 알 수 없는 모델은 gpt-4o-mini 가격으로 기본 설정
            logger.warning(f"Unknown model '{model}'. Using gpt-4o-mini pricing as fallback.")
            self.input_price = self.PRICING['gpt-4o-mini']['input']
            self.output_price = self.PRICING['gpt-4o-mini']['output']

    def _call_with_retry(self, func, *args, **kwargs):
        """
        Exponential backoff으로 API 호출 재시도

        Args:
            func: 호출할 함수
            *args, **kwargs: 함수 인자

        Returns:
            API 응답
        """
        delay = self.INITIAL_DELAY

        for attempt in range(self.MAX_RETRIES):
            try:
                response = func(*args, **kwargs)

                # 토큰 사용량 추적
                if hasattr(response, 'usage'):
                    self.total_tokens += response.usage.total_tokens
                    # 모델별 가격 적용
                    input_cost = (response.usage.prompt_tokens / 1_000_000) * self.input_price
                    output_cost = (response.usage.completion_tokens / 1_000_000) * self.output_price
                    self.total_cost += (input_cost + output_cost)

                return response

            except RateLimitError as e:
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(f"Rate Limit 초과: 최대 재시도 횟수 도달 ({self.MAX_RETRIES})")
                    raise

                logger.warning(f"Rate Limit 발생. {delay:.1f}초 후 재시도 ({attempt + 1}/{self.MAX_RETRIES})")
                time.sleep(delay)
                delay = min(delay * 2, self.MAX_DELAY)  # Exponential backoff

            except APIError as e:
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(f"API 오류: {str(e)}")
                    raise

                logger.warning(f"API 오류 발생. {delay:.1f}초 후 재시도: {str(e)}")
                time.sleep(delay)
                delay = min(delay * 2, self.MAX_DELAY)

            except Exception as e:
                logger.error(f"예상치 못한 오류: {str(e)}")
                raise

        raise Exception("API 호출 실패: 최대 재시도 횟수 초과")
    
    def _filter_negative_reviews(self, df: pd.DataFrame, rating_column: str = 'rating',
                                  text_column: str = 'review_text', threshold: float = 3.0) -> List[str]:
        """
        부정 리뷰만 필터링 (비용 절감)

        Args:
            df: 리뷰 DataFrame
            rating_column: 평점 컬럼명
            text_column: 리뷰 텍스트 컬럼명
            threshold: 부정 리뷰 기준 (이하)

        Returns:
            부정 리뷰 텍스트 리스트
        """
        if rating_column in df.columns:
            negative_df = df[df[rating_column] <= threshold]
            logger.info(f"부정 리뷰 필터링: {len(negative_df)}/{len(df)} (평점 <={threshold})")
        else:
            logger.warning(f"평점 컬럼 '{rating_column}' 없음. 전체 리뷰 사용")
            negative_df = df

        if text_column in negative_df.columns:
            return negative_df[text_column].dropna().tolist()
        else:
            logger.error(f"텍스트 컬럼 '{text_column}' 없음")
            return []

    def analyze_sentiment_batch(self, reviews: List[str], max_reviews: int = 100,
                                filter_negative: bool = False,
                                df: Optional[pd.DataFrame] = None,
                                rating_column: str = 'rating',
                                text_column: str = 'review_text') -> List[Dict]:
        """
        리뷰 감성을 GPT로 재분석 (문맥 이해)

        Args:
            reviews: 리뷰 텍스트 리스트
            max_reviews: 최대 분석 개수 (비용 절감)
            filter_negative: 부정 리뷰만 분석 (비용 최적화, df 필요)
            df: DataFrame (filter_negative=True일 때 필수)
            rating_column: 평점 컬럼명 (filter_negative=True일 때 사용)
            text_column: 리뷰 텍스트 컬럼명 (filter_negative=True일 때 사용)

        Returns:
            감성 분석 결과 리스트

        Note:
            filter_negative=True를 사용하려면 df 파라미터에 DataFrame을 전달해야 합니다.
        """
        logger.info(f"GPT 감성 분석 시작 (최대 {max_reviews}개, 부정 필터: {filter_negative})")

        # 부정 리뷰 필터링 (df 제공 시에만)
        if filter_negative:
            if df is not None:
                reviews = self._filter_negative_reviews(
                    df,
                    rating_column=rating_column,
                    text_column=text_column
                )
                logger.info(f"부정 리뷰 필터링 완료: {len(reviews)}개")
            else:
                logger.warning("filter_negative=True but df is None. Skipping filtering.")

        # 샘플링 (너무 많으면 비용 증가)
        if len(reviews) > max_reviews:
            import random
            reviews = random.sample(reviews, max_reviews)
            logger.info(f"리뷰 샘플링: {len(reviews)}개")
        
        results = []

        # 배치로 묶어서 처리 (10개씩)
        batch_size = 10
        total_batches = (len(reviews) + batch_size - 1) // batch_size

        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i+batch_size]
            batch_num = i // batch_size + 1

            logger.debug(f"배치 {batch_num}/{total_batches} 처리 중...")

            prompt = f"""다음 리뷰들의 감성을 분석해주세요. 각 리뷰에 대해 JSON 형식으로 답변하세요.

리뷰들:
{json.dumps(batch, ensure_ascii=False)}

각 리뷰에 대해 다음 형식으로 답변하세요:
{{
  "results": [
    {{
      "sentiment": "positive" or "neutral" or "negative",
      "confidence": 0.0 ~ 1.0,
      "reason": "짧은 이유 설명"
    }}
  ]
}}

문맥을 정확히 이해하세요. 예: "별로 나쁘지 않다" = neutral/positive"""

            try:
                # Retry 래퍼로 API 호출
                response = self._call_with_retry(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 한국어 리뷰 감성 분석 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )

                batch_results = json.loads(response.choices[0].message.content)
                results.extend(batch_results.get('results', []))

                # 배치 간 딜레이 (Rate Limit 방지)
                if i + batch_size < len(reviews):
                    time.sleep(self.BATCH_DELAY)
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"GPT 응답 파싱 오류 (배치 {batch_num}/{total_batches}): {str(e)}")
                # 오류 시 기본값
                results.extend([{"sentiment": "neutral", "confidence": 0.5, "reason": "분석 실패"}] * len(batch))
            except Exception as e:
                logger.error(f"GPT 분석 오류 (배치 {batch_num}/{total_batches}): {str(e)}")
                # 오류 시 기본값
                results.extend([{"sentiment": "neutral", "confidence": 0.5, "reason": "분석 실패"}] * len(batch))

        logger.info(f"감성 분석 완료: {len(results)}개 리뷰, 비용: ${self.total_cost:.4f}, 토큰: {self.total_tokens}")
        return results

    def get_cost_info(self) -> Dict[str, float]:
        """
        API 사용 비용 정보 반환

        Returns:
            {'total_tokens': int, 'total_cost': float}
        """
        return {
            'total_tokens': self.total_tokens,
            'total_cost': round(self.total_cost, 4)
        }

    def reset_cost_tracking(self):
        """비용 추적 초기화"""
        self.total_tokens = 0
        self.total_cost = 0.0
        logger.info("비용 추적 초기화됨")
    
    def generate_summary(self, reviews: List[str], max_reviews: int = 50) -> str:
        """
        리뷰 전체를 3-5줄로 요약
        
        Args:
            reviews: 리뷰 텍스트 리스트
            max_reviews: 최대 분석 개수
        
        Returns:
            요약 텍스트
        """
        # Generating summary with GPT
        
        if len(reviews) > max_reviews:
            import random
            reviews = random.sample(reviews, max_reviews)
        
        reviews_text = "\n".join([f"- {r}" for r in reviews[:50]])
        
        prompt = f"""다음 리뷰들을 3-5문장으로 핵심만 요약해주세요:

{reviews_text}

요약 시 포함할 내용:
1. 고객들의 전반적인 만족도
2. 가장 많이 언급된 장점
3. 가장 많이 언급된 단점
4. 특이사항이나 트렌드

간결하고 비즈니스 인사이트 중심으로 작성하세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 비즈니스 분석가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"GPT 요약 생성 오류: {str(e)}")
            return "요약 생성에 실패했습니다."
    
    def detect_issues(self, reviews: List[str], max_reviews: int = 50) -> Dict:
        """
        주요 이슈 자동 감지
        
        Args:
            reviews: 리뷰 텍스트 리스트
            max_reviews: 최대 분석 개수
        
        Returns:
            이슈 딕셔너리
        """
        # Detecting issues with GPT
        
        if len(reviews) > max_reviews:
            import random
            reviews = random.sample(reviews, max_reviews)
        
        reviews_text = "\n".join([f"- {r}" for r in reviews[:50]])
        
        prompt = f"""다음 리뷰들에서 주요 이슈나 문제점을 찾아주세요:

{reviews_text}

다음 JSON 형식으로 답변하세요:
{{
  "critical_issues": [
    {{
      "issue": "이슈 제목",
      "severity": "high" or "medium" or "low",
      "description": "상세 설명",
      "affected_count": "대략적인 영향 받은 고객 수"
    }}
  ],
  "positive_highlights": [
    "긍정적인 특징 1",
    "긍정적인 특징 2"
  ],
  "recommendations": [
    "개선 제안 1",
    "개선 제안 2"
  ]
}}"""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 고객 피드백 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"GPT issues detection error: {str(e)}")
            return {
                "critical_issues": [],
                "positive_highlights": [],
                "recommendations": []
            }
    
    def categorize_reviews(self, reviews: List[str], max_reviews: int = 50) -> Dict:
        """
        리뷰를 카테고리별로 자동 분류
        
        Args:
            reviews: 리뷰 텍스트 리스트
            max_reviews: 최대 분석 개수
        
        Returns:
            카테고리별 분류 결과
        """
        # Categorizing reviews with GPT
        
        if len(reviews) > max_reviews:
            import random
            reviews = random.sample(reviews, max_reviews)
        
        reviews_text = "\n".join([f"- {r}" for r in reviews[:50]])
        
        prompt = f"""다음 리뷰들을 주제별로 분류하고, 각 카테고리별 비율을 계산해주세요:

{reviews_text}

다음 JSON 형식으로 답변하세요:
{{
  "categories": {{
    "제품품질": {{"percentage": 45, "keywords": ["좋다", "훌륭"]}},
    "배송": {{"percentage": 30, "keywords": ["빠르다", "늦다"]}},
    "고객서비스": {{"percentage": 15, "keywords": [...]}},
    "가격": {{"percentage": 10, "keywords": [...]}}
  }}
}}

주요 카테고리: 제품품질, 배송, 고객서비스, 가격, 포장, 기타"""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 리뷰 분류 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=800
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"GPT categorization error: {str(e)}")
            return {"categories": {}}
    
    def generate_advanced_insights(self, reviews: List[str], 
                                   sentiment_summary: Dict,
                                   max_reviews: int = 50) -> str:
        """
        고급 비즈니스 인사이트 생성
        
        Args:
            reviews: 리뷰 텍스트 리스트
            sentiment_summary: 기본 감성 분석 결과
            max_reviews: 최대 분석 개수
        
        Returns:
            인사이트 텍스트
        """
        # Generating advanced insights with GPT
        
        if len(reviews) > max_reviews:
            import random
            reviews = random.sample(reviews, max_reviews)
        
        reviews_text = "\n".join([f"- {r}" for r in reviews[:30]])
        
        prompt = f"""다음 리뷰들과 통계를 분석하여 실행 가능한 비즈니스 인사이트를 제공해주세요:

통계:
- 전체 리뷰: {sentiment_summary.get('total_reviews', 0)}개
- 긍정: {sentiment_summary.get('positive_ratio', 0):.1f}%
- 부정: {sentiment_summary.get('negative_ratio', 0):.1f}%

샘플 리뷰:
{reviews_text}

다음 내용을 포함하여 분석해주세요:
1. 가장 시급한 개선 포인트 (우선순위별)
2. 경쟁 우위 요소
3. 고객 만족도 향상 전략
4. 예상되는 비즈니스 영향

실무에서 바로 사용할 수 있는 구체적인 제안을 해주세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 데이터 기반 비즈니스 전략 컨설턴트입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"GPT 인사이트 생성 오류: {str(e)}")
            return "인사이트 생성에 실패했습니다."

    # ===== E-commerce RFM 분석 메서드 =====

    def analyze_rfm_insights(self, rfm_df: pd.DataFrame, cluster_summary: pd.DataFrame) -> str:
        """
        RFM 분석 결과를 GPT로 해석

        Args:
            rfm_df: RFM 데이터프레임
            cluster_summary: 군집 요약 데이터

        Returns:
            str: GPT의 RFM 분석 해석
        """
        print("🤖 GPT로 RFM 분석 해석 중...")

        # 데이터 요약
        total_customers = len(rfm_df)
        total_revenue = cluster_summary['Monetary_총합'].sum()
        avg_recency = rfm_df['Recency'].mean()
        avg_frequency = rfm_df['Frequency'].mean()
        avg_monetary = rfm_df['Monetary'].mean()

        # 군집별 정보
        cluster_info = []
        for _, row in cluster_summary.iterrows():
            cluster_info.append({
                '세그먼트': row['cluster_name'],
                '고객수': int(row['고객 수']),
                '비율': f"{row['고객 비율(%)']}%",
                '평균_Recency': round(row['Recency_평균'], 1),
                '평균_Frequency': round(row['Frequency_평균'], 1),
                '평균_Monetary': round(row['Monetary_평균'], 0),
                '총매출': round(row['Monetary_총합'], 0)
            })

        prompt = f"""다음은 E-commerce 고객 RFM 분석 결과입니다. 전문가 관점에서 해석해주세요.

**전체 통계:**
- 총 고객 수: {total_customers:,}명
- 총 매출: ₩{total_revenue:,.0f}
- 평균 Recency: {avg_recency:.1f}일 (마지막 구매 후 경과 일수)
- 평균 Frequency: {avg_frequency:.1f}회
- 평균 Monetary: ₩{avg_monetary:,.0f}

**군집별 상세 정보:**
{json.dumps(cluster_info, ensure_ascii=False, indent=2)}

**요청사항:**
1. 전체적인 고객 포트폴리오 건강도 평가
2. 각 세그먼트의 특징 및 비즈니스 의미
3. 주목해야 할 위험 신호 또는 기회
4. 우선순위가 높은 세그먼트와 그 이유
5. 데이터에서 발견되는 특이사항

한국어로 간결하고 명확하게 답변하세요. 구체적인 숫자를 인용하세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 E-commerce 데이터 분석 및 CRM 전략 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT RFM 해석 오류: {str(e)}")
            return f"분석 해석에 실패했습니다: {str(e)}"

    def generate_segment_strategy(self, cluster_summary: pd.DataFrame) -> str:
        """
        각 고객 세그먼트별 마케팅 전략 제안

        Args:
            cluster_summary: 군집 요약 데이터

        Returns:
            str: 세그먼트별 전략 제안
        """
        print("🤖 GPT로 세그먼트 전략 생성 중...")

        # 군집별 정보
        cluster_info = []
        for _, row in cluster_summary.iterrows():
            cluster_info.append({
                '세그먼트': row['cluster_name'],
                '고객수': int(row['고객 수']),
                '비율': f"{row['고객 비율(%)']}%",
                '평균_Recency': round(row['Recency_평균'], 1),
                '평균_Frequency': round(row['Frequency_평균'], 1),
                '평균_Monetary': round(row['Monetary_평균'], 0),
                '총매출기여도': round(row['Monetary_총합'] / cluster_summary['Monetary_총합'].sum() * 100, 1)
            })

        prompt = f"""다음 고객 세그먼트별로 구체적인 마케팅 전략을 제안해주세요.

**세그먼트 정보:**
{json.dumps(cluster_info, ensure_ascii=False, indent=2)}

**각 세그먼트별로 제안해주세요:**
1. **목표**: 이 세그먼트에 대한 핵심 목표 (예: 재구매 유도, 충성도 강화, 재활성화 등)
2. **추천 액션**: 구체적인 마케팅 액션 3-5개 (예: 쿠폰, 이메일, VIP 프로그램 등)
3. **메시지 톤**: 커뮤니케이션 방식 및 메시지 예시
4. **예상 효과**: 이 전략의 기대 효과
5. **예산 우선순위**: High/Medium/Low

실행 가능한 구체적인 전략을 제시하세요. 한국 E-commerce 시장 특성을 고려하세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 E-commerce 마케팅 전략 및 CRM 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT 전략 생성 오류: {str(e)}")
            return f"전략 생성에 실패했습니다: {str(e)}"

    def simulate_revenue_growth(self, rfm_df: pd.DataFrame, cluster_summary: pd.DataFrame) -> str:
        """
        시나리오별 매출 성장 시뮬레이션

        Args:
            rfm_df: RFM 데이터프레임
            cluster_summary: 군집 요약 데이터

        Returns:
            str: 매출 시뮬레이션 결과
        """
        print("🤖 GPT로 매출 시뮬레이션 중...")

        # 현재 상태
        current_revenue = cluster_summary['Monetary_총합'].sum()
        total_customers = len(rfm_df)

        # 군집별 정보
        cluster_info = []
        for _, row in cluster_summary.iterrows():
            cluster_info.append({
                '세그먼트': row['cluster_name'],
                '고객수': int(row['고객 수']),
                '평균_구매액': round(row['Monetary_평균'], 0),
                '평균_구매빈도': round(row['Frequency_평균'], 1),
                '총매출': round(row['Monetary_총합'], 0),
                '매출기여도': round(row['Monetary_총합'] / current_revenue * 100, 1)
            })

        prompt = f"""다음 RFM 데이터를 바탕으로 3가지 시나리오별 매출 성장을 시뮬레이션하세요.

**현재 상태:**
- 총 고객: {total_customers:,}명
- 현재 총매출: ₩{current_revenue:,.0f}

**세그먼트별 현황:**
{json.dumps(cluster_info, ensure_ascii=False, indent=2)}

**시뮬레이션 시나리오:**

1. **보수적 시나리오** (현실적, 달성 가능성 높음):
   - VIP/충성 고객: 구매 빈도 +10% 증가
   - 이탈 위험 고객: 30% 재활성화
   - 신규 고객: 20% 재구매 전환

2. **중립적 시나리오** (일반적인 마케팅 성과):
   - VIP/충성 고객: 구매 빈도 +20%, 구매액 +15% 증가
   - 이탈 위험 고객: 50% 재활성화
   - 신규 고객: 40% 재구매 전환
   - 휴면 고객: 10% 재활성화

3. **낙관적 시나리오** (공격적 마케팅 + 높은 투자):
   - VIP/충성 고객: 구매 빈도 +30%, 구매액 +25% 증가
   - 이탈 위험 고객: 70% 재활성화
   - 신규 고객: 60% 재구매 전환, 구매액 +20%
   - 휴면 고객: 25% 재활성화

**요청사항:**
각 시나리오별로:
1. 예상 총매출 (구체적 금액)
2. 매출 증가율 (%)
3. 세그먼트별 기여도 변화
4. 이 시나리오를 달성하기 위한 핵심 조건
5. 필요한 예상 마케팅 비용 (매출 대비 %)

계산 과정을 명확히 보여주고, 실행 가능한 인사이트를 제공하세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 데이터 기반 비즈니스 성장 전략 및 재무 시뮬레이션 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT 매출 시뮬레이션 오류: {str(e)}")
            return f"매출 시뮬레이션에 실패했습니다: {str(e)}"

    def analyze_portfolio_risk(self, rfm_df: pd.DataFrame, cluster_summary: pd.DataFrame) -> str:
        """
        고객 포트폴리오 리스크 분석

        Args:
            rfm_df: RFM 데이터프레임
            cluster_summary: 군집 요약 데이터

        Returns:
            str: 리스크 분석 결과
        """
        print("🤖 GPT로 포트폴리오 리스크 분석 중...")

        # 리스크 지표 계산
        total_revenue = cluster_summary['Monetary_총합'].sum()
        total_customers = len(rfm_df)

        # 상위 20% 고객 매출 집중도 (파레토 법칙)
        rfm_sorted = rfm_df.sort_values('Monetary', ascending=False)
        top_20_pct_customers = int(len(rfm_sorted) * 0.2)
        top_20_revenue = rfm_sorted.head(top_20_pct_customers)['Monetary'].sum()
        concentration_ratio = (top_20_revenue / total_revenue * 100) if total_revenue > 0 else 0

        # 이탈 위험 고객 비율
        churn_segments = cluster_summary[cluster_summary['cluster_name'].str.contains('이탈|휴면', na=False)]
        churn_customers = churn_segments['고객 수'].sum() if not churn_segments.empty else 0
        churn_ratio = (churn_customers / total_customers * 100) if total_customers > 0 else 0
        churn_revenue = churn_segments['Monetary_총합'].sum() if not churn_segments.empty else 0

        # 신규 고객 비율
        new_segments = cluster_summary[cluster_summary['cluster_name'].str.contains('신규', na=False)]
        new_customers = new_segments['고객 수'].sum() if not new_segments.empty else 0
        new_ratio = (new_customers / total_customers * 100) if total_customers > 0 else 0

        # 평균 recency
        avg_recency = rfm_df['Recency'].mean()

        # 군집별 정보
        cluster_info = []
        for _, row in cluster_summary.iterrows():
            cluster_info.append({
                '세그먼트': row['cluster_name'],
                '고객수': int(row['고객 수']),
                '비율': f"{row['고객 비율(%)']}%",
                '매출기여도': round(row['Monetary_총합'] / total_revenue * 100, 1),
                '평균_Recency': round(row['Recency_평균'], 1)
            })

        prompt = f"""다음 E-commerce 고객 포트폴리오의 리스크를 분석하고 경고 신호를 찾아주세요.

**전체 지표:**
- 총 고객: {total_customers:,}명
- 총 매출: ₩{total_revenue:,.0f}
- 상위 20% 고객 매출 집중도: {concentration_ratio:.1f}%
- 이탈 위험/휴면 고객 비율: {churn_ratio:.1f}% ({churn_customers}명, 매출 ₩{churn_revenue:,.0f})
- 신규 고객 비율: {new_ratio:.1f}%
- 평균 마지막 구매 후 경과일: {avg_recency:.1f}일

**세그먼트별 분포:**
{json.dumps(cluster_info, ensure_ascii=False, indent=2)}

**요청사항:**
1. **주요 리스크 요인 (3-5개)**: 현재 포트폴리오의 취약점
2. **리스크 우선순위**: High/Medium/Low로 분류하고 이유 설명
3. **경고 신호**: 즉시 대응이 필요한 지표
4. **재무적 영향**: 각 리스크가 매출에 미칠 수 있는 영향 (금액 추정)
5. **리스크 완화 전략**: 구체적인 대응 방안 3-5개
6. **모니터링 지표**: 정기적으로 추적해야 할 KPI

비즈니스 연속성과 성장 가능성 관점에서 분석하세요."""

        try:
            response = self._call_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 E-commerce 비즈니스 리스크 관리 및 재무 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT 리스크 분석 오류: {str(e)}")
            return f"리스크 분석에 실패했습니다: {str(e)}"


if __name__ == "__main__":
    # 테스트 코드
    print("GPT Analyzer 모듈")
    print("사용하려면 OpenAI API 키가 필요합니다.")
    print("사용법:")
    print("""
    from modules.gpt_analyzer import GPTAnalyzer
    
    analyzer = GPTAnalyzer(api_key="your-api-key")
    
    # 리뷰 요약
    summary = analyzer.generate_summary(reviews)
    
    # 이슈 감지
    issues = analyzer.detect_issues(reviews)
    
    # 고급 인사이트
    insights = analyzer.generate_advanced_insights(reviews, sentiment_summary)
    """)
