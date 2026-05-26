#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析华为支持网站的产品规格数据
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
print("分析华为支持网站 - 产品规格")
print("=" * 60)

# 华为支持网站通常有更完整的产品规格
support_urls = [
    ("S16700 支持页面", "https://support.huawei.com/enterprise/zh/products/switch/s16700"),
]

for name, url in support_urls:
    print(f"\n{'=' * 60}")
    print(f"分析: {name}")
    print("=" * 60)
    
    try:
        response = session.get(url, timeout=30, allow_redirects=True)
        print(f"最终URL: {response.url}")
        print(f"HTTP 状态: {response.status_code}")
        print(f"页面长度: {len(response.text)}")
        
        # 搜索规格关键词
        keywords = ['交换容量', '包转发', '容量', '端口', 'slot', 'capacity', 'forwarding', 'spec', 'technical']
        
        for kw in keywords:
            matches = list(re.finditer(kw, response.text, re.IGNORECASE))
            if matches:
                print(f"  关键词 '{kw}' 出现 {len(matches)} 次")
                for m in matches[:2]:
                    ctx = response.text[max(0, m.start()-100):m.start()+300]
                    ctx_clean = re.sub(r'<[^>]+>', ' ', ctx)
                    ctx_clean = re.sub(r'\s+', ' ', ctx_clean).strip()
                    print(f"    位置 {m.start()}: ...{ctx_clean[:150]}...")
        
        # 查找彩页 PDF 链接
        brochure_links = re.findall(r'href="([^"]*brochure[^"]*|[^"]*datasheet[^"]*|[^"]*彩页[^"]*)"', response.text, re.IGNORECASE)
        if brochure_links:
            print(f"\n  找到 {len(brochure_links)} 个彩页/规格链接:")
            for link in brochure_links[:5]:
                print(f"    {link[:200]}")
                
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 60)
