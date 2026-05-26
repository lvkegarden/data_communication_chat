import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator, SimilarityCriteria

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("=" * 80)
print("竞品评分规则深度分析")
print("=" * 80)

print("\n--- 评分标准:")
print(f"  PRODUCT_TYPE_MATCH = {SimilarityCriteria.PRODUCT_TYPE_MATCH} 分 (产品类型匹配)")
print(f"  CATEGORY_MATCH = {SimilarityCriteria.CATEGORY_MATCH} 分 (产品类别匹配)")
print(f"  SERIES_PATTERN_MATCH = {SimilarityCriteria.SERIES_PATTERN_MATCH} 分 (系列定位匹配)")
print(f"  KEY_SPEC_SIMILARITY = {SimilarityCriteria.KEY_SPEC_SIMILARITY} 分 (规格相似度)")
print(f"  TARGET_SCENARIO_MATCH = {SimilarityCriteria.TARGET_SCENARIO_MATCH} 分 (适用场景匹配)")
print(f"  MIN_COMPETITOR_SCORE = {SimilarityCriteria.MIN_COMPETITOR_SCORE} 分 (竞品阈值)")
print(f"  SAME_BRAND_PENALTY = {SimilarityCriteria.SAME_BRAND_PENALTY} 分 (同品牌排除)")

product_code = "S5735-L-V2"
target_product = fetcher.get_product_by_code(product_code)

print(f"\n--- 目标产品: {target_product.get('product_name')} ({product_code})")
target_specs = evaluator._parse_specs(target_product.get('specs_json', ''))
print(f"  产品类型: {target_specs.get('产品类型')}")
print(f"  产品定位: {target_specs.get('产品定位')}")
print(f"  适用场景: {target_specs.get('适用场景')}")
print(f"  交换容量: {target_specs.get('交换容量')}")
print(f"  包转发率: {target_specs.get('包转发率')}")

all_products = fetcher.get_all_products_summary()

print(f"\n--- 遍历所有产品，找出 100 分产品 ---")
score_100_products = []

for p in all_products:
    if p.get('product_code') == product_code:
        continue
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    result = evaluator.evaluate(target_product, full)
    if result['total_score'] == 100:
        score_100_products.append({
            'product': full,
            'result': result
        })

print(f"\n100 分产品总数: {len(score_100_products)}")

print(f"\n--- 100 分产品详情 ---")
for i, item in enumerate(score_100_products, 1):
    p = item['product']
    result = item['result']
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    brand = result.get('candidate_brand')
    print(f"\n{i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {brand}")
    print(f"   产品类型: {specs.get('产品类型')}")
    print(f"   产品定位: {specs.get('产品定位')}")
    print(f"   适用场景: {specs.get('适用场景')}")
    print(f"   评分明细:")
    for bd in result['breakdown']:
        print(f"     - {bd['category']}: {bd['score']} 分")

print(f"\n--- 100 分产品按品牌统计 ---")
by_brand = {}
for item in score_100_products:
    brand = item['result'].get('candidate_brand') or '未知'
    if brand not in by_brand:
        by_brand[brand] = []
    by_brand[brand].append(item)

for brand, items in by_brand.items():
    print(f"  {brand}: {len(items)} 个产品")
    if len(items) > 5:
        print(f"    前5个:")
        for i, item in enumerate(items[:5], 1):
            p = item['product']
            print(f"      {i}. {p.get('product_code')}")
        print(f"    ... 还有 {len(items) - 5} 个")
    else:
        for i, item in enumerate(items, 1):
            p = item['product']
            print(f"    {i}. {p.get('product_code')}")
