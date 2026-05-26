import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator, SimilarityCriteria
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
parser = ProductNamingParser()

all_products = fetcher.get_all_products_summary()

target_code = 'S5735-L-V2'
target = fetcher.get_product_by_code(target_code)

print(f"=" * 80)
print(f"目标产品: {target.get('product_name')} ({target_code})")
print(f"=" * 80)

target_naming = parser.parse(target_code)
print(f"\n目标产品命名解析: {target_naming.get('details', {})}")

target_brand = evaluator._extract_brand(target)
print(f"目标产品品牌: {target_brand}")

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
    if 'S5130S-EI' in candidate_code or 'S5130S-LI' in candidate_code or 'S5130S-SI' in candidate_code:
        result = evaluator.evaluate(target, candidate_full)
        evaluated.append({
            'code': candidate_code,
            'brand': candidate_brand,
            'score': result['total_score'],
            'is_competitor': result['is_competitor'],
            'breakdown': result['breakdown']
        })

evaluated.sort(key=lambda x: x['score'], reverse=True)

print(f"\n{'=' * 80}")
print(f"S5130S 系列产品匹配情况")
print(f"{'=' * 80}")

for item in evaluated:
    print(f"\n{item['code']}: {item['score']}分, 竞品: {item['is_competitor']}")
    for bd in item['breakdown']:
        if bd['score'] != 0:
            sign = '+' if bd['score'] > 0 else ''
            print(f"  {sign}{bd['score']}分 - {bd['category']}")
