"""
Data Preprocessor Module
데이터 클렌징 및 전처리 기능
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from datetime import datetime


class DataPreprocessor:
    """데이터 전처리 및 클렌징"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: 원본 데이터프레임
        """
        self.df = df.copy()
        self.original_shape = df.shape
        self.preprocessing_log = []
    
    def handle_missing_values(self, strategy: str = 'auto') -> 'DataPreprocessor':
        """
        결측치 처리
        
        Args:
            strategy: 'auto', 'drop', 'fill_mean', 'fill_median', 'fill_mode'
        
        Returns:
            self: 체이닝을 위한 자기 자신 반환
        """
        initial_missing = self.df.isnull().sum().sum()
        
        if strategy == 'auto':
            # 각 컬럼별로 적절한 전략 자동 선택
            for col in self.df.columns:
                missing_pct = self.df[col].isnull().sum() / len(self.df) * 100

                # 결측치가 100%이면 건너뛰기
                if missing_pct == 100:
                    self.preprocessing_log.append(
                        f"⚠️  '{col}' 컬럼은 100% 결측치입니다. 컬럼 삭제를 고려하세요."
                    )
                    continue

                # 결측치가 50% 이상이면 경고 로그
                if missing_pct > 50:
                    self.preprocessing_log.append(
                        f"⚠️  '{col}' 컬럼의 결측치 비율이 {missing_pct:.1f}%로 매우 높습니다."
                    )

                # 결측치가 있는 경우 처리
                if self.df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        # 숫자형: 중앙값으로 대체
                        median_value = self.df[col].median()
                        if pd.notna(median_value):
                            self.df[col].fillna(median_value, inplace=True)
                    else:
                        # 범주형: 최빈값으로 대체
                        mode_value = self.df[col].mode()
                        if len(mode_value) > 0:
                            self.df[col].fillna(mode_value[0], inplace=True)
                        else:
                            self.df[col].fillna('Unknown', inplace=True)
        
        elif strategy == 'drop':
            self.df.dropna(inplace=True)
        
        final_missing = self.df.isnull().sum().sum()
        self.preprocessing_log.append(
            f"✅ 결측치 처리: {initial_missing}개 → {final_missing}개"
        )
        
        return self
    
    def remove_duplicates(self) -> 'DataPreprocessor':
        """중복 행 제거"""
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed = initial_rows - len(self.df)
        
        if removed > 0:
            self.preprocessing_log.append(f"✅ 중복 행 제거: {removed}개")
        
        return self
    
    def handle_outliers(self, columns: Optional[List[str]] = None, 
                       method: str = 'IQR', multiplier: float = 1.5) -> 'DataPreprocessor':
        """
        이상치 처리
        
        Args:
            columns: 처리할 컬럼 리스트 (None이면 모든 숫자형 컬럼)
            method: 'IQR' or 'zscore'
            multiplier: IQR 방식의 경우 사용할 배수
        
        Returns:
            self
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col not in self.df.columns or not pd.api.types.is_numeric_dtype(self.df[col]):
                continue
            
            initial_count = len(self.df)
            
            if method == 'IQR':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1

                # IQR이 0인 경우 (모든 값이 동일)
                if IQR == 0:
                    self.preprocessing_log.append(
                        f"ℹ️  '{col}' 컬럼의 IQR이 0입니다 (모든 값이 유사). 이상치 처리를 건너뜁니다."
                    )
                    continue

                lower_bound = Q1 - multiplier * IQR
                upper_bound = Q3 + multiplier * IQR

                # 이상치 플래깅
                outliers = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                outlier_count = outliers.sum()

                if outlier_count > 0:
                    # Winsorization (극단값을 경계값으로 대체)
                    self.df.loc[self.df[col] < lower_bound, col] = lower_bound
                    self.df.loc[self.df[col] > upper_bound, col] = upper_bound

                    self.preprocessing_log.append(
                        f"✅ '{col}' 이상치 처리 (IQR): {outlier_count}개 조정"
                    )
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outliers = z_scores > 3
                outlier_count = outliers.sum()
                
                if outlier_count > 0:
                    # 3 시그마를 벗어나는 값 제거
                    self.df = self.df[~outliers]
                    
                    self.preprocessing_log.append(
                        f"✅ '{col}' 이상치 제거 (Z-score): {outlier_count}개"
                    )
        
        return self
    
    def convert_date_columns(self, date_columns: List[str]) -> 'DataPreprocessor':
        """
        날짜 컬럼을 datetime 타입으로 변환
        
        Args:
            date_columns: 날짜 컬럼 리스트
        
        Returns:
            self
        """
        for col in date_columns:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_datetime(self.df[col])
                    self.preprocessing_log.append(f"✅ '{col}' 날짜 형식 변환 완료")
                except Exception as e:
                    self.preprocessing_log.append(f"⚠️  '{col}' 날짜 변환 실패: {str(e)}")
        
        return self
    
    def create_date_features(self, date_column: str) -> 'DataPreprocessor':
        """
        날짜 컬럼으로부터 파생 변수 생성
        
        Args:
            date_column: 날짜 컬럼명
        
        Returns:
            self
        """
        if date_column not in self.df.columns:
            self.preprocessing_log.append(f"⚠️  '{date_column}' 컬럼을 찾을 수 없습니다.")
            return self
        
        # datetime 타입으로 변환
        if self.df[date_column].dtype != 'datetime64[ns]':
            self.df[date_column] = pd.to_datetime(self.df[date_column])
        
        # 파생 변수 생성
        self.df[f'{date_column}_year'] = self.df[date_column].dt.year
        self.df[f'{date_column}_month'] = self.df[date_column].dt.month
        self.df[f'{date_column}_day'] = self.df[date_column].dt.day
        self.df[f'{date_column}_dayofweek'] = self.df[date_column].dt.dayofweek
        self.df[f'{date_column}_is_weekend'] = self.df[date_column].dt.dayofweek.isin([5, 6]).astype(int)
        
        # 계절 정보
        def get_season(month):
            if month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            elif month in [9, 10, 11]:
                return 'Fall'
            else:
                return 'Winter'
        
        self.df[f'{date_column}_season'] = self.df[f'{date_column}_month'].apply(get_season)
        
        self.preprocessing_log.append(f"✅ '{date_column}'에서 날짜 파생 변수 생성 완료")
        
        return self
    
    def normalize_column_names(self) -> 'DataPreprocessor':
        """컬럼명 정규화 (소문자 변환, 공백, 특수문자 제거)"""
        old_columns = self.df.columns.tolist()
        new_columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in old_columns]
        self.df.columns = new_columns

        if old_columns != new_columns:
            self.preprocessing_log.append("✅ 컬럼명 정규화 완료 (소문자 변환)")

        return self
    
    def filter_by_condition(self, condition: str) -> 'DataPreprocessor':
        """
        조건에 따라 데이터 필터링
        
        Args:
            condition: 필터링 조건 (예: "Quantity > 0")
        
        Returns:
            self
        """
        initial_rows = len(self.df)
        self.df = self.df.query(condition)
        removed = initial_rows - len(self.df)
        
        if removed > 0:
            self.preprocessing_log.append(f"✅ 조건 필터링 ('{condition}'): {removed}개 행 제거")
        
        return self
    
    def get_processed_data(self) -> Tuple[pd.DataFrame, List[str]]:
        """
        전처리된 데이터와 로그 반환
        
        Returns:
            (pd.DataFrame, List[str]): (전처리된 데이터, 로그 메시지 리스트)
        """
        final_shape = self.df.shape
        summary = f"\n📊 전처리 요약: {self.original_shape} → {final_shape}"
        self.preprocessing_log.append(summary)
        
        return self.df, self.preprocessing_log


if __name__ == "__main__":
    # 테스트 코드
    print("DataPreprocessor 모듈 테스트")
    
    # 샘플 데이터 생성
    sample_df = pd.DataFrame({
        'CustomerID': [1, 2, 3, None, 5, 1],  # 결측치, 중복
        'InvoiceDate': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-01'],
        'Quantity': [10, 20, None, 15, 1000, 10],  # 결측치, 이상치
        'UnitPrice': [100, 200, 300, 400, 500, 100]
    })
    
    print("\n원본 데이터:")
    print(sample_df)
    
    # 전처리 실행
    preprocessor = DataPreprocessor(sample_df)
    processed_df, logs = (preprocessor
                          .normalize_column_names()
                          .handle_missing_values()
                          .remove_duplicates()
                          .handle_outliers(method='IQR')
                          .convert_date_columns(['InvoiceDate'])
                          .create_date_features('InvoiceDate')
                          .get_processed_data())
    
    print("\n전처리된 데이터:")
    print(processed_df)
    
    print("\n전처리 로그:")
    for log in logs:
        print(log)
