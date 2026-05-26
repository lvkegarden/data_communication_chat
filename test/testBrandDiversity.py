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

user_message = "s5735-l-v2 竞品分析"
intent_value = "competitor_analysis"
entities = {"product_code": "S5735-L-V2"}

print(f"\n测试消息: {user_message}")
print(f"意图: {intent_value}")
print(f"实体: {entities}")

print("\n--- 优化前：直接按分数排序 ---")
product_data = fetcher.get_product_by_code("S5735-L-V2")
all_products = fetcher.get_all_products_summary()

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

print("\n优化前 Top 3:")
for i, item in enumerate(evaluated[:3], 1):
    p = item['product']
    print(f"  {i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {item['brand']} - 分数: {item['score']}")

print("\n--- 优化后：品牌多样性选择 ---")
selected_with_diversity = assembler._select_competitors_with_brand_diversity(evaluated, 3)

print("\n优化后 Top 3:")
for i, p in enumerate(selected_with_diversity, 1):
    brand = evaluator._extract_brand(p)
    print(f"  {i}. {p.get('product_name')} ({p.get('product_code')}) - 品牌: {brand}")

print("\n" + "=" * 80)
print("验证优化效果")
print("=" * 80)

brands_before = [item['brand'] for item in evaluated[:3]]
brands_after = [evaluator._extract_brand(p) for p in selected_with_diversity]

print(f"\n优化前品牌: {brands_before} (不同品牌数: {len(set(brands_before))})")
print(f"优化后品牌: {brands_after} (不同品牌数: {len(set(brands_after))})")

if len(set(brands_after)) > len(set(brands_before)):
    print("\n✅ 优化成功：品牌多样性提升！")
elif len(set(brands_after)) == len(set(brands_before)):
    print("\n⚠️ 品牌多样性未变化（可能所有高分产品都来自同一品牌）")
else:
    print("\n❌ 品牌多样性下降")
