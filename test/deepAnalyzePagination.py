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
print('分析 jh-all 页面 (显示 166 款交换机的页面)')
print('=' * 80)

resp = session.get(url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text
soup = BeautifulSoup(html, 'html.parser')

print(f'\n页面大小: {len(html)} 字节')

print(f'\n--- 搜索 166 相关内容 ---')
lines = html.split('\n')
for i, line in enumerate(lines):
    if '166' in line:
        print(f'  行 {i}: {line.strip()[:200]}')

print(f'\n--- 分页元素详情 ---')
pagination_divs = soup.find_all(class_=re.compile('pagination', re.IGNORECASE))
print(f'找到 {len(pagination_divs)} 个 pagination 元素')
for i, div in enumerate(pagination_divs[:3]):
    print(f'\n  pagination[{i}]:')
    print(f'    class: {div.get("class")}')
    inner_links = div.find_all('a', href=True)
    print(f'    内部链接数: {len(inner_links)}')
    for j, link in enumerate(inner_links[:20]):
        text = link.get_text(strip=True)
        href = link.get('href')
        print(f'    [{j}] "{text}" -> {href}')

print(f'\n--- 所有页码链接 ---')
all_links = soup.find_all('a', href=True)
page_links = []
for link in all_links:
    href = link.get('href')
    text = link.get_text(strip=True)
    if href and ('page' in href.lower() or text.isdigit() or '下一页' in text or '上一页' in text):
        page_links.append((text, href))

print(f'找到 {len(page_links)} 个可能的分页链接')
for text, href in page_links:
    print(f'  "{text}" -> {href}')

print(f'\n--- JavaScript 数据 ---')
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    content = script.get_text()
    if any(keyword in content for keyword in ['page', 'pagination', 'total', '166']):
        print(f'\n  script[{i}]:')
        lines = content.split('\n')
        for j, line in enumerate(lines[:20]):
            if any(kw in line.lower() for kw in ['page', 'pagination', 'total', '166', 'item']):
                print(f'    {line.strip()[:200]}')
