import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import logging
logging.disable(logging.CRITICAL)

import requests
import time
import json

print("=" * 80)
print("测试竞品分析预览接口")
print("=" * 80)

python_api_url = "http://localhost:5001/api/chat"

test_request = {
    "session_id": "test_optimization_002",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print(f"\n测试请求: s5735-l-v2 竞品分析 (flag='n' - 预览模式)")

start_time = time.time()

try:
    response = requests.post(
        python_api_url,
        json=test_request,
        timeout=60
    )
    elapsed = (time.time() - start_time) * 1000
    
    print(f"HTTP 状态码: {response.status_code}")
    print(f"总耗时: {elapsed:.2f} ms")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n响应数据结构:")
        print(f"  keys: {list(result.keys())}")
        
        for key, value in result.items():
            if isinstance(value, str):
                print(f"\n--- {key} (字符串, 长度: {len(value)}) ---")
                if key == 'preview' or key == 'prompt' or key == 'content':
                    print(value[:1500] if len(value) > 1500 else value)
                    
                    if '锐捷' in value:
                        print(f"\n✅ 锐捷产品已包含在竞品中")
                    else:
                        print(f"\n❌ 锐捷产品未包含在竞品中")
                    
                    if '华三' in value or 'H3C' in value:
                        print(f"✅ 华三产品已包含在竞品中")
                    else:
                        print(f"❌ 华三产品未包含在竞品中")
                    
                    print(f"\n--- 竞品列表 ---")
                    import re
                    competitor_pattern = r'【竞品(\d+)】\s*\n- 产品名称：([^\n]+)\s*\n- 产品型号：([^\n]+)'
                    competitors = re.findall(competitor_pattern, value)
                    for i, (num, name, code) in enumerate(competitors, 1):
                        print(f"  {i}. {name} ({code})")
                else:
                    print(f"  {value[:200]}")
            elif isinstance(value, dict):
                print(f"\n--- {key} (dict) ---")
                print(f"  keys: {list(value.keys())}")
            elif isinstance(value, list):
                print(f"\n--- {key} (list, 长度: {len(value)}) ---")
                if len(value) > 0:
                    first_item = value[0]
                    if isinstance(first_item, dict):
                        print(f"  第一个元素 keys: {list(first_item.keys())}")
                    else:
                        print(f"  第一个元素: {first_item}")
            else:
                print(f"\n--- {key} ({type(value)}) ---")
                print(f"  {value}")
                
    else:
        print(f"错误: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"请求超时")
except Exception as e:
    import traceback
    print(f"异常: {e}")
    print(traceback.format_exc())
