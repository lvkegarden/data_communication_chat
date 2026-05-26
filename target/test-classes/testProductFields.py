import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
import logging

logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher

fetcher = ProductDataFetcher()

print("=" * 80)
print("Checking product data fields for S5735-L-V2")
print("=" * 80)

product = fetcher.get_product_by_code('S5735-L-V2')
if product:
    print("\nProduct keys:", list(product.keys()))
    print("\nProduct data:")
    for key, value in product.items():
        if value:
            val_str = str(value)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            print(f"  {key}: {val_str}")
else:
    print("Product not found!")

print("\n" + "=" * 80)
print("Checking competitor data fields for S5130")
print("=" * 80)

comp = fetcher.get_product_by_code('S5130')
if comp:
    print("\nCompetitor keys:", list(comp.keys()))
    print("\nCompetitor data:")
    for key, value in comp.items():
        if value:
            val_str = str(value)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            print(f"  {key}: {val_str}")
else:
    print("Competitor not found!")

print("\n" + "=" * 80)
print("Fields used in _build_competitor_analysis_prompt:")
print("=" * 80)
print("- product_name")
print("- product_code")
print("- series")
print("- description")
print("- specs_json")
