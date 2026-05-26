import sys
import io
import re
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

subcategories = [
    ("园区网交换机", "https://www.ruijie.com.cn/cp/jh-yqw/"),
    ("数据中心交换机", "https://www.ruijie.com.cn/cp/jh-shjzhx/"),
    ("行业精选交换机", "https://www.ruijie.com.cn/cp/jh-zxwljj/"),
    ("工业交换机", "https://www.ruijie.com.cn/cp/jh-gyjh/"),
]

def analyze_subcategory(page, subcat_name, url):
    print('=' * 80)
    print(f'子分类: {subcat_name}')
    print(f'URL: {url}')
    print('=' * 80)
    
    page.goto(url, timeout=30000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    print(f'\n页面大小: {len(html)} 字节')
    
    pagination_selectors = [
        'div.pagination',
        '.pagination',
        '.pager',
        '.page-nav',
        '[class*="pagination"]',
        '[class*="pager"]',
    ]
    
    print(f'\n--- 分页元素 ---')
    pagination_found = False
    for selector in pagination_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            pagination_found = True
            print(f'选择器 {selector}: 找到 {len(elements)} 个元素')
            for i, elem in enumerate(elements[:3]):
                links = elem.query_selector_all('a[href]')
                print(f'  元素[{i}] 链接数: {len(links)}')
                for j, link in enumerate(links[:10]):
                    text = link.inner_text().strip()
                    href = link.get_attribute('href')
                    print(f'    [{j}] "{text}" -> {href}')
    
    print(f'\n--- 产品卡片数量 ---')
    product_selectors = [
        'div[class*="product"]',
        'div[class*="Product"]',
        'div[class*="card"]',
        'div[class*="Card"]',
        'article',
        'section[class*="product"]',
    ]
    
    all_products = set()
    for selector in product_selectors:
        elements = page.query_selector_all(selector)
        for elem in elements:
            text = elem.inner_text()
            if 'RG-' in text:
                model_match = re.search(r'(RG-[A-Z0-9\-]+)', text)
                if model_match:
                    model = model_match.group(1)
                    all_products.add(model)
    
    print(f'找到 {len(all_products)} 个唯一产品型号')
    print(f'型号列表: {sorted(all_products)[:20]}')
    
    return pagination_found, len(all_products)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    try:
        for subcat_name, url in subcategories:
            pagination_found, product_count = analyze_subcategory(page, subcat_name, url)
            
            if pagination_found:
                print(f'\n--- 尝试翻页测试 ---')
                page.goto(url, timeout=30000)
                page.wait_for_timeout(2000)
                
                page_products = set()
                for page_num in range(1, 6):
                    print(f'\n测试第 {page_num} 页...')
                    
                    products_on_page = set()
                    for selector in ['div[class*="product"]', 'div[class*="card"]']:
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            text = elem.inner_text()
                            model_match = re.search(r'(RG-[A-Z0-9\-]+)', text)
                            if model_match:
                                products_on_page.add(model_match.group(1))
                    
                    print(f'  本页产品数: {len(products_on_page)}')
                    new_products = products_on_page - page_products
                    print(f'  新增加产品: {len(new_products)} 个')
                    page_products.update(products_on_page)
                    
                    next_buttons = page.query_selector_all('a:has-text("下一页"), a:has-text(">"), li.next a, .pagination a:has-text(">")')
                    if not next_buttons:
                        next_buttons = page.query_selector_all('.pagination a')
                        if len(next_buttons) > 1:
                            next_buttons = [next_buttons[-1]]
                    
                    if next_buttons:
                        print(f'  找到下一页按钮，尝试点击...')
                        try:
                            next_buttons[0].click()
                            page.wait_for_timeout(2000)
                        except Exception as e:
                            print(f'  点击失败: {e}')
                            break
                    else:
                        print(f'  未找到下一页按钮')
                        break
                
                print(f'\n翻页累计产品数: {len(page_products)}')
    finally:
        browser.close()
