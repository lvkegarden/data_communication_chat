import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

all_products = fetcher.get_all_products_summary()

print("锐捷产品列表:")
for product in all_products:
    code = product.get('product_code', '')
    name = product.get('product_name', '')
    if 'RG-S575' in code or 'RG-S53' in code:
        print(f"  {name} ({code})")

print("\n\n测试S5735-L-V2匹配RG-S5750系列:")
target = fetcher.get_product_by_code('S5735-L-V2')
candidate = fetcher.get_product_by_code('RG-S5750V2-L')
if target and candidate:
    result = evaluator.evaluate(target, candidate)
    print(f"结果: {result['is_competitor']}, 分数: {result['total_score']}")
    for bd in result['breakdown']:
        print(f"  {bd['category']}: {bd['score']}")
