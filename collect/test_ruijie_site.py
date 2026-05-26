import requests
from bs4 import BeautifulSoup
import re

urls = [
    'https://www.ruijie.com.cn/cp/jh/',
    'https://www.ruijie.com.cn/cp/wx/',
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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
        
        # 查找交换机系列
        s_series = re.findall(r'RG-S\d{3,5}[A-Za-z0-9_-]*', html)
        unique_s = list(set(s_series))[:15]
        print(f"\n找到交换机系列 ({len(unique_s)}个): {unique_s}")
        
        # 查找无线AP系列
        ap_series = re.findall(r'RG-AP\d{3,5}[A-Za-z0-9_-]*', html)
        unique_ap = list(set(ap_series))[:10]
        print(f"找到无线AP系列 ({len(unique_ap)}个): {unique_ap}")
        
    except Exception as e:
        print(f"错误: {e}")
