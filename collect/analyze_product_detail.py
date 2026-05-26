#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
深入分析华为单个产品详情页，找到核心规格参数
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
print("分析华为产品详情页 - S16700")
print("=" * 60)

product_url = "https://e.huawei.com/cn/products/switches/campus-switches/s16700"

try:
    response = session.get(product_url, timeout=30)
    html = response.text
    
    print(f"页面长度: {len(html)}")
    
    keywords = ['交换容量', '转发', '容量', 'capacity', 'forwarding', 'spec', '规格', '参数', '性能']
    
    for kw in keywords:
        matches = list(re.finditer(kw, html, re.IGNORECASE))
        if matches:
            print(f"\n关键词 '{kw}' 出现 {len(matches)} 次")
            for m in matches[:3]:
                ctx = html[max(0, m.start()-100):m.start()+300]
                ctx_clean = re.sub(r'<[^>]+>', ' ', ctx)
                ctx_clean = re.sub(r'\s+', ' ', ctx_clean).strip()
                print(f"  位置 {m.start()}: ...{ctx_clean[:200]}...")
    
    # 查找包含规格数据的 JSON 结构
    spec_json_patterns = [
        r'"spec[^"]*"\s*:\s*"[^"]*"',
        r'"capacity[^"]*"\s*:\s*"[^"]*"',
        r'"forwarding[^"]*"\s*:\s*"[^"]*"',
        r'"productSpec[^"]*"\s*:\s*\{[^}]*\}',
        r'"technical[^"]*"\s*:\s*"[^"]*"',
    ]
    
    print("\n\n查找 JSON 规格数据...")
    for pattern in spec_json_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"\n  模式 '{pattern[:30]}' 找到 {len(matches)} 个匹配:")
            for m in matches[:5]:
                print(f"    {m[:150]}")
    
    # 查找彩页链接
    print("\n\n查找彩页链接...")
    brochure_links = re.findall(r'href="([^"]*彩页[^"]*|[^"]*brochure[^"]*|[^"]*datasheet[^"]*\.pdf[^"]*)"', html, re.IGNORECASE)
    if brochure_links:
        for link in brochure_links[:10]:
            print(f"  彩页链接: {link[:200]}")
    
    # 查找产品概览/技术规格区域
    print("\n\n查找产品规格相关区域...")
    spec_sections = re.findall(r'<div[^>]*class="[^"]*spec[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if spec_sections:
        print(f"  找到 {len(spec_sections)} 个 spec 区域")
        for i, section in enumerate(spec_sections[:3]):
            section_clean = re.sub(r'<[^>]+>', ' ', section)
            section_clean = re.sub(r'\s+', ' ', section_clean).strip()
            print(f"  区域 {i}: {section_clean[:300]}")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
