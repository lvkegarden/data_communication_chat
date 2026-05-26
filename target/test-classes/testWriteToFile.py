import requests
import json

url = 'http://localhost:5001/api/chat'
payload = {
    "session_id": "test-20260518-002",
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

response = requests.post(url, json=payload, timeout=120)
data = response.json()

output = []
output.append(f"Success: {data.get('success')}")
output.append(f"Has preview: {'preview' in data}")

if data.get('success') and data.get('preview'):
    preview = json.loads(data['preview'])
    
    intent = preview.get('intent', {})
    output.append(f"\nIntent: {intent.get('intent')}")
    output.append(f"Entities: {intent.get('entities')}")
    
    product = preview.get('product_data')
    if product:
        output.append(f"\nProduct: {product.get('product_name')}")
        output.append(f"Product code: {product.get('product_code')}")
        output.append(f"Product vendor: {product.get('vendor_name')}")
    else:
        output.append("\nERROR: No product data")
    
    competitors = preview.get('competitor_data', [])
    output.append(f"\nCompetitors count: {len(competitors)}")
    for i, c in enumerate(competitors, 1):
        output.append(f"  [{i}] {c.get('product_name')} ({c.get('product_code')}) - {c.get('vendor_name')}")
    
    api_req = preview.get('api_request', {})
    messages = api_req.get('messages', [])
    if messages:
        last_msg = messages[-1]
        content = last_msg.get('content', '')
        output.append(f"\nPrompt length: {len(content)} chars")
        output.append("\n=== FULL PROMPT ===")
        output.append(content)
    else:
        output.append("\nERROR: No messages in api_request")

with open('d:/project/ai/localrest/test/test_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Result written to test_result.txt")
