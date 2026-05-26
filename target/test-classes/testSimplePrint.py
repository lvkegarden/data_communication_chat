import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
import logging

logging.getLogger().setLevel(logging.ERROR)

from app import app

client = app.test_client()

payload = {
    "session_id": "test-20260518",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = client.post('/api/chat', json=payload)
data = response.get_json()

print("STATUS:", response.status_code)
print("SUCCESS:", data.get('success'))

if data.get('preview'):
    preview = json.loads(data['preview'])
    
    intent = preview.get('intent', {})
    print("\n=== INTENT ===")
    print("Type:", intent.get('intent'))
    print("Entities:", intent.get('entities'))
    
    product = preview.get('product_data')
    print("\n=== PRODUCT ===")
    if product:
        print("Name:", product.get('product_name'))
        print("Code:", product.get('product_code'))
        print("Vendor:", product.get('vendor_name'))
        print("Has desc:", bool(product.get('description')))
        print("Has specs:", bool(product.get('specs_json')))
    else:
        print("ERROR: NO PRODUCT")
    
    competitors = preview.get('competitor_data', [])
    print("\n=== COMPETITORS ===")
    print("Count:", len(competitors))
    for i, c in enumerate(competitors, 1):
        print(f"\n[{i}]", c.get('product_name'), "(" + c.get('product_code') + ")")
        print("    Vendor:", c.get('vendor_name'))
        print("    Has desc:", bool(c.get('description')))
    
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    print("\n=== MESSAGES ===")
    print("Count:", len(messages))
    for i, msg in enumerate(messages):
        role = msg.get('role')
        content = msg.get('content', '')
        print(f"\n--- [{i+1}] {role} ({len(content)} chars) ---")
        if len(content) > 500:
            print(content[:500])
            print("...")
        else:
            print(content)
