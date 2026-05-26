import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app

print("=" * 80)
print("Testing: s5735-l-v2 竞品分析")
print("=" * 80)

client = app.test_client()

payload = {
    "session_id": "test-competitor",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = client.post('/api/chat', json=payload)

if response.status_code == 200:
    data = response.get_json()
    print(f"\nSuccess: {data.get('success')}")
    
    if data.get('preview'):
        preview = json.loads(data['preview'])
        intent = preview.get('intent', {})
        print(f"\nIntent: {intent.get('intent')}")
        print(f"Entities: {intent.get('entities')}")
        
        if preview.get('product_data'):
            pd = preview['product_data']
            print(f"\nProduct: {pd.get('product_name')} ({pd.get('product_code')})")
        
        if preview.get('competitor_data'):
            comps = preview['competitor_data']
            print(f"\nCompetitors found: {len(comps)}")
            for i, comp in enumerate(comps, 1):
                print(f"  {i}. {comp.get('product_name')} ({comp.get('product_code')})")
        
        if preview.get('api_request'):
            messages = preview['api_request'].get('messages', [])
            print(f"\n{'=' * 80}")
            print("Assembled Prompt:")
            print(f"{'=' * 80}")
            for msg in messages:
                print(f"\n[{msg.get('role').upper()}]")
                print(msg.get('content', ''))
else:
    print(f"Error: {response.status_code}")

print("\n" + "=" * 80)
print("Test completed")
print("=" * 80)
