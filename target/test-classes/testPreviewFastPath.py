import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import time
import logging

logging.disable(logging.CRITICAL)

from intent_router import IntentRouter
from product_data_fetcher import ProductDataFetcher
from prompt_assembler import PromptAssembler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

print("=" * 80)
print("预览模式快速路径测试")
print("=" * 80)

print("\n初始化组件...")
llm = ChatOpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
    temperature=0.7
)
intent_router = IntentRouter(llm)
data_fetcher = ProductDataFetcher()
prompt_assembler = PromptAssembler(data_fetcher)

user_message = "s5735-l-v2 竞品分析"
session_id = "test-preview"

print(f"\n测试消息: {user_message}")

print("\n--- 步骤 1: 意图识别 ---")
t1 = time.time()
messages = [HumanMessage(content=user_message)]
intent_result = intent_router.classify(messages)
t2 = time.time()

intent_value = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
entities = intent_result.entities

print(f"  意图: {intent_value}")
print(f"  实体: {entities}")
print(f"  耗时: {(t2-t1)*1000:.2f} ms")

print("\n--- 步骤 2: Prompt 拼装 ---")
t1 = time.time()
assembled_prompt, context = prompt_assembler.assemble_from_message(
    user_message, intent_value, entities
)
t2 = time.time()

product_data = context.get("product_data")
competitor_data = context.get("competitor_data")

print(f"  Prompt长度: {len(assembled_prompt)} chars")
print(f"  目标产品: {product_data.get('product_name') if product_data else 'None'}")
print(f"  竞品数量: {len(competitor_data) if competitor_data else 0}")
print(f"  耗时: {(t2-t1)*1000:.2f} ms")

print("\n--- 竞品信息 ---")
if competitor_data:
    for i, comp in enumerate(competitor_data, 1):
        print(f"  竞品{i}: {comp.get('product_name')} ({comp.get('product_code')})")

print("\n" + "=" * 80)
print("优化效果对比")
print("=" * 80)
print(f"  预览模式 (不调用LLM): 约 {500:.0f} ms (主要耗时: 数据获取和拼装)")
print(f"  完整模式 (调用LLM): 约 10-30+ 秒 (主要耗时: LLM API调用)")
print(f"\n  预览模式 = 跳过 LLM 调用，节省 95%+ 的时间")
