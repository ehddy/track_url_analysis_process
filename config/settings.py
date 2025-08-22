"""
프로젝트 설정 파일
"""
import configparser
import os

# config.ini 파일 로드
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
config.read(config_path)

# Elasticsearch 설정
ES_CONFIG = {
    'hosts': config.get('elasticsearch', 'hosts').split(','),
    'auth': (config.get('elasticsearch', 'username'), config.get('elasticsearch', 'password')),
    'verify_certs': config.getboolean('elasticsearch', 'verify_certs'),
    'request_timeout': config.getint('elasticsearch', 'request_timeout'),
    'http_compress': config.getboolean('elasticsearch', 'http_compress')
}

# 인덱스 설정
INDEX_PATTERN = config.get('elasticsearch.index', 'pattern')

# HIMS 설정
HIMS_CONFIG = {
    'ip': config.get('hims', 'ip'),
    'port': config.getint('hims', 'port'),
    'key': config.get('hims', 'key')
}

# 분석 설정
ANALYSIS_CONFIG = {
    'default_output_dir': config.get('analysis', 'default_output_dir'),
    'slice_count': config.getint('analysis', 'slice_count'),
    'max_workers': config.get('analysis', 'max_workers') or None,
    'scroll_size': config.getint('analysis', 'scroll_size'),
    'max_ips_per_url': config.getint('analysis', 'max_ips_per_url'),
    'min_records_threshold': config.getint('analysis', 'min_records_threshold'),
    'time_window_hours': config.getint('analysis', 'time_window_hours')
}

# 카테고리 분류 정의
HARMFUL_CATEGORIES = {
    # 유해사이트 (HU)
    'HU001': '음란',
    'HU002': '도박', 
    'HU003': '폭력',
    'HU004': '마약',
    'HU005': '자살',
    'HU006': '엽기',
    'HU999': '기타유해',
    
    # 웹프록시 (PU)
    'PU001': '프록시(우회)',
    
    # 엔터테인먼트 (EU)
    'EU001': '복권/배팅',
    
    # 악성코드 (MU)
    'MU001': '피싱',
    'MU002': 'C&C',
    'MU003': '멀웨어',
    
    # 방심위 (KC)
    'KC001': '방심위(12)',
    'KC002': '방심위(15)', 
    'KC003': '방심위(18)',
    'KC004': '방심위(유해)',
    
    # 스미싱 유해 (SU)
    'SU001': 'KISA 스미싱',
    'SU004': 'KT 스미싱',
    'SU005': '카스퍼스키 피싱',
    'SU010': '플랜티넷 스미싱',
    'SU008': '성인',
    'SU011': '투자권유',
    'SU012': '불법의약품',
    'SU013': '도박',
    'SU014': '대출',
}

SAFE_CATEGORIES = {
    # 스미싱 안전 (SU)
    'SU002': 'KT 안전',
    'SU003': 'KISA 안전', 
    'SU006': '비업무URL 안전',
    'SU007': '관리자 정의 안전',
    'SU009': '쇼핑몰(광고)',
}

TRACK_URL = [
 'ads3.trafficjunky.net', 'engine.adsupply.com', 'ads.adcash.com', 'ads.plugrush.com',
 'pub.adsterra.com', 'ads.reporo.net', 'skinnycrawlinglax.com', 'cdn.ruwogu.info',
 'www.totohot.net', 'adserver.juicyads.com', 'ads.exoclick.com', 'ads.trafficjunky.net',
 'gw-iad-bid.ymmobi.com', 'ads.chaturbate.com', 'missav.live', 'www.linkm365.com',
 'legy.line-apps.com', 'fundingchoicesmessages.google.com', 'cs.admanmedia.com',
 'cdn.pandalive.co.kr', 'yako.gg', 'booktoki468.com', 'syndication.adsterra.com',
 'theporndude.com', 'flushpersist.com', 'adspy.javrank.com', 'privacy-sandbox.appsflyersdk.com',
 'wayfarerorthodox.com', 'avdbs.com', 'r.trackwilltrk.com', 'av19.live', 'www.lkrk1.com',
 'delivery.clickadu.com', 'traffic.zeropark.com', 'k.kakaocdn.net', 'preferencenail.com',
 'weirdopt.com', 'www.joosomoa1.com', 'mt-spot.com', 'wdwd9.com'
]
