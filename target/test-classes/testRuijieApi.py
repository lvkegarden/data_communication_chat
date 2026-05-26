import sys
import io
import json
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.ruijie.com.cn/cp/jh-all/',
}

session = requests.Session()
session.headers.update(headers)

print('=' * 80)
print('测试锐捷产品列表 API')
print('=' * 80)

api_url = 'https://www.ruijie.com.cn/application/api/product/getGoodsList'

# 从 jh-all 页面获取的分类ID
cat_id = '433108860989088000'

# 先获取第 1 页
print('\n--- 测试第 1 页 ---')
params = {
    'page': 1,
    'limit': 12,
    'classId': cat_id,
    'order': 2,
    'orderField': '',
    'screenValueIds': '',
}

try:
    resp = session.get(api_url, params=params, timeout=15)
    print(f'状态码: {resp.status_code}')
    data = resp.json()
    print(f'响应: {json.dumps(data, ensure_ascii=False, indent=2)[:2000]}')
    
    if data.get('code') == 200:
        total = data.get('data', {}).get('total', 0)
        items = data.get('data', {}).get('list', [])
        print(f'\n总商品数: {total}')
        print(f'本页商品数: {len(items)}')
        print(f'\n第 1 页商品:')
        for i, item in enumerate(items):
            print(f'  {i+1}. {item.get("modeName")} - {item.get("name")}')
            print(f'     URL: {item.get("linkUrl") or item.get("rootlist")}')

except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()

# 测试第 2 页
print('\n' + '=' * 80)
print('--- 测试第 2 页 ---')
params['page'] = 2

try:
    resp = session.get(api_url, params=params, timeout=15)
    data = resp.json()
    
    if data.get('code') == 200:
        items = data.get('data', {}).get('list', [])
        print(f'第 2 页商品数: {len(items)}')
        print(f'\n第 2 页商品:')
        for i, item in enumerate(items):
            print(f'  {i+1}. {item.get("modeName")} - {item.get("name")}')

except Exception as e:
    print(f'错误: {e}')

# 测试第 5 页
print('\n' + '=' * 80)
print('--- 测试第 5 页 ---')
params['page'] = 5

try:
    resp = session.get(api_url, params=params, timeout=15)
    data = resp.json()
    
    if data.get('code') == 200:
        items = data.get('data', {}).get('list', [])
        print(f'第 5 页商品数: {len(items)}')
        if items:
            print(f'\n第 5 页商品:')
            for i, item in enumerate(items):
                print(f'  {i+1}. {item.get("modeName")} - {item.get("name")}')
        else:
            print('  没有商品（说明已到最后一页）')

except Exception as e:
    print(f'错误: {e}')

print('\n' + '=' * 80)
print('--- 遍历所有子分类测试 ---')
print('=' * 80)

# 测试各个子分类
subcategories = [
    ("园区网交换机", "433108861000622336"),
    ("数据中心交换机", "433108860996952320"),
    ("行业精选交换机", "433108861012156672"),
    ("工业交换机", "433108861010321664"),
    ("SDN", "433108860994855168"),
    ("配件", "433108861013729536"),
]

for name, cid in subcategories:
    print(f'\n--- {name} (ID: {cid}) ---')
    params['page'] = 1
    params['classId'] = cid
    
    try:
        resp = session.get(api_url, params=params, timeout=15)
        data = resp.json()
        
        if data.get('code') == 200:
            total = data.get('data', {}).get('total', 0)
            pages = (total + 11) // 12
            items = data.get('data', {}).get('list', [])
            print(f'  总商品数: {total}')
            print(f'  总页数: {pages}')
            print(f'  第1页商品: {len(items)} 个')
            if items:
                print(f'  前3个: {[i.get("modeName") for i in items[:3]]}')
        else:
            print(f'  API 错误: {data}')
            
    except Exception as e:
        print(f'  错误: {e}')
