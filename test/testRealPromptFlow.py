import sys
import json
sys.path.insert(0, 'd:/project/ai/localrest/python')

from product_data_fetcher import ProductDataFetcher
from prompt_assembler import PromptAssembler

data_fetcher = ProductDataFetcher()

print('=' * 80)
print('测试1：查询实际存在的产品详情')
print('=' * 80)

# 先获取一个实际存在的产品
products = data_fetcher.search_products('S5735')
if products:
    first_product = products[0]
    product_code = first_product.get('product_code')
    print(f'实际存在的产品型号: {product_code}')
    print(f'产品名称: {first_product.get("product_name")}')
    
    # 获取完整产品详情
    print(f'\n--- 获取完整产品详情 ---')
    product_detail = data_fetcher.get_product_by_code(product_code)
    
    if product_detail:
        print(f'\nAPI 返回的产品详情字段:')
        for key, value in product_detail.items():
            if value:
                val_len = len(str(value))
                preview = str(value)[:100].replace('\n', ' ')
                print(f'  {key}: {val_len} 字符 - {preview}...' if val_len > 100 else f'  {key}: {value}')
    else:
        print('获取产品详情失败！')
else:
    print('没有找到 S5735 系列产品')

print('\n\n' + '=' * 80)
print('测试2：使用 PromptAssembler 拼装 Prompt')
print('=' * 80)

if products and product_detail:
    assembler = PromptAssembler(data_fetcher)
    
    prompt, context = assembler.assemble_from_message(
        f'{product_code} 产品介绍',
        'product_introduction',
        {'product_code': product_code}
    )
    
    print(f'\nContext 信息:')
    print(f'  has_data: {context.get("has_data")}')
    print(f'  fuzzy_matched: {context.get("fuzzy_matched")}')
    
    if context.get('product_data'):
        pd = context['product_data']
        print(f'\n传递给 LLM 的产品信息：')
        for key in ['product_code', 'product_name', 'series', 'category', 'status']:
            val = pd.get(key, 'N/A')
            print(f'  {key}: {val}')
        
        desc = pd.get('description', '')
        specs = pd.get('specs_json', '')
        print(f'  description: {len(desc)} 字符')
        print(f'  specs_json: {len(specs)} 字符')
    
    print(f'\nPrompt 总长度: {len(prompt)} 字符')
    print(f'\n--- Prompt 内容预览（前1000字符）---')
    print(prompt[:1000])
