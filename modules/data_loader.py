"""
Data Loader Module
파일 읽기 및 기본 검증 기능
"""

import pandas as pd
from pathlib import Path
from typing import Union, Tuple
import chardet


class DataLoader:
    """데이터 파일 로드 및 기본 검증"""
    
    @staticmethod
    def load_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """
        CSV 또는 Excel 파일 로드
        
        Args:
            file_path: 파일 경로
            
        Returns:
            pd.DataFrame: 로드된 데이터프레임
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        # 파일 확장자에 따라 로드
        if file_path.suffix.lower() == '.csv':
            return DataLoader._load_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_path.suffix}")
    
    @staticmethod
    def _load_csv(file_path: Path) -> pd.DataFrame:
        """
        CSV 파일 로드 (인코딩 자동 감지)
        
        Args:
            file_path: CSV 파일 경로
            
        Returns:
            pd.DataFrame: 로드된 데이터프레임
        """
        # 인코딩 감지
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
            encoding = result['encoding']
        
        # CSV 읽기 시도
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except UnicodeDecodeError:
            # 인코딩 실패 시 일반적인 인코딩 시도
            for enc in ['utf-8', 'cp949', 'euc-kr', 'latin1']:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    return df
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
                except Exception as e:
                    raise ValueError(f"CSV 파일 읽기 실패 ({enc} 인코딩): {str(e)}")
            raise ValueError("CSV 파일 인코딩을 인식할 수 없습니다. 파일이 손상되었거나 CSV 형식이 아닐 수 있습니다.")
    
    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> dict:
        """
        데이터 품질 리포트 생성
        
        Args:
            df: 데이터프레임
            
        Returns:
            dict: 품질 리포트 정보
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_missing': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'column_info': {
                col: {
                    'dtype': str(df[col].dtype),
                    'missing': int(df[col].isnull().sum()),
                    'missing_pct': float(df[col].isnull().sum() / len(df) * 100),
                    'unique': int(df[col].nunique()),
                    'unique_pct': float(df[col].nunique() / len(df) * 100)
                }
                for col in df.columns
            }
        }
        
        # 날짜 컬럼 감지
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # 샘플링하여 날짜 형식 확인
                sample = df[col].dropna().head(100)
                try:
                    pd.to_datetime(sample)
                    date_columns.append(col)
                except:
                    pass
        
        report['detected_date_columns'] = date_columns
        
        return report
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: list) -> Tuple[bool, list]:
        """
        필수 컬럼 존재 여부 확인
        
        Args:
            df: 데이터프레임
            required_columns: 필수 컬럼 리스트
            
        Returns:
            (bool, list): (검증 통과 여부, 누락된 컬럼 리스트)
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns


if __name__ == "__main__":
    # 테스트 코드
    print("DataLoader 모듈 테스트")
    
    # 샘플 데이터 생성
    sample_df = pd.DataFrame({
        'CustomerID': [1, 2, 3, None, 5],
        'InvoiceDate': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Quantity': [10, 20, None, 15, 25],
        'UnitPrice': [100, 200, 300, 400, 500]
    })
    
    # 품질 리포트
    loader = DataLoader()
    report = loader.get_data_quality_report(sample_df)
    print("\n데이터 품질 리포트:")
    print(f"총 행 수: {report['total_rows']}")
    print(f"총 컬럼 수: {report['total_columns']}")
    print(f"결측치: {report['total_missing']}")
    print(f"중복 행: {report['duplicate_rows']}")
    
    # 필수 컬럼 검증
    required = ['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice']
    is_valid, missing = loader.validate_required_columns(sample_df, required)
    print(f"\n필수 컬럼 검증: {is_valid}")
    if not is_valid:
        print(f"누락된 컬럼: {missing}")
