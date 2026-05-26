import requests
import json
import time

print("=" * 60)
print("服务验证测试")
print("=" * 60)

# Test 1: Java健康检查
print("\n[1/5] 测试 Java 健康检查...")
try:
    r = requests.get("http://localhost:8080/api/health", timeout=5)
    print(f"  状态: {r.status_code}")
    print(f"  响应: {r.json() if r.text else '无'}")
except Exception as e:
    print(f"  失败: {e}")

# Test 2: Python健康检查
print("\n[2/5] 测试 Python 健康检查...")
try:
    r = requests.get("http://localhost:5001/api/health", timeout=5)
    print(f"  状态: {r.status_code}")
    print(f"  响应: {r.json() if r.text else '无'}")
except Exception as e:
    print(f"  失败: {e}")

# Test 3: Java产品数据API
print("\n[3/5] 测试 Java 产品数据 API...")
try:
    r = requests.get("http://localhost:8080/api/product-data/detail/RG-AP820C", timeout=10)
    print(f"  状态: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  成功: {data.get('success')}")
        if data.get('product'):
            print(f"  产品: {data['product'].get('product_name')} ({data['product'].get('product_code')})")
except Exception as e:
    print(f"  失败: {e}")

# Test 4: Python聊天API - 问候
print("\n[4/5] 测试 Python 聊天 API (问候)...")
try:
    r = requests.post("http://localhost:5001/api/chat", 
                     json={"session_id": "test_1", "message": "你好", "flag": "y"}, 
                     timeout=30)
    print(f"  状态: {r.status_code}")
    data = r.json()
    print(f"  成功: {data.get('success')}")
    print(f"  回复: {data.get('message', '')[:80]}...")
except Exception as e:
    print(f"  失败: {e}")

# Test 5: Python聊天API - 产品介绍预览
print("\n[5/5] 测试 Python 聊天 API (产品介绍预览)...")
try:
    r = requests.post("http://localhost:5001/api/chat", 
                     json={"session_id": "test_2", "message": "请为RG-AP820C生成产品介绍", "flag": "n"}, 
                     timeout=30)
    print(f"  状态: {r.status_code}")
    data = r.json()
    print(f"  成功: {data.get('success')}")
    if data.get('preview'):
        preview = json.loads(data['preview'])
        print(f"  意图: {preview.get('intent', {}).get('intent')}")
        print(f"  路由到: {preview.get('intent', {}).get('routed_to')}")
        if preview.get('product_data'):
            print(f"  产品代码: {preview['product_data'].get('product_code')}")
            print(f"  产品名称: {preview['product_data'].get('product_name')}")
        if preview.get('api_request') and preview['api_request'].get('messages'):
            msgs = preview['api_request']['messages']
            print(f"  消息数: {len(msgs)}")
            for m in msgs:
                if m.get('role') == 'user':
                    print(f"  提示词长度: {len(m.get('content', ''))}")
except Exception as e:
    print(f"  失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
