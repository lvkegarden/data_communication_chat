import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_naming_parser import ProductNamingParser
from similarity_evaluator import SimilarityEvaluator


def test_naming_similarity():
    parser = ProductNamingParser()
    evaluator = SimilarityEvaluator(parser)
    
    target_product = {
        'product_code': 'S5735-L-V2',
        'product_name': '华为S5735-L-V2交换机',
        'product_type': '交换机',
    }
    
    candidates = [
        {
            'product_code': 'S5130S-28P-EI',
            'product_name': 'H3C S5130S-28P-EI',
            'product_type': '交换机',
        },
        {
            'product_code': 'S5560X-54C-EI',
            'product_name': 'H3C S5560X-54C-EI',
            'product_type': '交换机',
        },
        {
            'product_code': 'RG-S5750-48GT4XS-E',
            'product_name': '锐捷RG-S5750-48GT4XS-E',
            'product_type': '交换机',
        },
        {
            'product_code': 'RG-S5750-24GT4XS-P-L',
            'product_name': '锐捷RG-S5750-24GT4XS-P-L',
            'product_type': '交换机',
        },
        {
            'product_code': 'S6520X-54QC-EI',
            'product_name': 'H3C S6520X-54QC-EI',
            'product_type': '交换机',
        },
        {
            'product_code': 'RG-S6120-48XS4QXS-L',
            'product_name': '锐捷RG-S6120-48XS4QXS-L',
            'product_type': '交换机',
        },
        {
            'product_code': 'S5720-52X-PWR-SI',
            'product_name': '华为S5720-52X-PWR-SI',
            'product_type': '交换机',
        },
    ]
    
    print('=' * 80)
    print('基于命名解析的相似度测试 - 目标产品: S5735-L-V2')
    print('=' * 80)
    
    target_naming = parser.parse(target_product['product_code'])
    print(f'\n目标产品命名解析结果:')
    print(f'  品牌: {target_naming["brand"]}')
    print(f'  产品类型: {target_naming["product_type"]}')
    print(f'  详细信息: {json.dumps(target_naming["details"], ensure_ascii=False, indent=2)}')
    
    print(f'\n{"-" * 80}')
    print(f'{"产品型号":<30} {"品牌":<10} {"总分":<8} {"是否竞品":<10}')
    print(f'{"-" * 80}')
    
    results = []
    for candidate in candidates:
        result = evaluator.evaluate(target_product, candidate)
        results.append({
            'candidate': candidate,
            'result': result
        })
        status = '是' if result['is_competitor'] else '否'
        brand = result.get('candidate_brand', '未知')
        print(f'{candidate["product_code"]:<30} {brand:<10} {result["total_score"]:<8} {status:<10}')
    
    print(f'\n{"-" * 80}')
    print('详细评分分解:')
    print(f'{"-" * 80}')
    
    for item in results:
        candidate = item['candidate']
        result = item['result']
        
        print(f'\n【{candidate["product_code"]}】 vs 【S5735-L-V2】')
        print(f'  品牌: {result.get("candidate_brand", "未知")}')
        print(f'  总分: {result["total_score"]}')
        print(f'  是否竞品: {result["is_competitor"]}')
        
        candidate_naming = result.get('candidate_naming', {})
        if candidate_naming.get('parsed'):
            print(f'  候选产品命名解析: {json.dumps(candidate_naming["details"], ensure_ascii=False)}')
        
        print(f'  评分分解:')
        for breakdown in result['breakdown']:
            score_str = f'{breakdown["score"]:>3}分' if breakdown["score"] != 0 else '   0分'
            print(f'    {score_str} - {breakdown["category"]}: {breakdown["detail"]}')


def test_ap_similarity():
    parser = ProductNamingParser()
    evaluator = SimilarityEvaluator(parser)
    
    target_product = {
        'product_code': 'AirEngine 6760-X1',
        'product_name': '华为AirEngine 6760-X1',
        'product_type': '无线AP',
    }
    
    candidates = [
        {
            'product_code': 'WA6530',
            'product_name': 'H3C WA6530',
            'product_type': '无线AP',
        },
        {
            'product_code': 'RG-AP880(TR)',
            'product_name': '锐捷RG-AP880(TR)',
            'product_type': '无线AP',
        },
        {
            'product_code': 'WA6628',
            'product_name': 'H3C WA6628',
            'product_type': '无线AP',
        },
        {
            'product_code': 'RG-AP780',
            'product_name': '锐捷RG-AP780',
            'product_type': '无线AP',
        },
    ]
    
    print('\n\n' + '=' * 80)
    print('AP产品相似度测试 - 目标产品: AirEngine 6760-X1')
    print('=' * 80)
    
    target_naming = parser.parse(target_product['product_code'])
    print(f'\n目标产品命名解析结果:')
    print(f'  品牌: {target_naming["brand"]}')
    print(f'  产品类型: {target_naming["product_type"]}')
    print(f'  详细信息: {json.dumps(target_naming["details"], ensure_ascii=False, indent=2)}')
    
    print(f'\n{"-" * 80}')
    print(f'{"产品型号":<30} {"品牌":<10} {"总分":<8} {"是否竞品":<10}')
    print(f'{"-" * 80}')
    
    results = []
    for candidate in candidates:
        result = evaluator.evaluate(target_product, candidate)
        results.append({
            'candidate': candidate,
            'result': result
        })
        status = '是' if result['is_competitor'] else '否'
        brand = result.get('candidate_brand', '未知')
        print(f'{candidate["product_code"]:<30} {brand:<10} {result["total_score"]:<8} {status:<10}')
    
    print(f'\n{"-" * 80}')
    print('详细评分分解:')
    print(f'{"-" * 80}')
    
    for item in results:
        candidate = item['candidate']
        result = item['result']
        
        print(f'\n【{candidate["product_code"]}】 vs 【{target_product["product_code"]}】')
        print(f'  品牌: {result.get("candidate_brand", "未知")}')
        print(f'  总分: {result["total_score"]}')
        print(f'  是否竞品: {result["is_competitor"]}')
        
        candidate_naming = result.get('candidate_naming', {})
        if candidate_naming.get('parsed'):
            print(f'  候选产品命名解析: {json.dumps(candidate_naming["details"], ensure_ascii=False)}')
        
        print(f'  评分分解:')
        for breakdown in result['breakdown']:
            score_str = f'{breakdown["score"]:>3}分' if breakdown["score"] != 0 else '   0分'
            print(f'    {score_str} - {breakdown["category"]}: {breakdown["detail"]}')


def main():
    print('基于命名解析的相似度评估测试\n')
    
    test_naming_similarity()
    test_ap_similarity()
    
    print('\n\n' + '=' * 80)
    print('测试完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
