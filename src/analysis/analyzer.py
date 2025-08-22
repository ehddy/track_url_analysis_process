"""
URL 접속 패턴 분석 모듈
"""

import pandas as pd
from .categorizer import URLCategorizer


class URLAnalyzer:
    """URL 접속 패턴 분석기"""
    
    def __init__(self):
        self.categorizer = URLCategorizer()
    
    def analyze_url_categories(self, df, start_url, ip):
        """
        URL 카테고리 통계 분석
        
        Args:
            df: DataFrame with 'category' column
            start_url: 추적할 시작 URL
            ip: 사용자 IP
        
        Returns:
            dict: 분석 결과
        """
        df = df.copy()
        
        # 카테고리 분류 적용
        df = self.categorizer.classify_dataframe(df, start_url)
        
        # 시간 정보 파싱 및 정렬
        df['_ts'] = pd.to_datetime(df['@timestamp'], errors='coerce')
        df = df.sort_values('_ts').reset_index(drop=True)
        
        # 기본 통계
        stats = self._calculate_basic_stats(df, start_url, ip)
        
        # 시간 관련 통계
        time_stats = self._calculate_time_stats(df)
        stats.update(time_stats)
        
        # 유해 사이트 관련 통계
        harmful_stats = self._calculate_harmful_stats(df, start_url)
        stats.update(harmful_stats)
        
        # Timestamp 객체를 문자열로 변환
        stats = self._convert_timestamps(stats)
        
        return stats
    
    def _calculate_basic_stats(self, df, start_url, ip):
        """기본 통계 계산"""
        if df.empty:
            return self._get_empty_stats(start_url, ip)
        
        most_accessed_url = df['sHost'].value_counts().index[0]
        
        # 기본 집계
        total = len(df)
        nunique_all = df['sHost'].nunique()
        
        # 분류별 건수
        classification_counts = df['classification'].value_counts()
        n_track = classification_counts.get('추적 URL', 0)
        n_harm = classification_counts.get('유해', 0)
        n_safe = classification_counts.get('안전', 0)
        n_unknown = classification_counts.get('미분류', 0)
        
        # 고유 URL 개수
        uniq_harm = df.loc[df['classification'] == '유해', 'sHost'].nunique()
        uniq_safe = df.loc[df['classification'] == '안전', 'sHost'].nunique()
        uniq_unknown = df.loc[df['classification'] == '미분류', 'sHost'].nunique()
        uniq_track = df.loc[df['classification'] == '추적 URL', 'sHost'].nunique()
        
        # 재방문성(평균 방문 횟수)
        avg_hits_per_host = round(float(total / nunique_all), 3) if nunique_all else 0.0
        
        return {
            '사용자 IP': ip,
            '추적 URL': start_url,
            '접속 Top URL': most_accessed_url,
            '총 접속 건수': total,
            '고유 유해 URL 개수': uniq_harm,
            '유해 접속 여부': 1 if uniq_harm > 0 else 0,
            '고유 안전 URL 개수': uniq_safe,
            '고유 미분류 URL 개수': uniq_unknown,
            '고유 추적 URL 개수': uniq_track,
            '평균 방문 횟수(고유당)': avg_hits_per_host,
        }
    
    def _calculate_time_stats(self, df):
        """시간 관련 통계 계산"""
        if df.empty or df['_ts'].isna().all():
            return {
                '관측 시작 시각': None,
                '관측 종료 시각': None,
                '관측 구간(초)': 0.0,
            }
        
        # 관측 구간 계산
        first_ts = df['_ts'].dropna().min()
        last_ts = df['_ts'].dropna().max()
        span_sec = float((last_ts - first_ts).total_seconds()) if pd.notna(first_ts) and pd.notna(last_ts) else 0.0
        
        return {
            '관측 시작 시각': first_ts,
            '관측 종료 시각': last_ts,
            '관측 구간(초)': span_sec,
        }
    
    def _calculate_harmful_stats(self, df, start_url):
        """유해 사이트 관련 통계 계산"""
        # 유해 URL 리스트
        harmful_urls = df.loc[df['classification'] == '유해', 'sHost'].unique().tolist()
        
        # 추적 URL 이후 첫 유해까지 소요시간
        time_to_first_harm_sec = None
        try:
            track_indices = df.index[df['classification'] == '추적 URL']
            if len(track_indices) > 0:
                start_idx = track_indices[0]
                start_time = df.loc[start_idx, '_ts']
                
                harmful_after_track = df.loc[
                    (df.index > start_idx) & (df['classification'] == '유해'), 
                    '_ts'
                ]
                
                if not harmful_after_track.empty:
                    first_harm = harmful_after_track.min()
                    if pd.notna(first_harm) and pd.notna(start_time):
                        time_to_first_harm_sec = float((first_harm - start_time).total_seconds())
        except (IndexError, KeyError):
            pass
        
        return {
            '추적→첫 유해 소요(초)': time_to_first_harm_sec,
            '유해 URL 리스트': harmful_urls
        }
    
    def _get_empty_stats(self, start_url, ip):
        """빈 데이터프레임에 대한 기본 통계"""
        return {
            '사용자 IP': ip,
            '추적 URL': start_url,
            '접속 Top URL': 'N/A',
            '총 접속 건수': 0,
            '고유 유해 URL 개수': 0,
            '유해 접속 여부': 0,
            '고유 안전 URL 개수': 0,
            '고유 미분류 URL 개수': 0,
            '고유 추적 URL 개수': 0,
            '평균 방문 횟수(고유당)': 0.0,
            '관측 시작 시각': None,
            '관측 종료 시각': None,
            '관측 구간(초)': 0.0,
            '추적→첫 유해 소요(초)': None,
            '유해 URL 리스트': []
        }
    
    def _convert_timestamps(self, stats):
        """Timestamp 객체를 문자열로 변환"""
        converted_stats = {}
        for k, v in stats.items():
            if isinstance(v, pd.Timestamp):
                converted_stats[k] = v.isoformat() if pd.notna(v) else None
            else:
                converted_stats[k] = v
        return converted_stats