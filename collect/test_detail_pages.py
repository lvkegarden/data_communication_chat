import sys
import os
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from scraper_logger import log

def test_detail_fetch():
    import requests
    from bs4 import BeautifulSoup
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 先获取列表页
    list_url = "https://e.huawei.com/cn/products/switches/campus-switches"
    print(f"1. 获取列表页: {list_url}")
    resp = session.get(list_url, timeout=30)
    resp.encoding = 'utf-8'
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 查找包含产品详情的链接
    print("\n2. 查找详情页链接:")
    detail_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        
        if 'detail' in href.lower() or 'product' in href.lower():
            if any(kw in text for kw in ['S12700', 'S8700', 'S7700', 'S5735', 'S5731', 'S6735']):
                full_url = urljoin("https://e.huawei.com", href)
                detail_links.append({'text': text[:50], 'url': full_url})
                if len(detail_links) <= 5:
                    print(f"   {text[:50]}: {full_url}")
    
    if not detail_links:
        print("   未找到包含产品型号的链接，尝试提取所有链接...")
        for a in soup.find_all('a', href=True)[:20]:
            href = a['href']
            text = a.get_text(strip=True)
            print(f"   {text[:50]}: {href}")
    
    if detail_links:
        test_url = detail_links[0]['url']
        print(f"\n3. 抓取详情页: {test_url}")
        
        resp2 = session.get(test_url, timeout=20)
        resp2.encoding = 'utf-8'
        
        soup2 = BeautifulSoup(resp2.text, 'html.parser')
        
        # 提取描述信息
        print("\n4. 提取描述信息:")
        
        # meta description
        meta = soup2.find('meta', attrs={'name': 'description'})
        if meta:
            print(f"   Meta描述: {meta.get('content', '')[:100]}...")
        
        # h1
        h1 = soup2.find('h1')
        if h1:
            print(f"   H1标题: {h1.get_text(strip=True)[:100]}")
        
        # h2
        h2 = soup2.find('h2')
        if h2:
            print(f"   H2标题: {h2.get_text(strip=True)[:100]}")
        
        # 查找包含描述关键词的段落
        print("\n5. 查找描述性段落:")
        for p in soup2.find_all('p')[:20]:
            text = p.get_text(strip=True)
            if len(text) > 30 and any(kw in text for kw in ['交换机', '核心', '企业', '园区', '数据中心']):
                print(f"   {text[:100]}...")
        
        # 查找特定class的元素
        print("\n6. 查找特定class元素:")
        for cls in ['product-intro', 'product-description', 'intro-text', 'overview']:
            elements = soup2.select(f'[class*="{cls}"]')
            if elements:
                for elem in elements[:2]:
                    text = elem.get_text(strip=True)
                    if text:
                        print(f"   [{cls}] {text[:100]}...")

if __name__ == "__main__":
    test_detail_fetch()
