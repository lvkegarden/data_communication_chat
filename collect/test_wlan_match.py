import sys
import json
import os

sys.path.insert(0, os.path.dirname(__file__))

from huawei_scraper import HuaweiScraper, HUAWEI_WLAN_SPECS_DB

scraper = HuaweiScraper()

test_series = [
    'AirEngine 5760',
    'AirEngine 5761',
    'AirEngine 6760',
    'AirEngine 6776',
    'AirEngine 8760',
    'AirEngine 9700',
    'AirEngine 9701',
    'AirEngine 5700系列',
    'AirEngine Wi',
]

print("无线AP规格匹配测试:\n")

for series in test_series:
    specs = {}
    
    normalized_name = series.replace('-', '').replace(' ', '')
    
    for db_key, db_specs in HUAWEI_WLAN_SPECS_DB.items():
        db_key_normalized = db_key.replace('-', '').replace(' ', '')
        series_normalized = series.replace('-', '').replace(' ', '')
        
        if (db_key_normalized in series_normalized or 
            series_normalized.startswith(db_key_normalized) or
            series_normalized.startswith('AirEngine' + db_key_normalized.replace('AirEngine', ''))):
            specs.update(db_specs)
            print(f"[OK] '{series}' 匹配到 '{db_key}'")
            break
    
    if not specs:
        print(f"[FAIL] '{series}' 未匹配到任何规格")
    else:
        print(f"      速率: {specs.get('最大速率', '-')}")
        print(f"      终端: {specs.get('接入终端', '-')}")
        print()
