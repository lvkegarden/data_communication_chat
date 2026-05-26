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
print('分析 jh-all 页面 HTML 源码中的分页信息')
print('=' * 80)

resp = session.get(url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text
soup = BeautifulSoup(html, 'html.parser')

print(f'\n页面大小: {len(html)} 字节')

print(f'\n--- 搜索分页相关的 HTML 元素 ---')

patterns = [
    (r'pagination', 'pagination 类名'),
    (r'pager', 'pager 类名'),
    (r'page-nav', 'page-nav 类名'),
    (r'el-pagination', 'element-ui 分页'),
    (r'@page-change', 'Vue 分页事件'),
    (r':page-size', '分页大小'),
    (r'total.*\d+', '总数'),
    (r'166', '166'),
    (r'共\s*\d+\s*页', '共 N 页'),
    (r'共\s*\d+\s*款', '共 N 款'),
    (r'共\s*\d+\s*条', '共 N 条'),
    (r'下一页|上一页|首页|末页', '分页按钮'),
]

for pattern, desc in patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        print(f'\n{desc}: 找到 {len(matches)} 处')
        # 显示附近上下文
        for i, match in enumerate(matches[:3]):
            idx = html.find(match)
            if idx >= 0:
                start = max(0, idx - 100)
                end = min(len(html), idx + 150)
                context = html[start:end].replace('\n', ' ')
                print(f'  [{i}] ...{context}...')

print(f'\n--- 查找包含 pagination 的标签 ---')
pagination_tags = soup.find_all(class_=re.compile('pagination|pager|page-nav', re.IGNORECASE))
print(f'找到 {len(pagination_tags)} 个相关标签')
for i, tag in enumerate(pagination_tags[:3]):
    print(f'\n  标签[{i}] tag: {tag.name}')
    print(f'  class: {tag.get("class")}')
    inner_html = str(tag)[:500]
    print(f'  内容: {inner_html}...')

print(f'\n--- 查找所有 script 标签中的数据 ---')
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    content = script.get_text()
    if any(kw in content.lower() for kw in ['page', 'pagination', 'total', '166']):
        print(f'\n  script[{i}]:')
        lines = content.split('\n')
        for j, line in enumerate(lines[:50]):
            if any(kw in line.lower() for kw in ['page', 'pagination', 'total', '166', 'item']):
                print(f'    {j}: {line.strip()[:200]}')

print(f'\n--- 查找 __INITIAL_STATE__ 或 data-* 属性 ---')
data_attrs = soup.find_all(attrs={'data-*': True})
print(f'找到 {len(data_attrs)} 个 data-* 属性元素')

# 查找 __VUE__ 相关的
for tag in soup.find_all(True):
    if tag.name in ['div', 'section', 'main']:
        vdata = tag.get('data-v-app') or tag.get('v-for') or tag.get(':items')
        if vdata:
            print(f'  {tag.name}: {tag.get("class")} -> {vdata}')

print(f'\n--- 搜索 166 的具体位置 ---')
for i, line in enumerate(html.split('\n')):
    if '166' in line:
        print(f'  行 {i}: {line.strip()[:200]}')
        # 显示前后行
        all_lines = html.split('\n')
        start = max(0, i-5)
        end = min(len(all_lines), i+10)
        print(f'  上下文:')
        for j in range(start, end):
            print(f'    {j}: {all_lines[j].strip()[:200]}')
