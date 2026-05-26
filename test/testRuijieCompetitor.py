import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("=" * 80)
print("竞品分析 - 锐捷产品排查")
print("=" * 80)

product_code = "S5735-L-V2"
target_product = fetcher.get_product_by_code(product_code)

print(f"\n目标产品: {target_product.get('product_name')} ({target_product.get('product_code')})")
print(f"品牌: {evaluator._extract_brand(target_product)}")

all_products = fetcher.get_all_products_summary()
print(f"\n数据库总产品数: {len(all_products)}")

print("\n--- 统计各品牌产品 ---")
brand_stats = {}
for p in all_products:
    brand = evaluator._extract_brand(p)
    if brand not in brand_stats:
        brand_stats[brand] = []
    brand_stats[brand].append(p)

for brand, products in brand_stats.items():
    print(f"  {brand or '未知'}: {len(products)} 个产品")

print("\n--- 锐捷产品列表 ---")
ruijie_products = brand_stats.get('锐捷', [])
print(f"锐捷产品总数: {len(ruijie_products)}")
for p in ruijie_products[:10]:
    print(f"  - {p.get('product_name')} ({p.get('product_code')})")
if len(ruijie_products) > 10:
    print(f"  ... 还有 {len(ruijie_products) - 10} 个")

print("\n--- 锐捷接入交换机 ---")
ruijie_access = []
for p in ruijie_products:
    full = fetcher.get_product_by_code(p.get('product_code'))
    if full:
        specs = evaluator._parse_specs(full.get('specs_json', ''))
        product_type = specs.get('产品类型') or full.get('product_type')
        product_category = specs.get('产品定位') or full.get('category')
        if '交换机' in str(product_type) or '交换机' in str(product_category) or '接入' in str(product_category):
            ruijie_access.append(full)

print(f"锐捷交换机产品数: {len(ruijie_access)}")
for p in ruijie_access[:10]:
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    print(f"\n  产品: {p.get('product_name')} ({p.get('product_code')})")
    print(f"    产品类型: {specs.get('产品类型')}")
    print(f"    产品定位: {specs.get('产品定位')}")
    print(f"    适用场景: {specs.get('适用场景')}")

print("\n--- 详细评估几个锐捷产品 ---")
for p in ruijie_access[:3]:
    print(f"\n{'='*60}")
    print(f"评估: {p.get('product_name')} ({p.get('product_code')})")
    result = evaluator.evaluate(target_product, p)
    print(f"总分: {result['total_score']}")
    print(f"是否竞品: {result['is_competitor']}")
    print(f"原因: {result['reason']}")
    print("评分明细:")
    for bd in result['breakdown']:
        print(f"  - {bd['category']}: {bd['score']} 分 ({bd['detail']})")

print("\n" + "=" * 80)
print("当前选中的竞品:")
print("=" * 80)

evaluated = []
for p in all_products:
    if p.get('product_code') == product_code:
        continue
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    result = evaluator.evaluate(target_product, full)
    if result['is_competitor']:
        evaluated.append({
            'product': full,
            'score': result['total_score'],
            'brand': result.get('candidate_brand', ''),
            'breakdown': result['breakdown']
        })

evaluated.sort(key=lambda x: x['score'], reverse=True)
top_competitors = evaluated[:3]

for i, comp in enumerate(top_competitors, 1):
    p = comp['product']
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    print(f"\n--- 竞品 {i}: {p.get('product_name')} ---")
    print(f"  品牌: {comp['brand']}")
    print(f"  型号: {p.get('product_code')}")
    print(f"  总分: {comp['score']}")
    print(f"  产品类型: {specs.get('产品类型')}")
    print(f"  产品定位: {specs.get('产品定位')}")
