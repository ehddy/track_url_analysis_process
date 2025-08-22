"""
메인 실행 파일
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import ANALYSIS_CONFIG
from src.data.es_client import ESDataClient
from src.data.hims_client import HIMSClient
from src.analysis.analyzer import URLAnalyzer
from src.utils.file_manager import FileManager
from src.utils.checkpoint import CheckpointManager


class URLAnalysisRunner:
    """URL 분석 실행기 (날짜별 관리)"""
    
    def __init__(self, output_dir=None, analysis_date=None):
        """
        Args:
            output_dir: 출력 디렉토리 
            analysis_date: 분석 날짜 (YYYY-MM-DD), None이면 오늘 날짜
        """
        self.output_dir = output_dir or ANALYSIS_CONFIG['default_output_dir']
        self.analysis_date = analysis_date or datetime.now().strftime('%Y-%m-%d')
        
        # 각 모듈 초기화 (날짜별)
        self.es_client = ESDataClient()
        self.hims_client = HIMSClient()
        self.analyzer = URLAnalyzer()
        self.file_manager = FileManager(self.output_dir, self.analysis_date)
        self.checkpoint_manager = CheckpointManager(self.output_dir, self.analysis_date)
        
        # 설정값들
        self.max_ips_per_url = ANALYSIS_CONFIG['max_ips_per_url']
        self.min_records_threshold = ANALYSIS_CONFIG['min_records_threshold']
        self.time_window_hours = ANALYSIS_CONFIG['time_window_hours']
    
    def run_analysis(self, urls, resume=True):
        """
        URL 분석 실행 (날짜별 관리)
        
        Args:
            urls: 분석할 URL 리스트
            resume: 이전 진행상황에서 재시작할지 여부
        
        Returns:
            pandas.DataFrame: 분석 결과
        """
        self.file_manager.log_progress(f"=== {self.analysis_date} 날짜 분석 시작 ===")
        
        # 체크포인트 확인
        checkpoint = None
        processed_pairs = set()
        
        if resume:
            checkpoint = self.checkpoint_manager.load_checkpoint()
            processed_pairs = self.file_manager.get_processed_pairs()
            if checkpoint:
                self.file_manager.log_progress(f"체크포인트에서 재시작: {checkpoint['last_processed']}")
            else:
                self.file_manager.log_progress(f"{self.analysis_date} 날짜의 새로운 분석을 시작합니다.")
        else:
            self.file_manager.log_progress("이전 진행상황을 무시하고 새로 시작합니다.")
        
        # 시작 인덱스 설정
        start_url_index = checkpoint['url_index'] if checkpoint else 0
        
        try:
            for url_idx, url in enumerate(urls[start_url_index:], start_url_index):
                self._process_url(url, url_idx, len(urls), checkpoint, processed_pairs)
                
        except KeyboardInterrupt:
            self.file_manager.log_progress("사용자에 의해 중단됨")
        except Exception as e:
            self.file_manager.log_progress(f"예상치 못한 오류: {str(e)}")
        
        self.file_manager.log_progress(f"=== {self.analysis_date} 날짜 분석 완료 ===")
        return self.file_manager.load_all_results()
    
    def _process_url(self, url, url_idx, total_urls, checkpoint, processed_pairs):
        """단일 URL 처리"""
        self.file_manager.log_progress(f"Processing URL {url_idx+1}/{total_urls}: {url}")
        
        try:
            # IP 목록 조회
            source_ips = self.es_client.get_aggregated_ips(url)
            self.file_manager.log_progress(f"Found {len(source_ips)} source IPs for {url}")
            
            if not source_ips:
                self.file_manager.log_progress(f"No IPs found for {url}")
                return
            
            # IP 처리 시작 인덱스 설정
            start_ip_index = 0
            if checkpoint and checkpoint['url_index'] == url_idx:
                start_ip_index = checkpoint['ip_index'] + 1
            
            # 상위 N개 IP만 처리
            ip_list = [d['sSrcIP'] for d in source_ips[:self.max_ips_per_url]]
            
            for ip_idx, ip in enumerate(ip_list[start_ip_index:], start_ip_index):
                self._process_ip(url, ip, url_idx, ip_idx, total_urls, len(ip_list), processed_pairs)
                
        except Exception as e:
            self.file_manager.log_progress(f"✗ Error processing URL {url}: {str(e)}")
    
    def _process_ip(self, url, ip, url_idx, ip_idx, total_urls, total_ips, processed_pairs):
        """단일 IP 처리"""
        # 이미 처리된 쌍은 건너뛰기
        if (url, ip) in processed_pairs:
            self.file_manager.log_progress(f"Skipping already processed: {url} - {ip}")
            return
        
        self.file_manager.log_progress(f"  Processing IP {ip_idx+1}/{total_ips}: {ip}")
        
        try:
            # 원시 데이터 조회
            df = self.es_client.get_raw_data(ip)
            if df.empty:
                self.file_manager.log_progress(f"    Empty DataFrame for IP: {ip}")
                return
            
            # 데이터 전처리
            processed_df = self._preprocess_data(df, url, ip)
            if processed_df is None:
                return
            
            # 카테고리 정보 추가
            processed_df = self._add_category_info(processed_df)
            
            # 분석 실행
            result = self.analyzer.analyze_url_categories(processed_df, url, ip)
            
            # 결과 저장
            self.file_manager.save_result(result)
            processed_pairs.add((url, ip))
            
            self.file_manager.log_progress(f"    ✓ Analysis completed for {url} - {ip}")
            
        except Exception as e:
            self.file_manager.log_progress(f"    ✗ Error processing IP {ip}: {str(e)}")
        finally:
            # 체크포인트 저장
            self.checkpoint_manager.save_checkpoint(
                url_idx, ip_idx, total_urls, total_ips, url
            )
    
    def _preprocess_data(self, df, url, ip):
        """데이터 전처리"""
        # 정렬 및 인덱스 리셋
        df = df.sort_values("@timestamp", kind="mergesort").reset_index(drop=True)
        
        # 해당 URL 첫 등장 인덱스 찾기
        m = df['sHost'].eq(url)
        if not m.any():
            self.file_manager.log_progress(f"    '{url}' not found in DataFrame for IP: {ip}")
            return None
        
        start_index = m.idxmax() + 1
        subset_df = df.iloc[start_index:].copy()
        
        if subset_df.empty:
            self.file_manager.log_progress(f"    Empty subset for IP: {ip}")
            return None
        
        # 시간 필터링
        subset_df = self._apply_time_filter(subset_df, ip)
        if subset_df is None:
            return None
        
        # 최소 레코드 수 확인
        if len(subset_df) < self.min_records_threshold:
            self.file_manager.log_progress(
                f"    Insufficient data (< {self.min_records_threshold} records) for IP: {ip}"
            )
            return None
        
        return subset_df
    
    def _apply_time_filter(self, subset_df, ip):
        """시간 윈도우 필터링"""
        # timestamp 파싱
        ts = pd.to_datetime(subset_df["@timestamp"], errors="coerce")
        if ts.isna().all():
            self.file_manager.log_progress(f"    Invalid timestamps for IP: {ip}")
            return None
        
        # 시간 윈도우 적용
        start_time = ts.iloc[0]
        end_time = start_time + pd.Timedelta(hours=self.time_window_hours)
        
        filtered_df = subset_df[(ts >= start_time) & (ts <= end_time)].copy()
        
        if filtered_df.empty:
            self.file_manager.log_progress(f"    No data in time window for IP: {ip}")
            return None
        
        return filtered_df
    
    def _add_category_info(self, df):
        """카테고리 정보 추가"""
        # 고유 호스트에 대해서만 HIMS 조회
        unique_hosts = df['sHost'].unique().tolist()
        cat_map = self.hims_client.get_category_map(unique_hosts)
        
        # 벡터화 적용
        df['category'] = df['sHost'].map(cat_map)
        
        return df
    
    def get_analysis_summary(self, date_range=None):
        """
        분석 결과 요약 (날짜별)
        
        Args:
            date_range: 조회할 날짜 범위 리스트, None이면 현재 날짜만
        """
        df = self.file_manager.load_all_results(date_range)
        if df.empty:
            return "분석 결과가 없습니다."
        
        summary = {
            "분석 날짜": date_range or [self.analysis_date],
            "총 분석 건수": len(df),
            "고유 URL 수": df['추적 URL'].nunique() if '추적 URL' in df.columns else 0,
            "고유 IP 수": df['사용자 IP'].nunique() if '사용자 IP' in df.columns else 0,
            "유해 접속 건수": (df['유해 접속 여부'] == 1).sum() if '유해 접속 여부' in df.columns else 0,
        }
        
        # 날짜별 세부 정보 추가
        if '분석_날짜' in df.columns:
            daily_counts = df['분석_날짜'].value_counts().to_dict()
            summary["날짜별 건수"] = daily_counts
        
        return summary
    
    def clear_data(self, specific_date=None, clear_all=False):
        """
        데이터 초기화
        
        Args:
            specific_date: 특정 날짜만 삭제 (YYYY-MM-DD)
            clear_all: 모든 날짜 삭제 여부
        """
        if clear_all:
            self.file_manager.clear_all_results()
            print("모든 날짜의 데이터가 삭제되었습니다.")
        else:
            target_date = specific_date or self.analysis_date
            self.file_manager.clear_results(target_date)
            self.checkpoint_manager.clear_checkpoint(target_date)
            print(f"{target_date} 날짜의 데이터가 삭제되었습니다.")
    
    def get_available_dates(self):
        """분석 가능한 날짜 목록 반환"""
        return {
            'analysis_dates': self.file_manager.get_available_dates(),
            'checkpoint_dates': self.checkpoint_manager.get_available_checkpoint_dates()
        }
    
    def get_daily_summary(self):
        """날짜별 요약 정보"""
        file_summary = self.file_manager.get_daily_summary()
        checkpoint_summary = self.checkpoint_manager.get_all_checkpoints_summary()
        
        # 날짜별로 병합
        combined = {}
        
        # 파일 정보 추가
        for item in file_summary:
            date = item['date']
            combined[date] = {
                'date': date,
                'records': item['records'],
                'size_mb': item['size_mb'],
                'has_checkpoint': False,
                'progress': 0,
                'status': 'completed' if item['records'] > 0 else 'no_data'
            }
        
        # 체크포인트 정보 추가
        for item in checkpoint_summary:
            date = item['date']
            if date in combined:
                combined[date]['has_checkpoint'] = True
                combined[date]['progress'] = item['progress']
                combined[date]['status'] = 'in_progress' if item['progress'] < 100 else 'completed'
            else:
                combined[date] = {
                    'date': date,
                    'records': 0,
                    'size_mb': 0,
                    'has_checkpoint': True,
                    'progress': item['progress'],
                    'status': 'in_progress'
                }
        
        return sorted(combined.values(), key=lambda x: x['date'], reverse=True)

