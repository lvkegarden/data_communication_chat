import requests
import json
import time

url = "http://localhost:5001/api/chat"

def test_product_intro_preview_and_submit():
    print("=" * 60)
    print("测试: 产品介绍 - 预览 + 发送")
    print("=" * 60)
    
    # Step 1: 预览 (flag=n)
    print("\n[Step 1] 发送预览请求 (flag=n)")
    payload = {
        "session_id": "test_preview_flow",
        "message": "请为RG-AP820C生成产品介绍",
        "flag": "n"
    }
    
    start = time.time()
    resp = requests.post(url, json=payload, timeout=90)
    print(f"响应时间: {time.time()-start:.2f}s")
    data = resp.json()
    print(f"响应状态: {data.get('success')}")
    print(f"消息内容: '{data.get('message', '')}'")
    
    if data.get('preview'):
        preview = json.loads(data['preview'])
        print(f"\n预览报文包含:")
        print(f"  - session_id: {preview.get('session_id')}")
        print(f"  - message: {preview.get('message')}")
        print(f"  - flag: {preview.get('flag')}")
        
        if preview.get('intent'):
            intent = preview['intent']
            print(f"  - intent: {intent.get('intent')}")
            print(f"  - confidence: {intent.get('confidence')}")
            print(f"  - routed_to: {intent.get('routed_to')}")
        
        if preview.get('product_data'):
            pd = preview['product_data']
            print(f"  - product_code: {pd.get('product_code')}")
            print(f"  - product_name: {pd.get('product_name')}")
            print(f"  - category: {pd.get('category')}")
        
        if preview.get('api_request') and preview['api_request'].get('messages'):
            msgs = preview['api_request']['messages']
            print(f"\n[发送给大模型的messages]:")
            for msg in msgs:
                role = msg.get('role')
                content = msg.get('content', '')
                print(f"  [{role}] (length: {len(content)} chars)")
                if role == 'user':
                    print(f"    内容预览: {content[:200]}...")
    else:
        print("预览为空!")
    
    # Step 2: 发送 (flag=y)
    print("\n" + "-" * 60)
    print("[Step 2] 发送真实请求 (flag=y)")
    
    payload['flag'] = 'y'
    start = time.time()
    resp = requests.post(url, json=payload, timeout=90)
    print(f"响应时间: {time.time()-start:.2f}s")
    data = resp.json()
    print(f"响应状态: {data.get('success')}")
    
    if data.get('success'):
        msg = data.get('message', '')
        print(f"响应消息长度: {len(msg)} chars")
        print(f"响应消息:\n{msg[:500]}...")
    
    if data.get('prompt'):
        print(f"\n[Prompt内容预览]:")
        print(f"{data['prompt'][:300]}...")


def test_product_query_preview():
    print("\n" + "=" * 60)
    print("测试: 产品查询 - 预览")
    print("=" * 60)
    
    payload = {
        "session_id": "test_query_preview",
        "message": "查询产品 RG-AP820",
        "flag": "n"
    }
    
    start = time.time()
    resp = requests.post(url, json=payload, timeout=90)
    print(f"响应时间: {time.time()-start:.2f}s")
    data = resp.json()
    
    if data.get('preview'):
        preview = json.loads(data['preview'])
        if preview.get('intent'):
            print(f"识别意图: {preview['intent'].get('intent')}")
        if preview.get('api_request') and preview['api_request'].get('messages'):
            msgs = preview['api_request']['messages']
            for msg in msgs:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    print(f"\nPrompt长度: {len(content)} chars")
                    print(f"Prompt预览:\n{content[:300]}...")
    else:
        print("预览为空!")


def test_greeting():
    print("\n" + "=" * 60)
    print("测试: 问候")
    print("=" * 60)
    
    payload = {
        "session_id": "test_greet",
        "message": "你好",
        "flag": "y"
    }
    
    start = time.time()
    resp = requests.post(url, json=payload, timeout=90)
    print(f"响应时间: {time.time()-start:.2f}s")
    data = resp.json()
    print(f"响应: {data.get('message', '')}")
    if data.get('intent'):
        print(f"意图: {data['intent'].get('intent')}")


if __name__ == "__main__":
    test_greeting()
    test_product_intro_preview_and_submit()
    test_product_query_preview()
    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
