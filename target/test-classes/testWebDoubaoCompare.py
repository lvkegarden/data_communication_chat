import sys
import os
import json
import time
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser


class WebDoubaoComparator:
    def __init__(self):
        self.fetcher = ProductDataFetcher()
        self.evaluator = SimilarityEvaluator()
        self.parser = ProductNamingParser()
        self.all_products = None
        
    def get_all_products(self):
        if self.all_products is None:
            self.all_products = self.fetcher.get_all_products_summary()
        return self.all_products
    
    def is_target_product_type(self, product_code: str) -> bool:
        naming = self.parser.parse(product_code)
        product_type = naming.get('product_type', '')
        details = naming.get('details', {})
        switch_level = details.get('switch_level', '')
        
        if product_type == '无线AP':
            return True
        if product_type == '交换机' and '接入' in switch_level:
            return True
        return False
    
    def extract_test_products(self, limit_per_brand: int = 10) -> List[Dict[str, Any]]:
        all_products = self.get_all_products()
        
        by_brand = {}
        for product in all_products:
            brand = self.evaluator._extract_brand(product) or '未知'
            if brand not in ['华为', 'H3C', '锐捷']:
                continue
            
            code = product.get('product_code', '')
            if not self.is_target_product_type(code):
                continue
            
            if brand not in by_brand:
                by_brand[brand] = []
            by_brand[brand].append(product)
        
        print("=" * 80)
        print("数据库目标产品统计（接入交换机 + 无线AP）")
        print("=" * 80)
        for brand, products in sorted(by_brand.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {brand}: {len(products)} 个产品")
        
        test_products = []
        for brand in ['华为', 'H3C', '锐捷']:
            if brand in by_brand:
                products = by_brand[brand][:limit_per_brand]
                for product in products:
                    full_product = self.fetcher.get_product_by_code(product.get('product_code'))
                    if full_product:
                        test_products.append(full_product)
        
        print(f"\n选取测试产品数: {len(test_products)}")
        return test_products
    
    def match_local_competitors(self, target_product: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        all_products = self.get_all_products()
        
        target_code = target_product.get('product_code', '')
        target_brand = self.evaluator._extract_brand(target_product)
        
        evaluated = []
        for candidate in all_products:
            if candidate.get('product_code') == target_code:
                continue
            
            candidate_brand = self.evaluator._extract_brand(candidate)
            if candidate_brand == target_brand:
                continue
            
            candidate_full = self.fetcher.get_product_by_code(candidate.get('product_code'))
            if not candidate_full:
                continue
            
            result = self.evaluator.evaluate(target_product, candidate_full)
            if result['is_competitor']:
                evaluated.append({
                    'code': candidate.get('product_code', ''),
                    'name': candidate.get('product_name', ''),
                    'brand': candidate_brand or '未知',
                    'score': result['total_score']
                })
        
        evaluated.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"  [DEBUG] 目标品牌: {target_brand}")
        print(f"  [DEBUG] 找到 {len(evaluated)} 个竞品候选:")
        for i, item in enumerate(evaluated[:5], 1):
            print(f"    {i}. {item['code']} ({item['brand']}): {item['score']}分")
        
        selected = []
        used_brands = set()
        
        # 第一轮：每个品牌选1个
        for item in evaluated:
            if len(selected) >= limit:
                break
            brand = item['brand']
            if brand not in used_brands:
                selected.append(item)
                used_brands.add(brand)
        
        remaining_needed = limit - len(selected)
        # 第二轮：如果还需要更多竞品，但不要同品牌的
        if remaining_needed > 0:
            for item in evaluated:
                if remaining_needed <= 0:
                    break
                item_brand = item['brand']
                if item not in selected and item_brand not in used_brands:
                    selected.append(item)
                    used_brands.add(item_brand)
                    remaining_needed -= 1
        
        return selected
    
    def normalize_code(self, code: str) -> str:
        if not code:
            return ''
        return code.upper().replace('-', '').replace('_', '').replace(' ', '')
    
    def code_similarity(self, code1: str, code2: str) -> float:
        if not code1 or not code2:
            return 0.0
        
        norm1 = self.normalize_code(code1)
        norm2 = self.normalize_code(code2)
        
        if norm1 == norm2:
            return 1.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_best_match(self, target_code: str, local_codes: List[str]) -> Optional[Dict[str, Any]]:
        best_match = None
        best_score = 0.0
        
        for local_code in local_codes:
            similarity = self.code_similarity(target_code, local_code)
            if similarity > best_score:
                best_score = similarity
                best_match = {'code': local_code, 'similarity': similarity}
        
        return best_match
    
    def compare_results(self, target_product: Dict[str, Any], 
                       local_competitors: List[Dict[str, Any]],
                       doubao_competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        target_code = target_product.get('product_code', '')
        target_name = target_product.get('product_name', '')
        
        local_codes = [c['code'] for c in local_competitors]
        
        matched = []
        missed = []
        extra = []
        
        for doubao_comp in doubao_competitors:
            doubao_code = doubao_comp['code']
            doubao_brand = doubao_comp['brand']
            
            best_match = self.find_best_match(doubao_code, local_codes)
            
            if best_match and best_match['similarity'] >= 0.6:
                matched_local = next(c for c in local_competitors if c['code'] == best_match['code'])
                matched.append({
                    'doubao_code': doubao_code,
                    'doubao_brand': doubao_brand,
                    'local_code': best_match['code'],
                    'local_brand': matched_local['brand'],
                    'similarity': best_match['similarity'],
                    'local_score': matched_local['score']
                })
            else:
                missed.append({
                    'doubao_code': doubao_code,
                    'doubao_brand': doubao_brand,
                    'best_local_match': best_match
                })
        
        for local_comp in local_competitors:
            local_code = local_comp['code']
            found = False
            for m in matched:
                if m['local_code'] == local_code:
                    found = True
                    break
            
            if not found:
                best_doubao_match = self.find_best_match(local_code, [c['code'] for c in doubao_competitors])
                extra.append({
                    'local_code': local_code,
                    'local_brand': local_comp['brand'],
                    'local_score': local_comp['score'],
                    'best_doubao_match': best_doubao_match
                })
        
        total_expected = len(doubao_competitors)
        matched_count = len(matched)
        precision = matched_count / len(local_competitors) if local_competitors else 0
        recall = matched_count / total_expected if total_expected > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'target': {
                'code': target_code,
                'name': target_name
            },
            'local_competitors': local_competitors,
            'doubao_competitors': doubao_competitors,
            'matched': matched,
            'missed': missed,
            'extra': extra,
            'metrics': {
                'total_expected': total_expected,
                'matched_count': matched_count,
                'local_count': len(local_competitors),
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1_score': round(f1_score, 4)
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = 'web_doubao_compare_results.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {filename}")


def main():
    comparator = WebDoubaoComparator()
    
    print(f"\n{'=' * 80}")
    print(f"网页访问豆包竞品分析对比测试")
    print(f"{'=' * 80}")
    
    # 先只测试一个我们有豆包数据的产品：S5735-L-V2
    test_products = []
    target_code = 'S5735-L-V2'
    target = comparator.fetcher.get_product_by_code(target_code)
    if target:
        test_products.append(target)
    
    print(f"\n{'=' * 80}")
    print(f"测试产品列表")
    print(f"{'=' * 80}")
    for i, product in enumerate(test_products, 1):
        print(f"[{i}] {product.get('product_name')} ({product.get('product_code')})")
    
    print(f"\n{'=' * 80}")
    print(f"测试准备完成。目前使用 mock 数据进行测试")
    print(f"后续可以接入真实的浏览器交互来获取豆包数据")
    print(f"{'=' * 80}")
    
    sample_data = {
        'S5735-L-V2': {
            '华为': [],
            'H3C': ['S5130S-EI', 'S5130S-HI-G', 'S5800'],
            '锐捷': ['RG-S5760-X', 'RG-S5310-E']
        }
    }
    
    all_results = []
    summary = {
        'total_products': 0,
        'total_matched': 0,
        'total_missed': 0,
        'total_extra': 0,
        'avg_precision': 0.0,
        'avg_recall': 0.0,
        'avg_f1': 0.0,
        'by_brand': {}
    }
    
    for i, target_product in enumerate(test_products, 1):
        target_code = target_product.get('product_code', '')
        target_name = target_product.get('product_name', '')
        target_brand = comparator.evaluator._extract_brand(target_product)
        
        print(f"\n{'=' * 80}")
        print(f"[{i}/{len(test_products)}] 目标产品: {target_name} ({target_code}) [{target_brand}]")
        print(f"{'=' * 80}")
        
        local_competitors = comparator.match_local_competitors(target_product, limit=3)
        
        print(f"\n本地匹配结果 ({len(local_competitors)} 个):")
        for j, comp in enumerate(local_competitors, 1):
            print(f"  [{j}] {comp['name']} ({comp['code']}) - {comp['brand']} - {comp['score']}分")
        
        doubao_competitors = []
        if target_code in sample_data:
            for brand, codes in sample_data[target_code].items():
                for code in codes:
                    doubao_competitors.append({'brand': brand, 'code': code})
        else:
            print(f"\n豆包返回结果 (使用默认竞品):")
        print(f"\n豆包返回结果 ({len(doubao_competitors)} 个):")
        for j, comp in enumerate(doubao_competitors, 1):
            print(f"  [{j}] {comp['code']} - {comp['brand']}")
        
        if doubao_competitors:
            comparison = comparator.compare_results(target_product, local_competitors, doubao_competitors)
            
            print(f"\n对比分析:")
            print(f"  匹配成功: {len(comparison['matched'])} 个")
            print(f"  遗漏: {len(comparison['missed'])} 个")
            print(f"  额外: {len(comparison['extra'])} 个")
            
            print(f"\n指标:")
            metrics = comparison['metrics']
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1 Score: {metrics['f1_score']:.4f}")
            
            all_results.append(comparison)
            
            summary['total_products'] += 1
            summary['total_matched'] += metrics['matched_count']
            summary['total_missed'] += len(comparison['missed'])
            summary['total_extra'] += len(comparison['extra'])
            summary['avg_precision'] += metrics['precision']
            summary['avg_recall'] += metrics['recall']
            summary['avg_f1'] += metrics['f1_score']
            
            if target_brand not in summary['by_brand']:
                summary['by_brand'][target_brand] = {
                    'count': 0,
                    'matched': 0,
                    'missed': 0,
                    'extra': 0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1': 0.0
                }
            summary['by_brand'][target_brand]['count'] += 1
            summary['by_brand'][target_brand]['matched'] += metrics['matched_count']
            summary['by_brand'][target_brand]['missed'] += len(comparison['missed'])
            summary['by_brand'][target_brand]['extra'] += len(comparison['extra'])
            summary['by_brand'][target_brand]['precision'] += metrics['precision']
            summary['by_brand'][target_brand]['recall'] += metrics['recall']
            summary['by_brand'][target_brand]['f1'] += metrics['f1_score']
        
        time.sleep(0.5)
    
    if summary['total_products'] > 0:
        summary['avg_precision'] = round(summary['avg_precision'] / summary['total_products'], 4)
        summary['avg_recall'] = round(summary['avg_recall'] / summary['total_products'], 4)
        summary['avg_f1'] = round(summary['avg_f1'] / summary['total_products'], 4)
        
        for brand, brand_data in summary['by_brand'].items():
            if brand_data['count'] > 0:
                brand_data['precision'] = round(brand_data['precision'] / brand_data['count'], 4)
                brand_data['recall'] = round(brand_data['recall'] / brand_data['count'], 4)
                brand_data['f1'] = round(brand_data['f1'] / brand_data['count'], 4)
    
    print(f"\n{'=' * 80}")
    print(f"总体统计")
    print(f"{'=' * 80}")
    print(f"测试产品数: {summary['total_products']}")
    print(f"总匹配数: {summary['total_matched']}")
    print(f"总遗漏数: {summary['total_missed']}")
    print(f"总额外数: {summary['total_extra']}")
    print(f"平均 Precision: {summary['avg_precision']:.4f}")
    print(f"平均 Recall: {summary['avg_recall']:.4f}")
    print(f"平均 F1 Score: {summary['avg_f1']:.4f}")
    
    print(f"\n按品牌统计:")
    for brand, brand_data in sorted(summary['by_brand'].items()):
        print(f"\n  {brand}:")
        print(f"    测试数: {brand_data['count']}")
        print(f"    匹配数: {brand_data['matched']}")
        print(f"    遗漏数: {brand_data['missed']}")
        print(f"    额外数: {brand_data['extra']}")
        print(f"    Precision: {brand_data['precision']:.4f}")
        print(f"    Recall: {brand_data['recall']:.4f}")
        print(f"    F1: {brand_data['f1']:.4f}")
    
    comparator.save_results({'summary': summary, 'results': all_results})
    
    print(f"\n{'=' * 80}")
    print(f"测试完成")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
