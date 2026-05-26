import sys
import os
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))

from huawei_scraper import HuaweiScraper

scraper = HuaweiScraper()

switch_url = "https://e.huawei.com/cn/products/switches/campus-switches"

print("正在爬取交换机列表页...")
response = scraper.session.get(switch_url, timeout=30)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, 'html.parser')
products = scraper._extract_switch_products(soup)

print(f"\n找到 {len(products)} 个产品系列")
print("\n检查产品详情URL:")
for name, info in list(products.items())[:5]:
    detail_url = scraper._find_detail_url(info)
    links_count = len(info.get('links', []))
    print(f"  {name}: 链接数={links_count}, 详情页={detail_url or '无'}")
