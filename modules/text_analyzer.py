"""
Text Analyzer Module
리뷰/댓글 감성 분석 및 토픽 모델링
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
from collections import Counter

# NLP 라이브러리
try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    print("WARNING: KoNLPy is not installed. Korean morphological analysis will be limited.")

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class TextAnalyzer:
    """텍스트 감성 분석 및 토픽 모델링"""
    
    def __init__(self, df: pd.DataFrame, 
                 text_column: str = 'review',
                 rating_column: str = None):
        """
        Args:
            df: 텍스트 데이터프레임
            text_column: 텍스트 컬럼명
            rating_column: 평점 컬럼명 (선택, 있으면 감성 분석에 활용)
        """
        self.df = df.copy()
        self.text_column = text_column
        self.rating_column = rating_column
        
        # KoNLPy 형태소 분석기 초기화
        if KONLPY_AVAILABLE:
            self.okt = Okt()
        else:
            self.okt = None
        
        # 한국어 불용어
        self.stopwords = set([
            '은', '는', '이', '가', '을', '를', '에', '의', '와', '과', '도', '으로', '로',
            '에서', '으', 'ㄴ', '것', '수', '등', '들', '및', '더', '좀', '잘', '걍', '막',
            '게', '네', '요', '임', '음', '하', '아', '어', '의', '때', '거', '군', '듯',
            '나', '내', '네', '니', '다', '당신', '따', '또', '때', '뭐', '및', '수도',
            '안', '어디', '어떤', '여기', '오', '왜', '요', '우리', '이', '저', '제', '좀'
        ])
        
        self.processed_texts = None
        self.sentiment_results = None
    
    def preprocess_text(self) -> pd.DataFrame:
        """
        텍스트 전처리 (정규화, 토큰화, 불용어 제거)
        
        Returns:
            전처리된 데이터프레임
        """
        # 텍스트 전처리 중...
        
        processed = []
        
        for text in self.df[self.text_column]:
            if pd.isna(text) or not isinstance(text, str):
                processed.append("")
                continue
            
            # 1. 소문자 변환 및 특수문자 제거
            text = text.lower()
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 2. 형태소 분석 (명사 추출)
            if self.okt:
                try:
                    # 명사만 추출
                    nouns = self.okt.nouns(text)
                    # 불용어 제거 및 2글자 이상만
                    tokens = [word for word in nouns
                             if word not in self.stopwords and len(word) >= 2]
                    processed.append(' '.join(tokens))
                except Exception as e:
                    # 형태소 분석 실패 시 단순 분리 사용
                    import warnings
                    warnings.warn(f"형태소 분석 실패: {str(e)[:50]}, 단순 분리로 대체")
                    tokens = [word for word in text.split()
                             if word not in self.stopwords and len(word) >= 2]
                    processed.append(' '.join(tokens))
            else:
                # KoNLPy 없으면 단순 공백 분리
                tokens = [word for word in text.split() 
                         if word not in self.stopwords and len(word) >= 2]
                processed.append(' '.join(tokens))
        
        self.df['processed_text'] = processed
        self.processed_texts = processed
        
        print(f"OK 전처리 완료: {len(processed)}개 텍스트")
        return self.df
    
    def analyze_sentiment_simple(self) -> pd.DataFrame:
        """
        간단한 감성 분석 (평점과 키워드 하이브리드)
        수정사항: 평점이 애매(3점)하더라도 키워드가 확실하면 키워드 우선 적용
        """
        # 감성 분석 중...
        
        sentiments = []
        sentiment_scores = []
        
        # 긍정/부정 키워드 사전 (보강됨)
        positive_keywords = set([
            '좋', '최고', '훌륭', '멋지', '완벽', '추천', '만족', '감동', '재밌', '재미있', 
            '유익', '효과', '대박', '강추', '짱', '친절', '깔끔', '맛있', '편하', '행복',
            '사랑', '감사', '굳', '굿', 'good', 'nice'
        ])
        
        negative_keywords = set([
            '나쁘', '별로', '최악', '실망', '후회', '불만', '아쉽', '지루', '비추', '돈아깝', 
            '환불', '비싸', '비쌈', '불친절', '더럽', '짜증', '최하', '노답', '망', '쓰레기',
            '느리', '답답', 'bad', 'worst', '비추천', 
        ])
        
        for idx, row in self.df.iterrows():
            sentiment = 'neutral' # 기본값
            score = 0.5
            
            # 1. 키워드 기반 점수 계산 (텍스트 분석 우선)
            text = str(row[self.text_column]).lower()
            pos_count = sum(1 for keyword in positive_keywords if keyword in text)
            neg_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            keyword_sentiment = None
            if pos_count > neg_count:
                keyword_sentiment = 'positive'
            elif neg_count > pos_count:
                keyword_sentiment = 'negative'
                
            # 2. 평점 기반 점수 확인
            rating_sentiment = None
            if self.rating_column and self.rating_column in self.df.columns:
                rating = row[self.rating_column]
                if pd.notna(rating):
                    try:
                        rating = float(rating)
                        max_rating = self.df[self.rating_column].max()
                        if max_rating <= 5:
                            rating = rating * 2  # 10점 만점으로 환산

                        if rating >= 8:
                            rating_sentiment = 'positive'
                            score = 1.0
                        elif rating <= 4: # 4점 이하는 부정 (기준 강화)
                            rating_sentiment = 'negative'
                            score = 0.0
                        else:
                            rating_sentiment = 'neutral' # 5~7점은 중립
                            score = 0.5
                    except:
                        pass

            # 3. 최종 결정 로직 (하이브리드)
            # 키워드가 명확하면 키워드를 따르고, 아니면 평점을 따름
            if keyword_sentiment:
                sentiment = keyword_sentiment
                score = 1.0 if keyword_sentiment == 'positive' else 0.0
            elif rating_sentiment:
                sentiment = rating_sentiment
            
            sentiments.append(sentiment)
            sentiment_scores.append(score)
        
        self.df['sentiment'] = sentiments
        self.df['sentiment_score'] = sentiment_scores
        
        # 감성 분포 계산
        sentiment_dist = self.df['sentiment'].value_counts()
        print(f"OK 감성 분석 완료:")
        print(f"   긍정: {sentiment_dist.get('positive', 0)}개")
        print(f"   중립: {sentiment_dist.get('neutral', 0)}개")
        print(f"   부정: {sentiment_dist.get('negative', 0)}개")
        
        return self.df
    
    def extract_keywords(self, top_n: int = 20, by_sentiment: bool = True) -> Dict:
        """
        TF-IDF 기반 주요 키워드 추출
        
        Args:
            top_n: 추출할 키워드 개수
            by_sentiment: 감성별로 분리하여 추출
        
        Returns:
            키워드 딕셔너리
        """
        # 키워드 추출 중...
        
        if self.processed_texts is None:
            self.preprocess_text()
        
        results = {}
        
        if by_sentiment and 'sentiment' in self.df.columns:
            # 감성별로 키워드 추출
            for sentiment in ['positive', 'neutral', 'negative']:
                texts = self.df[self.df['sentiment'] == sentiment]['processed_text'].tolist()

                # 빈 텍스트 제거
                texts = [t for t in texts if t and len(t.strip()) > 0]

                if len(texts) < 2:
                    # 문서가 2개 미만이면 TF-IDF 불가능
                    results[sentiment] = []
                    continue

                # min_df를 동적으로 조정
                min_df_value = min(2, len(texts))
                tfidf = TfidfVectorizer(max_features=top_n, min_df=min_df_value)
                try:
                    tfidf_matrix = tfidf.fit_transform(texts)
                    feature_names = tfidf.get_feature_names_out()

                    # 평균 TF-IDF 점수 계산
                    avg_scores = tfidf_matrix.mean(axis=0).A1
                    top_indices = avg_scores.argsort()[-top_n:][::-1]

                    keywords = [(feature_names[i], float(avg_scores[i]))
                               for i in top_indices]
                    results[sentiment] = keywords
                except Exception as e:
                    import warnings
                    warnings.warn(f"{sentiment} 키워드 추출 실패: {str(e)[:100]}")
                    results[sentiment] = []
        else:
            # 전체 키워드 추출
            # 빈 텍스트 제거
            valid_texts = [t for t in self.processed_texts if t and len(t.strip()) > 0]

            if len(valid_texts) < 2:
                print("WARNING 유효한 텍스트가 2개 미만입니다. 키워드 추출을 건너뜁니다.")
                results['all'] = []
                return results

            min_df_value = min(2, len(valid_texts))
            tfidf = TfidfVectorizer(max_features=top_n, min_df=min_df_value)
            try:
                tfidf_matrix = tfidf.fit_transform(valid_texts)
                feature_names = tfidf.get_feature_names_out()

                avg_scores = tfidf_matrix.mean(axis=0).A1
                top_indices = avg_scores.argsort()[-top_n:][::-1]

                keywords = [(feature_names[i], float(avg_scores[i]))
                           for i in top_indices]
                results['all'] = keywords
            except Exception as e:
                import warnings
                warnings.warn(f"키워드 추출 실패: {str(e)[:100]}")
                results['all'] = []
        
        print(f"OK 키워드 추출 완료")
        return results
    
    def extract_topics(self, n_topics: int = 5, n_words: int = 10) -> Dict:
        """
        LDA 토픽 모델링
        
        Args:
            n_topics: 추출할 토픽 개수
            n_words: 토픽당 단어 개수
        
        Returns:
            토픽 딕셔너리
        """
        # 토픽 모델링 중...
        
        if self.processed_texts is None:
            self.preprocess_text()

        # 빈 텍스트 제거
        valid_texts = [t for t in self.processed_texts if t and len(t.strip()) > 0]

        if len(valid_texts) < n_topics:
            print(f"WARNING 문서 수({len(valid_texts)})가 토픽 수({n_topics})보다 적습니다. 토픽 모델링을 건너뜁니다.")
            return {}

        # min_df를 동적으로 조정
        min_df_value = min(2, len(valid_texts))

        # CountVectorizer로 단어 빈도 행렬 생성
        vectorizer = CountVectorizer(max_features=1000, min_df=min_df_value, max_df=0.8)

        try:
            doc_term_matrix = vectorizer.fit_transform(valid_texts)

            # 어휘 크기 확인
            vocab_size = doc_term_matrix.shape[1]
            if vocab_size == 0:
                print("WARNING 추출된 단어가 없습니다. 불용어 설정을 확인하세요.")
                return {}

            # LDA 모델 학습
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=20,
                learning_method='online'
            )
            lda.fit(doc_term_matrix)

            # 토픽별 주요 단어 추출
            feature_names = vectorizer.get_feature_names_out()
            topics = {}

            for topic_idx, topic in enumerate(lda.components_):
                top_indices = topic.argsort()[-n_words:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                topics[f'Topic {topic_idx + 1}'] = top_words

            print(f"OK 토픽 모델링 완료")
            return topics

        except Exception as e:
            print(f"WARNING 토픽 모델링 실패: {str(e)}")
            return {}
    
    def get_word_frequency(self, top_n: int = 50) -> List[Tuple[str, int]]:
        """
        단어 빈도수 계산 (Word Cloud용)
        
        Args:
            top_n: 상위 N개 단어
        
        Returns:
            (단어, 빈도수) 튜플 리스트
        """
        if self.processed_texts is None:
            self.preprocess_text()
        
        # 모든 단어 추출
        all_words = []
        for text in self.processed_texts:
            all_words.extend(text.split())
        
        # 빈도수 계산
        word_counts = Counter(all_words)
        
        return word_counts.most_common(top_n)
    
    def get_sentiment_summary(self) -> Dict:
        """감성 분석 요약 통계"""
        if 'sentiment' not in self.df.columns:
            return {}
        
        total = len(self.df)
        sentiment_counts = self.df['sentiment'].value_counts()
        
        summary = {
            'total_reviews': total,
            'positive_count': int(sentiment_counts.get('positive', 0)),
            'neutral_count': int(sentiment_counts.get('neutral', 0)),
            'negative_count': int(sentiment_counts.get('negative', 0)),
            'positive_ratio': float(sentiment_counts.get('positive', 0) / total * 100),
            'neutral_ratio': float(sentiment_counts.get('neutral', 0) / total * 100),
            'negative_ratio': float(sentiment_counts.get('negative', 0) / total * 100),
            'avg_sentiment_score': float(self.df['sentiment_score'].mean()),
        }
        
        return summary