import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
parser = ProductNamingParser()

all_products = fetcher.get_all_products_summary()

access_switches = []
wireless_aps = []

for p in all_products:
    code = p.get('product_code', '')
    naming = parser.parse(code)
    product_type = naming.get('product_type', '')
    details = naming.get('details', {})
    switch_level = details.get('switch_level', '')
    
    if product_type == '交换机' and '接入' in switch_level:
        access_switches.append({
            'brand': evaluator._extract_brand(p),
            'code': code,
            'name': p.get('product_name', ''),
            'level': switch_level,
            'feature': details.get('feature_level', '')
        })
    elif product_type == '无线AP':
        wireless_aps.append({
            'brand': evaluator._extract_brand(p),
            'code': code,
            'name': p.get('product_name', ''),
            'wifi': details.get('wifi_generation', ''),
            'level': details.get('level', '')
        })

print("=" * 80)
print("接入交换机产品")
print("=" * 80)

by_brand = {}
for s in access_switches:
    brand = s['brand'] or '未知'
    if brand not in by_brand:
        by_brand[brand] = []
    by_brand[brand].append(s)

for brand in ['华为', 'H3C', '锐捷']:
    if brand in by_brand:
        print(f"\n{brand} ({len(by_brand[brand])} 个):")
        for s in by_brand[brand]:
            print(f"  {s['name']} ({s['code']}) - {s['level']} - {s['feature']}")

print("\n" + "=" * 80)
print("无线AP产品")
print("=" * 80)

by_brand_ap = {}
for ap in wireless_aps:
    brand = ap['brand'] or '未知'
    if brand not in by_brand_ap:
        by_brand_ap[brand] = []
    by_brand_ap[brand].append(ap)

for brand in ['华为', 'H3C', '锐捷']:
    if brand in by_brand_ap:
        print(f"\n{brand} ({len(by_brand_ap[brand])} 个):")
        for ap in by_brand_ap[brand][:10]:
            print(f"  {ap['name']} ({ap['code']}) - {ap['wifi']} - {ap['level']}")
