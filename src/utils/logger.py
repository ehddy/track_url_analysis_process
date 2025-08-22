"""
로깅 설정 모듈 - 날짜별 로그 파일 관리
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class DateBasedLogger:
    """날짜별 로그 파일을 생성하는 로거"""
    
    def __init__(self, name="url_analysis", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        # 로그 디렉토리 생성
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 오늘 날짜로 로그 파일명 생성
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f"{self.name}_{today}.log")
        
        # 로거 생성
        self.logger = logging.getLogger(f"{self.name}_{today}")
        
        # 이미 핸들러가 있으면 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러 설정 (최대 10MB, 5개 백업 파일)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        
        # 포매터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """정보 레벨 로그"""
        self.logger.info(message)
    
    def error(self, message):
        """에러 레벨 로그"""
        self.logger.error(message)
    
    def warning(self, message):
        """경고 레벨 로그"""
        self.logger.warning(message)
    
    def debug(self, message):
        """디버그 레벨 로그"""
        self.logger.debug(message)
    
    def critical(self, message):
        """크리티컬 레벨 로그"""
        self.logger.critical(message)


# 전역 로거 인스턴스
_global_logger = None


def get_logger(name="url_analysis", log_dir="logs"):
    """전역 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = DateBasedLogger(name, log_dir)
    return _global_logger


def setup_logging(log_dir="logs"):
    """로깅 초기 설정"""
    global _global_logger
    _global_logger = DateBasedLogger("url_analysis", log_dir)
    return _global_logger