import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import time
import logging

logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from prompt_assembler import PromptAssembler

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
assembler = PromptAssembler(fetcher, evaluator)

print("=" * 80)
print("优化前后耗时对比测试")
print("=" * 80)

target_code = 'S5735-L-V2'
user_message = 's5735-l-v2 竞品分析'
intent = 'competitor_analysis'

print("\n【优化前 - 原逻辑】")
print("-" * 80)
t1 = time.time()
target = fetcher.get_product_by_code(target_code)
t2 = time.time()
all_products = fetcher.get_all_products_summary()
t3 = time.time()

qualified_count_old = 0
fetch_count_old = 0
old_fetch_start = time.time()
for candidate in all_products:
    if candidate.get('product_code') == target_code:
        continue
    candidate_full = fetcher.get_product_by_code(candidate.get('product_code'))
    fetch_count_old += 1
    if candidate_full:
        result = evaluator.evaluate(target, candidate_full)
        if result['is_competitor']:
            qualified_count_old += 1
old_fetch_end = time.time()

old_total = (old_fetch_end - t1) * 1000
old_fetch_total = (old_fetch_end - old_fetch_start) * 1000

print(f"  目标产品: {target.get('product_name')}")
print(f"  所有产品: {len(all_products)}")
print(f"  数据获取次数: {fetch_count_old}")
print(f"  合格竞品: {qualified_count_old}")
print(f"  耗时:")
print(f"    - 获取目标产品: {(t2-t1)*1000:.2f} ms")
print(f"    - 获取产品列表: {(t3-t2)*1000:.2f} ms")
print(f"    - 遍历获取完整数据: {old_fetch_total:.2f} ms")
print(f"    - 总计: {old_total:.2f} ms")

print("\n【优化后 - 带预筛选】")
print("-" * 80)
entities = {'product_code': target_code}

new_start = time.time()
prompt, context = assembler.assemble_from_message(user_message, intent, entities)
new_end = time.time()

new_total = (new_end - new_start) * 1000
product_data = context.get('product_data', {})
competitors = context.get('competitor_data', [])

print(f"  目标产品: {product_data.get('product_name')}")
print(f"  合格竞品: {len(competitors)}")
print(f"  Prompt长度: {len(prompt)} chars")
print(f"  耗时: {new_total:.2f} ms")
for i, comp in enumerate(competitors, 1):
    print(f"  竞品{i}: {comp.get('product_name')} ({comp.get('product_code')})")

print("\n" + "=" * 80)
print("优化效果对比")
print("=" * 80)
improvement = ((old_total - new_total) / old_total * 100) if old_total > 0 else 0
print(f"  优化前: {old_total:.2f} ms")
print(f"  优化后: {new_total:.2f} ms")
print(f"  减少: {old_total - new_total:.2f} ms")
print(f"  提升: {improvement:.1f}%")

print("\n" + "=" * 80)
print("详细日志")
print("=" * 80)
