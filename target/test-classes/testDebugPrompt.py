import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app

print("=" * 100)
print("DEBUG: s5735-l-v2 竞品分析 - 完整Prompt检查")
print("=" * 100)

client = app.test_client()

payload = {
    "session_id": "test-debug-prompt",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print(f"\n发送请求: {payload['message']}")
response = client.post('/api/chat', json=payload)

if response.status_code == 200:
    data = response.get_json()
    print(f"响应状态: success={data.get('success')}")
    
    if data.get('preview'):
        preview = json.loads(data['preview'])
        
        print("\n" + "=" * 100)
        print("Step 1: 意图识别结果")
        print("=" * 100)
        intent = preview.get('intent', {})
        print(f"  意图: {intent.get('intent')}")
        print(f"  实体: {intent.get('entities')}")
        
        print("\n" + "=" * 100)
        print("Step 2: 产品数据检查")
        print("=" * 100)
        product_data = preview.get('product_data')
        if product_data:
            print(f"  目标产品: {product_data.get('product_name')}")
            print(f"  产品型号: {product_data.get('product_code')}")
            print(f"  产品描述: {product_data.get('description')[:100] if product_data.get('description') else 'None'}...")
        else:
            print("  ERROR: 没有目标产品数据!")
        
        competitor_data = preview.get('competitor_data', [])
        print(f"\n  竞品数量: {len(competitor_data)}")
        for i, comp in enumerate(competitor_data, 1):
            print(f"\n  [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
            print(f"      描述: {comp.get('description')[:80] if comp.get('description') else 'None'}...")
        
        print("\n" + "=" * 100)
        print("Step 3: 完整Prompt内容")
        print("=" * 100)
        if preview.get('api_request'):
            messages = preview['api_request'].get('messages', [])
            print(f"  消息数量: {len(messages)}")
            for msg in messages:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                print(f"\n  --- [{role}] ({len(content)} chars) ---")
                print(content)
        else:
            print("  ERROR: 没有api_request数据!")
    else:
        print("ERROR: 没有preview数据!")
else:
    print(f"ERROR: HTTP {response.status_code}")
    print(response.data)

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
