import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator, SimilarityCriteria

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("=" * 80)
print("规格相似度优化效果测试")
print("=" * 80)

print(f"\n--- 当前评分标准 ---")
print(f"产品类型匹配: {SimilarityCriteria.PRODUCT_TYPE_MATCH} 分")
print(f"产品类别匹配: {SimilarityCriteria.CATEGORY_MATCH} 分")
print(f"系列定位匹配: {SimilarityCriteria.SERIES_PATTERN_MATCH} 分")
print(f"规格相似度: {SimilarityCriteria.KEY_SPEC_SIMILARITY} 分")
print(f"  - 交换容量匹配: {SimilarityCriteria.SWITCHING_CAPACITY_MATCH} 分")
print(f"  - 包转发率匹配: {SimilarityCriteria.PACKET_FORWARDING_MATCH} 分")
print(f"  - 端口数量匹配: {SimilarityCriteria.PORT_COUNT_MATCH} 分")
print(f"  - 上行端口类型匹配: {SimilarityCriteria.UPLINK_TYPE_MATCH} 分")
print(f"  - PoE支持匹配: {SimilarityCriteria.POE_MATCH} 分")
print(f"  - 电源类型匹配: {SimilarityCriteria.POWER_TYPE_MATCH} 分")
print(f"适用场景匹配: {SimilarityCriteria.TARGET_SCENARIO_MATCH} 分")
print(f"竞品阈值: {SimilarityCriteria.MIN_COMPETITOR_SCORE} 分")

product_code = "S5735-L-V2"
target_product = fetcher.get_product_by_code(product_code)

print(f"\n--- 目标产品 ---")
print(f"产品: {target_product.get('product_name')} ({product_code})")
target_specs = evaluator._parse_specs(target_product.get('specs_json', ''))
for key, value in target_specs.items():
    print(f"  {key}: {value}")

all_products = fetcher.get_all_products_summary()

print(f"\n--- 遍历所有产品，重新评分 ---")

score_products = {}

for p in all_products:
    if p.get('product_code') == product_code:
        continue
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    result = evaluator.evaluate(target_product, full)
    score = result['total_score']
    if score not in score_products:
        score_products[score] = []
    score_products[score].append({
        'product': full,
        'result': result
    })

print(f"\n--- 评分分布 ---")
for score in sorted(score_products.keys(), reverse=True):
    products = score_products[score]
    print(f"{score} 分: {len(products)} 个产品")
    if len(products) <= 5:
        for item in products:
            p = item['product']
            brand = item['result'].get('candidate_brand')
            print(f"  - {p.get('product_name')} ({p.get('product_code')}) - {brand}")
    else:
        brands = {}
        for item in products:
            brand = item['result'].get('candidate_brand') or '未知'
            brands[brand] = brands.get(brand, 0) + 1
        brand_str = ', '.join([f"{b}:{c}" for b, c in brands.items()])
        print(f"  品牌分布: {brand_str}")

print(f"\n--- Top 10 产品详情 ---")
all_evaluated = []
for score, products in score_products.items():
    for item in products:
        all_evaluated.append({
            'score': score,
            'product': item['product'],
            'result': item['result']
        })

all_evaluated.sort(key=lambda x: x['score'], reverse=True)

for i, item in enumerate(all_evaluated[:10], 1):
    p = item['product']
    result = item['result']
    brand = result.get('candidate_brand')
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    
    print(f"\n{i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {brand} - 总分: {item['score']}")
    print(f"   评分明细:")
    for bd in result['breakdown']:
        print(f"     - {bd['category']}: {bd['score']} 分 ({bd['detail']})")

print(f"\n--- 100 分产品分析 ---")
score_100 = score_products.get(100, [])
print(f"100 分产品总数: {len(score_100)}")

if score_100:
    by_brand = {}
    for item in score_100:
        brand = item['result'].get('candidate_brand') or '未知'
        if brand not in by_brand:
            by_brand[brand] = []
        by_brand[brand].append(item)
    
    for brand, items in by_brand.items():
        print(f"  {brand}: {len(items)} 个")

print(f"\n--- 品牌多样性检查 (Top 3) ---")
top_3 = all_evaluated[:3]
brands = []
for i, item in enumerate(top_3, 1):
    p = item['product']
    brand = item['result'].get('candidate_brand')
    brands.append(brand)
    print(f"{i}. {p.get('product_name')} - {brand} - {item['score']} 分")

unique_brands = set(brands)
print(f"\nTop 3 品牌: {brands}")
print(f"不同品牌数: {len(unique_brands)}")
