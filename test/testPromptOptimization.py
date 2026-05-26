import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from prompt_assembler import PromptAssembler

fetcher = ProductDataFetcher()
evaluator = SimilarityEvaluator()
assembler = PromptAssembler(fetcher, evaluator)

print("=" * 80)
print("竞品分析 Prompt 优化验证")
print("=" * 80)

user_message = "s5735-l-v2 竞品分析"
intent_value = "competitor_analysis"
entities = {"product_code": "S5735-L-V2"}

print(f"\n测试消息: {user_message}")
print(f"意图: {intent_value}")
print(f"实体: {entities}")

print("\n--- 拼装 Prompt ---")
assembled_prompt, context = assembler.assemble_from_message(
    user_message, intent_value, entities
)

product_data = context.get("product_data")
competitor_data = context.get("competitor_data")

print(f"\n目标产品: {product_data.get('product_name') if product_data else 'None'}")
print(f"竞品数量: {len(competitor_data) if competitor_data else 0}")
if competitor_data:
    for i, comp in enumerate(competitor_data, 1):
        print(f"  竞品{i}: {comp.get('product_name')} ({comp.get('product_code')})")

print(f"\n--- Prompt 内容 (前 2000 字符) ---")
print(assembled_prompt[:2000])

if len(assembled_prompt) > 2000:
    print(f"\n... (剩余 {len(assembled_prompt) - 2000} 字符)")

print("\n" + "=" * 80)
print("优化内容")
print("=" * 80)
print("""
1. Prompt 结构优化:
   - 添加了完整的报告结构模板
   - 包含标准化的表格格式
   - 明确的输出格式要求

2. 表格格式:
   - 核心参数对比表 (9个维度)
   - 优劣势分析表
   - SWOT分析表

3. 页面展示优化:
   - Markdown 语法解析
   - 表格美观渲染（渐变表头、斑马纹、圆角）
   - 标题层级样式
   - 列表和粗体样式
""")
