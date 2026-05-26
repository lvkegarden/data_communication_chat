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

subcategories = [
    ("园区网交换机", "https://www.ruijie.com.cn/cp/jh-yqw/"),
    ("数据中心交换机", "https://www.ruijie.com.cn/cp/jh-shjzhx/"),
    ("行业精选交换机", "https://www.ruijie.com.cn/cp/jh-zxwljj/"),
    ("工业交换机", "https://www.ruijie.com.cn/cp/jh-gyjh/"),
]

pagination_patterns = [
    ('页码', r'<li[^>]*>\s*<a[^>]*>(\d+)</a>\s*</li>'),
    ('下一页', r'下一页|下页|>'),
    ('分页容器', r'pagination|pager|page-nav|page-navigator'),
    ('页码链接', r'href="[^"]*[?&]page[=:]\d+'),
    ('总页数', r'共\s*(\d+)\s*页'),
    ('总数量', r'共\s*(\d+)\s*(条|个|款)'),
]

for subcat_name, subcat_url in subcategories:
    print('=' * 80)
    print(f'子分类: {subcat_name}')
    print(f'URL: {subcat_url}')
    print('=' * 80)
    
    try:
        resp = session.get(subcat_url, timeout=15)
        resp.encoding = 'utf-8'
        html = resp.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f'\n页面大小: {len(html)} 字节')
        
        print(f'\n--- 分页模式检测 ---')
        for pattern_name, pattern in pagination_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f'{pattern_name}: {matches[:10]}')
        
        print(f'\n--- 分页相关元素 ---')
        for elem_name in ['pagination', 'pager', 'page-nav', 'page-list', 'page-box']:
            elements = soup.find_all(class_=re.compile(elem_name, re.IGNORECASE))
            if elements:
                print(f'找到 {len(elements)} 个 {elem_name} 元素')
                for elem in elements[:2]:
                    links = elem.find_all('a', href=True)
                    page_links = [a.get_text(strip=True) for a in links]
                    print(f'  页码链接: {page_links}')
        
        print(f'\n--- 页面中的链接 ---')
        all_links = soup.find_all('a', href=True)
        page_links = [a for a in all_links if 'page' in a.get('href', '').lower()]
        if page_links:
            print(f'找到 {len(page_links)} 个包含 page 的链接')
            for link in page_links[:10]:
                print(f'  {link.get_text(strip=True)}: {link.get("href")}')
        
        print(f'\n--- 产品卡片数量 ---')
        cards = []
        for div in soup.find_all(['div', 'article', 'section']):
            classes = div.get('class', [])
            has_product_class = any(c for c in classes if 'product' in c.lower())
            has_card_class = any(c for c in classes if 'card' in c.lower())
            has_item_class = any(c for c in classes if 'item' in c.lower())
            if has_product_class or has_card_class or has_item_class:
                has_h2 = div.find('h2')
                has_link_with_rg = any(
                    link.get_text(strip=True).startswith('RG-') 
                    for link in div.find_all('a') 
                    if link.get_text(strip=True)
                )
                if has_h2 or has_link_with_rg:
                    cards.append(div)
        print(f'找到 {len(cards)} 个产品卡片')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
