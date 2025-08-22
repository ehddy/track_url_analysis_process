#!/usr/bin/env python3
"""
URL 분석 실행 스크립트 (완전 자동화)
"""

import sys
import os
from datetime import datetime
import pandas as pd

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(__file__))

from src.url_analysis_runner import URLAnalysisRunner
from config.settings import TRACK_URL
from src.utils.logger import setup_logging


def main():
    """메인 함수 - 완전 자동화된 분석"""
    
    # 로깅 설정
    logger = setup_logging("logs")
    
    # 기본 설정
    today = datetime.now().strftime('%Y-%m-%d')

    
    logger.info("="*60)
    logger.info(f"URL 접속 패턴 분석 - {today}")
    logger.info("="*60)
    logger.info(f"분석 대상 URL: {len(TRACK_URL)}개")
    for i, url in enumerate(TRACK_URL, 1):
        logger.info(f"  {i}. {url}")
    logger.info("")
    
    try:
        # 분석 실행기 생성 (날짜별 관리)
        runner = URLAnalysisRunner("data/analysis_results", today)
        
        logger.info(f"📅 분석 날짜: {today}")
        logger.info(f"📁 저장 위치: {runner.file_manager.date_dir}")
        
        # 체크포인트 자동 확인 및 처리
        checkpoint_info = runner.checkpoint_manager.get_checkpoint_info()
        if checkpoint_info['exists']:
            logger.info(f"✅ 체크포인트 발견: {checkpoint_info['last_processed']}")
            logger.info(f"📊 진행률: {checkpoint_info['progress_percentage']}%")
            logger.info("🔄 자동으로 이전 진행상황에서 계속합니다...")
        else:
            logger.info("🆕 새로운 분석을 시작합니다.")
        
        logger.info("")
        
        # 분석 실행 (항상 resume=True로 자동 처리)
        results = runner.run_analysis(TRACK_URL, resume=True)
        
        # 결과 출력
        logger.info("="*60)
        logger.info("🎉 분석 완료!")
        logger.info("="*60)
        logger.info(f"📊 총 분석 결과: {len(results)}개 레코드")
        
        if not results.empty:
            # 분석 요약
            summary = runner.get_analysis_summary()
            logger.info("\n📈 분석 요약:")
            for key, value in summary.items():
                logger.info(f"  {key}: {value}")
            
            # 유해 접속 사례
            if '유해 접속 여부' in results.columns:
                harmful_cases = results[results['유해 접속 여부'] == 1]
                if not harmful_cases.empty:
                    logger.info(f"\n🚨 유해 접속 사례: {len(harmful_cases)}건")
                    for _, row in harmful_cases.head(5).iterrows():
                        ip = row.get('사용자 IP', 'N/A')
                        url = row.get('추적 URL', 'N/A')
                        harmful_count = row.get('고유 유해 URL 개수', 0)
                        logger.info(f"  - {ip} → {url} (유해 URL {harmful_count}개)")
                else:
                    logger.info("\n✅ 유해 접속 사례가 없습니다.")
        else:
            logger.warning("⚠️ 분석 결과가 없습니다.")
        
        # 파일 정보
        file_info = runner.file_manager.get_file_info()
        logger.info(f"\n💾 결과 파일 정보:")
        logger.info(f"   파일 경로: {file_info['results_file']}")
        logger.info(f"   저장 레코드: {file_info['total_records']}개")
        logger.info(f"   파일 크기: {file_info['file_size_mb']} MB")
        
        logger.info(f"\n✨ 분석이 완료되었습니다!")
        return results
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        logger.info("💡 다음 실행 시 자동으로 중단된 지점부터 계속됩니다.")
    except Exception as e:
        logger.error(f"\n\n❌ 오류 발생: {e}")
        logger.info("📋 자세한 내용은 로그 파일을 확인하세요.")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()