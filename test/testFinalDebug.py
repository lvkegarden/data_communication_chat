import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app

client = app.test_client()

payload = {
    "session_id": "test-20260518-final",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = client.post('/api/chat', json=payload)
data = response.get_json()

lines = []
lines.append(f"Status: {response.status_code}")
lines.append(f"Success: {data.get('success')}")

if data.get('preview'):
    preview = json.loads(data['preview'])
    
    intent = preview.get('intent', {})
    lines.append(f"\n=== Intent ===")
    lines.append(f"Type: {intent.get('intent')}")
    lines.append(f"Entities: {intent.get('entities')}")
    
    product = preview.get('product_data')
    lines.append(f"\n=== Product Data ===")
    if product:
        lines.append(f"Name: {product.get('product_name')}")
        lines.append(f"Code: {product.get('product_code')}")
        lines.append(f"Vendor: {product.get('vendor_name') or product.get('source')}")
        desc = product.get('description', '')
        lines.append(f"Description: {desc[:100] if desc else 'EMPTY'}...")
        specs = product.get('specs_json', '')
        lines.append(f"Specs: {specs[:100] if specs else 'EMPTY'}...")
    else:
        lines.append("ERROR: NO PRODUCT DATA")
    
    competitors = preview.get('competitor_data', [])
    lines.append(f"\n=== Competitors ({len(competitors)}) ===")
    for i, c in enumerate(competitors, 1):
        lines.append(f"\n[{i}] {c.get('product_name')} ({c.get('product_code')})")
        lines.append(f"    Vendor: {c.get('vendor_name') or c.get('source')}")
        desc = c.get('description', '')
        lines.append(f"    Desc: {desc[:80] if desc else 'EMPTY'}...")
    
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    lines.append(f"\n=== API Request Messages ({len(messages)}) ===")
    for i, msg in enumerate(messages):
        role = msg.get('role')
        content = msg.get('content', '')
        lines.append(f"\n--- [{i+1}] {role} ({len(content)} chars) ---")
        if len(content) > 2000:
            lines.append(content[:1000])
            lines.append(f"\n... (truncated, {len(content)} total) ...")
            lines.append(content[-1000:])
        else:
            lines.append(content)

with open('d:/project/ai/localrest/test/debug_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Output written to test/debug_output.txt")
