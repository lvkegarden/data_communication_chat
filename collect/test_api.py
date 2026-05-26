import requests
import json

BASE_URL = "http://localhost:8080/api/collect"

print("=" * 60)
print("测试数据采集 API")
print("=" * 60)

print("\n1. 测试统计接口 GET /stats")
r = requests.get(f"{BASE_URL}/stats")
print(f"   Status: {r.status_code}")
print(f"   Data: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")

print("\n2. 测试产品列表接口 GET /products")
r = requests.get(f"{BASE_URL}/products")
print(f"   Status: {r.status_code}")
products = r.json()
print(f"   共有 {len(products)} 个产品")
print("\n   前 10 个产品:")
for i, p in enumerate(products[:10]):
    print(f"   {i+1}. [{p['category']}] {p['product_code']}")
    print(f"      {p['product_name']}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
