#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的华为产品页面分析器
分析产品详情页和规格参数位置
"""

import json
import re
import io
import sys
import traceback
from typing import List, Dict, Any

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_with_browser():
    """使用 Playwright 浏览器分析"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[WARN] Playwright 未安装或浏览器未配置")
        return None
    
    print("=" * 60)
    print("使用 Playwright 分析华为产品页面")
    print("=" * 60)
    
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            switch_url = "https://e.huawei.com/cn/products/switches/"
            print(f"\n访问交换机页面: {switch_url}")
            page.goto(switch_url, wait_until="networkidle", timeout=30000)
            
            print(f"页面标题: {page.title()}")
            
            content = page.content()
            print(f"页面内容长度: {len(content)}")
            
            links = page.query_selector_all("a")
            product_links = []
            
            print(f"\n找到 {len(links)} 个链接，分析产品相关链接...")
            
            keywords = ['系列', '交换机', 'CloudEngine', '彩页', '了解更多', '查看详情']
            model_patterns = [r'S\d{3,4}[-A-Za-z0-9]*', r'CloudEngine\s+S\d{3,4}']
            
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text() or ""
                
                has_keyword = any(k in text for k in keywords)
                has_model = any(re.search(p, text) for p in model_patterns)
                
                if has_keyword or has_model:
                    if href and not href.startswith('#') and not href.startswith('javascript'):
                        if href.startswith('/'):
                            href = "https://e.huawei.com" + href
                        
                        product_links.append({
                            'text': text.strip()[:100],
                            'href': href[:300]
                        })
            
            print(f"\n找到 {len(product_links)} 个产品相关链接:")
            for i, link in enumerate(product_links[:20]):
                print(f"  {i+1}. {link['text'][:50]}")
                print(f"     {link['href']}")
            
            results['switch_links'] = product_links
            
            if product_links:
                print("\n" + "=" * 60)
                print("分析第一个产品链接的详情...")
                print("=" * 60)
                
                first_link = product_links[0]['href']
                if first_link.startswith('http'):
                    try:
                        page.goto(first_link, wait_until="networkidle", timeout=60000)
                        print(f"\n访问详情页: {first_link}")
                        print(f"详情页标题: {page.title()}")
                        
                        detail_content = page.content()
                        
                        spec_keywords = [
                            '参数', '规格', '技术', '性能', '接口', '端口',
                            '电源', '尺寸', '重量', 'Spec', 'spec', 'parameter'
                        ]
                        
                        spec_tables = []
                        tables = page.query_selector_all("table")
                        print(f"\n详情页有 {len(tables)} 个表格")
                        
                        for i, table in enumerate(tables[:10]):
                            table_text = table.inner_text()
                            if any(kw in table_text for kw in spec_keywords):
                                spec_tables.append({
                                    'index': i,
                                    'content': table_text[:1000]
                                })
                                print(f"\n表格 {i+1} (包含规格关键词):")
                                print(table_text[:300])
                        
                        results['detail_page'] = {
                            'url': first_link,
                            'title': page.title(),
                            'spec_tables_count': len(spec_tables),
                            'spec_tables': spec_tables
                        }
                    except Exception as e:
                        print(f"访问详情页出错: {e}")
                        
        except Exception as e:
            print(f"错误: {e}")
            traceback.print_exc()
        
        finally:
            browser.close()
    
    return results

def analyze_with_requests():
    """使用 requests 分析（不需要浏览器）"""
    import requests
    from bs4 import BeautifulSoup
    
    print("=" * 60)
    print("使用 requests 分析华为产品页面")
    print("=" * 60)
    
    results = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        switch_url = "https://e.huawei.com/cn/products/switches/"
        print(f"\n访问交换机页面: {switch_url}")
        
        response = requests.get(switch_url, headers=headers, timeout=30)
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            links = soup.find_all('a')
            product_links = []
            
            keywords = ['系列', '交换机', 'CloudEngine', '彩页', '了解更多']
            model_patterns = [r'S\d{3,4}[-A-Za-z0-9]*', r'CloudEngine\s+S\d{3,4}']
            
            for link in links:
                href = link.get('href') or ''
                text = link.get_text() or ''
                
                has_keyword = any(k in text for k in keywords)
                has_model = any(re.search(p, text) for p in model_patterns)
                
                if has_keyword or has_model:
                    if href and not href.startswith('#'):
                        if href.startswith('/'):
                            href = "https://e.huawei.com" + href
                        
                        product_links.append({
                            'text': text.strip()[:100],
                            'href': href[:300]
                        })
            
            print(f"\n找到 {len(product_links)} 个产品相关链接:")
            for i, link in enumerate(product_links[:20]):
                print(f"  {i+1}. {link['text'][:50]}")
                print(f"     {link['href']}")
            
            results['switch_links'] = product_links
            
            series = []
            patterns = [r'S\d{3,4}[-A-Za-z0-9]*', r'CloudEngine\s+S\d{3,4}[-A-Za-z0-9]*']
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                for match in matches:
                    clean = re.sub(r'CloudEngine\s+', '', match).strip()
                    if len(clean) >= 4 and clean not in series:
                        series.append(clean)
            
            print(f"\n找到 {len(series)} 个产品系列:")
            print(series[:20])
            
            results['series'] = series
            
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()
    
    return results

if __name__ == "__main__":
    try:
        print("\n尝试使用 Playwright 分析...")
        results = analyze_with_browser()
        
        if not results:
            print("\nPlaywright 不可用，使用 requests 分析...")
            results = analyze_with_requests()
        
        print("\n" + "=" * 60)
        print("分析结果摘要:")
        print("=" * 60)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"程序错误: {e}")
        traceback.print_exc()
