import requests
from bs4 import BeautifulSoup
import re

urls = [
    'https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/Switches/',
    'https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/IP_Wlan/',
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

for url in urls:
    print(f"\n{'='*80}")
    print(f"测试: {url}")
    print(f"{'='*80}")
    
    try:
        response = session.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"页面标题: {soup.title.string if soup.title else '无标题'}")
        
        html = str(soup)
        s_series = re.findall(r'S\d{4}[A-Za-z0-9_-]*', html)
        unique_s = list(set(s_series))[:15]
        print(f"找到交换机系列 ({len(unique_s)}个): {unique_s}")
        
        wa_series = re.findall(r'WA\d{4,5}[A-Za-z0-9_-]*', html)
        unique_wa = list(set(wa_series))[:10]
        print(f"找到无线系列 ({len(unique_wa)}个): {unique_wa}")
        
    except Exception as e:
        print(f"错误: {e}")
