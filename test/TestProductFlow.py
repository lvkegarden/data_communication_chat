import requests
import json
import time

print("=" * 60)
print("产品介绍测试")
print("=" * 60)

# Test 1: 预览产品介绍
print("\n[1/2] 测试产品介绍预览...")
start = time.time()
r = requests.post("http://localhost:5001/api/chat", 
                 json={"session_id": "test_intro", "message": "请为RG-AP820C生成产品介绍", "flag": "n"}, 
                 timeout=90)
elapsed = time.time() - start
print(f"  耗时: {elapsed:.2f}秒")
print(f"  状态: {r.status_code}")
data = r.json()
print(f"  成功: {data.get('success')}")
if data.get('preview'):
    preview = json.loads(data['preview'])
    print(f"\n  预览内容:")
    print(f"    意图: {preview.get('intent', {}).get('intent')}")
    print(f"    路由到: {preview.get('intent', {}).get('routed_to')}")
    if preview.get('product_data'):
        print(f"    产品: {preview['product_data'].get('product_name')} ({preview['product_data'].get('product_code')})")
    if preview.get('api_request') and preview['api_request'].get('messages'):
        for m in preview['api_request']['messages']:
            if m.get('role') == 'user':
                content = m.get('content', '')
                print(f"\n    完整提示词长度: {len(content)}")
                print(f"    提示词预览:\n{content[:400]}...")

# Test 2: 发送产品介绍请求
print("\n" + "=" * 60)
print("\n[2/2] 测试产品介绍发送...")
start = time.time()
r = requests.post("http://localhost:5001/api/chat", 
                 json={"session_id": "test_intro", "message": "请为RG-AP820C生成产品介绍", "flag": "y"}, 
                 timeout=120)
elapsed = time.time() - start
print(f"  耗时: {elapsed:.2f}秒")
print(f"  状态: {r.status_code}")
data = r.json()
print(f"  成功: {data.get('success')}")
if data.get('success'):
    print(f"\n  AI回复长度: {len(data.get('message', ''))}")
    print(f"\n  AI回复:\n{data.get('message', '')}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
