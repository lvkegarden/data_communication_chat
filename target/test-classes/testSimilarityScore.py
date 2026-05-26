import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator

data_fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

target = data_fetcher.get_product_by_code('S5735-L-V2')

print("=" * 80)
print("目标产品详细信息")
print("=" * 80)
print(f"产品名称: {target.get('product_name')}")
print(f"产品型号: {target.get('product_code')}")
print(f"规格: {target.get('specs_json')[:200]}...")

print("\n" + "=" * 80)
print("测试几个潜在竞品的相似性评分")
print("=" * 80)

test_candidates = [
    ('RG-S2910-L', '锐捷 RG-S2910-L 系列'),
    ('RG-S5300-E', '锐捷 RG-S5300-E 系列'),
    ('RG-S5760-L', '锐捷 RG-S5760-L 系列'),
    ('S5130', '华三 S5130 系列'),
    ('S5500', '华三 S5500 系列'),
]

for code, name in test_candidates:
    product = data_fetcher.get_product_by_code(code)
    if product:
        result = evaluator.evaluate(target, product)
        print(f"\n{name} ({code}):")
        print(f"  品牌: {result.get('target_brand')} vs {result.get('candidate_brand')}")
        print(f"  总分: {result.get('total_score')}")
        print(f"  是否竞品: {result.get('is_competitor')}")
        print(f"  评分明细:")
        for item in result.get('breakdown', []):
            print(f"    - {item.get('category')}: +{item.get('score')} ({item.get('detail')})")
    else:
        print(f"\n{name} ({code}): 产品未找到")
