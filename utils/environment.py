"""
환경 감지 및 설정 모듈
로컬 vs 배포 환경 자동 감지
"""

import os
import streamlit as st
from typing import Optional


class Environment:
    """환경 감지 및 설정 관리 클래스"""

    @staticmethod
    def is_local() -> bool:
        """
        로컬 환경 여부 확인

        Returns:
            True: 로컬 환경
            False: 배포 환경 (Streamlit Cloud)
        """
        # 방법 1: Streamlit Secrets 확인
        # 배포 환경에서는 secrets.toml에 deployed=true 설정
        try:
            if hasattr(st, 'secrets') and 'deployed' in st.secrets:
                deployed = st.secrets.get('deployed', False)
                if isinstance(deployed, str):
                    deployed = deployed.lower() == 'true'
                if deployed:
                    return False
        except Exception:
            pass

        # 방법 2: 환경변수 확인
        # 로컬 .env에 DEPLOYED=false 설정
        env_deployed = os.getenv('DEPLOYED', 'false').lower()
        if env_deployed == 'true':
            return False

        # 방법 3: Streamlit Cloud 특정 환경변수 확인
        # Streamlit Cloud에서는 특정 환경변수가 자동 설정됨
        if os.getenv('STREAMLIT_RUNTIME_ENVIRONMENT') == 'cloud':
            return False

        # 기본값: 로컬 환경
        return True

    @staticmethod
    def is_deployed() -> bool:
        """
        배포 환경 여부 확인

        Returns:
            True: 배포 환경
            False: 로컬 환경
        """
        return not Environment.is_local()

    @staticmethod
    def get_api_key(service: str) -> Optional[str]:
        """
        API 키 조회 (우선순위: Secrets > 환경변수 > .env)

        Args:
            service: 서비스명 (예: 'OPENAI_API_KEY')

        Returns:
            API 키 문자열 또는 None
        """
        # 1순위: Streamlit Secrets (배포 환경)
        try:
            if hasattr(st, 'secrets') and service in st.secrets:
                key = st.secrets[service]
                if key:
                    return key
        except Exception:
            pass

        # 2순위: 환경변수
        key = os.getenv(service)
        if key:
            return key

        # 3순위: .env 파일 (로컬 환경)
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv(service)
            if key:
                return key
        except ImportError:
            pass

        return None

    @staticmethod
    def has_api_key(service: str) -> bool:
        """
        API 키 존재 여부 확인

        Args:
            service: 서비스명

        Returns:
            True: API 키 있음
            False: API 키 없음
        """
        key = Environment.get_api_key(service)
        return key is not None and len(key.strip()) > 0

    @staticmethod
    def get_config(key: str, default: any = None) -> any:
        """
        설정값 조회 (Secrets > 환경변수 > 기본값)

        Args:
            key: 설정 키
            default: 기본값

        Returns:
            설정값
        """
        # Streamlit Secrets
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass

        # 환경변수
        value = os.getenv(key)
        if value is not None:
            return value

        # 기본값
        return default

    @staticmethod
    def get_environment_info() -> dict:
        """
        환경 정보 요약

        Returns:
            환경 정보 딕셔너리
        """
        is_local = Environment.is_local()

        info = {
            'environment': 'LOCAL' if is_local else 'DEPLOYED',
            'is_local': is_local,
            'is_deployed': not is_local,
            'crawling_enabled': is_local,  # 로컬에서만 크롤링 가능
            'api_keys': {
                'openai': Environment.has_api_key('OPENAI_API_KEY'),
            },
            'python_version': os.sys.version.split()[0],
            'working_directory': os.getcwd()
        }

        return info

    @staticmethod
    def show_environment_info():
        """
        환경 정보 표시 (디버깅용)
        """
        info = Environment.get_environment_info()

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔧 환경 정보")

        env_emoji = "💻" if info['is_local'] else "☁️"
        st.sidebar.info(f"{env_emoji} 환경: **{info['environment']}**")

        if info['is_local']:
            st.sidebar.success("✅ 크롤링 기능 사용 가능")
        else:
            st.sidebar.warning("⚠️ 크롤링 기능 비활성화 (샘플 데이터 사용)")

        # API 키 상태
        with st.sidebar.expander("API 키 상태"):
            openai_status = "✅ 설정됨" if info['api_keys']['openai'] else "❌ 없음"
            st.write(f"OpenAI: {openai_status}")

    @staticmethod
    def require_local(message: str = "이 기능은 로컬 환경에서만 사용 가능합니다."):
        """
        로컬 환경 필수 체크 (배포 환경에서는 경고)

        Args:
            message: 경고 메시지

        Returns:
            True: 로컬 환경
            False: 배포 환경 (경고 표시)
        """
        if Environment.is_deployed():
            st.warning(f"⚠️ {message}")
            return False
        return True

    @staticmethod
    def require_api_key(service: str, message: str = None):
        """
        API 키 필수 체크

        Args:
            service: 서비스명
            message: 경고 메시지 (선택)

        Returns:
            True: API 키 있음
            False: API 키 없음 (경고 표시)
        """
        if not Environment.has_api_key(service):
            if message is None:
                message = f"이 기능을 사용하려면 {service} API 키가 필요합니다."

            st.warning(f"⚠️ {message}")

            if Environment.is_local():
                st.info(
                    f"💡 `.env` 파일에 `{service}=your_api_key` 를 추가하세요.\n\n"
                    "또는 Streamlit Secrets을 사용하세요."
                )
            else:
                st.info(
                    "💡 Streamlit Cloud 대시보드에서 Secrets 설정을 추가하세요.\n\n"
                    f"Settings > Secrets > `{service}=\"your_api_key\"`"
                )

            return False
        return True

    @staticmethod
    def get_sample_data_path() -> str:
        """
        샘플 데이터 경로 조회

        Returns:
            샘플 데이터 디렉토리 경로
        """
        return os.path.join(os.getcwd(), 'sample_data')

    @staticmethod
    def list_sample_data() -> list:
        """
        사용 가능한 샘플 데이터 목록 조회

        Returns:
            샘플 데이터 파일명 리스트
        """
        sample_dir = Environment.get_sample_data_path()

        if not os.path.exists(sample_dir):
            return []

        # 버그 #47 수정: 파일 리스트 읽기 오류 처리 추가
        try:
            files = [
                f for f in os.listdir(sample_dir)
                if f.endswith(('.csv', '.xlsx'))
            ]
            return sorted(files)
        except (PermissionError, OSError) as e:
            import warnings
            warnings.warn(f"샘플 데이터 폴더 접근 실패: {str(e)}")
            return []
