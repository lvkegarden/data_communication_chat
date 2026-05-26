import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

product_code = "S5735-L-V2"
target_product = fetcher.get_product_by_code(product_code)

print("=" * 80)
print("目标产品详情")
print("=" * 80)
print(f"产品名称: {target_product.get('product_name')}")
print(f"产品型号: {target_product.get('product_code')}")
print(f"产品系列: {target_product.get('series')}")
print(f"产品类型: {target_product.get('product_type')}")
print(f"产品类别: {target_product.get('category')}")

target_specs = evaluator._parse_specs(target_product.get('specs_json', ''))
print(f"\n技术规格:")
for key, value in target_specs.items():
    print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("锐捷接入交换机评估")
print("=" * 80)

all_products = fetcher.get_all_products_summary()

ruijie_access = []
for p in all_products:
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    brand = evaluator._extract_brand(full)
    if brand == '锐捷':
        specs = evaluator._parse_specs(full.get('specs_json', ''))
        product_type = specs.get('产品类型') or full.get('product_type')
        product_pos = specs.get('产品定位') or full.get('category')
        if '接入' in str(product_pos) or '接入层' in str(product_pos):
            ruijie_access.append(full)

print(f"\n锐捷接入交换机数量: {len(ruijie_access)}")

for p in ruijie_access:
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    result = evaluator.evaluate(target_product, p)
    
    print(f"\n--- {p.get('product_name')} ({p.get('product_code')}) ---")
    print(f"  总分: {result['total_score']}")
    print(f"  是否竞品: {result['is_competitor']}")
    print(f"  目标产品定位: {target_specs.get('产品定位')}")
    print(f"  竞品产品定位: {specs.get('产品定位')}")
    print(f"  评分明细:")
    for bd in result['breakdown']:
        print(f"    - {bd['category']}: {bd['score']} 分 ({bd['detail']})")

print("\n" + "=" * 80)
print("华三接入交换机评估（前3个）")
print("=" * 80)

h3c_access = []
for p in all_products:
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    brand = evaluator._extract_brand(full)
    if brand == 'H3C':
        specs = evaluator._parse_specs(full.get('specs_json', ''))
        product_pos = specs.get('产品定位') or full.get('category')
        if '接入' in str(product_pos) or '接入层' in str(product_pos):
            h3c_access.append(full)

print(f"\n华三接入交换机数量: {len(h3c_access)}")

for p in h3c_access[:3]:
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    result = evaluator.evaluate(target_product, p)
    
    print(f"\n--- {p.get('product_name')} ({p.get('product_code')}) ---")
    print(f"  总分: {result['total_score']}")
    print(f"  是否竞品: {result['is_competitor']}")
    print(f"  目标产品定位: {target_specs.get('产品定位')}")
    print(f"  竞品产品定位: {specs.get('产品定位')}")
    print(f"  评分明细:")
    for bd in result['breakdown']:
        print(f"    - {bd['category']}: {bd['score']} 分 ({bd['detail']})")
