import requests
import json
import time

url = "http://localhost:5001/api/chat"

# 测试：产品介绍
print("=" * 60)
print("测试: 产品介绍意图")
print("=" * 60)

payload = {
    "session_id": "test_001",
    "message": "请为RG-AP820C生成产品介绍",
    "flag": "y"
}

print(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")

start_time = time.time()
try:
    response = requests.post(url, json=payload, timeout=90)
    elapsed = time.time() - start_time

    print(f"响应状态: {response.status_code}")
    print(f"请求耗时: {elapsed:.2f} 秒")

    result = response.json()
    print(f"响应消息长度: {len(result.get('message', ''))} 字符")

    if result.get('intent'):
        print(f"识别意图: {result['intent'].get('intent')}")
        print(f"置信度: {result['intent'].get('confidence')}")
        print(f"路由节点: {result['intent'].get('routed_to')}")

    if result.get('product_data'):
        pd = result['product_data']
        print(f"产品数据: {pd.get('product_code')} - {pd.get('product_name')}")

    print(f"\n响应消息:\n{result.get('message', 'N/A')[:500]}")
except requests.exceptions.Timeout:
    print("请求超时 (>90秒)")
except Exception as e:
    print(f"错误: {e}")
