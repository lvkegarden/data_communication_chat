import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

data_fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("=" * 80)
print("测试品牌识别")
print("=" * 80)

test_products = [
    ('S5735-L-V2', '华为 S5735-L-V2 系列'),
    ('S16700', '华为 S16700 系列'),
    ('S12700H', '华为 S12700H 系列'),
    ('S5130', '华三 S5130 系列'),
    ('RG-AP820C', '锐捷 RG-AP820C 系列'),
    ('RG-S2910-L', '锐捷 RG-S2910-L 系列'),
    ('WA6530', '华三 WA6530 系列'),
    ('WX5500X', '华三 WX5500X 系列'),
]

for code, name in test_products:
    product = data_fetcher.get_product_by_code(code)
    if product:
        brand = evaluator._extract_brand(product)
        print(f"{name} -> 识别品牌: {brand}")
    else:
        print(f"{name} -> 产品未找到")

print("\n" + "=" * 80)
print("测试竞品选择")
print("=" * 80)

target = data_fetcher.get_product_by_code('S5735-L-V2')
all_products = data_fetcher.get_all_products_summary()

print(f"\n目标产品: {target.get('product_name')} ({target.get('product_code')})")
print(f"目标品牌: {evaluator._extract_brand(target)}")
print(f"数据库产品总数: {len(all_products)}")

competitors = evaluator.find_competitors(target, all_products, limit=5)

print(f"\n找到的竞品: {len(competitors)} 个")
for i, comp in enumerate(competitors, 1):
    brand = evaluator._extract_brand(comp)
    print(f"\n  [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
    print(f"      品牌: {brand}")
    print(f"      描述: {comp.get('description')[:50] if comp.get('description') else 'N/A'}...")

print("\n" + "=" * 80)
print("旧逻辑 vs 新逻辑对比")
print("=" * 80)

old_competitors = data_fetcher.get_competitors('S5735-L-V2', limit=3)
print(f"\n旧逻辑找到的竞品: {len(old_competitors)} 个")
for i, comp in enumerate(old_competitors, 1):
    brand = evaluator._extract_brand(comp)
    print(f"  [{i}] {comp.get('product_name')} ({comp.get('product_code')}) - 品牌: {brand}")
