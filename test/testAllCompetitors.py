import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator, SimilarityCriteria

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("=" * 80)
print("S5735-L-V2 竞品评分完整列表")
print("=" * 80)

product_code = "S5735-L-V2"
target_product = fetcher.get_product_by_code(product_code)

print(f"\n目标产品: {target_product.get('product_name')} ({product_code})")
print(f"产品类型: 交换机")
print(f"产品定位: 接入交换机")

all_products = fetcher.get_all_products_summary()

print(f"\n数据库总产品数: {len(all_products)}")

evaluated_list = []

for p in all_products:
    if p.get('product_code') == product_code:
        continue
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    result = evaluator.evaluate(target_product, full)
    if result['total_score'] > 0 and result.get('is_competitor', False):
        evaluated_list.append({
            'product': full,
            'score': result['total_score'],
            'brand': result.get('candidate_brand', '未知'),
            'breakdown': result['breakdown']
        })

evaluated_list.sort(key=lambda x: x['score'], reverse=True)

print(f"\n合格竞品数: {len(evaluated_list)} (≥{SimilarityCriteria.MIN_COMPETITOR_SCORE}分)")

print(f"\n{'=' * 80}")
print("所有竞品评分详情 (按分数降序)")
print(f"{'=' * 80}")

score_groups = {}
for item in evaluated_list:
    score = item['score']
    if score not in score_groups:
        score_groups[score] = []
    score_groups[score].append(item)

for score in sorted(score_groups.keys(), reverse=True):
    items = score_groups[score]
    print(f"\n{'-' * 80}")
    print(f"【{score} 分】共 {len(items)} 个产品")
    print(f"{'-' * 80}")
    
    brands = {}
    for item in items:
        brand = item['brand'] or '未知'
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(item)
    
    for brand, brand_items in brands.items():
        print(f"\n  品牌: {brand} ({len(brand_items)} 个)")
        for item in brand_items:
            p = item['product']
            print(f"    - {p.get('product_name')} ({p.get('product_code')})")
    
    if len(items) > 0:
        sample_item = items[0]
        print(f"\n  评分明细示例:")
        for bd in sample_item['breakdown']:
            print(f"    - {bd['category']}: {bd['score']} 分")

print(f"\n{'=' * 80}")
print("品牌分布统计")
print(f"{'=' * 80}")

brand_counts = {}
for item in evaluated_list:
    brand = item['brand'] or '未知'
    brand_counts[brand] = brand_counts.get(brand, 0) + 1

for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {brand}: {count} 个产品")

print(f"\n{'=' * 80}")
print("Top 10 竞品详情")
print(f"{'=' * 80}")

for i, item in enumerate(evaluated_list[:10], 1):
    p = item['product']
    specs = evaluator._parse_specs(p.get('specs_json', ''))
    
    print(f"\n{i}. {p.get('product_name')} ({p.get('product_code')})")
    print(f"   品牌: {item['brand']}")
    print(f"   总分: {item['score']} 分")
    print(f"   评分明细:")
    for bd in item['breakdown']:
        print(f"     - {bd['category']}: {bd['score']} 分")

print(f"\n{'=' * 80}")
print("Top 3 竞品 (品牌多样性优先)")
print(f"{'=' * 80}")

by_brand = {}
for item in evaluated_list:
    brand = item['brand'] or '未知'
    if brand not in by_brand:
        by_brand[brand] = []
    by_brand[brand].append(item)

for brand, items in by_brand.items():
    items.sort(key=lambda x: x['score'], reverse=True)

top_3_diverse = []
used_brands = set()
for brand, items in sorted(by_brand.items(), key=lambda x: x[1][0]['score'], reverse=True):
    if len(top_3_diverse) >= 3:
        break
    if items:
        top_3_diverse.append(items[0])
        used_brands.add(brand)

remaining_needed = 3 - len(top_3_diverse)
if remaining_needed > 0:
    for item in evaluated_list:
        if remaining_needed <= 0:
            break
        if item not in top_3_diverse:
            top_3_diverse.append(item)
            remaining_needed -= 1

for i, item in enumerate(top_3_diverse, 1):
    p = item['product']
    print(f"\n{i}. {p.get('product_name')} ({p.get('product_code')}) - {item['brand']} - {item['score']} 分")
