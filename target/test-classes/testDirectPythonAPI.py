import requests
import json
import time

API_URL = "http://localhost:5001/api/chat"

payload = {
    "session_id": "test-direct-" + str(int(time.time())),
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print("=" * 80)
print("直接调用 Python API (flag='n')")
print("=" * 80)
print(f"\n测试请求: {json.dumps(payload, ensure_ascii=False)}")

print("\n--- 发送请求 ---")
try:
    start_time = time.time()
    response = requests.post(API_URL, json=payload, timeout=30)
    elapsed = (time.time() - start_time) * 1000
    
    print(f"HTTP 状态码: {response.status_code}")
    print(f"总耗时: {elapsed:.2f} ms")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n--- 响应数据 ---")
        print(f"Success: {data.get('success')}")
        
        if data.get('success'):
            preview = data.get('preview', '{}')
            try:
                preview_data = json.loads(preview)
                print(f"\n--- 预览内容 ---")
                print(f"意图: {preview_data.get('intent', {})}")
                api_request = preview_data.get('api_request', {})
                messages = api_request.get('messages', [])
                if messages:
                    for msg in messages:
                        content = msg.get('content', '')
                        print(f"\n{msg.get('role', 'N/A').upper()}:")
                        print(f"  长度: {len(content)} 字符")
                        print(f"  前 500 字符: {content[:500]}...")
            except json.JSONDecodeError:
                print(f"预览内容 (原始): {preview[:500]}...")
        else:
            print(f"Error: {data.get('error')}")
    else:
        print(f"\n--- 错误响应 ---")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
except requests.exceptions.Timeout:
    print("请求超时 (>30秒)")
except Exception as e:
    print(f"请求异常: {e}")
    import traceback
    traceback.print_exc()
