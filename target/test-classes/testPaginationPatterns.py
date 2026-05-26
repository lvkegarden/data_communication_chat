import sys
import io
import re
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

session = requests.Session()
session.headers.update(headers)

# 1. 先查看 jh-all 页面的内联 script，loadData 可能在内联 script 中
print('=' * 80)
print('1. 分析 jh-all 页面的内联 JavaScript')
print('=' * 80)

url = "https://www.ruijie.com.cn/cp/jh-all/"
resp = session.get(url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text

# 提取所有内联 script 内容
inline_scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
print(f'找到 {len(inline_scripts)} 个内联 script 标签')

for i, content in enumerate(inline_scripts):
    if 'loadData' in content or 'pagination' in content.lower():
        print(f'\n--- 内联 script[{i}] ---')
        lines = content.split('\n')
        for j, line in enumerate(lines):
            if any(kw in line.lower() for kw in ['loaddata', 'pagination', 'page', 'ajax', 'url', 'action']):
                print(f'  {j}: {line.strip()[:200]}')

# 2. 测试不同分页 URL 模式
print('\n' + '=' * 80)
print('2. 测试分页 URL 模式')
print('=' * 80)

test_patterns = [
    ('?page=2', 'page 参数'),
    ('?p=2', 'p 参数'),
    ('?pageNum=2', 'pageNum 参数'),
    ('?pageIndex=2', 'pageIndex 参数'),
    ('?catId=433108860989088000', 'catId 参数'),
    ('?categoryId=433108860989088000', 'categoryId 参数'),
    ('?page=2&catId=433108860989088000', '组合参数'),
]

cat_id = '433108860989088000'
base_url = 'https://www.ruijie.com.cn/cp/jh-all/'

for suffix, desc in test_patterns:
    test_url = base_url + suffix
    try:
        resp = session.get(test_url, timeout=15)
        resp.encoding = 'utf-8'
        test_html = resp.text
        # 提取产品型号
        products = re.findall(r'(RG-[A-Z0-9\-]+)', test_html)
        unique_products = list(set(products))
        print(f'\n{desc}: {test_url}')
        print(f'  响应大小: {len(test_html)} 字节')
        print(f'  找到 RG- 型号: {len(unique_products)} 个')
        if len(unique_products) > 5:
            print(f'  前10个: {unique_products[:10]}')
    except Exception as e:
        print(f'\n{desc}: {test_url}')
        print(f'  错误: {e}')

# 3. 查看其他子分类页面的分页情况
print('\n' + '=' * 80)
print('3. 检查各子分类页面的分页')
print('=' * 80)

subcategories = [
    ("园区网交换机", "https://www.ruijie.com.cn/cp/jh-yqw/"),
    ("数据中心交换机", "https://www.ruijie.com.cn/cp/jh-shjzhx/"),
    ("行业精选交换机", "https://www.ruijie.com.cn/cp/jh-zxwljj/"),
    ("工业交换机", "https://www.ruijie.com.cn/cp/jh-gyjh/"),
]

for name, url in subcategories:
    try:
        resp = session.get(url, timeout=15)
        resp.encoding = 'utf-8'
        sub_html = resp.text
        
        # 查找分页
        pagination_match = re.search(r'<div class="n-pagination"[^>]*>[\s\S]*?</div>', sub_html)
        if pagination_match:
            pagination_html = pagination_match.group(0)
            # 提取页码
            pages = re.findall(r'loadData\(\'(\d+)\',\'([^\']+)\'\)', pagination_html)
            if pages:
                unique_pages = list(set(pages))
                print(f'\n{name}: 找到分页')
                print(f'  页码范围: {min(p for p,_ in unique_pages)} - {max(p for p,_ in unique_pages)}')
                print(f'  分类ID: {unique_pages[0][1]}')
            else:
                print(f'\n{name}: 找到 pagination 但无页码')
        else:
            print(f'\n{name}: 未找到 pagination')
        
        # 统计产品数量
        products = re.findall(r'(RG-[A-Z0-9\-]+)', sub_html)
        unique_products = list(set(products))
        print(f'  页面中 RG- 型号: {len(unique_products)} 个')
        
    except Exception as e:
        print(f'\n{name}: 错误 - {e}')
