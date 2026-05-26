import requests
import json

url = "http://localhost:5001/api/chat"

# Test 1: Greeting
print("Test 1: Greeting (flag=y)")
r = requests.post(url, json={"session_id":"t1","message":"你好","flag":"y"}, timeout=30)
d = r.json()
print(f"  Message: {d.get('message','')[:80]}")

# Test 2: Product intro preview
print("\nTest 2: Product Intro Preview (flag=n)")
r = requests.post(url, json={"session_id":"t2","message":"请为RG-AP820C生成产品介绍","flag":"n"}, timeout=60)
d = r.json()
print(f"  Success: {d.get('success')}")
preview = json.loads(d.get('preview', '{}'))
print(f"  Intent: {preview.get('intent', {}).get('intent')}")
if preview.get('product_data'):
    print(f"  Product: {preview['product_data'].get('product_code')} - {preview['product_data'].get('product_name')}")
msgs = preview.get('api_request', {}).get('messages', [])
print(f"  Messages: {len(msgs)}")
for m in msgs:
    role = m.get('role')
    content = m.get('content', '')
    print(f"    [{role}] length={len(content)}")
    if role == 'user' and len(content) > 100:
        print(f"    Preview: {content[:200]}...")

# Test 3: Product intro submit
print("\nTest 3: Product Intro Submit (flag=y)")
r = requests.post(url, json={"session_id":"t3","message":"请为RG-AP820C生成产品介绍","flag":"y"}, timeout=90)
d = r.json()
print(f"  Success: {d.get('success')}")
print(f"  Message length: {len(d.get('message',''))}")
print(f"  Message: {d.get('message','')[:300]}...")
