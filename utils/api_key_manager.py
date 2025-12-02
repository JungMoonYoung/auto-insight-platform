"""
API 키 관리 모듈
Streamlit Secrets > 환경변수 > .env 순서로 API 키 로드
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class APIKeyManager:
    """API 키 관리 클래스"""

    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        """
        OpenAI API 키 가져오기
        우선순위: Streamlit Secrets > 환경변수 > .env 파일

        Returns:
            API 키 (str) 또는 None
        """
        api_key = None

        # 1. Streamlit Secrets 확인 (배포 환경)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
                logger.info("API 키 로드 성공: Streamlit Secrets")
                return api_key
        except Exception as e:
            logger.debug(f"Streamlit Secrets 로드 실패: {e}")

        # 2. 환경변수 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            logger.info("API 키 로드 성공: 환경변수")
            return api_key

        # 3. .env 파일 확인
        try:
            from dotenv import load_dotenv
            env_path = Path('.env')
            if env_path.exists():
                load_dotenv(env_path)
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    logger.info("API 키 로드 성공: .env 파일")
                    return api_key
        except ImportError:
            logger.debug("python-dotenv가 설치되지 않음")
        except Exception as e:
            logger.debug(f".env 파일 로드 실패: {e}")

        logger.warning("API 키를 찾을 수 없음")
        return None

    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        API 키 마스킹 (보안)

        Args:
            api_key: 원본 API 키

        Returns:
            마스킹된 API 키 (예: "sk-proj...xyz")
        """
        if not api_key or len(api_key) < 12:
            return "***"

        # sk-proj-...xyz 형식으로 마스킹
        prefix = api_key[:8]
        suffix = api_key[-4:]
        return f"{prefix}...{suffix}"

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        API 키 유효성 검사 (간단한 형식 체크)

        Args:
            api_key: 검사할 API 키

        Returns:
            유효 여부
        """
        if not api_key:
            return False

        # OpenAI API 키 형식: sk-로 시작, 최소 20자 이상
        if not api_key.startswith('sk-'):
            logger.warning("API 키가 'sk-'로 시작하지 않음")
            return False

        if len(api_key) < 20:
            logger.warning("API 키가 너무 짧음")
            return False

        return True

    @staticmethod
    def estimate_cost(num_tokens: int, model: str = "gpt-4o-mini") -> float:
        """
        예상 비용 계산

        Args:
            num_tokens: 토큰 수
            model: 모델명

        Returns:
            예상 비용 (USD)
        """
        # 간단한 비용 추정 (input 토큰으로 가정)
        pricing = {
            'gpt-4o-mini': 0.15,  # per 1M tokens
            'gpt-4o': 2.50,
            'gpt-4-turbo': 10.0,
            'gpt-4': 30.0,
            'gpt-3.5-turbo': 0.50,
        }

        price_per_million = pricing.get(model, 0.15)
        cost = (num_tokens / 1_000_000) * price_per_million

        return cost

    @staticmethod
    def get_api_key_status() -> dict:
        """
        API 키 상태 확인

        Returns:
            {
                'available': bool,
                'source': str,  # 'streamlit', 'env', 'dotenv', 'none'
                'masked_key': str,
                'valid': bool
            }
        """
        api_key = APIKeyManager.get_openai_api_key()

        if not api_key:
            return {
                'available': False,
                'source': 'none',
                'masked_key': None,
                'valid': False
            }

        # 소스 확인
        source = 'none'
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                source = 'streamlit'
        except:
            pass

        if source == 'none' and os.getenv('OPENAI_API_KEY'):
            source = 'env'

        if source == 'none':
            try:
                from dotenv import load_dotenv
                env_path = Path('.env')
                if env_path.exists():
                    source = 'dotenv'
            except:
                pass

        return {
            'available': True,
            'source': source,
            'masked_key': APIKeyManager.mask_api_key(api_key),
            'valid': APIKeyManager.validate_api_key(api_key)
        }


# 편의 함수
def get_api_key() -> Optional[str]:
    """API 키 가져오기 (간편 함수)"""
    return APIKeyManager.get_openai_api_key()


def has_api_key() -> bool:
    """API 키 존재 여부"""
    return APIKeyManager.get_openai_api_key() is not None


if __name__ == "__main__":
    # 테스트
    print("=" * 60)
    print("API 키 매니저 테스트")
    print("=" * 60)

    status = APIKeyManager.get_api_key_status()
    print(f"\nAPI 키 상태:")
    print(f"  사용 가능: {status['available']}")
    print(f"  소스: {status['source']}")
    print(f"  마스킹된 키: {status['masked_key']}")
    print(f"  유효성: {status['valid']}")

    if status['available']:
        # 비용 추정 테스트
        test_tokens = 1000
        cost = APIKeyManager.estimate_cost(test_tokens, 'gpt-4o-mini')
        print(f"\n예상 비용 (1,000 토큰):")
        print(f"  gpt-4o-mini: ${cost:.6f}")

        cost_4 = APIKeyManager.estimate_cost(test_tokens, 'gpt-4')
        print(f"  gpt-4: ${cost_4:.6f}")
    else:
        print("\n[참고] API 키 설정 방법:")
        print("  1. 환경변수: export OPENAI_API_KEY='sk-...'")
        print("  2. .env 파일: OPENAI_API_KEY=sk-...")
        print("  3. Streamlit Secrets: .streamlit/secrets.toml")
