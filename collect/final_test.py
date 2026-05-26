import requests
import json
import time

# Clear log file
log_file = 'collect/final_test.log'
try:
    os.remove(log_file)
except:
    pass

import os

BASE_URL = "http://localhost:8080/api/collect"

print("开始采集华为数据...")
response = requests.post(f"{BASE_URL}/huawei", timeout=180)
result = response.json()

print(f"\n采集结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

# Check stats
time.sleep(1)
stats = requests.get(f"{BASE_URL}/stats").json()
print(f"\n数据库统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

# Check products
products = requests.get(f"{BASE_URL}/products").json()
print(f"\n产品数量: {len(products)}")

# Log summary
switch_count = sum(1 for p in products if p.get('category') == '交换机')
wlan_count = sum(1 for p in products if p.get('category') == '无线')
with_desc = sum(1 for p in products if p.get('description') and len(p.get('description', '')) > 30)

print(f"\n统计:")
print(f"  交换机: {switch_count}")
print(f"  无线AP: {wlan_count}")
print(f"  有描述: {with_desc}")

# Show sample products
print(f"\n交换机样本:")
for p in [x for x in products if x.get('category') == '交换机'][:3]:
    print(f"  - {p.get('product_code')}")
    print(f"    描述长度: {len(p.get('description', ''))}")
    print(f"    规格数: {len(p.get('specs', {}))}")

print(f"\n无线AP样本:")
for p in [x for x in products if x.get('category') == '无线'][:3]:
    print(f"  - {p.get('product_code')}")
    print(f"    描述长度: {len(p.get('description', ''))}")
    print(f"    规格数: {len(p.get('specs', {}))}")
