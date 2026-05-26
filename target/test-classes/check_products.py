#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from product_naming_parser import ProductNamingParser

fetcher = ProductDataFetcher()
parser = ProductNamingParser()

all_products = fetcher.get_all_products_summary()

print("=" * 80)
print("数据库全部产品统计")
print("=" * 80)
print(f"总产品数: {len(all_products)}")
print()

by_type = {}
by_brand = {}

for product in all_products:
    code = product.get('product_code', '')
    name = product.get('product_name', '')
    
    naming = parser.parse(code)
    product_type = naming.get('product_type', '未知')
    details = naming.get('details', {})
    switch_level = details.get('switch_level', '')
    
    # 提取品牌
    brand = '未知'
    if '华为' in name or (code.startswith('S') and not code.startswith('S6') and not code.startswith('S51') and not code.startswith('S55') and not code.startswith('S50') and not code.startswith('S3')):
        brand = '华为'
    elif '华三' in name or 'H3C' in name or code.startswith('S51') or code.startswith('S55') or code.startswith('S50') or code.startswith('S3') or code.startswith('WX') or code.startswith('S68') or code.startswith('S65'):
        brand = 'H3C'
    elif '锐捷' in name or code.startswith('RG'):
        brand = '锐捷'
    
    if brand not in by_brand:
        by_brand[brand] = []
    by_brand[brand].append(product)
    
    key = f"{product_type}"
    if switch_level:
        key += f" - {switch_level}"
    
    if key not in by_type:
        by_type[key] = []
    by_type[key].append(product)

print("按产品类型分类:")
for key in sorted(by_type.keys()):
    print(f"  {key}: {len(by_type[key])} 个")

print()
print("按品牌分类:")
for brand in sorted(by_brand.keys()):
    print(f"  {brand}: {len(by_brand[brand])} 个")

print()
print("=" * 80)
print("目标产品（接入交换机 + 无线AP）统计:")
print("=" * 80)

target_by_brand = {}
total_target = 0

for product in all_products:
    code = product.get('product_code', '')
    name = product.get('product_name', '')
    
    naming = parser.parse(code)
    product_type = naming.get('product_type', '')
    details = naming.get('details', {})
    switch_level = details.get('switch_level', '')
    
    is_target = False
    if product_type == '无线AP':
        is_target = True
    if product_type == '交换机' and '接入' in switch_level:
        is_target = True
    
    if is_target:
        total_target += 1
        
        brand = '未知'
        if '华为' in name or (code.startswith('S') and not code.startswith('S6') and not code.startswith('S51') and not code.startswith('S55')):
            brand = '华为'
        elif '华三' in name or 'H3C' in name or code.startswith('S51') or code.startswith('S55') or code.startswith('WX'):
            brand = 'H3C'
        elif '锐捷' in name or code.startswith('RG'):
            brand = '锐捷'
        
        if brand not in target_by_brand:
            target_by_brand[brand] = []
        target_by_brand[brand].append(product)

for brand in sorted(target_by_brand.keys()):
    print(f"  {brand}: {len(target_by_brand[brand])} 个")
print(f"  总计: {total_target} 个")

print()
print("目标产品列表示例（前10个）:")
count = 0
for product in all_products:
    if count >= 10:
        break
    code = product.get('product_code', '')
    name = product.get('product_name', '')
    
    naming = parser.parse(code)
    product_type = naming.get('product_type', '')
    details = naming.get('details', {})
    switch_level = details.get('switch_level', '')
    
    is_target = False
    if product_type == '无线AP':
        is_target = True
    if product_type == '交换机' and '接入' in switch_level:
        is_target = True
    
    if is_target:
        print(f"  [{count+1}] {name} ({code})")
        count += 1
