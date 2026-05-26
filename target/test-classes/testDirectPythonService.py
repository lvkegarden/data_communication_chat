import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import requests
import json

print("=" * 100)
print("测试 Python LangGraph 服务直接调用")
print("=" * 100)

url = 'http://localhost:5001/api/chat'
payload = {
    "session_id": "test-direct-python",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print(f"\n发送请求到: {url}")
print(f"消息: {payload['message']}")

try:
    response = requests.post(url, json=payload)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"success: {data.get('success')}")
        
        if data.get('preview'):
            preview = json.loads(data['preview'])
            
            print("\n" + "=" * 100)
            print("意图识别结果")
            print("=" * 100)
            intent = preview.get('intent', {})
            print(f"  意图: {intent.get('intent')}")
            print(f"  实体: {intent.get('entities')}")
            
            print("\n" + "=" * 100)
            print("产品数据")
            print("=" * 100)
            product = preview.get('product_data')
            if product:
                print(f"  目标产品: {product.get('product_name')} ({product.get('product_code')})")
                print(f"  品牌: {product.get('vendor_name') or product.get('source')}")
            else:
                print("  无目标产品数据!")
            
            competitors = preview.get('competitor_data', [])
            print(f"\n  竞品数量: {len(competitors)}")
            for i, comp in enumerate(competitors, 1):
                print(f"\n    [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
                print(f"        品牌: {comp.get('vendor_name') or comp.get('source')}")
            
            print("\n" + "=" * 100)
            print("拼装的 Prompt (messages[1].content)")
            print("=" * 100)
            api_request = preview.get('api_request', {})
            messages = api_request.get('messages', [])
            if len(messages) >= 2:
                user_msg = messages[1]
                content = user_msg.get('content', '')
                print(f"长度: {len(content)} 字符")
                print("\n内容:")
                print("-" * 100)
                print(content[:3000] if len(content) > 3000 else content)
                if len(content) > 3000:
                    print(f"\n... (省略 {len(content)-3000} 字符) ...")
            else:
                print("ERROR: 没有足够的消息")
                print(f"messages: {messages}")
        else:
            print("没有preview数据!")
    else:
        print(f"错误响应: {response.text}")
except Exception as e:
    print(f"请求异常: {e}")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
