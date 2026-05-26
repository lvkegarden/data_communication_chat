import requests
from bs4 import BeautifulSoup

urls = [
    'https://www.h3c.com/cn/Products_and_Solutions/Products/Enterprise/SDN/SDN_Switch/',
    'https://www.h3c.com/cn/Products_and_Solutions/Products/Enterprise/WLAN/',
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

for url in urls:
    print(f"\n{'='*80}")
    print(f"测试: {url}")
    print(f"{'='*80}")
    
    try:
        response = session.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应编码: {response.encoding}")
        print(f"内容长度: {len(response.text)}")
        
        # 尝试查看响应内容前500字符
        preview = response.text[:500]
        print(f"内容预览: {preview[:300]}...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"页面标题: {soup.title.string if soup.title else '无标题'}")
        
        # 查找产品相关内容
        import re
        html = str(soup)
        s_series = re.findall(r'S\d{4}[-A-Za-z0-9]*', html)
        print(f"找到交换机系列: {s_series[:10]}...")
        
        wa_series = re.findall(r'WA\d{4,5}[-A-Za-z0-9]*', html)
        print(f"找到无线系列: {wa_series[:10]}...")
        
    except Exception as e:
        print(f"错误: {e}")
