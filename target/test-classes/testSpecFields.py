import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
import json

fetcher = ProductDataFetcher()

print("=" * 80)
print("产品规格字段分析")
print("=" * 80)

product_codes = ["S5735-L-V2", "S5130", "RG-S2910-L", "RG-S5310-E"]

all_fields = set()

for code in product_codes:
    product = fetcher.get_product_by_code(code)
    if not product:
        print(f"\n未找到产品: {code}")
        continue
    
    specs_str = product.get('specs_json', '{}')
    try:
        specs = json.loads(specs_str) if isinstance(specs_str, str) else specs_str
    except:
        specs = {}
    
    print(f"\n--- {product.get('product_name')} ({code}) ---")
    print(f"规格字段数: {len(specs)}")
    
    for key, value in specs.items():
        all_fields.add(key)
        value_str = str(value)[:80]
        print(f"  {key}: {value_str}")

print(f"\n{'=' * 80}")
print(f"所有规格字段汇总 (共 {len(all_fields)} 个):")
print(f"{'=' * 80}")

for i, field in enumerate(sorted(all_fields), 1):
    print(f"{i:2d}. {field}")

print(f"\n{'=' * 80}")
print("查看更多产品的规格数据...")
print(f"{'=' * 80}")

all_products = fetcher.get_all_products_summary()
print(f"数据库总产品数: {len(all_products)}")

field_counts = {}
for p in all_products[:50]:
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    specs_str = full.get('specs_json', '{}')
    try:
        specs = json.loads(specs_str) if isinstance(specs_str, str) else specs_str
    except:
        specs = {}
    for key in specs.keys():
        field_counts[key] = field_counts.get(key, 0) + 1

print(f"\nTop 20 最常见的规格字段:")
sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
for i, (field, count) in enumerate(sorted_fields[:20], 1):
    print(f"{i:2d}. {field}: {count} 个产品")
