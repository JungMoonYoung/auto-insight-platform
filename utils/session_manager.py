"""
세션 상태 중앙 관리 모듈
페이지 간 데이터 공유 및 상태 관리
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


class SessionManager:
    """Streamlit 세션 상태 중앙 관리 클래스"""

    # 세션 키 상수
    KEY_INITIALIZED = 'initialized'
    KEY_CURRENT_PAGE = 'current_page'
    KEY_DATA = 'uploaded_data'
    KEY_DATA_TYPE = 'data_type'
    KEY_DATA_SOURCE = 'data_source'
    KEY_FILE_NAME = 'file_name'
    KEY_ANALYSIS_TYPE = 'analysis_type'
    KEY_COLUMN_MAPPING = 'column_mapping'
    KEY_ANALYSIS_COMPLETE = 'analysis_complete'
    KEY_ANALYSIS_RESULTS = 'analysis_results'
    KEY_MAPPED_COLUMNS = 'mapped_columns'
    KEY_INSIGHTS = 'insights'

    # E-commerce 관련
    KEY_RFM_DF = 'rfm_df'
    KEY_CLUSTER_SUMMARY = 'cluster_summary'
    KEY_CLUSTERED_DF = 'clustered_df'

    # 리뷰 관련
    KEY_REVIEW_ANALYZER = 'review_analyzer'
    KEY_REVIEW_SENTIMENT = 'review_sentiment_summary'
    KEY_REVIEW_KEYWORDS = 'review_keywords'
    KEY_REVIEW_TOPICS = 'review_topics'

    # 판매 관련
    KEY_SALES_ANALYZER = 'sales_analyzer'
    KEY_SALES_TRENDS = 'sales_trends'

    @staticmethod
    def init_session():
        """
        세션 상태 초기화
        앱 시작 시 한 번만 실행
        """
        if SessionManager.KEY_INITIALIZED not in st.session_state:
            st.session_state[SessionManager.KEY_INITIALIZED] = True
            st.session_state[SessionManager.KEY_CURRENT_PAGE] = 'start'
            st.session_state[SessionManager.KEY_DATA] = None
            st.session_state[SessionManager.KEY_DATA_TYPE] = None
            st.session_state[SessionManager.KEY_DATA_SOURCE] = None
            st.session_state[SessionManager.KEY_FILE_NAME] = None
            st.session_state[SessionManager.KEY_ANALYSIS_TYPE] = None
            st.session_state[SessionManager.KEY_COLUMN_MAPPING] = {}
            st.session_state[SessionManager.KEY_ANALYSIS_COMPLETE] = False
            st.session_state[SessionManager.KEY_ANALYSIS_RESULTS] = {}
            st.session_state[SessionManager.KEY_MAPPED_COLUMNS] = {}
            st.session_state[SessionManager.KEY_INSIGHTS] = []

            # E-commerce
            st.session_state[SessionManager.KEY_RFM_DF] = None
            st.session_state[SessionManager.KEY_CLUSTER_SUMMARY] = None
            st.session_state[SessionManager.KEY_CLUSTERED_DF] = None

            # 리뷰
            st.session_state[SessionManager.KEY_REVIEW_ANALYZER] = None
            st.session_state[SessionManager.KEY_REVIEW_SENTIMENT] = {}
            st.session_state[SessionManager.KEY_REVIEW_KEYWORDS] = {}
            st.session_state[SessionManager.KEY_REVIEW_TOPICS] = {}

            # 판매
            st.session_state[SessionManager.KEY_SALES_ANALYZER] = None
            st.session_state[SessionManager.KEY_SALES_TRENDS] = None

    @staticmethod
    def clear_all():
        """
        모든 세션 데이터 삭제
        새로 시작하기 버튼에 사용
        """
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionManager.init_session()

    @staticmethod
    def save_data(
        data: pd.DataFrame,
        data_type: Optional[str] = None,
        source: str = 'upload',
        file_name: Optional[str] = None
    ):
        """
        데이터 저장

        Args:
            data: 업로드/크롤링된 DataFrame
            data_type: 'ecommerce' | 'review' | 'sales' | None (자동 감지)
            source: 'upload' | 'crawl_movie' | 'crawl_place' | 'sample'
            file_name: 파일명 (선택)
        """
        st.session_state[SessionManager.KEY_DATA] = data
        st.session_state[SessionManager.KEY_DATA_TYPE] = data_type
        st.session_state[SessionManager.KEY_DATA_SOURCE] = source
        st.session_state[SessionManager.KEY_FILE_NAME] = file_name

    @staticmethod
    def get_data() -> Optional[pd.DataFrame]:
        """데이터 조회"""
        return st.session_state.get(SessionManager.KEY_DATA)

    @staticmethod
    def has_data() -> bool:
        """데이터 존재 여부"""
        data = st.session_state.get(SessionManager.KEY_DATA)
        return data is not None and not data.empty

    @staticmethod
    def get_data_type() -> Optional[str]:
        """데이터 타입 조회"""
        return st.session_state.get(SessionManager.KEY_DATA_TYPE)

    @staticmethod
    def get_data_source() -> Optional[str]:
        """데이터 소스 조회"""
        return st.session_state.get(SessionManager.KEY_DATA_SOURCE)

    @staticmethod
    def get_file_name() -> Optional[str]:
        """파일명 조회"""
        return st.session_state.get(SessionManager.KEY_FILE_NAME)

    @staticmethod
    def save_column_mapping(mapping: Dict[str, str]):
        """
        컬럼 매핑 저장

        Args:
            mapping: {표준_컬럼명: 실제_컬럼명} 딕셔너리
        """
        st.session_state[SessionManager.KEY_COLUMN_MAPPING] = mapping

    @staticmethod
    def get_column_mapping() -> Dict[str, str]:
        """컬럼 매핑 조회"""
        return st.session_state.get(SessionManager.KEY_COLUMN_MAPPING, {})

    @staticmethod
    def save_results(results: Dict[str, Any]):
        """
        분석 결과 저장

        Args:
            results: 분석 결과 딕셔너리
        """
        st.session_state[SessionManager.KEY_ANALYSIS_RESULTS] = results
        st.session_state[SessionManager.KEY_ANALYSIS_COMPLETE] = True

    @staticmethod
    def get_results() -> Dict[str, Any]:
        """분석 결과 조회"""
        return st.session_state.get(SessionManager.KEY_ANALYSIS_RESULTS, {})

    @staticmethod
    def has_results() -> bool:
        """분석 결과 존재 여부"""
        return st.session_state.get(SessionManager.KEY_ANALYSIS_COMPLETE, False)

    @staticmethod
    def save_insights(insights: list):
        """인사이트 저장"""
        st.session_state[SessionManager.KEY_INSIGHTS] = insights

    @staticmethod
    def get_insights() -> list:
        """인사이트 조회"""
        return st.session_state.get(SessionManager.KEY_INSIGHTS, [])

    @staticmethod
    def set_analysis_type(analysis_type: str):
        """
        분석 타입 설정

        Args:
            analysis_type: 'ecommerce' | 'review' | 'sales'
        """
        st.session_state[SessionManager.KEY_ANALYSIS_TYPE] = analysis_type

    @staticmethod
    def get_analysis_type() -> Optional[str]:
        """분석 타입 조회"""
        return st.session_state.get(SessionManager.KEY_ANALYSIS_TYPE)

    @staticmethod
    def set_current_page(page: str):
        """현재 페이지 설정"""
        st.session_state[SessionManager.KEY_CURRENT_PAGE] = page

    @staticmethod
    def get_current_page() -> str:
        """현재 페이지 조회"""
        return st.session_state.get(SessionManager.KEY_CURRENT_PAGE, 'start')

    @staticmethod
    def get_data_info() -> Dict[str, Any]:
        """
        데이터 정보 요약

        Returns:
            데이터 정보 딕셔너리
        """
        data = SessionManager.get_data()
        if data is None:
            return {
                'exists': False,
                'rows': 0,
                'columns': 0,
                'source': None,
                'file_name': None,
                'data_type': None
            }

        return {
            'exists': True,
            'rows': len(data),
            'columns': len(data.columns),
            'source': SessionManager.get_data_source(),
            'file_name': SessionManager.get_file_name(),
            'data_type': SessionManager.get_data_type()
        }

    @staticmethod
    def clear_analysis():
        """분석 결과만 삭제 (데이터는 유지)"""
        st.session_state[SessionManager.KEY_ANALYSIS_RESULTS] = {}
        st.session_state[SessionManager.KEY_ANALYSIS_COMPLETE] = False
        st.session_state[SessionManager.KEY_INSIGHTS] = []
        st.session_state[SessionManager.KEY_COLUMN_MAPPING] = {}

        # E-commerce 초기화
        st.session_state[SessionManager.KEY_RFM_DF] = None
        st.session_state[SessionManager.KEY_CLUSTER_SUMMARY] = None
        st.session_state[SessionManager.KEY_CLUSTERED_DF] = None

        # 리뷰 초기화
        st.session_state[SessionManager.KEY_REVIEW_ANALYZER] = None
        st.session_state[SessionManager.KEY_REVIEW_SENTIMENT] = {}
        st.session_state[SessionManager.KEY_REVIEW_KEYWORDS] = {}
        st.session_state[SessionManager.KEY_REVIEW_TOPICS] = {}

        # 판매 초기화
        st.session_state[SessionManager.KEY_SALES_ANALYZER] = None
        st.session_state[SessionManager.KEY_SALES_TRENDS] = None

    @staticmethod
    def get_state_summary() -> str:
        """
        세션 상태 요약 (디버깅용)

        Returns:
            상태 요약 문자열
        """
        info = SessionManager.get_data_info()

        summary = [
            "=== 세션 상태 요약 ===",
            f"데이터: {'있음' if info['exists'] else '없음'}",
        ]

        if info['exists']:
            summary.extend([
                f"  - 행/열: {info['rows']:,} × {info['columns']}",
                f"  - 소스: {info['source']}",
                f"  - 파일명: {info['file_name'] or 'N/A'}",
                f"  - 타입: {info['data_type'] or '미설정'}",
            ])

        summary.append(f"분석 완료: {'예' if SessionManager.has_results() else '아니오'}")

        if SessionManager.has_results():
            results = SessionManager.get_results()
            summary.append(f"  - 결과 키: {', '.join(results.keys())}")

        return "\n".join(summary)
