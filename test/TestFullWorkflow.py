import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app, workflow_app, build_system_prompt

from langchain_core.messages import HumanMessage

print("=" * 80)
print("Testing: s5735-l-v2 产品介绍")
print("=" * 80)

test_messages = [
    "s5735-l-v2 产品介绍",
    "S5735-L-V2 产品介绍",
    "rg-ap820c 竞品分析",
]

client = app.test_client()

for message in test_messages:
    print(f"\n{'=' * 80}")
    print(f"Test: {message}")
    print(f"{'=' * 80}")
    
    payload = {
        "session_id": "test-session",
        "message": message,
        "flag": "n"
    }
    
    response = client.post('/api/chat', json=payload)
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"\nSuccess: {data.get('success')}")
        
        if data.get('preview'):
            preview = json.loads(data['preview'])
            print(f"\nIntent: {preview.get('intent')}")
            
            if preview.get('product_data'):
                pd = preview['product_data']
                print(f"Product: {pd.get('product_name')} ({pd.get('product_code')})")
            
            if preview.get('api_request'):
                messages = preview['api_request'].get('messages', [])
                print(f"\nMessages count: {len(messages)}")
                if messages:
                    for msg in messages:
                        print(f"\n[{msg.get('role').upper()}]")
                        content = msg.get('content', '')
                        print(content[:600] if len(content) > 600 else content)
                        if len(content) > 600:
                            print(f"... ({len(content) - 600} more chars)")
    else:
        print(f"Error: {response.status_code}")

print("\n" + "=" * 80)
print("Test completed")
print("=" * 80)
