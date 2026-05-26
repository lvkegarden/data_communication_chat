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
        try:
            data = json.loads(data)
        except:
            print(f"字符串内容: {data[:500]}")
            exit()
    
    preview = data.get('preview', '')
    
    print(f"预览类型: {type(preview)}")
    
    preview_data = None
    if isinstance(preview, str):
        try:
            preview_data = json.loads(preview)
        except:
            print(f"预览字符串: {preview[:500]}")
            exit()
    elif isinstance(preview, dict):
        preview_data = preview
    
    if not preview_data:
        print("无法解析预览数据")
        exit()
    
    print(f"\n--- 预览数据 ---")
    intent = preview_data.get('intent', {})
    competitor_data = preview_data.get('competitor_data', [])
    
    print(f"意图: {intent.get('intent') if isinstance(intent, dict) else intent}")
    
    print(f"\n--- 竞品列表 ---")
    if competitor_data:
        for i, comp in enumerate(competitor_data, 1):
            name = comp.get('product_name', '未知')
            code = comp.get('product_code', '未知')
            print(f"  {i}. {name} ({code})")
    else:
        print("  没有竞品数据")
    
    print(f"\n--- 检查竞品品牌多样性 ---")
    brands = []
    for comp in competitor_data:
        name = comp.get('product_name', '')
        code = comp.get('product_code', '')
        
        brand = '未知'
        if name.startswith('华三') or name.startswith('H3C') or code.startswith('S'):
            brand = 'H3C'
        elif name.startswith('锐捷') or code.startswith('RG'):
            brand = '锐捷'
        elif name.startswith('华为'):
            brand = '华为'
        
        brands.append(brand)
        print(f"  {len(brands)}. {name} - 品牌: {brand}")
    
    unique_brands = set(brands)
    print(f"\n品牌列表: {brands}")
    print(f"不同品牌数: {len(unique_brands)}")
    
    if len(unique_brands) > 1:
        print("\n[OK] 品牌多样性优化成功！竞品来自不同品牌。")
    else:
        print(f"\n[INFO] 所有竞品都来自同一品牌: {list(unique_brands)[0]}")
else:
    print(f"\n请求失败: {response.status_code}")
    print(response.text[:500])
