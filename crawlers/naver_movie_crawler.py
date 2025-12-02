"""
Naver Movie Review Crawler
네이버 영화 리뷰 크롤링 스크립트

사용법:
    python naver_movie_crawler.py --movie-id 12345 --count 1000 --output reviews.csv
"""

import argparse
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from tqdm import tqdm
from pathlib import Path


class NaverMovieCrawler:
    """네이버 영화 리뷰 크롤러"""
    
    def __init__(self, headless: bool = True, delay: float = 1.0):
        """
        Args:
            headless: 브라우저를 보이지 않게 실행
            delay: 요청 간 지연 시간 (초)
        """
        self.delay = delay
        self.reviews = []
        
        # Chrome 옵션 설정
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # WebDriver 초기화
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def crawl_reviews(self, movie_id: str, max_reviews: int = 100) -> pd.DataFrame:
        """
        영화 리뷰 크롤링
        
        Args:
            movie_id: 네이버 영화 ID
            max_reviews: 수집할 최대 리뷰 수
        
        Returns:
            pd.DataFrame: 리뷰 데이터프레임
        """
        base_url = f"https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code={movie_id}&type=after&page="
        
        print(f"🎬 영화 ID {movie_id}의 리뷰 크롤링 시작...")
        print(f"목표: {max_reviews}개 리뷰 수집")
        
        page = 1
        pbar = tqdm(total=max_reviews, desc="리뷰 수집 중")
        
        while len(self.reviews) < max_reviews:
            try:
                # 페이지 로드
                url = base_url + str(page)
                self.driver.get(url)
                time.sleep(self.delay)
                
                # 리뷰 요소 찾기
                review_elements = self.driver.find_elements(By.CSS_SELECTOR, '.score_result li')
                
                if not review_elements:
                    print(f"\n더 이상 리뷰가 없습니다. (페이지 {page})")
                    break
                
                # 각 리뷰 파싱
                for element in review_elements:
                    if len(self.reviews) >= max_reviews:
                        break
                    
                    try:
                        # 평점
                        score_elem = element.find_element(By.CSS_SELECTOR, '.star_score em')
                        score = int(score_elem.text)
                        
                        # 리뷰 텍스트
                        review_elem = element.find_element(By.CSS_SELECTOR, '.score_reple p')
                        review_text = review_elem.text.strip()
                        
                        # 작성자
                        author_elem = element.find_element(By.CSS_SELECTOR, '.score_reple a')
                        author = author_elem.text.strip()
                        
                        # 작성일
                        date_elem = element.find_element(By.CSS_SELECTOR, '.score_reple em:nth-of-type(2)')
                        date = date_elem.text.strip()
                        
                        # 공감 수
                        like_elem = element.find_element(By.CSS_SELECTOR, '.sympathy_button')
                        like_text = like_elem.text.replace('공감', '').strip()
                        likes = int(like_text) if like_text else 0
                        
                        self.reviews.append({
                            'movie_id': movie_id,
                            'author': author,
                            'score': score,
                            'review': review_text,
                            'date': date,
                            'likes': likes,
                            'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        pbar.update(1)

                    except (ValueError, AttributeError) as e:
                        # 개별 리뷰 파싱 실패는 무시 (예상 가능한 에러만)
                        continue
                    except Exception as e:
                        # 예상치 못한 에러는 경고 출력
                        import warnings
                        warnings.warn(f"리뷰 파싱 중 예상치 못한 에러: {str(e)[:100]}")
                        continue
                
                page += 1
                
            except Exception as e:
                print(f"\n⚠️  페이지 {page} 로드 실패: {str(e)}")
                break
        
        pbar.close()
        
        # DataFrame 변환
        df = pd.DataFrame(self.reviews)
        print(f"\n✅ 크롤링 완료! 총 {len(df)}개 리뷰 수집")
        
        return df
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='네이버 영화 리뷰 크롤러')
    parser.add_argument('--movie-id', type=str, required=True, help='네이버 영화 ID')
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
        output_file = output_dir / f'naver_movie_{args.movie_id}_{timestamp}.csv'
    else:
        output_file = args.output
    
    # 크롤링 실행
    crawler = NaverMovieCrawler(headless=args.headless, delay=args.delay)
    
    try:
        df = crawler.crawl_reviews(args.movie_id, args.count)
        
        # CSV 저장
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"💾 저장 완료: {output_file}")
        
        # 통계 출력
        print("\n📊 수집 통계:")
        print(f"  - 평균 평점: {df['score'].mean():.2f}")
        print(f"  - 긍정 리뷰 (8점 이상): {len(df[df['score'] >= 8])}개 ({len(df[df['score'] >= 8])/len(df)*100:.1f}%)")
        print(f"  - 부정 리뷰 (4점 이하): {len(df[df['score'] <= 4])}개 ({len(df[df['score'] <= 4])/len(df)*100:.1f}%)")
    
    except KeyboardInterrupt:
        print("\n\n중단됨. 수집된 데이터를 저장합니다...")
        if crawler.reviews:
            df = pd.DataFrame(crawler.reviews)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"💾 저장 완료: {output_file}")
    
    finally:
        crawler.close()


if __name__ == "__main__":
    main()


# 사용 예시:
# python naver_movie_crawler.py --movie-id 215095 --count 500 --headless
# (215095 = 범죄도시4 영화 ID 예시)
