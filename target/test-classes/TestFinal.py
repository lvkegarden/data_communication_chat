import requests
import json
import time

url = "http://localhost:5001/api/chat"

print("=" * 60)
print("Test: Product Intro Preview (flag=n)")
print("=" * 60)

r = requests.post(url, json={"session_id":"t_preview","message":"请为RG-AP820C生成产品介绍","flag":"n"}, timeout=30)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Success: {d.get('success')}")
print(f"Message: '{d.get('message', '')}'")

if d.get('preview'):
    preview = json.loads(d['preview'])
    print(f"\nPreview content:")
    print(f"  session_id: {preview.get('session_id')}")
    print(f"  message: {preview.get('message')}")
    print(f"  flag: {preview.get('flag')}")
    
    if preview.get('intent'):
        intent = preview['intent']
        print(f"  intent: {intent.get('intent')}")
        print(f"  confidence: {intent.get('confidence')}")
        print(f"  routed_to: {intent.get('routed_to')}")
    
    if preview.get('product_data'):
        pd = preview['product_data']
        print(f"  product_code: {pd.get('product_code')}")
        print(f"  product_name: {pd.get('product_name')}")
        print(f"  category: {pd.get('category')}")
        print(f"  source: {pd.get('source')}")
        print(f"  description: {pd.get('description', '')[:50]}...")
    
    if preview.get('api_request') and preview['api_request'].get('messages'):
        msgs = preview['api_request']['messages']
        print(f"\n  Messages to LLM ({len(msgs)}):")
        for m in msgs:
            role = m.get('role')
            content = m.get('content', '')
            print(f"    [{role}] length={len(content)}")
            if role == 'user' and len(content) > 50:
                print(f"    Content preview:\n{content[:300]}...")
else:
    print("No preview!")

print("\n" + "=" * 60)
print("Test: Product Intro Submit (flag=y)")
print("=" * 60)

r = requests.post(url, json={"session_id":"t_submit","message":"请为RG-AP820C生成产品介绍","flag":"y"}, timeout=60)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Success: {d.get('success')}")
print(f"Message length: {len(d.get('message', ''))}")
print(f"Message: {d.get('message', '')[:300]}...")

if d.get('intent'):
    print(f"\nIntent: {d['intent'].get('intent')}")
    print(f"Routed to: {d['intent'].get('routed_to')}")

print("\nDone!")
