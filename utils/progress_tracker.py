"""
프로그레스 추적 시스템
분석 단계별 진행 상황 표시
"""

import time
import logging
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProgressStep:
    """단일 프로그레스 단계"""
    name: str
    description: str
    progress_percent: int


class ProgressTracker:
    """분석 프로그레스 추적 클래스"""

    # 기본 분석 단계 정의 (5단계)
    DEFAULT_STEPS = [
        ProgressStep("preprocessing", "데이터 전처리 중", 20),
        ProgressStep("analysis", "분석 실행 중", 60),
        ProgressStep("visualization", "시각화 생성 중", 80),
        ProgressStep("report", "리포트 생성 중", 95),
        ProgressStep("complete", "분석 완료", 100)
    ]

    def __init__(self,
                 steps: Optional[list] = None,
                 update_callback: Optional[Callable] = None,
                 delay: float = 0.3):
        """
        Args:
            steps: 커스텀 단계 리스트 (None이면 DEFAULT_STEPS 사용)
            update_callback: 진행 상황 업데이트 콜백 함수
                             callback(progress_percent, message)
            delay: 각 단계 사이 딜레이 (초)
        """
        self.steps = steps or self.DEFAULT_STEPS
        self.current_step = 0
        self.update_callback = update_callback
        self.delay = delay
        self.start_time = None
        self.is_running = False

    def start(self, message: str = "분석 시작"):
        """
        프로그레스 추적 시작

        Args:
            message: 시작 메시지
        """
        self.start_time = time.time()
        self.current_step = 0
        self.is_running = True
        self._update(0, message)
        logger.info(f"Progress tracking started: {message}")

    def next_step(self, custom_message: Optional[str] = None):
        """
        다음 단계로 이동

        Args:
            custom_message: 커스텀 메시지 (None이면 단계 기본 메시지 사용)
        """
        if not self.is_running:
            logger.warning("Progress tracker not started")
            return

        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            message = custom_message or step.description
            self._update(step.progress_percent, message)

            # 딜레이 (시각적 효과)
            if self.delay > 0 and self.current_step < len(self.steps) - 1:
                time.sleep(self.delay)

            self.current_step += 1
            logger.debug(f"Progress: {step.progress_percent}% - {message}")

    def update_current(self, message: str):
        """
        현재 단계의 메시지만 업데이트 (진행률은 유지)

        Args:
            message: 업데이트할 메시지
        """
        if not self.is_running or self.current_step == 0:
            return

        current_progress = self.steps[self.current_step - 1].progress_percent
        self._update(current_progress, message)

    def complete(self, message: str = "분석 완료"):
        """
        프로그레스 완료

        Args:
            message: 완료 메시지
        """
        if not self.is_running:
            return

        self._update(100, message)
        self.is_running = False

        elapsed = time.time() - self.start_time if self.start_time else 0
        logger.info(f"Progress tracking completed in {elapsed:.2f}s")

    def error(self, message: str = "분석 중 오류 발생"):
        """
        에러 발생 시 프로그레스 중단

        Args:
            message: 에러 메시지
        """
        if not self.is_running:
            return

        self._update(self.get_current_progress(), message)
        self.is_running = False
        logger.error(f"Progress tracking stopped due to error: {message}")

    def get_current_progress(self) -> int:
        """
        현재 진행률 반환

        Returns:
            진행률 (0-100)
        """
        if self.current_step == 0:
            return 0
        elif self.current_step >= len(self.steps):
            return 100
        else:
            return self.steps[self.current_step - 1].progress_percent

    def get_elapsed_time(self) -> float:
        """
        경과 시간 반환 (초)

        Returns:
            경과 시간
        """
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def _update(self, progress: int, message: str):
        """
        내부: 진행 상황 업데이트

        Args:
            progress: 진행률 (0-100)
            message: 메시지
        """
        if self.update_callback:
            try:
                self.update_callback(progress, message)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")


class RFMProgressTracker(ProgressTracker):
    """RFM 분석 전용 프로그레스 추적"""

    RFM_STEPS = [
        ProgressStep("loading", "데이터 로딩 중", 10),
        ProgressStep("preprocessing", "데이터 전처리 중", 25),
        ProgressStep("rfm_calculation", "RFM 지표 계산 중", 50),
        ProgressStep("clustering", "고객 군집화 중", 75),
        ProgressStep("visualization", "시각화 생성 중", 90),
        ProgressStep("complete", "RFM 분석 완료", 100)
    ]

    def __init__(self, update_callback: Optional[Callable] = None, delay: float = 0.3):
        super().__init__(steps=self.RFM_STEPS, update_callback=update_callback, delay=delay)


class TextProgressTracker(ProgressTracker):
    """텍스트 분석 전용 프로그레스 추적"""

    TEXT_STEPS = [
        ProgressStep("loading", "리뷰 데이터 로딩 중", 10),
        ProgressStep("preprocessing", "텍스트 전처리 중", 30),
        ProgressStep("sentiment", "감성 분석 중", 55),
        ProgressStep("keywords", "키워드 추출 중", 75),
        ProgressStep("topics", "토픽 모델링 중", 90),
        ProgressStep("complete", "텍스트 분석 완료", 100)
    ]

    def __init__(self, update_callback: Optional[Callable] = None, delay: float = 0.3):
        super().__init__(steps=self.TEXT_STEPS, update_callback=update_callback, delay=delay)


# 테스트 코드
if __name__ == "__main__":
    import sys

    # 콘솔 출력 콜백
    def console_callback(progress, message):
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f'\r[{bar}] {progress}% - {message}')
        sys.stdout.flush()

    print("프로그레스 추적 테스트")
    print("=" * 60)

    # 기본 프로그레스
    print("\n1. 기본 프로그레스:")
    tracker = ProgressTracker(update_callback=console_callback, delay=0.5)
    tracker.start("분석 시작")

    for _ in range(len(tracker.steps)):
        tracker.next_step()

    tracker.complete()

    # RFM 프로그레스
    print("\n\n2. RFM 분석 프로그레스:")
    rfm_tracker = RFMProgressTracker(update_callback=console_callback, delay=0.5)
    rfm_tracker.start("RFM 분석 시작")

    for _ in range(len(rfm_tracker.steps)):
        rfm_tracker.next_step()

    rfm_tracker.complete()

    # 텍스트 프로그레스
    print("\n\n3. 텍스트 분석 프로그레스:")
    text_tracker = TextProgressTracker(update_callback=console_callback, delay=0.5)
    text_tracker.start("텍스트 분석 시작")

    for _ in range(len(text_tracker.steps)):
        text_tracker.next_step()

    text_tracker.complete()

    print("\n\n테스트 완료!")
