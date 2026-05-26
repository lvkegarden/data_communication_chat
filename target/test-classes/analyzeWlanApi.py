import sys
import io
import json
import requests
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
}

session = requests.Session()
session.headers.update(headers)

print('=' * 80)
print('分析无线分类的 classId')
print('=' * 80)

# 先从无线页面获取分类ID
wx_url = 'https://www.ruijie.com.cn/cp/wx-all/'
resp = session.get(wx_url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text

soup = BeautifulSoup(html, 'html.parser')

# 查找 n-search-tab 链接
tab_links = soup.find_all('a', class_='n-search-tab')
print(f'\n找到 {len(tab_links)} 个分类标签:')

for link in tab_links:
    class_id = link.get('id', '')
    href = link.get('href', '')
    text = link.get_text(strip=True)
    print(f'  {text}: classId={class_id}, href={href}')

# 测试 API
api_url = 'https://www.ruijie.com.cn/application/api/product/getGoodsList'

print('\n' + '=' * 80)
print('测试无线分类 API')
print('=' * 80)

# 从 n-search-tab 获取的无线分类
wx_categories = [
    ("全部", "", "https://www.ruijie.com.cn/cp/wx-all/"),
]

for link in tab_links:
    class_id = link.get('id', '')
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if class_id and href.startswith('/cp/wx-'):
        wx_categories.append((text, class_id, href))

for name, cid, url in wx_categories:
    if not cid:
        continue
    
    print(f'\n--- {name} (ID: {cid}) ---')
    
    params = {
        'page': 1,
        'limit': 12,
        'classId': cid,
        'order': 2,
        'orderField': '',
        'screenValueIds': '',
    }
    
    try:
        resp = session.get(api_url, params=params, timeout=15)
        data = resp.json()
        
        if data.get('code') == 200:
            total = data.get('data', {}).get('total', 0)
            pages = (total + 11) // 12
            items = data.get('data', {}).get('list', [])
            print(f'  总商品数: {total}')
            print(f'  总页数: {pages}')
            if items:
                print(f'  前3个型号: {[i.get("modeName") for i in items[:3]]}')
        else:
            print(f'  API 错误: {data}')
            
    except Exception as e:
        print(f'  错误: {e}')

# 验证 jh-all 的 classId
print('\n' + '=' * 80)
print('验证交换机分类的 classId')
print('=' * 80)

jh_url = 'https://www.ruijie.com.cn/cp/jh-all/'
resp = session.get(jh_url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text

soup = BeautifulSoup(html, 'html.parser')
tab_links = soup.find_all('a', class_='n-search-tab')

print(f'\n找到 {len(tab_links)} 个交换机分类标签:')
jh_categories = []
for link in tab_links:
    class_id = link.get('id', '')
    href = link.get('href', '')
    text = link.get_text(strip=True)
    is_selected = 'n-search-tab-selected' in link.get('class', [])
    marker = '*' if is_selected else ' '
    print(f' {marker} {text}: classId={class_id}, href={href}')
    if class_id:
        jh_categories.append((text, class_id, href, is_selected))

# 从页面分页中获取当前选中分类的 classId
pagination_div = soup.find('div', class_='n-pagination')
if pagination_div:
    onclick_pattern = r"loadData\('(\d+)','([^']+)'\)"
    matches = re.findall(onclick_pattern, str(pagination_div))
    if matches:
        all_class_ids = list(set(m[1] for m in matches))
        print(f'\n从分页获取的 classId: {all_class_ids}')
