import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

sys.path.insert(0, 'd:/project/ai/localrest/python')

from prompt_assembler import PromptAssembler
from product_data_fetcher import ProductDataFetcher

print("=" * 80)
print("Test Prompt Assembly (Case Insensitive)")
print("=" * 80)

data_fetcher = ProductDataFetcher()
assembler = PromptAssembler(data_fetcher)

test_messages = [
    ('S5735-L-V2 产品介绍', 'product_introduction', {}),
    ('s5735-l-v2 产品介绍', 'product_introduction', {}),
    ('为RG-AP820C生成产品介绍', 'product_introduction', {}),
    ('为rg-ap820c生成产品介绍', 'product_introduction', {}),
]

success_count = 0
fail_count = 0

for message, intent, entities in test_messages:
    print(f"\n{'=' * 80}")
    print(f"Test: {message}")
    print(f"Intent: {intent}")
    print(f"{'=' * 80}")
    
    prompt, context = assembler.assemble_from_message(message, intent, entities)
    
    print(f"\nContext:")
    print(f"  has_data: {context.get('has_data')}")
    
    if context.get('product_data'):
        product = context['product_data']
        print(f"  Product Name: {product.get('product_name')}")
        print(f"  Product Code: {product.get('product_code')}")
    
    if context.get('has_data'):
        print(f"\n[OK] Data fetched and prompt assembled")
        success_count += 1
    else:
        print(f"\n[FAIL] Failed to fetch product data")
        fail_count += 1

print("\n" + "=" * 80)
print(f"Test Summary: {success_count} passed, {fail_count} failed")
print("=" * 80)
