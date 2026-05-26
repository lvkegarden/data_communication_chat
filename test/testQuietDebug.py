import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
import logging

logging.disable(logging.CRITICAL)

from app import app

client = app.test_client()

payload = {
    "session_id": "test-20260518-final",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = client.post('/api/chat', json=payload)
data = response.get_json()

result = []
result.append(f"Status: {response.status_code}")
result.append(f"Success: {data.get('success')}")

if data.get('preview'):
    preview = json.loads(data['preview'])
    
    intent = preview.get('intent', {})
    result.append(f"\n=== Intent ===")
    result.append(f"Type: {intent.get('intent')}")
    result.append(f"Entities: {intent.get('entities')}")
    
    product = preview.get('product_data')
    result.append(f"\n=== Product Data ===")
    if product:
        result.append(f"Name: {product.get('product_name')}")
        result.append(f"Code: {product.get('product_code')}")
        result.append(f"Vendor: {product.get('vendor_name') or product.get('source')}")
    else:
        result.append("ERROR: NO PRODUCT DATA")
    
    competitors = preview.get('competitor_data', [])
    result.append(f"\n=== Competitors ({len(competitors)}) ===")
    for i, c in enumerate(competitors, 1):
        result.append(f"\n[{i}] {c.get('product_name')} ({c.get('product_code')})")
        result.append(f"    Vendor: {c.get('vendor_name') or c.get('source')}")
    
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    result.append(f"\n=== API Request Messages ({len(messages)}) ===")
    for i, msg in enumerate(messages):
        role = msg.get('role')
        content = msg.get('content', '')
        result.append(f"\n--- [{i+1}] {role} ({len(content)} chars) ---")
        result.append(content)

with open('d:/project/ai/localrest/test/debug_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result))

print("Done, check test/debug_output.txt")
