import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_naming_parser import ProductNamingParser
from similarity_evaluator import SimilarityEvaluator
from product_data_fetcher import ProductDataFetcher


def main():
    parser = ProductNamingParser()
    evaluator = SimilarityEvaluator(parser)
    data_fetcher = ProductDataFetcher()
    
    target_code = 'S5735-L-V2'
    candidate_code = 'S9820'
    
    print('=' * 100)
    print('详细分析: S5735-L-V2 vs S9820')
    print('=' * 100)
    
    target_data = data_fetcher.get_product_by_code(target_code)
    candidate_data = data_fetcher.get_product_by_code(candidate_code)
    
    if not target_data or not candidate_data:
        print(f'产品数据缺失: target={target_data is not None}, candidate={candidate_data is not None}')
        return
    
    print('\n=== 目标产品 S5735-L-V2 命名解析 ===')
    target_naming = parser.parse(target_code)
    print(json.dumps(target_naming, ensure_ascii=False, indent=2))
    
    print('\n=== 候选产品 S9820 命名解析 ===')
    candidate_naming = parser.parse(candidate_code)
    print(json.dumps(candidate_naming, ensure_ascii=False, indent=2))
    
    print('\n=== 相似度评估详细结果 ===')
    result = evaluator.evaluate(target_data, candidate_data)
    
    print(f'\n总分: {result["total_score"]}')
    print(f'是否竞品: {result["is_competitor"]}')
    print(f'目标品牌: {result.get("target_brand", "")}')
    print(f'候选品牌: {result.get("candidate_brand", "")}')
    
    print(f'\n评分分解:')
    for i, breakdown in enumerate(result['breakdown'], 1):
        score = breakdown.get('score', 0)
        category = breakdown.get('category', '')
        detail = breakdown.get('detail', '')
        mark = '+' if score > 0 else ' '
        print(f'{mark} {i:2d}. {score:>4}分 | {category:<35} | {detail}')
    
    print(f'\n{"=" * 100}')
    print('分析总结')
    print(f'{"=" * 100}')
    
    total_score = result['total_score']
    min_score = 40
    
    if total_score >= min_score:
        print(f'\nS9820 被选中为竞品的原因:')
        print(f'  1. 总分 {total_score} 分 >= 最低阈值 {min_score} 分')
        print(f'  2. 品牌不同（{result.get("target_brand")} vs {result.get("candidate_brand")}）')
        print(f'  3. 主要匹配项:')
        
        matching_scores = []
        for breakdown in result['breakdown']:
            if breakdown.get('score', 0) > 0:
                matching_scores.append({
                    'category': breakdown['category'],
                    'score': breakdown['score'],
                    'detail': breakdown['detail']
                })
        
        matching_scores.sort(key=lambda x: x['score'], reverse=True)
        
        for i, ms in enumerate(matching_scores, 1):
            print(f'     {i}. {ms["score"]}分 - {ms["category"]}: {ms["detail"]}')
    else:
        print(f'\nS9820 不应该被选中为竞品，因为:')
        print(f'  1. 总分 {total_score} 分 < 最低阈值 {min_score} 分')
    
    print(f'\n命名解析问题:')
    if candidate_naming['brand'] == '未知':
        print(f'  - S9820 品牌识别为"未知"，但实际是华三产品')
        print(f'  - 这可能导致它通过品牌过滤（因为无法识别为同品牌）')
    
    if not candidate_naming['parsed']:
        print(f'  - S9820 命名解析失败，无法提取交换机等级、功能等级等信息')
        print(f'  - 这会导致命名解析相关的评分项全部为0分')


if __name__ == '__main__':
    main()
