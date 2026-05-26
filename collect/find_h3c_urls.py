import requests

# 测试各种可能的URL
test_urls = [
    'https://www.h3c.com/cn/Products_and_Solutions/Products/Switches/',
    'https://www.h3c.com/cn/Product_And_Solution/Switches/',
    'https://www.h3c.com/cn/Products/Enterprise/Switches/',
    'https://www.h3c.com/cn/Product/SDN_Switch/',
    'https://www.h3c.com/cn/Products_and_Solutions/Products/Switches/SDN_Switch/',
    'https://www.h3c.com/cn/Product/Products/Enterprise/SDN/SDN_Switch/',
    'https://www.h3c.com/cn/products/switches/',
    'https://www.h3c.com/cn/Product/Switches/',
    'https://www.h3c.com/cn/products/wlan/',
    'https://www.h3c.com/cn/Product/WLAN/',
    'https://www.h3c.com/cn/products/switches/campus-switches/',
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

print("测试华三网站URL:\n")
for url in test_urls:
    try:
        response = session.get(url, timeout=15)
        status = response.status_code
        has_products = status == 200 and len(response.text) > 50000 and 'S' in response.text[:10000]
        status_str = f"{status} {'[可能正确]' if has_products else ''}"
        print(f"{url}: {status_str}")
    except Exception as e:
        print(f"{url}: 错误 - {e}")
