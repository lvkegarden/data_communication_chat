import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/project/ai/localrest/collect')

import requests
from bs4 import BeautifulSoup
import re

from h3c_scraper import H3CScraper

print('=' * 80)
print('测试华三老产品系列过滤')
print('=' * 80)

old_series_prefixes = [
    'S1000', 'S1008', 'S1016', 'S1024', 'S1048', 'S1050T',
    'S1200', 'S1208', 'S1209', 'S1224', 'S1248',
    'S1300', 'S1324', 'S1348',
    'S1500', 'S1526', 'S1550',
    'S1600', 'S1650', 'S1750',
    'S1800', 'S1850',
    'S2000', 'S2008', 'S2100', 'S2108', 'S2126',
    'S2600',
    'S3100', 'S3110', 'S3200', 'S3210',
    'S3600',
    'S5000', 'S5008', 'S5016', 'S5024', 'S5048',
    'S5110', 'S5120',
]

test_series = [
    # 老产品系列（应该被过滤）
    'S1000', 'S1000V', 'S1008A', 'S1016', 'S1024', 'S1048', 'S1050T',
    'S1200', 'S1200F', 'S1208', 'S1224', 'S1248',
    'S1300', 'S1324', 'S1348',
    'S1500', 'S1500E', 'S1526', 'S1550',
    'S1600', 'S1650', 'S1750',
    'S1800', 'S1800G', 'S1850', 'S1850V2',
    'S2000', 'S2000EA', 'S2100', 'S2108', 'S2126', 'S2126-EI',
    'S2600', 'S2600V2',
    'S3100', 'S3100V3', 'S3110',
    'S3210', 'S3210S',
    'S3600', 'S3600V2', 'S3600V3',
    'S5000', 'S5000E', 'S5000X', 'S5024FV3',
    
    # 新产品系列（不应该被过滤）
    'S9820', 'S9825', 'S9826', 'S9827', 'S9850', 'S9855', 'S9857',
    'S12500', 'S12500G', 'S12500R', 'S12500X', 'S12500AI',
    'S10500', 'S10500X', 'S10500X-G',
    'S7500', 'S7500E', 'S7500X', 'S7500X-G',
    'S6800', 'S6805', 'S6813', 'S6825', 'S6826', 'S6850', 'S6855', 'S6860', 'S6880', 'S6890',
    'S5500', 'S5560', 'S5560S', 'S5560X', 'S5570S', 'S5580X', 'S5590',
    'S5130', 'S5130S', 'S5135', 'S5170', 'S5175S',
]

print('\n--- 测试老产品过滤 ---')
filtered_count = 0
kept_count = 0

for series in test_series:
    is_old = False
    for prefix in old_series_prefixes:
        if series.startswith(prefix):
            is_old = True
            break
    
    if is_old:
        filtered_count += 1
        print(f'  [过滤] {series}')
    else:
        kept_count += 1
        print(f'  [保留] {series}')

print(f'\n--- 过滤结果汇总 ---')
print(f'总测试数: {len(test_series)}')
print(f'被过滤数: {filtered_count}')
print(f'保留数: {kept_count}')

print('\n--- 实际测试华三页面 ---')
scraper = H3CScraper()
switch_url = "https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/Switches/"

try:
    print(f'请求页面: {switch_url}')
    response = requests.get(switch_url, timeout=30, headers=scraper.headers)
    print(f'HTTP状态: {response.status_code}')
    print(f'页面大小: {len(response.text)} 字节')
    
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    html_str = str(soup)
    
    switch_series_patterns = [r'\bS\d{3,5}[A-Za-z0-9_-]*\b']
    
    all_matches = []
    for pattern in switch_series_patterns:
        matches = re.findall(pattern, html_str)
        all_matches.extend(matches)
    
    print(f'\n正则匹配总数: {len(all_matches)}')
    
    # 应用过滤逻辑
    kept_products = {}
    for match in all_matches:
        clean_name = match.strip().rstrip('-')
        
        if not clean_name.startswith('S'):
            continue
        if len(clean_name) < 4 or len(clean_name) > 30:
            continue
        if '_' in clean_name:
            continue
        
        is_old_series = False
        for prefix in old_series_prefixes:
            if clean_name.startswith(prefix):
                is_old_series = True
                break
        
        if is_old_series:
            continue
        
        if clean_name not in kept_products:
            kept_products[clean_name] = True
    
    print(f'过滤后保留数: {len(kept_products)}')
    print(f'\n保留的系列:')
    for i, name in enumerate(sorted(kept_products.keys()), 1):
        print(f'  {i:3d}. {name}')
        
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 80)
