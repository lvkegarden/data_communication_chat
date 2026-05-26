import sys
import io
import requests
import re
import json
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

session = requests.Session()
session.headers.update(headers)

print('=' * 80)
print('分析华三交换机主页面的产品结构')
print('=' * 80)

main_url = 'https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/Switches/'

import time
time.sleep(0.5)

try:
    resp = session.get(main_url, timeout=30)
    resp.encoding = 'utf-8'
    print(f'状态码: {resp.status_code}')
    print(f'内容长度: {len(resp.text)} 字节')
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    print('\n--- 1. 查找所有产品卡片/链接 ---')
    product_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        
        if ('/Products/Switches' in href or '/Switches/Products' in href) and '/cn/' in href:
            if text and len(text) > 2 and len(text) < 80:
                product_links.append((text, href))
    
    product_links = list(dict.fromkeys(product_links))
    print(f'找到 {len(product_links)} 个产品相关链接')
    
    switch_links = [
        (text, href) for text, href in product_links 
        if 'S' in text and ('Switches' in href or 'Switch' in href)
    ]
    print(f'其中 {len(switch_links)} 个是交换机系列链接')
    
    print('\n--- 交换机系列链接 ---')
    for i, (text, href) in enumerate(switch_links[:30], 1):
        print(f'  {i}. {text}')
        print(f'     -> {href}')
    
    if len(switch_links) > 30:
        print(f'  ... 还有 {len(switch_links) - 30} 个')
    
    print('\n--- 2. 分析正则匹配问题 ---')
    html = resp.text
    
    switch_series_patterns = [
        r'\bS\d{3,5}[A-Za-z0-9_-]*\b',
    ]
    
    for pattern in switch_series_patterns:
        matches = re.findall(pattern, html)
        unique = sorted(list(set(matches)))
        print(f'\n模式 "{pattern}":')
        print(f'  匹配总数: {len(matches)}')
        print(f'  去重后: {len(unique)} 个')
        print(f'  前 30 个: {unique[:30]}')
        if len(unique) > 30:
            print(f'  ... 还有 {len(unique) - 30} 个')
    
    print('\n--- 3. 检查老产品系列 ---')
    old_series_prefixes = ['S100', 'S120', 'S130', 'S150', 'S160', 'S170', 'S180', 'S200', 'S210', 'S260', 'S310', 'S320', 'S360']
    
    old_series = []
    for match in unique:
        for prefix in old_series_prefixes:
            if match.startswith(prefix):
                old_series.append(match)
                break
    
    print(f'老产品系列数量: {len(old_series)}')
    print(f'老产品系列: {old_series[:20]}')
    
    print('\n--- 4. 建议保留的系列 ---')
    current_series_prefixes = ['S10500', 'S12500', 'S16700', 'S5500', 'S5560', 'S5580', 'S5590', 'S5700', 'S5800', 'S5850', 'S6500', 'S6520', 'S6550', 'S6800', 'S6850', 'S6860', 'S6880', 'S7000', 'S7300', 'S7500', 'S7600', 'S7700', 'S9800', 'S9820', 'S9825', 'S9826', 'S9850', 'S9855', 'S9857', 'S5120', 'S5130', 'S5170', 'S5175', 'S5100', 'S5000', 'S9900', 'S6900', 'S6300']
    
    current_series = []
    for match in unique:
        for prefix in current_series_prefixes:
            if match.startswith(prefix):
                current_series.append(match)
                break
    
    print(f'当前产品系列数量: {len(current_series)}')
    print(f'当前产品系列: {current_series}')
    
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
