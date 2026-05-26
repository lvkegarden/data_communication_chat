#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
深入分析华为产品详情页的技术规格组件
"""

import requests
import re
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

session = requests.Session()
session.headers.update(headers)

print("=" * 60)
print("分析华为产品技术规格组件")
print("=" * 60)

product_url = "https://e.huawei.com/cn/products/switches/campus-switches/s16700"

try:
    response = session.get(product_url, timeout=30)
    html = response.text
    
    # 查找技术规格区域的完整HTML
    spec_start = html.find('pep-technical-specifications')
    if spec_start > 0:
        # 获取规格区域前后5000字符
        spec_region = html[max(0, spec_start-500):spec_start+5000]
        spec_clean = re.sub(r'<[^>]+>', '\n', spec_region)
        spec_clean = re.sub(r'\n\s*\n', '\n', spec_clean)
        spec_clean = re.sub(r'\s+', ' ', spec_clean)
        print(f"\n技术规格区域内容:")
        print(spec_clean[:3000])
    
    # 查找所有 data- 属性中的规格相关值
    print("\n\n查找 data-* 属性中的规格数据...")
    data_attrs = re.findall(r'data-([\w-]+)\s*=\s*["\']([^"\']{50,})["\']', html)
    for attr_name, attr_value in data_attrs:
        if any(kw in attr_value.lower() for kw in ['spec', 'capacity', 'forward', 'port', 'slot', 'power']):
            value_preview = attr_value[:200]
            print(f"  data-{attr_name}: {value_preview}")
    
    # 查找 window.__INITIAL_DATA__ 或类似的初始数据
    print("\n\n查找初始数据...")
    init_patterns = [
        r'window\.__([\w]+)__\s*=\s*({[^;]+});',
        r'var\s+([\w]+)\s*=\s*JSON\.parse\(([^)]+)\)',
        r'__NUXT__\s*=\s*({[^;]+});',
    ]
    for pattern in init_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f"  模式 '{pattern[:40]}' 找到 {len(matches)} 个匹配")
            for m in matches[:3]:
                content = str(m)[:500]
                print(f"    {content}")
    
    # 查找 API 调用
    print("\n\n查找 API 调用 URL...")
    api_patterns = [
        r'"/api/[^"]*"',
        r'url:\s*["\'](/[^"\']+)["\']',
        r'fetch\(["\'](/[^"\']+)["\']',
        r'axios\.[\w]+\(["\'](/[^"\']+)["\']',
        r'baseURL\s*[=:]\s*["\']([^"\']+)["\']',
    ]
    for pattern in api_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"  模式 '{pattern[:40]}' 找到 {len(matches)} 个API:")
            unique_apis = list(set(matches))
            for api in unique_apis[:20]:
                print(f"    {api[:200]}")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
