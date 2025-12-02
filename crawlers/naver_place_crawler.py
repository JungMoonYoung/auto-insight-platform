"""
Naver Place Review Crawler
네이버 플레이스 리뷰 크롤링 스크립트

사용법:
    python naver_place_crawler.py --place-id 1234567890 --count 100 --output reviews.csv
"""

import argparse
import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from tqdm import tqdm
from pathlib import Path


class NaverPlaceCrawler:
    """네이버 플레이스 리뷰 크롤러"""

    def __init__(self, headless: bool = True, delay: float = 1.0):
        """
        Args:
            headless: 브라우저를 보이지 않게 실행
            delay: 요청 간 지연 시간 (초)
        """
        self.delay = delay
        self.reviews = []

        # Chrome 옵션 설정 (undetected_chromedriver용)
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')  # 새로운 headless 모드
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # WebDriver 초기화 (undetected_chromedriver 사용)
        self.driver = uc.Chrome(options=options, version_main=None)
        self.wait = WebDriverWait(self.driver, 15)  # 대기 시간 증가

    def crawl_reviews(self, place_id: str, max_reviews: int = 100) -> pd.DataFrame:
        """
        플레이스 리뷰 크롤링

        Args:
            place_id: 네이버 플레이스 ID
            max_reviews: 수집할 최대 리뷰 수

        Returns:
            pd.DataFrame: 리뷰 데이터프레임
        """
        # 여러 URL 패턴 시도
        urls = [
            f"https://m.place.naver.com/restaurant/{place_id}/review/visitor",
            f"https://m.place.naver.com/place/{place_id}/review/visitor",
            f"https://pcmap.place.naver.com/restaurant/{place_id}/review/visitor",
        ]

        print(f"🏪 플레이스 ID {place_id}의 리뷰 크롤링 시작...")
        print(f"목표: {max_reviews}개 리뷰 수집")

        success = False
        for url in urls:
            print(f"\n시도 중: {url}")
            try:
                self.driver.get(url)
                print("⏳ 페이지 로딩 중...")
                # 랜덤 대기 (10-15초) - 사람처럼 보이기
                wait_time = random.uniform(10, 15)
                time.sleep(wait_time)

                # 리뷰 탭 확인
                print("📄 페이지 로딩 완료")
                print(f"현재 URL: {self.driver.current_url}")
                print(f"페이지 제목: {self.driver.title}")

                # iframe 확인 및 전환
                try:
                    iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                    if iframes:
                        print(f"🔍 {len(iframes)}개의 iframe 발견, 첫 번째 iframe으로 전환 시도...")
                        self.driver.switch_to.frame(iframes[0])
                        print("✅ iframe으로 전환 완료")
                        time.sleep(2)
                except Exception as e:
                    print(f"ℹ️ iframe 없음 또는 전환 불필요: {str(e)}")

                # 리뷰 요소가 있는지 확인
                test_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li, div, span')
                if test_elements:
                    print(f"✅ 페이지에 {len(test_elements)}개의 요소 발견")

                    # 디버깅용 스크린샷 저장
                    try:
                        screenshot_path = Path(__file__).parent / 'output' / f'debug_screenshot_{place_id}.png'
                        screenshot_path.parent.mkdir(exist_ok=True)
                        self.driver.save_screenshot(str(screenshot_path))
                        print(f"📸 스크린샷 저장: {screenshot_path}")
                    except:
                        pass

                    success = True
                    break
                else:
                    print("⚠️ 페이지가 비어있습니다. 다음 URL 시도...")
                    self.driver.switch_to.default_content()
            except Exception as e:
                print(f"❌ URL 로딩 실패: {str(e)}")
                continue

        if not success:
            print("\n❌ 모든 URL 시도 실패")
            # 최종 스크린샷 저장
            try:
                screenshot_path = Path(__file__).parent / 'output' / f'debug_failed_{place_id}.png'
                screenshot_path.parent.mkdir(exist_ok=True)
                self.driver.save_screenshot(str(screenshot_path))
                print(f"📸 실패 스크린샷 저장: {screenshot_path}")
            except:
                pass
            return pd.DataFrame()

        try:
            # 스크롤하며 리뷰 수집
            pbar = tqdm(total=max_reviews, desc="리뷰 수집 중")
            last_review_count = 0
            no_change_count = 0

            while len(self.reviews) < max_reviews:
                # 현재 페이지의 모든 리뷰 파싱
                self._parse_reviews()

                current_count = len(self.reviews)
                pbar.n = min(current_count, max_reviews)
                pbar.refresh()

                # 더 이상 새로운 리뷰가 없으면 종료
                if current_count == last_review_count:
                    no_change_count += 1
                    if no_change_count >= 3:
                        print(f"\n더 이상 리뷰가 없습니다. (총 {current_count}개)")
                        break
                else:
                    no_change_count = 0

                last_review_count = current_count

                if current_count >= max_reviews:
                    break

                # 자연스러운 스크롤 (단계적으로)
                scroll_pause = random.uniform(0.5, 1.5)
                for i in range(3):  # 3단계로 나눠서 스크롤
                    scroll_position = (i + 1) * (self.driver.execute_script("return document.body.scrollHeight") // 3)
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                    time.sleep(scroll_pause)

                print("💤 스크롤 후 대기 중...")
                time.sleep(random.uniform(3, 6))  # 3-6초 랜덤 대기

                # "더보기" 버튼 클릭 시도
                try:
                    more_button = self.driver.find_element(By.CSS_SELECTOR,
                        'a.fvwqf, button.fvwqf, a[class*="more"], button[class*="more"]')
                    if more_button.is_displayed():
                        more_button.click()
                        print("💤 더보기 클릭 후 대기 중...")
                        time.sleep(random.uniform(2, 4))  # 2-4초 랜덤
                except:
                    pass

            pbar.close()

            # 중복 제거 (리뷰 텍스트 기준)
            df = pd.DataFrame(self.reviews)
            if len(df) > 0:
                df = df.drop_duplicates(subset=['review'], keep='first')
                df = df.head(max_reviews)  # 최대 개수만큼만
                print(f"\n✅ 크롤링 완료! 총 {len(df)}개 리뷰 수집")
                return df
            else:
                print("\n⚠️ 수집된 리뷰가 없습니다.")
                return pd.DataFrame()

        except Exception as e:
            print(f"\n❌ 크롤링 오류: {str(e)}")
            if self.reviews:
                df = pd.DataFrame(self.reviews)
                df = df.drop_duplicates(subset=['review'], keep='first')
                print(f"⚠️ 부분 수집: {len(df)}개 리뷰")
                return df
            return pd.DataFrame()

    def _parse_reviews(self):
        """현재 페이지의 리뷰 파싱"""
        try:
            # 다양한 CSS 선택자 시도
            review_selectors = [
                'li.pui__X35jYm',  # 최신 구조
                'li[class*="review"]',
                'div.review_li',
                'li.YeINN',
                'div.place_section_content ul li',  # 추가 선택자
                'li[data-review-id]',  # 추가 선택자
            ]

            review_elements = []
            for selector in review_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ '{selector}' 선택자로 {len(elements)}개 요소 발견")
                        review_elements = elements
                        break
                    else:
                        print(f"⚠️ '{selector}' 선택자로 요소 없음")
                except Exception as e:
                    print(f"❌ '{selector}' 선택자 오류: {str(e)}")
                    continue

            if not review_elements:
                print("❌ 리뷰 요소를 찾을 수 없습니다. 페이지 소스를 확인합니다...")
                # 페이지 소스 일부 출력 (디버깅용)
                page_source_sample = self.driver.page_source[:500]
                print(f"페이지 소스 샘플: {page_source_sample}")
                return

            parsed_count = 0
            for element in review_elements:
                try:
                    # 이미 수집한 리뷰인지 확인 (텍스트로 체크)
                    review_text = self._extract_text(element)

                    if not review_text:
                        continue

                    if any(r['review'] == review_text for r in self.reviews):
                        continue

                    # 평점 추출
                    rating = self._extract_rating(element)

                    # 작성자
                    author = self._extract_author(element)

                    # 작성일
                    date = self._extract_date(element)

                    # 방문 형태 (선택)
                    visit_type = self._extract_visit_type(element)

                    self.reviews.append({
                        'place_id': None,  # 나중에 추가
                        'author': author,
                        'rating': rating,
                        'review': review_text,
                        'date': date,
                        'visit_type': visit_type,
                        'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    parsed_count += 1

                except Exception as e:
                    print(f"⚠️ 리뷰 파싱 오류: {str(e)}")
                    continue

            if parsed_count > 0:
                print(f"✅ {parsed_count}개 새로운 리뷰 파싱 완료")

        except Exception as e:
            pass

    def _extract_text(self, element) -> str:
        """리뷰 텍스트 추출"""
        selectors = [
            'span.pui__xtsQN-',  # 최신
            'div.pui__vn15t2',
            'span[class*="review"]',
            'div.review_text',
            'span.zPfVt',
            'a.pui__xtsQN-',  # "더보기" 링크 안의 텍스트
            'div[class*="text"]',
        ]

        for selector in selectors:
            try:
                text_elem = element.find_element(By.CSS_SELECTOR, selector)
                text = text_elem.text.strip()
                if text and len(text) > 5:  # 최소 길이 체크
                    return text
            except:
                continue

        # 전체 텍스트에서 추출 시도
        try:
            text = element.text.strip()
            # 리뷰 텍스트만 추출 (너무 길거나 짧으면 제외)
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if 10 <= len(line) <= 1000:  # 적절한 길이의 텍스트
                    return line
        except:
            pass

        return ""

    def _extract_rating(self, element) -> int:
        """평점 추출 (1~5점)"""
        selectors = [
            'div.pui__star-wrap span.pui__nR0cX6',  # 별점 개수
            'em.pui__nR0cX6',
            'div[class*="star"]',
            'span.star',
        ]

        for selector in selectors:
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, selector)
                # aria-label에서 추출 시도
                aria_label = rating_elem.get_attribute('aria-label')
                if aria_label and '5' in aria_label:
                    # "5점 만점에 4점" 같은 형식
                    import re
                    match = re.search(r'(\d+)점', aria_label)
                    if match:
                        return int(match.group(1))

                # class에서 추출 시도
                class_name = rating_elem.get_attribute('class')
                if 'star' in class_name:
                    # 별 개수 세기
                    stars = element.find_elements(By.CSS_SELECTOR, 'em.pui__nR0cX6')
                    if stars:
                        return len(stars)
            except:
                continue

        return 5  # 기본값

    def _extract_author(self, element) -> str:
        """작성자 추출"""
        selectors = [
            'span.pui__gx7M46',
            'div.pui__-KNYym strong',
            'span[class*="author"]',
            'strong.reviewer',
        ]

        for selector in selectors:
            try:
                author_elem = element.find_element(By.CSS_SELECTOR, selector)
                author = author_elem.text.strip()
                if author:
                    return author
            except:
                continue

        return "익명"

    def _extract_date(self, element) -> str:
        """작성일 추출"""
        selectors = [
            'time.pui__9SOu_O',
            'span.pui__-KNYym time',
            'time',
            'span[class*="date"]',
        ]

        for selector in selectors:
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, selector)
                date = date_elem.text.strip()
                if date:
                    return date
            except:
                continue

        return ""

    def _extract_visit_type(self, element) -> str:
        """방문 형태 추출 (방문/포장/배달)"""
        try:
            # 방문 형태 표시 찾기
            badges = element.find_elements(By.CSS_SELECTOR, 'span.pui__badge, span[class*="badge"]')
            for badge in badges:
                text = badge.text.strip()
                if text in ['방문', '포장', '배달']:
                    return text
        except:
            pass

        return "방문"  # 기본값

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='네이버 플레이스 리뷰 크롤러')
    parser.add_argument('--place-id', type=str, required=True, help='네이버 플레이스 ID')
    parser.add_argument('--count', type=int, default=100, help='수집할 리뷰 개수 (기본: 100)')
    parser.add_argument('--output', type=str, default=None, help='출력 CSV 파일명')
    parser.add_argument('--delay', type=float, default=1.0, help='요청 간 지연 시간 (초)')
    parser.add_argument('--headless', action='store_true', help='헤드리스 모드로 실행')

    args = parser.parse_args()

    # 출력 파일명 생성
    if args.output is None:
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'naver_place_{args.place_id}_{timestamp}.csv'
    else:
        output_file = args.output

    # 크롤링 실행
    crawler = NaverPlaceCrawler(headless=args.headless, delay=args.delay)

    try:
        df = crawler.crawl_reviews(args.place_id, args.count)

        if len(df) > 0:
            # place_id 추가
            df['place_id'] = args.place_id

            # CSV 저장
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"💾 저장 완료: {output_file}")

            # 통계 출력
            print("\n📊 수집 통계:")
            print(f"  - 평균 평점: {df['rating'].mean():.2f}")
            if 'rating' in df.columns:
                print(f"  - 5점 리뷰: {len(df[df['rating'] == 5])}개 ({len(df[df['rating'] == 5])/len(df)*100:.1f}%)")
                print(f"  - 1-2점 리뷰: {len(df[df['rating'] <= 2])}개 ({len(df[df['rating'] <= 2])/len(df)*100:.1f}%)")
        else:
            print("⚠️ 수집된 리뷰가 없습니다.")

    except KeyboardInterrupt:
        print("\n\n중단됨. 수집된 데이터를 저장합니다...")
        if crawler.reviews:
            df = pd.DataFrame(crawler.reviews)
            df['place_id'] = args.place_id
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"💾 저장 완료: {output_file}")

    finally:
        crawler.close()


if __name__ == "__main__":
    main()


# 사용 예시:
# python naver_place_crawler.py --place-id 1234567890 --count 200 --headless
