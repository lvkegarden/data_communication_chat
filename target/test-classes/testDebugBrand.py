import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
parser = ProductNamingParser()

target_code = 'RG-S5300-L'
target_product = fetcher.get_product_by_code(target_code)

print(f"目标产品: {target_product.get('product_name')} ({target_code})")
target_brand = evaluator._extract_brand(target_product)
print(f"目标产品品牌: {target_brand}")

all_products = fetcher.get_all_products_summary()

print(f"\n检查几个产品的品牌:")
for product in all_products[:10]:
    code = product.get('product_code', '')
    brand = evaluator._extract_brand(product)
    print(f"  {code}: {brand}")

print(f"\n检查特定产品的品牌:")
specific_codes = ['S5755-H', 'S5800', 'S5735-L-V2']
for code in specific_codes:
    product = fetcher.get_product_by_code(code)
    if product:
        brand = evaluator._extract_brand(product)
        print(f"  {code}: {brand}")
