import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from huawei_scraper import HuaweiScraper

scraper = HuaweiScraper()

# 只测试交换机采集
products = scraper.scrape_switch_products()

print(f"\n{'='*60}")
print(f"采集结果:")
print(f"{'='*60}")
print(f"产品数: {len(products)}")

for p in products[:5]:
    print(f"\n- {p.product_code}")
    print(f"  URL: {p.product_url[:60]}...")
    print(f"  描述长度: {len(p.description) if p.description else 0}")
    print(f"  规格数: {len(p.specs) if p.specs else 0}")
