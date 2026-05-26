import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app

print("=" * 100)
print("完整测试: s5735-l-v2 竞品分析")
print("=" * 100)

client = app.test_client()

payload = {
    "session_id": "test-competitor-optimized",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print(f"\n[1] 发送请求: {payload['message']}")
response = client.post('/api/chat', json=payload)

if response.status_code == 200:
    data = response.get_json()
    print(f"    状态: 成功")
    
    if data.get('preview'):
        preview = json.loads(data['preview'])
        
        intent = preview.get('intent', {})
        print(f"\n[2] 意图识别:")
        print(f"    意图: {intent.get('intent')}")
        print(f"    置信度: {intent.get('confidence')}")
        print(f"    实体: {intent.get('entities')}")
        
        product_data = preview.get('product_data')
        if product_data:
            print(f"\n[3] 目标产品:")
            print(f"    产品名称: {product_data.get('product_name')}")
            print(f"    产品型号: {product_data.get('product_code')}")
        
        competitor_data = preview.get('competitor_data', [])
        print(f"\n[4] 竞品数据:")
        print(f"    找到竞品数量: {len(competitor_data)}")
        for i, comp in enumerate(competitor_data, 1):
            print(f"\n    [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
        
        if preview.get('api_request'):
            messages = preview['api_request'].get('messages', [])
            print(f"\n[5] 拼装的 Prompt:")
            print(f"    消息数量: {len(messages)}")
            for msg in messages:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                if len(content) > 2000:
                    print(f"\n    [{role}] (长度: {len(content)} 字符)")
                    print(f"    --- 前 1000 字符 ---")
                    print(content[:1000])
                    print(f"\n    ... (省略 {len(content)-2000} 字符) ...")
                    print(f"\n    --- 后 1000 字符 ---")
                    print(content[-1000:])
                else:
                    print(f"\n    [{role}]")
                    print(content)

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
