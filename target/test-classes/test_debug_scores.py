import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

target = fetcher.get_product_by_code('S5735-L-V2')

all_products = fetcher.get_all_products_summary()

print("前20个产品的品牌:")
for product in all_products[:20]:
    code = product.get('product_code', '')
    brand = product.get('brand', '')
    print(f"  {code}: brand={brand}")

print("\n所有锐捷产品的匹配分数:")
for product in all_products:
    code = product.get('product_code', '')
    brand = product.get('brand', '')
    if '锐捷' in str(brand) or 'RG-' in str(code):
        try:
            candidate = fetcher.get_product_by_code(code)
            if candidate:
                result = evaluator.evaluate(target, candidate)
                print(f"  {code}: {result['total_score']}, is_competitor={result['is_competitor']}")
        except Exception as e:
            print(f"  {code}: error {e}")
