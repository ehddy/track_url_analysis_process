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
HARMFUL_CATEGORIES = dict(config.items('categories.harmful'))
SAFE_CATEGORIES = dict(config.items('categories.safe'))

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
