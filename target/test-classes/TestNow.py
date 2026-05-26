import requests
import json
import time

url = "http://localhost:5001/api/chat"

print("Test: Product Intro Preview (flag=n)")
r = requests.post(url, json={"session_id":"t_preview","message":"请为RG-AP820C生成产品介绍","flag":"n"}, timeout=60)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Success: {d.get('success')}")
preview = json.loads(d.get('preview', '{}'))
print(f"Intent: {preview.get('intent')}")
if preview.get('product_data'):
    pd = preview['product_data']
    print(f"Product: {pd.get('product_code')} - {pd.get('product_name')}")
msgs = preview.get('api_request', {}).get('messages', [])
print(f"Messages count: {len(msgs)}")
for m in msgs:
    role = m.get('role')
    content = m.get('content', '')
    print(f"  [{role}] length={len(content)}")
    if role == 'user':
        print(f"  Content preview: {content[:300]}...")
