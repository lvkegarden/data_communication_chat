#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试产品规格参数抓取和展示
"""

import requests
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8080/api/collect"

def main():
    print("=" * 60)
    print("测试产品规格参数抓取和展示")
    print("=" * 60)
    
    print("\n1. 获取产品列表...")
    r = requests.get(f"{BASE_URL}/products")
    products = r.json()
    print(f"   共有 {len(products)} 个产品")
    
    print("\n2. 查看产品统计...")
    r = requests.get(f"{BASE_URL}/stats")
    stats = r.json()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n3. 查看第一个产品的完整规格...")
    if products:
        first = products[0]
        r = requests.get(f"{BASE_URL}/products/{first['id']}")
        detail = r.json()
        
        print(f"\n   产品: {detail.get('product_name', '-')}")
        print(f"   型号: {detail.get('product_code', '-')}")
        print(f"   系列: {detail.get('series', '-')}")
        print(f"   分类: {detail.get('category', '-')}")
        
        specs = detail.get('specs', {})
        if specs:
            print(f"\n   规格参数 ({len(specs)} 个):")
            print("   " + "-" * 40)
            for key, value in specs.items():
                print(f"   {key}: {value}")
        
        links = detail.get('links', [])
        if links:
            print(f"\n   相关链接 ({len(links)} 个):")
            print("   " + "-" * 40)
            for link in links:
                print(f"   [{link.get('type', '-')}] {link.get('title', '-')[:50]}")
                print(f"      {link.get('url', '-')[:80]}")
    
    print("\n4. 查看交换机产品的规格...")
    switch_products = [p for p in products if p.get('category') == '交换机']
    print(f"   交换机产品: {len(switch_products)} 个")
    
    if switch_products:
        for p in switch_products[:3]:
            r = requests.get(f"{BASE_URL}/products/{p['id']}")
            detail = r.json()
            specs = detail.get('specs', {})
            print(f"\n   {p['product_code']} 的规格:")
            for key in ['产品定位', '适用场景', '品牌', '系列', '产品类型']:
                if key in specs:
                    print(f"     {key}: {specs[key]}")
    
    print("\n5. 查看无线产品的规格...")
    wlan_products = [p for p in products if p.get('category') == '无线']
    print(f"   无线产品: {len(wlan_products)} 个")
    
    if wlan_products:
        for p in wlan_products[:3]:
            r = requests.get(f"{BASE_URL}/products/{p['id']}")
            detail = r.json()
            specs = detail.get('specs', {})
            print(f"\n   {p['product_code']} 的规格:")
            for key in ['产品类型', '适用场景', '品牌', '系列']:
                if key in specs:
                    print(f"     {key}: {specs[key]}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
