import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(__file__))

# 尝试抓取S12700E详情页
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
})

# 尝试几个可能的URL
urls_to_try = [
    'https://e.huawei.com/cn/products/switches/campus-switches/s12700e',
    'https://e.huawei.com/cn/products/switches/s12700e',
]

for url in urls_to_try:
    print(f"\n{'='*80}")
    print(f"尝试URL: {url}")
    print(f"{'='*80}")
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = 'utf-8'
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            print(f"\n[Meta描述] {meta_desc.get('content', '')[:300]}")
        
        # 提取h1
        h1 = soup.find('h1')
        if h1:
            print(f"\n[H1] {h1.get_text(strip=True)}")
        
        # 提取所有包含"产品概述"、"产品描述"等关键词的区域
        keywords = ['产品概述', '产品简介', '产品描述', '产品特点', 'CloudEngine', 'S12700E', '交换机']
        for kw in keywords:
            elements = soup.find_all(string=lambda text: text and kw in text)
            if elements:
                for elem in elements[:3]:
                    parent = elem.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        if len(text) > 20 and len(text) < 500:
                            print(f"\n[包含'{kw}'的文本] {text[:200]}")
        
        # 查找特定的描述容器
        desc_selectors = [
            '.product-intro', '.product-description', '.overview', 
            '.product-overview', '.intro-text', '.description',
            '[class*="intro"]', '[class*="overview"]', '[class*="description"]',
            '.summary', '[class*="summary"]', '.product-brief'
        ]
        
        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n[选择器: {selector}] 找到 {len(elements)} 个元素")
                for elem in elements[:2]:
                    text = elem.get_text(strip=True)
                    if len(text) > 20:
                        print(f"  {text[:200]}")
        
        # 检查是否有JSON-LD或其他结构化数据
        scripts = soup.find_all('script', type='application/ld+json')
        if scripts:
            print(f"\n[结构化数据] 找到 {len(scripts)} 个JSON-LD脚本")
            for script in scripts:
                print(f"  {script.string[:200] if script.string else '无内容'}")
        
        # 查找所有p标签，过滤可能包含产品描述的
        print(f"\n[P标签内容示例]")
        paragraphs = soup.find_all('p')
        for p in paragraphs[:10]:
            text = p.get_text(strip=True)
            if len(text) > 30:
                print(f"  {text[:150]}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
