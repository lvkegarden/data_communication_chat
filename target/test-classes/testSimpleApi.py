import requests
import json

url = 'http://localhost:5001/api/chat'
payload = {
    "session_id": "test-20260518",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = requests.post(url, json=payload)
data = response.json()

if data.get('success') and data.get('preview'):
    preview = json.loads(data['preview'])
    
    print("=== Intent ===")
    print(preview.get('intent', {}))
    
    print("\n=== Product Data ===")
    product = preview.get('product_data')
    if product:
        print(f"Name: {product.get('product_name')}")
        print(f"Code: {product.get('product_code')}")
        print(f"Vendor: {product.get('vendor_name')}")
        print(f"Has desc: {bool(product.get('description'))}")
        print(f"Has specs: {bool(product.get('specs_json'))}")
    else:
        print("NO PRODUCT DATA!")
    
    print("\n=== Competitors ===")
    competitors = preview.get('competitor_data', [])
    print(f"Count: {len(competitors)}")
    for i, c in enumerate(competitors, 1):
        print(f"[{i}] {c.get('product_name')} ({c.get('product_code')})")
        print(f"    Vendor: {c.get('vendor_name')}")
    
    print("\n=== API Request Messages ===")
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    print(f"Message count: {len(messages)}")
    for i, msg in enumerate(messages):
        role = msg.get('role')
        content = msg.get('content', '')
        print(f"\n--- [{i+1}] {role} ({len(content)} chars) ---")
        print(content[:2000])
        if len(content) > 2000:
            print(f"... (truncated, {len(content)} total)")
