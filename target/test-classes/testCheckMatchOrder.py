import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
parser = ProductNamingParser()

all_products = fetcher.get_all_products_summary()

target_code = 'S5735-L-V2'
target = fetcher.get_product_by_code(target_code)
target_brand = evaluator._extract_brand(target)

print(f"=" * 80)
print(f"目标产品: {target.get('product_name')} ({target_code}) [{target_brand}]")
print(f"=" * 80)

evaluated = []
for candidate in all_products:
    if candidate.get('product_code') == target_code:
        continue
    
    candidate_brand = evaluator._extract_brand(candidate)
    if candidate_brand == target_brand:
        continue
    
    candidate_full = fetcher.get_product_by_code(candidate.get('product_code'))
    if not candidate_full:
        continue
    
    candidate_code = candidate.get('product_code', '')
    if 'S5130' in candidate_code:
        result = evaluator.evaluate(target, candidate_full)
        evaluated.append({
            'code': candidate_code,
            'brand': candidate_brand,
            'score': result['total_score'],
            'is_competitor': result['is_competitor']
        })

evaluated.sort(key=lambda x: x['score'], reverse=True)

print(f"\nS5130 系列产品匹配情况（按分数排序）:")
print("-" * 80)
for i, item in enumerate(evaluated, 1):
    print(f"[{i}] {item['code']} - {item['brand']} - {item['score']}分 - 竞品: {item['is_competitor']}")
