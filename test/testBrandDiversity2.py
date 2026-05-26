import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from prompt_assembler import PromptAssembler

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
assembler = PromptAssembler(fetcher, evaluator)

print("=" * 80)
print("竞品分析 - 品牌多样性优化测试")
print("=" * 80)

product_data = fetcher.get_product_by_code("S5735-L-V2")
all_products = fetcher.get_all_products_summary()

print(f"\n目标产品: {product_data.get('product_name')} ({product_data.get('product_code')})")

evaluated = []
for p in all_products:
    if p.get('product_code') == 'S5735-L-V2':
        continue
    full = fetcher.get_product_by_code(p.get('product_code'))
    if not full:
        continue
    result = evaluator.evaluate(product_data, full)
    if result['is_competitor']:
        evaluated.append({
            'product': full,
            'score': result['total_score'],
            'brand': result.get('candidate_brand', '')
        })

evaluated.sort(key=lambda x: x['score'], reverse=True)

print(f"\n--- 所有合格竞品（按分数排序）---")
for i, item in enumerate(evaluated[:20], 1):
    p = item['product']
    print(f"  {i:2d}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {item['brand']} - 分数: {item['score']}")

print("\n--- 按品牌统计 ---")
by_brand = {}
for item in evaluated:
    brand = item['brand'] or '未知'
    if brand not in by_brand:
        by_brand[brand] = []
    by_brand[brand].append(item)

for brand, items in by_brand.items():
    print(f"  {brand}: {len(items)} 个产品，最高分: {items[0]['score']}")

print("\n--- 优化前：直接按分数排序 Top 3 ---")
before = [item['product'] for item in evaluated[:3]]
before_brands = [item['brand'] for item in evaluated[:3]]
for i, item in enumerate(evaluated[:3], 1):
    p = item['product']
    print(f"  {i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {item['brand']}")

print("\n--- 优化后：品牌多样性选择 ---")
after = assembler._select_competitors_with_brand_diversity(evaluated, 3)
after_brands = [evaluator._extract_brand(p) for p in after]
for i, p in enumerate(after, 1):
    brand = evaluator._extract_brand(p)
    print(f"  {i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {brand}")

print("\n" + "=" * 80)
print("优化结果对比")
print("=" * 80)
print(f"优化前品牌: {before_brands} (不同品牌数: {len(set(before_brands))})")
print(f"优化后品牌: {after_brands} (不同品牌数: {len(set(after_brands))})")

if len(set(after_brands)) > len(set(before_brands)):
    print("\n[OK] 优化成功：品牌多样性提升！")
elif len(set(after_brands)) == len(set(before_brands)):
    print("\n[INFO] 品牌多样性未变化（可能所有高分产品都来自同一品牌）")
else:
    print("\n[ERROR] 品牌多样性下降")
