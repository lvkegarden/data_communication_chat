import sys
import json
sys.path.insert(0, 'd:/project/ai/localrest/python')

from product_data_fetcher import ProductDataFetcher
from prompt_assembler import PromptAssembler

print("=" * 100)
print("DIRECT TEST: s5735-l-v2 Competitor Analysis")
print("=" * 100)

data_fetcher = ProductDataFetcher()
assembler = PromptAssembler(data_fetcher)

product_code = 'S5735-L-V2'

print("\n[Step 1] Fetching product:", product_code)
product = data_fetcher.get_product_by_code(product_code)
if product:
    print("  OK Product found:", product.get('product_name'))
    print("     - Code:", product.get('product_code'))
    print("     - Vendor:", product.get('vendor_name'))
    print("     - Product Type:", product.get('product_type'))
else:
    print("  FAIL Product NOT found")

print("\n[Step 2] Fetching competitors for:", product_code)
competitors = data_fetcher.get_competitors(product_code, limit=3)
print("  OK Competitors found:", len(competitors))
for i, comp in enumerate(competitors, 1):
    print(f"     [{i}] {comp.get('product_name')} ({comp.get('product_code')}) - {comp.get('vendor_name')}")

print("\n[Step 3] Building competitor analysis prompt")
prompt = assembler._build_competitor_analysis_prompt(product, competitors, "s5735-l-v2 竞品分析")
print("  OK Prompt length:", len(prompt), "chars")

print("\n" + "=" * 100)
print("FULL PROMPT CONTENT:")
print("=" * 100)
print(prompt)
print("\n" + "=" * 100)
print("END OF PROMPT")
print("=" * 100)
