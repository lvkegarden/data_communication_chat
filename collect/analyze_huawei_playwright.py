#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用 Playwright 分析华为产品页面结构
"""

import json
import re
from playwright.sync_api import sync_playwright

def analyze_campus_switches():
    """分析园区交换机产品列表"""
    print("=" * 60)
    print("分析园区交换机页面...")
    print("=" * 60)
    
    url = "https://e.huawei.com/cn/products/switches/campus-switches"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"访问: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        print("\n页面标题:", page.title())
        
        products = []
        
        links = page.query_selector_all("a")
        print(f"\n找到 {len(links)} 个链接")
        
        product_keywords = ['S16700', 'S12700', 'S8700', 'S7700', 'S6730', 'S5735', 'S5731', 'S5755']
        
        for link in links:
            href = link.get_attribute("href") or ""
            text = link.inner_text() or ""
            
            for keyword in product_keywords:
                if keyword in text or keyword in href:
                    print(f"\n找到产品链接: {keyword}")
                    print(f"  文本: {text[:200]}")
                    print(f"  href: {href}")
                    products.append({
                        'keyword': keyword,
                        'text': text,
                        'href': href
                    })
                    break
        
        browser.close()
        return products

def analyze_product_detail(product_url):
    """分析产品详情页"""
    print("\n" + "=" * 60)
    print(f"分析产品详情页: {product_url}")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(product_url, wait_until="networkidle", timeout=60000)
        
        print("\n页面标题:", page.title())
        
        title = page.title()
        
        specs = []
        
        spec_patterns = [
            'spec', 'Spec', '参数', '规格', '技术', '特性',
            '性能', '接口', '端口', '电源', '尺寸', '重量'
        ]
        
        tables = page.query_selector_all("table")
        print(f"\n找到 {len(tables)} 个表格")
        
        for i, table in enumerate(tables[:10]):
            text = table.inner_text()
            if any(p in text for p in spec_patterns):
                print(f"\n表格 {i+1} (可能包含规格):")
                print(text[:500])
                specs.append({
                    'index': i,
                    'text': text[:2000]
                })
        
        headings = page.query_selector_all("h1, h2, h3, h4")
        print(f"\n找到 {len(headings)} 个标题:")
        for heading in headings:
            text = heading.inner_text()
            if any(p in text for p in spec_patterns):
                print(f"  - {text}")
        
        dl_elements = page.query_selector_all("dl")
        print(f"\n找到 {len(dl_elements)} 个定义列表")
        for dl in dl_elements:
            text = dl.inner_text()
            if any(p in text for p in spec_patterns):
                print(f"\n定义列表 (可能包含规格):")
                print(text[:500])
        
        browser.close()
        
        return {
            'title': title,
            'specs': specs
        }

if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    try:
        products = analyze_campus_switches()
        
        if products:
            print(f"\n共找到 {len(products)} 个相关产品链接")
            print(json.dumps(products, ensure_ascii=False, indent=2))
            
            for product in products[:3]:
                href = product.get('href', '')
                if href and href.startswith('http'):
                    detail = analyze_product_detail(href)
                    print(f"\n产品 {product['keyword']} 详情:")
                    print(json.dumps(detail, ensure_ascii=False, indent=2))
        else:
            print("\n未找到产品链接，可能需要深入分析页面结构")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://e.huawei.com/cn/products/switches/campus-switches", 
                         wait_until="networkidle", timeout=30000)
                
                content = page.content()
                print(f"\n页面内容长度: {len(content)}")
                
                patterns = [r'S\d{3,4}[-A-Za-z0-9]*', r'CloudEngine\s+S\d{3,4}[-A-Za-z0-9]*']
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    unique_matches = list(set(matches))
                    print(f"\n模式 '{pattern}' 找到 {len(unique_matches)} 个匹配:")
                    print(unique_matches[:20])
                
                browser.close()
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
