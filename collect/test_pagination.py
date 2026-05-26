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

base_url = "https://www.ruijie.com.cn/cp/jh-all/"

def count_products(soup):
    cards = soup.find_all(['div', 'article', 'section'])
    product_cards = []
    for card in cards:
        classes = card.get('class', [])
        if any('product' in c.lower() or 'card' in c.lower() for c in classes):
            if card.find('h2'):
                product_cards.append(card)
    return product_cards

print("="*60)
print("测试不同的分页URL模式")
print("="*60)

patterns_to_test = [
    ("page=1", "?page=1"),
    ("page=2", "?page=2"),
    ("page=3", "?page=3"),
    ("p=1", "?p=1"),
    ("p=2", "?p=2"),
    ("p=3", "?p=3"),
    ("pageNum=1", "?pageNum=1"),
    ("pageNum=2", "?pageNum=2"),
    ("pn=1", "?pn=1"),
    ("pn=2", "?pn=2"),
]

results = {}

for name, query in patterns_to_test:
    test_url = base_url + query
    try:
        resp = session.get(test_url, timeout=15)
        resp.encoding = 'utf-8'
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = count_products(soup)
            
            product_names = []
            for card in cards:
                h2 = card.find('h2')
                if h2:
                    product_names.append(h2.get_text(strip=True))
            
            results[name] = {
                'url': test_url,
                'status': 200,
                'len': len(resp.text),
                'cards': len(cards),
                'products': product_names[:5]
            }
            print(f"{name}: {len(cards)} 个产品, 前5个: {product_names[:5]}")
        else:
            results[name] = {'status': resp.status_code}
            print(f"{name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"{name}: Error - {e}")

print("\n" + "="*60)
print("检查不同页面的产品是否有差异")
print("="*60)

if 'page=1' in results and 'page=2' in results:
    p1_products = results['page=1'].get('products', [])
    p2_products = results['page=2'].get('products', [])
    
    if p1_products and p2_products:
        print(f"page=1 前5个产品: {p1_products}")
        print(f"page=2 前5个产品: {p2_products}")
        
        if p1_products == p2_products:
            print("产品列表相同，可能分页参数不正确")
        else:
            print("产品列表不同，分页成功!")

print("\n" + "="*60)
print("检查页面元数据")
print("="*60)

resp = session.get(base_url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text

count_patterns = [
    r'共\s*\d+\s*条',
    r'共\s*\d+\s*个',
    r'总(共)?\s*\d+\s*(项|条|个)',
    r'total\s*[:=]\s*\d+',
    r'count\s*[:=]\s*\d+',
    r'166',
    r'166个',
]

for pattern in count_patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f"Pattern '{pattern}' -> {list(set(matches))}")

meta_patterns = [r'itemsPerPage', r'perPage', r'pageSize', r'rowCount', r'totalCount']
scripts = BeautifulSoup(html, 'html.parser').find_all('script')
for i, script in enumerate(scripts):
    content = script.get_text()
    for p in meta_patterns:
        if p in content:
            lines = content.split('\n')
            for j, line in enumerate(lines):
                if p in line:
                    print(f"Script[{i}]: {line.strip()[:150]}")
