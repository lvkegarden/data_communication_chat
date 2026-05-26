#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析华为产品页面，找到核心规格参数的位置
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
print("分析华为交换机产品页面")
print("=" * 60)

urls_to_analyze = [
    ("交换机首页", "https://e.huawei.com/cn/products/switches/"),
    ("园区交换机", "https://e.huawei.com/cn/products/switches/campus-switches"),
]

for name, url in urls_to_analyze:
    print(f"\n{'=' * 60}")
    print(f"分析: {name} - {url}")
    print("=" * 60)
    
    try:
        response = session.get(url, timeout=30)
        html = response.text
        
        print(f"页面长度: {len(html)}")
        
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        print(f"找到 {len(script_tags)} 个 script 标签")
        
        for i, script in enumerate(script_tags):
            if len(script) > 500:
                if 'spec' in script.lower() or '规格' in script or '参数' in script or 'capacity' in script.lower():
                    print(f"\n  Script {i} 可能包含规格数据 (长度: {len(script)})")
                    print(f"  内容预览: {script[:300]}...")
        
        json_patterns = [
            r'var\s+\w+\s*=\s*({.*?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'__NUXT__\s*=\s*({.*?});',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                print(f"\n  找到 JSON 数据 (模式: {pattern[:30]})")
                for j, match in enumerate(matches[:3]):
                    if len(match) > 100:
                        print(f"    匹配 {j}: 长度 {len(match)}")
                        print(f"    内容: {match[:500]}...")
        
        keywords = ['S16700', 'CloudEngine', '交换容量', '转发性能', 'spec', 'capacity']
        for kw in keywords:
            count = len(re.findall(kw, html, re.IGNORECASE))
            if count > 0:
                print(f"  关键词 '{kw}' 出现 {count} 次")
                
                positions = [(m.start(), html[m.start()-50:m.start()+200]) for m in re.finditer(kw, html, re.IGNORECASE)]
                for pos, ctx in positions[:3]:
                    ctx_clean = re.sub(r'<[^>]+>', ' ', ctx)
                    ctx_clean = re.sub(r'\s+', ' ', ctx_clean).strip()
                    print(f"    位置 {pos}: ...{ctx_clean}...")
        
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 60)
print("分析完成")
print("=" * 60)
