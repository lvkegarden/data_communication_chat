import sys
import os
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

output_file = os.path.join('d:', os.sep, 'project', 'ai', 'localrest', 'test', 'debug_output.txt')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Status: {response.status_code}\n")
    f.write(f"Success: {data.get('success')}\n")

    if data.get('preview'):
        preview = json.loads(data['preview'])
        
        intent = preview.get('intent', {})
        f.write(f"\n=== Intent ===\n")
        f.write(f"Type: {intent.get('intent')}\n")
        f.write(f"Entities: {intent.get('entities')}\n")
        
        product = preview.get('product_data')
        f.write(f"\n=== Product Data ===\n")
        if product:
            f.write(f"Name: {product.get('product_name')}\n")
            f.write(f"Code: {product.get('product_code')}\n")
            f.write(f"Vendor: {product.get('vendor_name') or product.get('source')}\n")
        else:
            f.write("ERROR: NO PRODUCT DATA\n")
        
        competitors = preview.get('competitor_data', [])
        f.write(f"\n=== Competitors ({len(competitors)}) ===\n")
        for i, c in enumerate(competitors, 1):
            f.write(f"\n[{i}] {c.get('product_name')} ({c.get('product_code')})\n")
            f.write(f"    Vendor: {c.get('vendor_name') or c.get('source')}\n")
        
        api_req = preview.get('api_request', {})
        messages = api_req.get('messages', [])
        f.write(f"\n=== API Request Messages ({len(messages)}) ===\n")
        for i, msg in enumerate(messages):
            role = msg.get('role')
            content = msg.get('content', '')
            f.write(f"\n--- [{i+1}] {role} ({len(content)} chars) ---\n")
            f.write(content)
            f.write("\n")

print(f"Output written to: {output_file}")
