import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
parser = ProductNamingParser()

all_products = fetcher.get_all_products_summary()

by_brand_type = {}
for p in all_products:
    brand = evaluator._extract_brand(p) or '未知'
    code = p.get('product_code', '')
    
    naming = parser.parse(code)
    product_type = naming.get('product_type', '未知')
    
    if brand not in by_brand_type:
        by_brand_type[brand] = {}
    if product_type not in by_brand_type[brand]:
        by_brand_type[brand][product_type] = []
    
    by_brand_type[brand][product_type].append({
        'code': code,
        'name': p.get('product_name', ''),
        'naming': naming.get('details', {})
    })

print("=" * 80)
print("数据库产品统计（按品牌和类型）")
print("=" * 80)

for brand in ['华为', 'H3C', '锐捷']:
    if brand in by_brand_type:
        print(f"\n{brand}:")
        for ptype, products in sorted(by_brand_type[brand].items(), key=lambda x: -len(x[1])):
            print(f"  {ptype}: {len(products)} 个")
            for p in products[:5]:
                print(f"    - {p['name']} ({p['code']})")
