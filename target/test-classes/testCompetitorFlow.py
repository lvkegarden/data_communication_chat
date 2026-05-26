import sys
sys.path.insert(0, 'd:/project/ai/localrest/python')

import json
from app import app

def test_competitor_analysis():
    print("=" * 100)
    print("TEST: s5735-l-v2 竞品分析")
    print("=" * 100)

    client = app.test_client()

    payload = {
        "session_id": "test-competitor-flow",
        "message": "s5735-l-v2 竞品分析",
        "flag": "n"
    }

    print(f"\n[Step 1] Sending request to /api/chat")
    print(f"  - message: {payload['message']}")
    print(f"  - flag: {payload['flag']} (preview mode)")
    
    response = client.post('/api/chat', json=payload)
    
    print(f"\n[Step 2] Response received:")
    print(f"  - status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"  - success: {data.get('success')}")
        
        if data.get('preview'):
            preview = json.loads(data['preview'])
            
            print(f"\n{'=' * 100}")
            print("[Step 3] Workflow Execution Flow")
            print(f"{'=' * 100}")
            
            intent = preview.get('intent', {})
            print(f"\n--- Intent Classification ---")
            print(f"  Intent: {intent.get('intent')}")
            print(f"  Confidence: {intent.get('confidence')}")
            print(f"  Reason: {intent.get('reason')}")
            print(f"  Entities: {intent.get('entities')}")
            print(f"  Routed to: {intent.get('routed_to')}")
            
            print(f"\n--- Data Fetching ---")
            if preview.get('product_data'):
                pd = preview['product_data']
                print(f"  Product found: YES")
                print(f"    - Name: {pd.get('product_name')}")
                print(f"    - Code: {pd.get('product_code')}")
                print(f"    - Vendor: {pd.get('vendor_name')}")
                print(f"    - Product type: {pd.get('product_type')}")
                if pd.get('description'):
                    desc = pd['description'][:200] + '...' if len(pd['description']) > 200 else pd['description']
                    print(f"    - Description: {desc}")
                if pd.get('specifications'):
                    print(f"    - Specifications: {len(pd['specifications'])} items")
            else:
                print(f"  Product found: NO")
            
            if preview.get('competitor_data'):
                comps = preview['competitor_data']
                print(f"\n  Competitors found: {len(comps)}")
                for i, comp in enumerate(comps, 1):
                    print(f"\n    [{i}] {comp.get('product_name')} ({comp.get('product_code')})")
                    print(f"        Vendor: {comp.get('vendor_name')}")
            else:
                print(f"\n  Competitors found: NO")
            
            print(f"\n{'=' * 100}")
            print("[Step 4] Assembled Prompt (user message)")
            print(f"{'=' * 100}")
            
            if preview.get('api_request'):
                messages = preview['api_request'].get('messages', [])
                for msg in messages:
                    role = msg.get('role', 'unknown').upper()
                    content = msg.get('content', '')
                    print(f"\n[{role}]")
                    if len(content) > 3000:
                        print(f"[Content length: {len(content)} chars - showing first and last 1500 chars]")
                        print(f"\n--- FIRST 1500 CHARS ---")
                        print(content[:1500])
                        print(f"\n... (truncated, total {len(content)} chars) ...")
                        print(f"\n--- LAST 1500 CHARS ---")
                        print(content[-1500:])
                    else:
                        print(content)
            else:
                print("No api_request in preview")
        else:
            print(f"  No preview data")
    else:
        print(f"  Error: {response.data}")

    print("\n" + "=" * 100)
    print("TEST COMPLETED")
    print("=" * 100)

if __name__ == '__main__':
    test_competitor_analysis()
