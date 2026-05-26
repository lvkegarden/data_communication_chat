import requests
import json
import time

print("=" * 80)
print("验证品牌多样性优化效果")
print("=" * 80)

url = "http://localhost:5001/api/chat"
payload = {
    "message": "s5735-l-v2 竞品分析",
    "flag": "n"
}

print(f"\n请求: {url}")
print(f"消息: {payload['message']}")
print(f"Flag: {payload['flag']} (预览模式)")

start_time = time.time()
response = requests.post(url, json=payload)
elapsed = (time.time() - start_time) * 1000

print(f"\nHTTP 状态码: {response.status_code}")
print(f"总耗时: {elapsed:.2f} ms")

if response.status_code == 200:
    data = response.json()
    
    print(f"\n--- 响应内容 ---")
    print(f"响应类型: {type(data)}")
    
    if isinstance(data, str):
        print(f"\n响应是字符串，尝试解析...")
        try:
            data = json.loads(data)
        except:
            print(f"字符串内容: {data[:500]}")
            exit()
    
    preview = data.get('preview', {}) if isinstance(data, dict) else {}
    
    print(f"预览类型: {type(preview)}")
    
    if isinstance(preview, str):
        try:
            preview = json.loads(preview)
        except:
            print(f"预览字符串: {preview[:500]}")
            exit()
    
    intent = preview.get('intent', {}) if isinstance(preview, dict) else {}
    entities = preview.get('entities', {}) if isinstance(preview, dict) else {}
    prompt = preview.get('prompt', '') if isinstance(preview, dict) else ''
    
    print(f"意图: {intent.get('intent') if isinstance(intent, dict) else intent}")
    print(f"产品代码: {entities.get('product_code') if isinstance(entities, dict) else entities}")
    print(f"Prompt长度: {len(prompt)} 字符")
    
    print(f"\n--- 检查 Prompt 中是否包含锐捷竞品 ---")
    if '锐捷' in prompt:
        print("✅ 成功：Prompt 中包含锐捷竞品信息！")
        # 提取锐捷相关的部分
        import re
        ruijie_lines = []
        for line in prompt.split('\n'):
            if '锐捷' in line or 'RG-S' in line:
                ruijie_lines.append(line)
        if ruijie_lines:
            print("\n锐捷竞品信息:")
            for line in ruijie_lines[:10]:
                print(f"  {line[:80]}")
    else:
        print("❌ 失败：Prompt 中没有锐捷竞品信息")
        print("\n--- Prompt 中竞品部分 ---")
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if '竞品' in line or '产品名称' in line or '产品型号' in line:
                print(f"  {i}: {line[:80]}")
else:
    print(f"\n❌ 请求失败: {response.status_code}")
    print(response.text[:500])
