import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher

fetcher = ProductDataFetcher()

all_products = fetcher.get_all_products_summary()

print("搜索包含S5750或S5760的锐捷产品:")
for product in all_products:
    code = product.get('product_code', '')
    if 'S575' in code or 'S576' in code:
        print(f"  {product.get('product_name')} ({code})")
