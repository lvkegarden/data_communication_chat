import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'd:/project/ai/localrest/collect')

from ruijie_scraper import RuijieScraper

print('=' * 80)
print('测试锐捷 API 分页采集')
print('=' * 80)

scraper = RuijieScraper()

print('\n--- 测试交换机采集 ---')
switch_products = scraper.scrape_switch_products()

print(f'\n交换机采集结果: {len(switch_products)} 个')
if switch_products:
    print(f'\n前 10 个产品:')
    for i, p in enumerate(switch_products[:10], 1):
        print(f'  {i}. {p.product_code} - {p.series}')

print('\n--- 测试无线采集 ---')
wlan_products = scraper.scrape_wlan_products()

print(f'\n无线采集结果: {len(wlan_products)} 个')
if wlan_products:
    print(f'\n前 10 个产品:')
    for i, p in enumerate(wlan_products[:10], 1):
        print(f'  {i}. {p.product_code} - {p.series}')

print('\n' + '=' * 80)
print('采集汇总')
print('=' * 80)
print(f'交换机: {len(switch_products)} 个')
print(f'无线: {len(wlan_products)} 个')
print(f'总计: {len(switch_products) + len(wlan_products)} 个')
