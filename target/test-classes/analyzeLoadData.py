import sys
import io
import re
import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

session = requests.Session()
session.headers.update(headers)

url = "https://www.ruijie.com.cn/cp/jh-all/"

print('=' * 80)
print('分析 loadData 函数和分页机制')
print('=' * 80)

resp = session.get(url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text
soup = BeautifulSoup(html, 'html.parser')

print(f'\n--- 分页 HTML 完整结构 ---')
pagination_div = soup.find('div', class_='n-pagination', id='pagination')
if pagination_div:
    print(str(pagination_div))

print(f'\n--- 搜索 loadData 函数定义 ---')
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    content = script.get_text()
    if 'loadData' in content:
        print(f'\n  script[{i}] - 包含 loadData:')
        # 提取函数定义
        func_match = re.search(r'function\s+loadData\s*\([^)]*\)\s*\{[\s\S]*?\}', content)
        if func_match:
            func_code = func_match.group(0)
            print(f'  loadData 函数:')
            print(func_code)
        else:
            # 显示包含 loadData 的行
            lines = content.split('\n')
            for j, line in enumerate(lines):
                if 'loadData' in line or 'page' in line.lower():
                    print(f'    {j}: {line.strip()[:200]}')

print(f'\n--- 搜索 AJAX 请求相关代码 ---')
for i, script in enumerate(scripts):
    content = script.get_text()
    if 'ajax' in content.lower() or 'fetch' in content.lower() or '$http' in content:
        print(f'\n  script[{i}] - 包含 AJAX:')
        lines = content.split('\n')
        for j, line in enumerate(lines):
            if any(kw in line.lower() for kw in ['ajax', 'fetch', 'url:', 'url =', 'href =']):
                print(f'    {j}: {line.strip()[:200]}')

print(f'\n--- 分页参数分析 ---')
# 从 onclick 中提取
onclick_pattern = r"loadData\('(\d+)','([^']+)'\)"
matches = re.findall(onclick_pattern, html)
if matches:
    print(f'找到 loadData 调用:')
    pages = set()
    for page_num, cat_id in matches:
        pages.add((page_num, cat_id))
    for page_num, cat_id in sorted(pages):
        print(f'  页码: {page_num}, 分类ID: {cat_id}')

print(f'\n--- 搜索 API 接口 ---')
api_patterns = [
    r'["\']([^"\']*\/api\/[^"\']*)["\']',
    r'["\']([^"\']*\/ajax\/[^"\']*)["\']',
    r'url:\s*["\']([^"\']+)["\']',
    r'action=["\']([^"\']+)["\']',
]

for pattern, desc in [
    (r'["\']([^"\']*\/api\/[^"\']*)["\']', 'API'),
    (r'["\']([^"\']*\/ajax\/[^"\']*)["\']', 'AJAX'),
    (r'url:\s*["\']([^"\']+)["\']', 'URL'),
]:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        unique_matches = list(set(matches))[:20]
        print(f'\n{desc}: 找到 {len(unique_matches)} 个')
        for m in unique_matches:
            print(f'  {m}')

print(f'\n--- 查看所有 script 标签的 src ---')
for i, script in enumerate(scripts):
    src = script.get('src')
    if src:
        print(f'  script[{i}]: {src}')
