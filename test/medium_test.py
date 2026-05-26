#!/usr/bin/env python3
import sys
import os
import json
import time
import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser


class MediumScaleTest:
    """
    中等规模竞品分析测试
    """
    
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
    
    def extract_test_products(self, limit_per_brand: int = 20) -> List[Dict[str, Any]]:
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
        print("中等规模测试产品统计（接入交换机 + 无线AP）")
        print("=" * 80)
        for brand, products in sorted(by_brand.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {brand}: 总共 {len(products)} 个，测试 {min(limit_per_brand, len(products))} 个")
        
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
    
    def query_doubao(self, product_name: str, product_code: str) -> List[Dict[str, Any]]:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key or api_key == "your-dashscope-api-key-here":
            return self._get_mock_data(product_code)
        
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            query = f"{product_code} 产品 竞品分析，给出 华三 锐捷 三个品牌的竞品名称"
            
            system_prompt = """你是一个专业的数通产品竞品分析师。
请根据用户提供的产品信息，给出其他品牌的竞品产品型号，不要包含同品牌产品。

要求：
1. 只输出竞品型号，不要输出其他内容
2. 只给出其他品牌的竞品，不要包含同品牌产品
3. 每个品牌给出1-3个竞品
4. 格式要求：品牌:型号1,型号2
5. 示例：
华为:S5735-L-V2
H3C:S5130S-28P-EI
锐捷:RG-S5750-24GT4XS-P-L"""
            
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content, product_code)
        except Exception as e:
            print(f"  豆包API调用失败: {e}")
            return self._get_mock_data(product_code)
    
    def _get_mock_data(self, product_code: str) -> List[Dict[str, Any]]:
        target_brand = self._guess_brand(product_code)
        competitors = []
        
        if target_brand == '华为':
            competitors = [
                {'brand': 'H3C', 'code': 'S5130S-EI'},
                {'brand': 'H3C', 'code': 'S5130S-LI'},
                {'brand': '锐捷', 'code': 'RG-S5750-L'}
            ]
        elif target_brand == 'H3C':
            competitors = [
                {'brand': '华为', 'code': 'S5735-L-V2'},
                {'brand': '华为', 'code': 'S5735-S-V2'},
                {'brand': '锐捷', 'code': 'RG-S5310-E'}
            ]
        elif target_brand == '锐捷':
            competitors = [
                {'brand': '华为', 'code': 'S5735-L-V2'},
                {'brand': '华为', 'code': 'S5735-S-V2'},
                {'brand': 'H3C', 'code': 'S5130S-EI'}
            ]
        
        return competitors
    
    def _guess_brand(self, product_code: str) -> Optional[str]:
        if product_code.startswith('S') and not product_code.startswith('S6') and not product_code.startswith('S51') and not product_code.startswith('S55'):
            return '华为'
        elif product_code.startswith('S51') or product_code.startswith('S55') or product_code.startswith('WX'):
            return 'H3C'
        elif product_code.startswith('RG'):
            return '锐捷'
        return None
    
    def _parse_response(self, content: str, target_code: str) -> List[Dict[str, Any]]:
        competitors = []
        target_brand = self._guess_brand(target_code)
        
        brand_patterns = {
            '华为': r'华为[：:]\s*([^\n]+)',
            'H3C': r'H3C[：:]\s*([^\n]+)',
            '锐捷': r'锐捷[：:]\s*([^\n]+)'
        }
        
        for brand in ['华为', 'H3C', '锐捷']:
            if target_brand and brand == target_brand:
                continue
                
            pattern = brand_patterns.get(brand, '')
            if pattern:
                matches = re.findall(pattern, content)
                for code_list in matches:
                    codes = re.split(r'[,，]', code_list.strip())
                    for code in codes:
                        code = code.strip()
                        if code:
                            competitors.append({
                                'brand': brand,
                                'code': code
                            })
        
        return competitors
    
    def match_local(self, target_product: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        all_products = self.get_all_products()
        
        target_code = target_product.get('product_code', '')
        target_brand = self.evaluator._extract_brand(target_product)
        
        by_brand = {}
        for candidate in all_products:
            candidate_code = candidate.get('product_code', '')
            if candidate_code == target_code:
                continue
            
            candidate_full = self.fetcher.get_product_by_code(candidate_code)
            if not candidate_full:
                continue
            
            candidate_brand = self.evaluator._extract_brand(candidate_full)
            if candidate_brand == target_brand:
                continue
            
            result = self.evaluator.evaluate(target_product, candidate_full)
            if result['is_competitor']:
                if candidate_brand not in by_brand:
                    by_brand[candidate_brand] = []
                by_brand[candidate_brand].append({
                    'code': candidate_full.get('product_code', ''),
                    'name': candidate_full.get('product_name', ''),
                    'brand': candidate_brand or '未知',
                    'score': result['total_score']
                })
        
        final_result = []
        for brand, products in by_brand.items():
            products.sort(key=lambda x: x['score'], reverse=True)
            final_result.extend(products[:2])
        
        final_result.sort(key=lambda x: x['score'], reverse=True)
        return final_result[:limit]
    
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
    
    def compare(self, target_code: str, local: List[Dict], doubao: List[Dict]) -> Dict:
        local_codes = [c['code'] for c in local]
        
        matched = []
        missed = []
        extra = []
        
        for dc in doubao:
            dc_code = dc['code']
            dc_brand = dc['brand']
            
            best_match = None
            best_score = 0.0
            for lc in local_codes:
                sim = self.code_similarity(dc_code, lc)
                if sim > best_score:
                    best_score = sim
                    best_match = lc
            
            if best_match and best_score >= 0.55:
                matched_local = next(c for c in local if c['code'] == best_match)
                matched.append({
                    'doubao_code': dc_code,
                    'doubao_brand': dc_brand,
                    'local_code': best_match,
                    'local_brand': matched_local['brand'],
                    'similarity': best_score,
                    'local_score': matched_local['score']
                })
            else:
                missed.append({
                    'doubao_code': dc_code,
                    'doubao_brand': dc_brand
                })
        
        for lc in local:
            lc_code = lc['code']
            found = False
            for m in matched:
                if m['local_code'] == lc_code:
                    found = True
                    break
            
            if not found:
                extra.append({
                    'local_code': lc_code,
                    'local_brand': lc['brand'],
                    'local_score': lc['score']
                })
        
        total_expected = len(doubao)
        matched_count = len(matched)
        precision = matched_count / len(local) if local else 0
        recall = matched_count / total_expected if total_expected else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
        
        return {
            'matched': matched,
            'missed': missed,
            'extra': extra,
            'metrics': {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4)
            }
        }
    
    def run(self):
        print(f"\n{'=' * 80}")
        print(f"中等规模豆包竞品分析测试")
        print(f"{'=' * 80}")
        
        test_products = self.extract_test_products(limit_per_brand=15)
        
        print(f"\n{'=' * 80}")
        print(f"测试产品列表")
        print(f"{'=' * 80}")
        for i, product in enumerate(test_products, 1):
            print(f"[{i}] {product.get('product_name')} ({product.get('product_code')})")
        
        all_results = []
        summary = {
            'total': 0,
            'total_matched': 0,
            'total_missed': 0,
            'total_extra': 0,
            'precision_sum': 0,
            'recall_sum': 0,
            'f1_sum': 0,
            'by_brand': {}
        }
        
        for i, target in enumerate(test_products, 1):
            code = target.get('product_code', '')
            name = target.get('product_name', '')
            brand = self.evaluator._extract_brand(target)
            
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(test_products)}] {name} ({code}) [{brand}]")
            print(f"{'=' * 80}")
            
            local = self.match_local(target, limit=5)
            print(f"\n本地匹配: {len(local)} 个")
            for j, comp in enumerate(local, 1):
                print(f"  [{j}] {comp['name']} ({comp['code']}) - {comp['brand']} - {comp['score']}")
            
            doubao = self.query_doubao(name, code)
            print(f"\n豆包返回: {len(doubao)} 个")
            for j, comp in enumerate(doubao, 1):
                print(f"  [{j}] {comp['code']} - {comp['brand']}")
            
            if doubao:
                comp_result = self.compare(code, local, doubao)
                
                print(f"\n对比:")
                print(f"  匹配: {len(comp_result['matched'])} 个")
                for m in comp_result['matched']:
                    print(f"    ✓ {m['doubao_code']} ↔ {m['local_code']} ({m['similarity']:.2f})")
                
                print(f"  遗漏: {len(comp_result['missed'])} 个")
                for m in comp_result['missed']:
                    print(f"    ✗ {m['doubao_code']}")
                
                print(f"  额外: {len(comp_result['extra'])} 个")
                for e in comp_result['extra']:
                    print(f"    + {e['local_code']}")
                
                metrics = comp_result['metrics']
                print(f"\n指标:")
                print(f"  Precision: {metrics['precision']:.4f}")
                print(f"  Recall: {metrics['recall']:.4f}")
                print(f"  F1: {metrics['f1']:.4f}")
                
                all_results.append({
                    'target': {'code': code, 'name': name, 'brand': brand},
                    'local': local,
                    'doubao': doubao,
                    'comparison': comp_result
                })
                
                summary['total'] += 1
                summary['total_matched'] += len(comp_result['matched'])
                summary['total_missed'] += len(comp_result['missed'])
                summary['total_extra'] += len(comp_result['extra'])
                summary['precision_sum'] += metrics['precision']
                summary['recall_sum'] += metrics['recall']
                summary['f1_sum'] += metrics['f1']
                
                if brand not in summary['by_brand']:
                    summary['by_brand'][brand] = {'count': 0, 'precision': 0, 'recall': 0, 'f1': 0}
                summary['by_brand'][brand]['count'] += 1
                summary['by_brand'][brand]['precision'] += metrics['precision']
                summary['by_brand'][brand]['recall'] += metrics['recall']
                summary['by_brand'][brand]['f1'] += metrics['f1']
            
            time.sleep(0.5)
        
        print(f"\n{'=' * 80}")
        print(f"总体统计")
        print(f"{'=' * 80}")
        print(f"测试产品: {summary['total']}")
        print(f"总匹配数: {summary['total_matched']}")
        print(f"总遗漏数: {summary['total_missed']}")
        print(f"总额外数: {summary['total_extra']}")
        
        if summary['total'] > 0:
            avg_precision = summary['precision_sum'] / summary['total']
            avg_recall = summary['recall_sum'] / summary['total']
            avg_f1 = summary['f1_sum'] / summary['total']
            print(f"平均 Precision: {avg_precision:.4f}")
            print(f"平均 Recall: {avg_recall:.4f}")
            print(f"平均 F1: {avg_f1:.4f}")
        
        print(f"\n按品牌统计:")
        for brand, stats in summary['by_brand'].items():
            if stats['count'] > 0:
                p = stats['precision'] / stats['count']
                r = stats['recall'] / stats['count']
                f = stats['f1'] / stats['count']
                print(f"\n  {brand}:")
                print(f"    测试数: {stats['count']}")
                print(f"    平均 Precision: {p:.4f}")
                print(f"    平均 Recall: {r:.4f}")
                print(f"    平均 F1: {f:.4f}")
        
        with open('medium_test_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'summary': summary,
                'results': all_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: medium_test_results.json")
        print(f"\n{'=' * 80}")
        print(f"测试完成")
        print(f"{'=' * 80}")


if __name__ == '__main__':
    test = MediumScaleTest()
    test.run()
