"""
URL 카테고리 분류 모듈
"""

import pandas as pd
from config.settings import HARMFUL_CATEGORIES, SAFE_CATEGORIES


class URLCategorizer:
    """URL 카테고리 분류기"""
    
    def __init__(self):
        self.harmful_categories = HARMFUL_CATEGORIES
        self.safe_categories = SAFE_CATEGORIES
    
    def classify_category(self, category):
        """개별 카테고리 분류"""
        if pd.isna(category) or category == '' or category is None:
            return '미분류'
        elif str(category) in self.harmful_categories:
            return '유해'
        elif str(category) in self.safe_categories:
            return '안전'
        else:
            return '미분류'
    
    def classify_dataframe(self, df, track_url=None):
        """데이터프레임에 분류 컬럼 추가"""
        df = df.copy()
        
        # 기본 카테고리 분류
        df['classification'] = df['category'].apply(self.classify_category)
        
        # 추적 URL이 있는 경우 별도 표시
        if track_url:
            df['classification'] = df.apply(
                lambda row: "추적 URL" if row['sHost'] == track_url else row['classification'], 
                axis=1
            )
        
        return df
    
    def get_category_info(self, category):
        """카테고리 상세 정보 반환"""
        if str(category) in self.harmful_categories:
            return {
                'type': '유해',
                'description': self.harmful_categories[str(category)],
                'code': str(category)
            }
        elif str(category) in self.safe_categories:
            return {
                'type': '안전',
                'description': self.safe_categories[str(category)],
                'code': str(category)
            }
        else:
            return {
                'type': '미분류',
                'description': '분류되지 않음',
                'code': str(category) if not pd.isna(category) else 'None'
            }
    
    def get_harmful_categories(self):
        """유해 카테고리 목록 반환"""
        return list(self.harmful_categories.keys())
    
    def get_safe_categories(self):
        """안전 카테고리 목록 반환"""
        return list(self.safe_categories.keys())
    
    def is_harmful(self, category):
        """유해 카테고리 여부 확인"""
        return str(category) in self.harmful_categories
    
    def is_safe(self, category):
        """안전 카테고리 여부 확인"""
        return str(category) in self.safe_categories