import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_naming_parser import ProductNamingParser
from similarity_evaluator import SimilarityEvaluator
from product_data_fetcher import ProductDataFetcher


def analyze_s9820():
    parser = ProductNamingParser()
    evaluator = SimilarityEvaluator(parser)
    data_fetcher = ProductDataFetcher()
    
    target_code = 'S5735-L-V2'
    candidate_code = 'S9820'
    
    print('=' * 80)
    print('分析: S5735-L-V2 vs S9820')
    print('=' * 80)
    
    print('\n1. 从数据库获取产品信息...')
    target_data = data_fetcher.get_product_by_code(target_code)
    candidate_data = data_fetcher.get_product_by_code(candidate_code)
    
    if not target_data:
        print(f'  未找到 {target_code}')
        return
    
    if not candidate_data:
        print(f'  未找到 {candidate_code}')
        print('\n尝试搜索包含 S9820 的产品...')
        search_results = data_fetcher.search_products(keyword='S9820')
        if search_results:
            print(f'  找到 {len(search_results)} 个相关产品:')
            for prod in search_results:
                print(f'    - {prod.get("product_code")}: {prod.get("product_name")}')
                candidate_data = prod
                candidate_code = prod.get('product_code', candidate_code)
        else:
            print('  未找到任何 S9820 相关产品')
            return
    
    print(f'\n2. 目标产品 {target_code} 信息:')
    print(f'   产品名称: {target_data.get("product_name", "")}')
    print(f'   产品系列: {target_data.get("series", "")}')
    print(f'   产品类别: {target_data.get("category", "")}')
    print(f'   产品类型: {target_data.get("product_type", "")}')
    print(f'   产品来源: {target_data.get("source", "")}')
    print(f'   产品描述: {target_data.get("description", "")[:100]}...')
    if target_data.get('specs_json'):
        print(f'   技术规格: {target_data.get("specs_json", "")[:200]}...')
    
    print(f'\n3. 候选产品 {candidate_code} 信息:')
    print(f'   产品名称: {candidate_data.get("product_name", "")}')
    print(f'   产品系列: {candidate_data.get("series", "")}')
    print(f'   产品类别: {candidate_data.get("category", "")}')
    print(f'   产品类型: {candidate_data.get("product_type", "")}')
    print(f'   产品来源: {candidate_data.get("source", "")}')
    print(f'   产品描述: {candidate_data.get("description", "")[:100]}...')
    if candidate_data.get('specs_json'):
        print(f'   技术规格: {candidate_data.get("specs_json", "")[:200]}...')
    
    print(f'\n4. 目标产品 {target_code} 命名解析结果:')
    target_naming = parser.parse(target_code)
    print(f'   品牌: {target_naming["brand"]}')
    print(f'   产品类型: {target_naming["product_type"]}')
    print(f'   详细信息: {json.dumps(target_naming["details"], ensure_ascii=False, indent=4)}')
    
    print(f'\n5. 候选产品 {candidate_code} 命名解析结果:')
    candidate_naming = parser.parse(candidate_code)
    print(f'   品牌: {candidate_naming["brand"]}')
    print(f'   产品类型: {candidate_naming["product_type"]}')
    print(f'   详细信息: {json.dumps(candidate_naming["details"], ensure_ascii=False, indent=4)}')
    
    print(f'\n6. 相似度评估结果:')
    result = evaluator.evaluate(target_data, candidate_data)
    print(f'   总分: {result["total_score"]}')
    print(f'   是否竞品: {result["is_competitor"]}')
    print(f'   原因: {result["reason"]}')
    print(f'   目标品牌: {result.get("target_brand", "")}')
    print(f'   候选品牌: {result.get("candidate_brand", "")}')
    
    print(f'\n7. 评分分解:')
    for i, breakdown in enumerate(result['breakdown'], 1):
        score = breakdown.get('score', 0)
        category = breakdown.get('category', '')
        detail = breakdown.get('detail', '')
        print(f'   {i}. {score:>3}分 - {category}: {detail}')
    
    print(f'\n{"=" * 80}')
    print('分析总结')
    print(f'{"=" * 80}')
    
    total_score = result['total_score']
    min_score = 40
    
    if total_score >= min_score:
        print(f'\nS9820 被选中为竞品的原因:')
        print(f'  1. 总分 {total_score} 分 >= 最低阈值 {min_score} 分')
        print(f'  2. 品牌不同（{result.get("target_brand")} vs {result.get("candidate_brand")}）')
        print(f'  3. 主要匹配项:')
        for breakdown in result['breakdown']:
            if breakdown.get('score', 0) > 0:
                print(f'     - {breakdown["category"]}: {breakdown["detail"]} ({breakdown["score"]}分)')
    else:
        print(f'\nS9820 不应该被选中为竞品，因为:')
        print(f'  1. 总分 {total_score} 分 < 最低阈值 {min_score} 分')


def list_all_products():
    print('\n\n' + '=' * 80)
    print('查看数据库中所有产品')
    print('=' * 80)
    
    data_fetcher = ProductDataFetcher()
    products = data_fetcher.get_all_products_summary()
    
    print(f'\n数据库中共有 {len(products)} 个产品:')
    
    h3c_products = []
    ruijie_products = []
    huawei_products = []
    unknown_products = []
    
    parser = ProductNamingParser()
    
    for prod in products:
        code = prod.get('product_code', '')
        naming = parser.parse(code)
        brand = naming.get('brand', '未知')
        
        prod_info = {
            'code': code,
            'name': prod.get('product_name', ''),
            'category': prod.get('category', ''),
            'product_type': prod.get('product_type', ''),
            'naming_brand': brand
        }
        
        if brand == '华为':
            huawei_products.append(prod_info)
        elif brand == 'H3C':
            h3c_products.append(prod_info)
        elif brand == '锐捷':
            ruijie_products.append(prod_info)
        else:
            unknown_products.append(prod_info)
    
    print(f'\n华为产品 ({len(huawei_products)}):')
    for p in huawei_products:
        print(f'  {p["code"]:20} - {p["name"]:30} - {p["category"] or p["product_type"]}')
    
    print(f'\nH3C 产品 ({len(h3c_products)}):')
    for p in h3c_products:
        print(f'  {p["code"]:20} - {p["name"]:30} - {p["category"] or p["product_type"]}')
    
    print(f'\n锐捷产品 ({len(ruijie_products)}):')
    for p in ruijie_products:
        print(f'  {p["code"]:20} - {p["name"]:30} - {p["category"] or p["product_type"]}')
    
    print(f'\n未知品牌产品 ({len(unknown_products)}):')
    for p in unknown_products:
        print(f'  {p["code"]:20} - {p["name"]:30} - {p["category"] or p["product_type"]}')


if __name__ == '__main__':
    analyze_s9820()
    list_all_products()
