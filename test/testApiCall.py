import requests
import json

url = 'http://localhost:5001/api/chat'
payload = {
    "session_id": "test-20260518-001",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print("Calling Python service directly...")
response = requests.post(url, json=payload)
data = response.json()

print(f"Success: {data.get('success')}")
print(f"Has preview: {'preview' in data}")

if data.get('success') and data.get('preview'):
    preview = json.loads(data['preview'])
    
    intent = preview.get('intent', {})
    print(f"Intent: {intent.get('intent')}")
    print(f"Entities: {intent.get('entities')}")
    
    product = preview.get('product_data')
    if product:
        print(f"Product: {product.get('product_name')}")
        print(f"Product code: {product.get('product_code')}")
    else:
        print("ERROR: No product data")
    
    competitors = preview.get('competitor_data', [])
    print(f"Competitors count: {len(competitors)}")
    
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    if messages:
        last_msg = messages[-1]
        content = last_msg.get('content', '')
        print(f"Prompt length: {len(content)} chars")
        print("\nFirst 500 chars of prompt:")
        print(content[:500])
    else:
        print("ERROR: No messages in api_request")
