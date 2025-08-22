"""
파일 저장/로드 관리 모듈
"""

import json
import os
import pandas as pd
from datetime import datetime
import glob
import shutil
from .logger import get_logger


class FileManager:
    """분석 결과 파일 관리자 (날짜별 관리)"""
    
    def __init__(self, output_dir, analysis_date=None):
        """
        Args:
            output_dir: 결과 파일을 저장할 디렉토리
            analysis_date: 분석 날짜 (YYYY-MM-DD), None이면 오늘 날짜
        """
        self.output_dir = output_dir
        self.analysis_date = analysis_date or datetime.now().strftime('%Y-%m-%d')
        self.logger = get_logger()
        
        # 날짜별 서브디렉토리 생성
        self.date_dir = os.path.join(output_dir, self.analysis_date)
        self.results_file = os.path.join(self.date_dir, f"analysis_results_{self.analysis_date}.jsonl")
        self.progress_file = os.path.join(self.date_dir, f"progress_{self.analysis_date}.txt")
        
        # 디렉토리 생성
        os.makedirs(self.date_dir, exist_ok=True)
    
    def save_result(self, result_dict):
        """단일 분석 결과를 파일에 저장"""
        with open(self.results_file, 'a', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, default=str)
            f.write('\n')
    
    def load_all_results(self, date_range=None):
        """
        저장된 분석 결과를 로드하여 DataFrame으로 반환
        
        Args:
            date_range: 날짜 범위 리스트 ['2025-01-01', '2025-01-02'] 또는 None (현재 날짜만)
        """
        results = []
        
        if date_range is None:
            # 현재 날짜만 로드
            files_to_load = [self.results_file] if os.path.exists(self.results_file) else []
        else:
            # 지정된 날짜 범위의 파일들 로드
            files_to_load = []
            for date_str in date_range:
                date_file = os.path.join(self.output_dir, date_str, f"analysis_results_{date_str}.jsonl")
                if os.path.exists(date_file):
                    files_to_load.append(date_file)
        
        for file_path in files_to_load:
            results.extend(self._load_single_file(file_path))
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def _load_single_file(self, file_path):
        """단일 파일에서 결과 로드"""
        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        result = json.loads(line.strip())
                        # 분석 날짜 정보 추가
                        result['분석_날짜'] = os.path.basename(os.path.dirname(file_path))
                        results.append(result)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON 파싱 오류 ({file_path}, 라인 {line_num}): {e}")
                        continue
        return results
    
    def get_available_dates(self):
        """분석 결과가 있는 날짜 목록 반환"""
        dates = []
        if os.path.exists(self.output_dir):
            for item in os.listdir(self.output_dir):
                date_path = os.path.join(self.output_dir, item)
                if os.path.isdir(date_path) and self._is_valid_date_format(item):
                    result_file = os.path.join(date_path, f"analysis_results_{item}.jsonl")
                    if os.path.exists(result_file):
                        dates.append(item)
        return sorted(dates)
    
    def _is_valid_date_format(self, date_str):
        """날짜 형식 유효성 검사 (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def get_processed_pairs(self, date_range=None):
        """이미 처리된 (URL, IP) 쌍들을 반환"""
        processed = set()
        
        if date_range is None:
            # 현재 날짜만 확인
            files_to_check = [self.results_file] if os.path.exists(self.results_file) else []
        else:
            # 지정된 날짜 범위 확인
            files_to_check = []
            for date_str in date_range:
                date_file = os.path.join(self.output_dir, date_str, f"analysis_results_{date_str}.jsonl")
                if os.path.exists(date_file):
                    files_to_check.append(date_file)
        
        for file_path in files_to_check:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            result = json.loads(line.strip())
                            url = result.get('추적 URL')
                            ip = result.get('사용자 IP')
                            if url and ip:
                                processed.add((url, ip))
                        except json.JSONDecodeError:
                            continue
        
        return processed
    
    def clear_results(self, specific_date=None):
        """
        결과 파일들 초기화
        
        Args:
            specific_date: 특정 날짜만 삭제 (YYYY-MM-DD), None이면 현재 날짜
        """
        if specific_date:
            date_dir = os.path.join(self.output_dir, specific_date)
            files_to_remove = [
                os.path.join(date_dir, f"analysis_results_{specific_date}.jsonl"),
                os.path.join(date_dir, f"progress_{specific_date}.txt")
            ]
        else:
            files_to_remove = [self.results_file, self.progress_file]
        
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Removed: {file_path}")
        
        target_date = specific_date or self.analysis_date
        self.logger.info(f"{target_date} 날짜의 분석 결과가 초기화되었습니다.")
    
    def clear_all_results(self):
        """모든 날짜의 결과 파일 초기화"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
            self.logger.info("모든 분석 결과가 초기화되었습니다.")
    
    def log_progress(self, message):
        """진행상황 로그 (날짜별)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        with open(self.progress_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        self.logger.info(message)
    
    def clear_results(self, specific_date=None):
        """
        결과 파일들 초기화
        
        Args:
            specific_date: 특정 날짜만 삭제 (YYYY-MM-DD), None이면 현재 날짜
        """
        if specific_date:
            date_dir = os.path.join(self.output_dir, specific_date)
            files_to_remove = [
                os.path.join(date_dir, f"analysis_results_{specific_date}.jsonl"),
                os.path.join(date_dir, f"progress_{specific_date}.txt")
            ]
        else:
            files_to_remove = [self.results_file, self.progress_file]
        
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Removed: {file_path}")
        
        target_date = specific_date or self.analysis_date
        self.logger.info(f"{target_date} 날짜의 분석 결과가 초기화되었습니다.")
    
    def get_file_info(self, date_range=None):
        """
        결과 파일 정보 반환
        
        Args:
            date_range: 확인할 날짜 범위, None이면 현재 날짜만
        """
        info = {
            'analysis_date': self.analysis_date,
            'current_date_dir': self.date_dir,
            'results_file': self.results_file,
            'progress_file': self.progress_file,
            'results_exists': os.path.exists(self.results_file),
            'progress_exists': os.path.exists(self.progress_file),
            'available_dates': self.get_available_dates()
        }
        
        if date_range is None:
            # 현재 날짜만 확인
            info.update(self._get_single_date_info(self.results_file))
        else:
            # 여러 날짜 확인
            total_records = 0
            total_size = 0
            
            for date_str in date_range:
                date_file = os.path.join(self.output_dir, date_str, f"analysis_results_{date_str}.jsonl")
                if os.path.exists(date_file):
                    single_info = self._get_single_date_info(date_file)
                    total_records += single_info.get('total_records', 0)
                    total_size += single_info.get('file_size_mb', 0)
            
            info.update({
                'total_records': total_records,
                'file_size_mb': round(total_size, 2),
                'date_range': date_range
            })
        
        return info
    
    def _get_single_date_info(self, file_path):
        """단일 날짜 파일 정보"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f if line.strip())
                return {
                    'total_records': line_count,
                    'file_size_mb': round(os.path.getsize(file_path) / (1024*1024), 2)
                }
            except Exception as e:
                return {
                    'total_records': 0,
                    'file_size_mb': 0,
                    'error': str(e)
                }
        else:
            return {
                'total_records': 0,
                'file_size_mb': 0
            }
    
    def get_daily_summary(self):
        """날짜별 요약 정보 반환"""
        available_dates = self.get_available_dates()
        summary = []
        
        for date_str in available_dates:
            date_file = os.path.join(self.output_dir, date_str, f"analysis_results_{date_str}.jsonl")
            file_info = self._get_single_date_info(date_file)
            
            summary.append({
                'date': date_str,
                'records': file_info['total_records'],
                'size_mb': file_info['file_size_mb']
            })
        
        return summary