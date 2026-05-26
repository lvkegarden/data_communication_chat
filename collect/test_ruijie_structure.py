import requests
from bs4 import BeautifulSoup
import re

# 测试锐捷网站结构
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
})

urls = [
    ('交换机', 'https://www.ruijie.com.cn/cp/jh/'),
    ('无线', 'https://www.ruijie.com.cn/cp/wx/'),
]

for category, url in urls:
    print(f"\n{'='*80}")
    print(f"测试 {category}: {url}")
    print(f"{'='*80}")
    
    try:
        response = session.get(url, timeout=30)
        response.encoding = 'utf-8'
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查看产品链接格式
        links = soup.find_all('a', href=True)
        product_links = []
        
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            if '/cp/' in href and ('S' in href.upper() or 'AP' in href.upper()):
                product_links.append((href, text[:50]))
                if len(product_links) >= 10:
                    break
        
        print(f"\n示例产品链接:")
        for href, text in product_links:
            print(f"  {text[:40]}: {href}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
