import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from prompt_assembler import PromptAssembler

print("=" * 100)
print("测试优化后的竞品选择逻辑")
print("目标产品: 华为 S5735-L-V2 系列")
print("=" * 100)

data_fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()

print("\n[Step 1] 获取目标产品")
target_product = data_fetcher.get_product_by_code('S5735-L-V2')
if target_product:
    print("  产品名称:", target_product.get('product_name'))
    print("  产品型号:", target_product.get('product_code'))
    print("  产品描述:", target_product.get('description')[:100] if target_product.get('description') else "N/A")
else:
    print("  未找到目标产品")

print("\n[Step 2] 获取所有产品（用于相似性评估）")
all_products = data_fetcher.get_all_products_summary()
print("  数据库中共有", len(all_products), "个产品")
print("  产品列表:")
for p in all_products:
    print(f"    - {p.get('product_name')} ({p.get('product_code')})")

print("\n[Step 3] 使用相似性评估器查找竞品")
print("  相似性评估维度:")
print("    - 产品类型匹配 (30分)")
print("    - 产品类别匹配 (25分)")
print("    - 系列定位匹配 (20分)")
print("    - 规格相似度 (15分)")
print("    - 适用场景匹配 (10分)")
print("  最小竞品阈值: 50分")
print("  同品牌产品: 自动排除")

competitors = evaluator.find_competitors(target_product, all_products, limit=5)

print("\n[Step 4] 详细评估每个候选产品")
for candidate in all_products:
    if candidate.get('product_code') == 'S5735-L-V2':
        continue
    
    result = evaluator.evaluate(target_product, candidate)
    print(f"\n  候选: {candidate.get('product_name')} ({candidate.get('product_code')})")
    print(f"    总分: {result['total_score']}")
    print(f"    是否竞品: {result['is_competitor']}")
    print(f"    原因: {result['reason']}")
    print(f"    品牌: 目标={result.get('target_brand')}, 候选={result.get('candidate_brand')}")
    for item in result['breakdown']:
        print(f"      - {item['category']}: +{item['score']} ({item['detail']})")

print("\n" + "=" * 100)
print("最终选择的竞品:")
print("=" * 100)
if competitors:
    for i, comp in enumerate(competitors, 1):
        print(f"\n  [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
        print(f"      描述: {comp.get('description')[:80] if comp.get('description') else 'N/A'}...")
else:
    print("  未找到符合条件的竞品")

print("\n" + "=" * 100)
print("对比：旧逻辑选择的竞品")
print("=" * 100)
old_competitors = data_fetcher.get_competitors('S5735-L-V2', limit=3)
if old_competitors:
    for i, comp in enumerate(old_competitors, 1):
        print(f"\n  [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
        print(f"      描述: {comp.get('description')[:80] if comp.get('description') else 'N/A'}...")
else:
    print("  旧逻辑也未找到竞品")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
