import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'd:/project/ai/localrest/collect')

from h3c_scraper import H3CScraper

print('=' * 80)
print('华三采集器修复测试')
print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 80)

scraper = H3CScraper()

print('\n--- 采集交换机产品 ---')
switch_products = scraper.scrape_switch_products()
print(f'交换机采集结果: {len(switch_products)} 个产品')

if switch_products:
    print(f'\n交换机前 10 个产品:')
    for i, p in enumerate(switch_products[:10], 1):
        print(f'  {i}. {p.product_code} - 系列: {p.series}')

print('\n--- 采集无线产品 ---')
wlan_products = scraper.scrape_wlan_products()
print(f'无线采集结果: {len(wlan_products)} 个产品')

if wlan_products:
    print(f'\n无线前 10 个产品:')
    for i, p in enumerate(wlan_products[:10], 1):
        print(f'  {i}. {p.product_code} - 系列: {p.series}')

print('\n' + '=' * 80)
print('采集汇总')
print('=' * 80)
print(f'交换机: {len(switch_products)} 个')
print(f'无线: {len(wlan_products)} 个')
print(f'总计: {len(switch_products) + len(wlan_products)} 个')
print(f'完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
