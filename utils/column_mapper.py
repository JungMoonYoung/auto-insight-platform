"""
컬럼 자동 매핑 모듈
사용자 데이터의 컬럼을 표준 컬럼에 자동으로 매핑
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# 로깅 설정
logger = logging.getLogger(__name__)


class ColumnMapper:
    """컬럼 자동 매핑 클래스"""

    # 매핑 임계값 상수
    MIN_SIMILARITY_THRESHOLD = 50  # 최소 유사도 임계값
    ID_UNIQUE_RATIO_THRESHOLD = 0.9  # ID 컬럼 고유값 비율
    DATE_PARSE_RATIO_THRESHOLD = 0.7  # 날짜 파싱 성공 비율

    # 텍스트 길이 임계값
    TEXT_LENGTH_LONG = 50  # 긴 텍스트
    TEXT_LENGTH_MEDIUM = 20  # 중간 텍스트

    # 타입 추론 점수
    SCORE_HIGH = 90
    SCORE_MEDIUM_HIGH = 80
    SCORE_MEDIUM = 70
    SCORE_MEDIUM_LOW = 60
    SCORE_LOW = 30

    # 평점 범위
    RATING_MIN = 0
    RATING_MAX = 10

    # E-commerce 표준 컬럼 정의
    ECOMMERCE_COLUMNS = {
        'customerid': {
            'names': ['customerid', 'customer_id', 'customer', 'cust_id', 'user_id', 'userid', '고객ID', '고객아이디', '회원ID'],
            'type': 'id',
            'required': True
        },
        'invoicedate': {
            'names': ['invoicedate', 'invoice_date', 'date', 'order_date', 'orderdate', 'purchase_date', '주문일', '구매일', '날짜'],
            'type': 'date',
            'required': True
        },
        'quantity': {
            'names': ['quantity', 'qty', 'amount', 'count', '수량', '개수'],
            'type': 'numeric',
            'required': True
        },
        'unitprice': {
            'names': ['unitprice', 'unit_price', 'price', 'amount', '가격', '단가', '금액'],
            'type': 'numeric',
            'required': True
        }
    }

    # 리뷰 분석 표준 컬럼 정의
    REVIEW_COLUMNS = {
        'review_text': {
            'names': ['review', 'text', 'comment', 'review_text', 'content', '리뷰', '내용', '댓글', '평가'],
            'type': 'text',
            'required': True
        },
        'rating': {
            'names': ['rating', 'score', 'star', 'point', '평점', '별점', '점수'],
            'type': 'rating',
            'required': False
        },
        'date': {
            'names': ['date', 'review_date', 'created_at', '날짜', '작성일'],
            'type': 'date',
            'required': False
        }
    }

    # 판매 분석 표준 컬럼 정의
    SALES_COLUMNS = {
        'date': {
            'names': ['date', 'sales_date', 'order_date', 'invoicedate', '날짜', '판매일', '주문일'],
            'type': 'date',
            'required': True
        },
        'product': {
            'names': ['product', 'product_name', 'item', 'description', '상품', '제품', '상품명'],
            'type': 'text',
            'required': True
        },
        'quantity': {
            'names': ['quantity', 'qty', 'amount', '수량', '개수'],
            'type': 'numeric',
            'required': True
        },
        'price': {
            'names': ['price', 'unitprice', 'unit_price', 'amount', '가격', '단가'],
            'type': 'numeric',
            'required': True
        }
    }

    AVAILABLE_DATA_TYPES = ['ecommerce', 'review', 'sales']

    def __init__(self, data_type: str = 'ecommerce'):
        """
        Args:
            data_type: 'ecommerce', 'review', 'sales' 중 하나

        Raises:
            ValueError: 지원하지 않는 데이터 타입인 경우
        """
        self.data_type = data_type

        if data_type == 'ecommerce':
            self.standard_columns = self.ECOMMERCE_COLUMNS
        elif data_type == 'review':
            self.standard_columns = self.REVIEW_COLUMNS
        elif data_type == 'sales':
            self.standard_columns = self.SALES_COLUMNS
        else:
            raise ValueError(
                f"Unknown data type: '{data_type}'. "
                f"Available types: {', '.join(self.AVAILABLE_DATA_TYPES)}"
            )

    @staticmethod
    def normalize_column_name(col_name: str) -> str:
        """
        컬럼명 정규화 (소문자, 공백/언더스코어 제거)

        Args:
            col_name: 원본 컬럼명

        Returns:
            정규화된 컬럼명
        """
        if not isinstance(col_name, str):
            return str(col_name)

        # 소문자 변환
        normalized = col_name.lower()

        # 공백, 언더스코어, 하이픈 제거
        normalized = normalized.replace(' ', '').replace('_', '').replace('-', '')

        return normalized

    def calculate_similarity(self, user_col: str, standard_col: str) -> int:
        """
        두 컬럼명의 유사도 계산 (FuzzyWuzzy)

        Args:
            user_col: 사용자 컬럼명
            standard_col: 표준 컬럼명

        Returns:
            유사도 점수 (0-100)
        """
        # 정규화
        user_normalized = self.normalize_column_name(user_col)
        standard_normalized = self.normalize_column_name(standard_col)

        # FuzzyWuzzy ratio 사용
        similarity = fuzz.ratio(user_normalized, standard_normalized)

        return similarity

    def find_best_match(self, user_col: str) -> Tuple[Optional[str], int]:
        """
        사용자 컬럼에 가장 유사한 표준 컬럼 찾기

        Args:
            user_col: 사용자 컬럼명

        Returns:
            (표준_컬럼명, 유사도_점수) 또는 (None, 0)
        """
        best_match = None
        best_score = 0

        for std_col, config in self.standard_columns.items():
            # 각 표준 컬럼의 모든 별칭과 비교
            for alias in config['names']:
                score = self.calculate_similarity(user_col, alias)

                if score > best_score:
                    best_score = score
                    best_match = std_col

        # 최소 임계값 이상만 반환
        if best_score >= self.MIN_SIMILARITY_THRESHOLD:
            return best_match, best_score
        else:
            return None, 0

    def auto_map_columns(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        데이터프레임의 컬럼을 자동으로 매핑 (중복 방지)

        Args:
            df: 사용자 데이터프레임

        Returns:
            매핑 결과 딕셔너리
            {
                '표준_컬럼명': {
                    'user_column': '사용자_컬럼명',
                    'confidence': 85,
                    'method': 'fuzzy',
                    'alternatives': ['other_col1', 'other_col2']  # 충돌 시
                }
            }

        Note:
            중복 매핑이 감지되면 신뢰도가 높은 것을 선택하고,
            낮은 것은 'alternatives'에 저장
        """
        # 1단계: 모든 사용자 컬럼에 대해 매핑 후보 수집
        candidates = {}  # {표준_컬럼: [(사용자_컬럼, 점수), ...]}

        for user_col in df.columns:
            std_col, score = self.find_best_match(user_col)

            if std_col:
                if std_col not in candidates:
                    candidates[std_col] = []
                candidates[std_col].append((user_col, score))

        # 2단계: 중복 매핑 해결 (신뢰도 기준)
        mapping_result = {}
        duplicates_detected = []

        for std_col, user_cols in candidates.items():
            if len(user_cols) == 1:
                # 중복 없음 - 바로 매핑
                user_col, score = user_cols[0]
                mapping_result[std_col] = {
                    'user_column': user_col,
                    'confidence': score,
                    'method': 'fuzzy'
                }
            else:
                # 중복 발생 - 점수 높은 순으로 정렬
                sorted_cols = sorted(user_cols, key=lambda x: x[1], reverse=True)
                best_col, best_score = sorted_cols[0]
                alternatives = [col for col, _ in sorted_cols[1:]]

                mapping_result[std_col] = {
                    'user_column': best_col,
                    'confidence': best_score,
                    'method': 'fuzzy',
                    'alternatives': alternatives
                }

                # 로깅
                duplicates_detected.append({
                    'standard': std_col,
                    'selected': best_col,
                    'rejected': alternatives
                })
                logger.warning(
                    f"Duplicate mapping detected for '{std_col}': "
                    f"selected '{best_col}' (score: {best_score}), "
                    f"rejected {alternatives}"
                )

        return mapping_result

    def get_missing_columns(self, mapping: Dict[str, Dict]) -> List[str]:
        """
        매핑되지 않은 필수 컬럼 찾기

        Args:
            mapping: 매핑 결과

        Returns:
            매핑되지 않은 필수 컬럼 리스트
        """
        missing = []

        for std_col, config in self.standard_columns.items():
            if config['required'] and std_col not in mapping:
                missing.append(std_col)

        return missing

    def validate_mapping(self, mapping: Dict[str, Dict]) -> Tuple[bool, List[str]]:
        """
        매핑 결과 검증 (필수 컬럼 존재 여부)

        Args:
            mapping: 매핑 결과

        Returns:
            (검증_성공_여부, 오류_메시지_리스트)
        """
        missing = self.get_missing_columns(mapping)

        if missing:
            error_messages = [f"필수 컬럼 '{col}'이(가) 매핑되지 않았습니다." for col in missing]
            return False, error_messages
        else:
            return True, []

    def get_mapping_summary(self, mapping: Dict[str, Dict]) -> str:
        """
        매핑 결과 요약 문자열

        Args:
            mapping: 매핑 결과

        Returns:
            요약 문자열
        """
        summary = []
        summary.append(f"데이터 타입: {self.data_type}")
        summary.append(f"매핑된 컬럼 수: {len(mapping)}/{len(self.standard_columns)}")
        summary.append("")

        for std_col, info in mapping.items():
            summary.append(f"  {std_col} ← {info['user_column']} (신뢰도: {info['confidence']}%)")

        missing = self.get_missing_columns(mapping)
        if missing:
            summary.append("")
            summary.append(f"[WARNING] 매핑되지 않은 필수 컬럼: {', '.join(missing)}")

        return "\n".join(summary)

    def analyze_column_data(self, df: pd.DataFrame, col_name: str) -> Dict[str, Any]:
        """
        컬럼 데이터 샘플 분석 (통계적 특성 추출)

        Args:
            df: 데이터프레임
            col_name: 분석할 컬럼명

        Returns:
            분석 결과 딕셔너리
            {
                'dtype': 데이터 타입,
                'unique_ratio': 고유값 비율,
                'missing_ratio': 결측치 비율,
                'is_date': 날짜 여부,
                'is_numeric': 숫자형 여부,
                'is_id': ID 컬럼 여부,
                'numeric_range': (min, max, mean) 또는 None,
                'avg_length': 평균 문자열 길이 (텍스트일 경우)
            }
        """
        col_data = df[col_name]
        total_rows = len(df)

        result = {
            'dtype': str(col_data.dtype),
            'unique_ratio': col_data.nunique() / total_rows if total_rows > 0 else 0,
            'missing_ratio': col_data.isna().sum() / total_rows if total_rows > 0 else 0,
            'is_date': False,
            'is_numeric': False,
            'is_id': False,
            'numeric_range': None,
            'avg_length': None
        }

        # 숫자형 검사
        if pd.api.types.is_numeric_dtype(col_data):
            result['is_numeric'] = True
            if not col_data.isna().all():
                result['numeric_range'] = (
                    float(col_data.min()),
                    float(col_data.max()),
                    float(col_data.mean())
                )

        # 날짜 검사 (성능 개선: pd.to_datetime 사용)
        if not result['is_numeric']:
            # 샘플 10개로 빠르게 테스트
            sample = col_data.dropna().head(10)

            if len(sample) > 0:
                try:
                    # pd.to_datetime은 dateutil보다 훨씬 빠름
                    parsed = pd.to_datetime(sample, errors='coerce')
                    valid_dates = parsed.notna().sum()

                    # 70% 이상 파싱 성공 시 날짜로 판정
                    if valid_dates / len(sample) >= self.DATE_PARSE_RATIO_THRESHOLD:
                        result['is_date'] = True
                        logger.debug(f"Column '{col_name}' detected as date ({valid_dates}/{len(sample)} valid)")
                except (ValueError, TypeError) as e:
                    logger.debug(f"Date parsing failed for '{col_name}': {e}")

                # 평균 문자열 길이 계산 (텍스트 타입 추론용)
                try:
                    result['avg_length'] = sample.astype(str).str.len().mean()
                except Exception as e:
                    logger.debug(f"Failed to calculate avg_length for '{col_name}': {e}")

        # ID 검사 (고유값 비율 임계값 이상)
        if result['unique_ratio'] >= self.ID_UNIQUE_RATIO_THRESHOLD:
            result['is_id'] = True

        return result

    def infer_column_type(self, df: pd.DataFrame, col_name: str,
                          analysis: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        컬럼 타입 추론 (데이터 특성 기반)

        타입 우선순위 (충돌 시):
        1. 날짜 (is_date=True) → 다른 모든 타입보다 우선
        2. 평점 (숫자 + 0-10 범위)
        3. 숫자 (is_numeric=True)
        4. ID (고유값 90% 이상)
        5. 텍스트 (기본)

        Args:
            df: 데이터프레임 (avg_length 계산 시에만 사용)
            col_name: 컬럼명
            analysis: 미리 계산된 분석 결과 (필수 권장)

        Returns:
            {타입명: 신뢰도 점수} 딕셔너리
        """
        if analysis is None:
            analysis = self.analyze_column_data(df, col_name)

        scores = {}

        # 우선순위 1: 날짜 (가장 명확한 타입)
        if analysis['is_date']:
            scores['date'] = self.SCORE_HIGH
            # 날짜이면서 다른 타입일 수 있으므로 낮은 점수 부여
            # 예: '2024-01-01-001' 형식 주문번호 (날짜 + ID)
            if analysis['is_id']:
                scores['id'] = self.SCORE_LOW  # 30점
            else:
                scores['id'] = 0
            scores['numeric'] = 0
            scores['rating'] = 0
            scores['text'] = 0
            # 조기 반환하지 않고 계속 진행 (유연성 확보)

        # 숫자형 컬럼 (평점 검사 포함)
        if analysis['is_numeric']:
            scores['numeric'] = self.SCORE_MEDIUM_HIGH

            # 평점 판단 (0-10 범위)
            if analysis['numeric_range']:
                min_val, max_val, _ = analysis['numeric_range']
                if min_val is not None and max_val is not None:
                    # 최소값이 0 이상, 최대값이 10 이하면 평점으로 판단
                    if self.RATING_MIN <= min_val and max_val <= self.RATING_MAX:
                        scores['rating'] = self.SCORE_MEDIUM
                    else:
                        scores['rating'] = 0
                else:
                    scores['rating'] = 0
            else:
                scores['rating'] = 0

            # ID 컬럼 점수 (숫자이면서 고유값 높음)
            if analysis['is_id']:
                scores['id'] = self.SCORE_HIGH
            else:
                scores['id'] = int(analysis['unique_ratio'] * 50)

            scores['text'] = 0
            scores['date'] = 0

        else:
            # 비숫자형
            scores['numeric'] = 0
            scores['rating'] = 0

            # ID 검사 (문자열 ID도 가능)
            if analysis['is_id']:
                scores['id'] = self.SCORE_MEDIUM_HIGH  # 숫자 ID보다는 낮음
            else:
                scores['id'] = int(analysis['unique_ratio'] * 30)

            # 텍스트 컬럼 점수 (avg_length 재사용)
            avg_length = analysis.get('avg_length')
            if avg_length is not None:
                if avg_length >= self.TEXT_LENGTH_LONG:
                    scores['text'] = self.SCORE_MEDIUM_HIGH
                elif avg_length >= self.TEXT_LENGTH_MEDIUM:
                    scores['text'] = self.SCORE_MEDIUM_LOW
                else:
                    scores['text'] = self.SCORE_LOW
            else:
                # avg_length 없으면 계산 (fallback)
                col_data = df[col_name].dropna()
                if len(col_data) > 0:
                    avg_length = col_data.astype(str).str.len().mean()
                    if avg_length >= self.TEXT_LENGTH_LONG:
                        scores['text'] = self.SCORE_MEDIUM_HIGH
                    elif avg_length >= self.TEXT_LENGTH_MEDIUM:
                        scores['text'] = self.SCORE_MEDIUM_LOW
                    else:
                        scores['text'] = self.SCORE_LOW

            scores['date'] = 0

        return scores

    def hybrid_map_columns(self, df: pd.DataFrame,
                          name_weight: float = 0.6,
                          data_weight: float = 0.4,
                          max_columns: int = 200) -> Dict[str, Dict[str, Any]]:
        """
        하이브리드 매핑: 컬럼명 유사도 + 데이터 타입 추론 결합

        Args:
            df: 사용자 데이터프레임
            name_weight: 컬럼명 유사도 가중치 (기본: 60%)
            data_weight: 데이터 타입 가중치 (기본: 40%)
            max_columns: 최대 분석 컬럼 수 (성능 보호, 기본: 200)

        Returns:
            매핑 결과 딕셔너리
            {
                '표준_컬럼명': {
                    'user_column': '사용자_컬럼명',
                    'confidence': 85.5,  # 종합 점수
                    'method': 'hybrid',
                    'name_score': 90,  # 컬럼명 유사도
                    'data_score': 78,  # 데이터 타입 점수
                    'alternatives': [...]  # 충돌 시
                }
            }

        Note:
            종합 점수 = (컬럼명 유사도 × 0.6) + (데이터 타입 점수 × 0.4)
            신뢰도 임계값(50점) 이상만 매핑

        Warning:
            컬럼 수가 max_columns를 초과하면 경고 로그 출력
        """
        # 대용량 데이터 경고
        if len(df.columns) > max_columns:
            logger.warning(
                f"Column count ({len(df.columns)}) exceeds max_columns ({max_columns}). "
                f"This may cause performance issues. Consider reducing columns or increasing max_columns."
            )

        # 1단계: 모든 컬럼 분석 (데이터 타입 추론)
        logger.info(f"Analyzing {len(df.columns)} columns for hybrid mapping...")
        column_analyses = {}

        for user_col in df.columns:
            try:
                analysis = self.analyze_column_data(df, user_col)
                type_scores = self.infer_column_type(df, user_col, analysis)
                column_analyses[user_col] = {
                    'analysis': analysis,
                    'type_scores': type_scores
                }
            except Exception as e:
                logger.error(f"Failed to analyze column '{user_col}': {e}")
                column_analyses[user_col] = {
                    'analysis': None,
                    'type_scores': {}
                }

        # 2단계: 표준 컬럼별로 모든 사용자 컬럼과 매칭 점수 계산
        candidates = {}  # {표준_컬럼: [(사용자_컬럼, 종합_점수, 상세), ...]}

        for std_col, config in self.standard_columns.items():
            std_type = config['type']  # 'id', 'date', 'numeric', 'text', 'rating'
            candidates[std_col] = []

            for user_col in df.columns:
                # 컬럼명 유사도 점수
                name_score = 0
                for alias in config['names']:
                    score = self.calculate_similarity(user_col, alias)
                    name_score = max(name_score, score)

                # 데이터 타입 점수
                type_scores = column_analyses[user_col].get('type_scores', {})
                data_score = type_scores.get(std_type, 0)

                # 종합 점수 계산
                combined_score = (name_score * name_weight) + (data_score * data_weight)

                # 임계값 이상만 후보로 추가
                if combined_score >= self.MIN_SIMILARITY_THRESHOLD:
                    candidates[std_col].append((
                        user_col,
                        combined_score,
                        {
                            'name_score': name_score,
                            'data_score': data_score
                        }
                    ))

        # 3단계: 중복 해결 (종합 점수 기준)
        mapping_result = {}

        for std_col, user_cols in candidates.items():
            if len(user_cols) == 0:
                continue
            elif len(user_cols) == 1:
                # 중복 없음
                user_col, combined_score, details = user_cols[0]
                mapping_result[std_col] = {
                    'user_column': user_col,
                    'confidence': round(combined_score, 1),
                    'method': 'hybrid',
                    'name_score': details['name_score'],
                    'data_score': details['data_score']
                }
            else:
                # 중복 발생 - 종합 점수 높은 순 정렬
                sorted_cols = sorted(user_cols, key=lambda x: x[1], reverse=True)
                best_col, best_score, best_details = sorted_cols[0]
                alternatives = [col for col, _, _ in sorted_cols[1:]]

                mapping_result[std_col] = {
                    'user_column': best_col,
                    'confidence': round(best_score, 1),
                    'method': 'hybrid',
                    'name_score': best_details['name_score'],
                    'data_score': best_details['data_score'],
                    'alternatives': alternatives
                }

                logger.warning(
                    f"Duplicate mapping for '{std_col}': "
                    f"selected '{best_col}' (score: {best_score:.1f}), "
                    f"rejected {alternatives}"
                )

        logger.info(f"Hybrid mapping completed: {len(mapping_result)}/{len(self.standard_columns)} columns mapped")
        return mapping_result

    def get_mapping_confidence_level(self, confidence: float) -> str:
        """
        신뢰도 점수를 레벨로 변환

        Args:
            confidence: 신뢰도 점수 (0-100)

        Returns:
            'high', 'medium', 'low' 중 하나
        """
        if confidence >= 80:
            return 'high'
        elif confidence >= 65:
            return 'medium'
        else:
            return 'low'

    def apply_mapping(self, df: pd.DataFrame, mapping: Dict[str, Dict]) -> pd.DataFrame:
        """
        매핑 결과를 데이터프레임에 적용 (컬럼명 변경)

        Args:
            df: 원본 데이터프레임
            mapping: 매핑 결과

        Returns:
            컬럼명이 변경된 새 데이터프레임
        """
        # 매핑된 컬럼만 선택 및 이름 변경
        rename_dict = {}
        for std_col, info in mapping.items():
            user_col = info['user_column']
            rename_dict[user_col] = std_col

        # 매핑된 컬럼만 선택하여 새 DataFrame 생성
        mapped_cols = list(rename_dict.keys())
        df_mapped = df[mapped_cols].copy()
        df_mapped.rename(columns=rename_dict, inplace=True)

        logger.info(f"Applied mapping: {len(mapped_cols)} columns renamed")
        return df_mapped


# 테스트 코드
if __name__ == "__main__":
    print("ColumnMapper 테스트")
    print("=" * 50)

    # 테스트 데이터
    test_df = pd.DataFrame({
        'Customer_ID': [1, 2, 3],
        'Order Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Qty': [5, 10, 3],
        'Unit Price': [100, 200, 150]
    })

    print("\n테스트 데이터:")
    print(test_df.head())

    # E-commerce 매퍼
    mapper = ColumnMapper(data_type='ecommerce')
    mapping = mapper.auto_map_columns(test_df)

    print("\n매핑 결과:")
    print(mapper.get_mapping_summary(mapping))

    # 검증
    is_valid, errors = mapper.validate_mapping(mapping)
    print(f"\n검증 결과: {'성공' if is_valid else '실패'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
