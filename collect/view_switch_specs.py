#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8080/api/collect"

r = requests.get(f"{BASE_URL}/products")
products = r.json()

switch_products = [p for p in products if p['category'] == '交换机']
print(f"共有 {len(switch_products)} 个交换机产品")

for p in switch_products:
    detail = requests.get(f"{BASE_URL}/products/{p['id']}").json()
    specs = detail.get('specs', {})
    print(f"\n{'=' * 60}")
    print(f"产品: {p['product_code']} - {p['product_name']}")
    print(f"{'=' * 60}")
    for key, value in specs.items():
        print(f"  {key}: {value}")

# 统计所有规格字段
all_keys = set()
for p in switch_products:
    detail = requests.get(f"{BASE_URL}/products/{p['id']}").json()
    specs = detail.get('specs', {})
    all_keys.update(specs.keys())

print(f"\n\n{'=' * 60}")
print("当前已抓取的规格字段统计:")
print(f"{'=' * 60}")
print(f"共有 {len(all_keys)} 个规格字段:")
for key in sorted(all_keys):
    print(f"  - {key}")
