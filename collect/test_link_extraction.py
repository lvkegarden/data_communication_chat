import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

response = session.get('https://e.huawei.com/cn/products/switches/campus-switches', timeout=30)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 查找包含产品系列名的链接
series_names = ['S12700E', 'S12700H', 'S8700', 'S7700', 'S5735', 'S6735']

print("查找包含产品系列的链接:")
for link in soup.find_all('a', href=True):
    href = link['href']
    text = link.get_text(strip=True)
    
    for series in series_names:
        if series.lower() in href.lower() or series in text:
            if '/products/' in href and not href.endswith('.pdf'):
                full_url = urljoin('https://e.huawei.com', href)
                print(f"  {series}: {text[:60]} -> {full_url[:80]}")
                break
