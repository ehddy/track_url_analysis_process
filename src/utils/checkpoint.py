"""
체크포인트 관리 모듈 (날짜별 관리)
"""

import json
import os
from datetime import datetime


class CheckpointManager:
    """체크포인트 관리자 (날짜별 관리)"""
    
    def __init__(self, output_dir, analysis_date=None):
        """
        Args:
            output_dir: 출력 디렉토리
            analysis_date: 분석 날짜 (YYYY-MM-DD), None이면 오늘 날짜
        """
        self.output_dir = output_dir
        self.analysis_date = analysis_date or datetime.now().strftime('%Y-%m-%d')
        
        # 날짜별 서브디렉토리
        self.date_dir = os.path.join(output_dir, self.analysis_date)
        self.checkpoint_file = os.path.join(self.date_dir, f"checkpoint_{self.analysis_date}.json")
        
        # 디렉토리 생성
        os.makedirs(self.date_dir, exist_ok=True)
    
    def save_checkpoint(self, url_index, ip_index, total_urls, total_ips_for_current_url, current_url=None):
        """체크포인트 저장 (날짜별)"""
        checkpoint = {
            'analysis_date': self.analysis_date,
            'url_index': url_index,
            'ip_index': ip_index,
            'total_urls': total_urls,
            'total_ips_for_current_url': total_ips_for_current_url,
            'current_url': current_url,
            'timestamp': datetime.now().isoformat(),
            'last_processed': f"URL {url_index+1}/{total_urls}, IP {ip_index+1}/{total_ips_for_current_url}",
            'progress_percentage': round(((url_index * 100) + (ip_index * 100 / total_ips_for_current_url)) / total_urls, 2)
        }
        
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    def load_checkpoint(self, specific_date=None):
        """
        체크포인트 로드
        
        Args:
            specific_date: 특정 날짜 체크포인트 로드 (YYYY-MM-DD), None이면 현재 날짜
        """
        if specific_date:
            checkpoint_file = os.path.join(self.output_dir, specific_date, f"checkpoint_{specific_date}.json")
        else:
            checkpoint_file = self.checkpoint_file
            
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    
                # 날짜 검증
                checkpoint_date = checkpoint.get('analysis_date', self.analysis_date)
                if checkpoint_date != self.analysis_date and not specific_date:
                    print(f"경고: 체크포인트 날짜({checkpoint_date})와 현재 분석 날짜({self.analysis_date})가 다릅니다.")
                    
                return checkpoint
            except json.JSONDecodeError as e:
                print(f"체크포인트 파일 파싱 오류: {e}")
                return None
        return None
    
    def clear_checkpoint(self, specific_date=None):
        """
        체크포인트 파일 삭제
        
        Args:
            specific_date: 특정 날짜 체크포인트 삭제 (YYYY-MM-DD), None이면 현재 날짜
        """
        if specific_date:
            checkpoint_file = os.path.join(self.output_dir, specific_date, f"checkpoint_{specific_date}.json")
            target_date = specific_date
        else:
            checkpoint_file = self.checkpoint_file
            target_date = self.analysis_date
            
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print(f"{target_date} 날짜의 체크포인트가 삭제되었습니다.")
    
    def get_available_checkpoint_dates(self):
        """체크포인트가 있는 날짜 목록 반환"""
        dates = []
        if os.path.exists(self.output_dir):
            for item in os.listdir(self.output_dir):
                date_path = os.path.join(self.output_dir, item)
                if os.path.isdir(date_path) and self._is_valid_date_format(item):
                    checkpoint_file = os.path.join(date_path, f"checkpoint_{item}.json")
                    if os.path.exists(checkpoint_file):
                        dates.append(item)
        return sorted(dates)
    
    def _is_valid_date_format(self, date_str):
        """날짜 형식 유효성 검사 (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def get_checkpoint_info(self, specific_date=None):
        """
        체크포인트 정보 반환
        
        Args:
            specific_date: 특정 날짜 정보 조회 (YYYY-MM-DD), None이면 현재 날짜
        """
        checkpoint = self.load_checkpoint(specific_date)
        target_date = specific_date or self.analysis_date
        
        if checkpoint:
            return {
                'exists': True,
                'analysis_date': checkpoint.get('analysis_date', target_date),
                'last_processed': checkpoint.get('last_processed', 'N/A'),
                'progress_percentage': checkpoint.get('progress_percentage', 0),
                'timestamp': checkpoint.get('timestamp', 'N/A'),
                'current_url': checkpoint.get('current_url', 'N/A'),
                'url_index': checkpoint.get('url_index', 0),
                'ip_index': checkpoint.get('ip_index', 0)
            }
        else:
            return {
                'exists': False,
                'analysis_date': target_date,
                'last_processed': 'N/A',
                'progress_percentage': 0,
                'timestamp': 'N/A',
                'current_url': 'N/A',
                'url_index': 0,
                'ip_index': 0
            }
    
    def get_all_checkpoints_summary(self):
        """모든 날짜의 체크포인트 요약 정보"""
        available_dates = self.get_available_checkpoint_dates()
        summary = []
        
        for date_str in available_dates:
            checkpoint_info = self.get_checkpoint_info(date_str)
            summary.append({
                'date': date_str,
                'progress': checkpoint_info['progress_percentage'],
                'last_processed': checkpoint_info['last_processed'],
                'timestamp': checkpoint_info['timestamp']
            })
        
        return summary