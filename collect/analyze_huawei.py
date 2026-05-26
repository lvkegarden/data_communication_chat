import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

urls = [
    ("交换机", "https://e.huawei.com/cn/products/switches/"),
    ("无线", "https://e.huawei.com/cn/products/wlan/")
]

def extract_hrefs(html):
    hrefs = []
    pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    for href, text in matches:
        text = re.sub(r'<[^>]+>', '', text).strip()
        if text and len(text) > 1 and len(text) < 100:
            hrefs.append((text[:60], href[:100]))
    return hrefs

for name, url in urls:
    print(f"\n{'=' * 80}")
    print(f"分析: {name} - {url}")
    print(f"{'=' * 80}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.content)} 字节")
        
        html = response.text
        
        print("\n--- 1. 查找所有 href 链接 (包含 'product' 或 型号) ---")
        all_hrefs = extract_hrefs(html)
        
        product_hrefs = []
        for text, href in all_hrefs:
            if ('product' in href.lower() or 
                '/cn/' in href.lower() or
                re.search(r'S\d{3,4}', text) or
                re.search(r'AP\d{3,4}', text) or
                '系列' in text or
                '交换机' in text or
                '无线' in text):
                product_hrefs.append((text, href))
        
        print(f"找到 {len(product_hrefs)} 个潜在产品链接:")
        for text, href in product_hrefs[:30]:
            print(f"  [{text}] -> {href}")
        
        print("\n--- 2. 查找产品型号 ---")
        patterns = [
            (r'S\d{3,4}-?[A-Za-z0-9-]*', '交换机型号'),
            (r'AP\d{3,4}-?[A-Za-z0-9-]*', 'AP型号'),
            (r'AC\d{3,4}-?[A-Za-z0-9-]*', 'AC控制器型号'),
        ]
        
        for pattern, label in patterns:
            matches = re.findall(pattern, html)
            if matches:
                unique = sorted(list(set(matches)))[:30]
                print(f"\n  {label} ({len(unique)}个): {unique}")
        
        print("\n--- 3. 查找 JSON 数据块 ---")
        json_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;',
            r'var\s+\w+Data\s*=\s*(\[.*?\])\s*;',
            r'"products"\s*:\s*(\[.*?\])',
            r'"productList"\s*:\s*(\[.*?\])',
        ]
        
        for i, pattern in enumerate(json_patterns):
            match = re.search(pattern, html, re.DOTALL)
            if match:
                print(f"\n  找到 JSON 数据块 #{i+1}")
                try:
                    data = json.loads(match.group(1))
                    print(f"  类型: {type(data)}")
                    if isinstance(data, list):
                        print(f"  长度: {len(data)}")
                        if len(data) > 0:
                            print(f"  第一项: {str(data[0])[:200]}")
                    elif isinstance(data, dict):
                        print(f"  键: {list(data.keys())[:20]}")
                except:
                    pass
        
        print("\n--- 4. 查找内联脚本中的数据 ---")
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html, re.DOTALL)
        print(f"找到 {len(scripts)} 个 script 标签")
        
        for i, script in enumerate(scripts[:10]):
            if ('product' in script.lower() or 
                'S57' in script or 'S67' in script or 'AP6' in script):
                print(f"\n  Script #{i} 包含产品关键词:")
                print(f"  长度: {len(script)} 字符")
                lines = script.split('\n')
                for j, line in enumerate(lines[:10]):
                    if ('product' in line.lower() or 
                        'S57' in line or 'S67' in line or 'AP6' in line):
                        print(f"    {j}: {line[:150]}")
        
        print("\n--- 5. 保存 HTML 样本 (前 5000 字符) ---")
        print(html[:5000])
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
