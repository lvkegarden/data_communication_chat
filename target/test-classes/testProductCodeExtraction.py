import re
import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

from app import extract_product_code_from_message
from prompt_assembler import PromptAssembler
from product_data_fetcher import ProductDataFetcher

print("=" * 60)
print("测试产品型号提取功能")
print("=" * 60)

test_cases = [
    'S5735-L-V2 产品介绍',
    '为RG-AP820C生成产品介绍',
    '华为S5735-L24P4S-A交换机',
    'RG-S5310-24GT4S-E交换机',
    'WA6520-E 产品介绍',
    'WX5500X 产品介绍',
    'S5735-L-V2',
    '请介绍RG-S5760-X',
    '产品型号:S5735-L',
]

print("\n测试 app.py 中的 extract_product_code_from_message:")
print("-" * 60)
for test in test_cases:
    result = extract_product_code_from_message(test)
    print(f"  输入: {test}")
    print(f"  输出: {result}")
    print()

print("\n测试 prompt_assembler.py 中的 extract_product_code_from_message:")
print("-" * 60)
assembler = PromptAssembler(ProductDataFetcher())
for test in test_cases:
    result = assembler.extract_product_code_from_message(test)
    print(f"  输入: {test}")
    print(f"  输出: {result}")
    print()

print("=" * 60)
print("测试完成")
print("=" * 60)
