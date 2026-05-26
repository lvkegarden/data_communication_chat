import sys
import os
import json
import logging
import re
import time
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

logging.disable(logging.CRITICAL)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator, SimilarityCriteria
from product_naming_parser import ProductNamingParser


class DoubaoClient:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key or self.api_key == "your-dashscope-api-key-here":
            raise ValueError("DASHSCOPE_API_KEY 环境变量未配置")
        
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-plus"
        self._init_client()
    
    def _init_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.llm_available = True
        except ImportError:
            self.llm_available = False
            print("警告: openai 库未安装，将使用 mock 数据")
    
    def query_competitors(self, product_name: str, product_code: str, brands: List[str] = ['华为', 'H3C', '锐捷']) -> Dict[str, Any]:
        if not self.llm_available:
            return self._get_mock_competitors(product_code, brands)
        
        brands_str = '、'.join(brands)
        query = f"{product_name} 产品 竞品分析，给出 {brands_str} 三个品牌的竞品名称"
        
        system_prompt = """你是一个专业的数通产品竞品分析师。
请根据用户提供的产品信息，给出其他品牌的竞品产品型号。

要求：
1. 只输出竞品型号，不要输出其他内容
2. 每个品牌给出1-2个竞品
3. 格式要求：品牌:型号1,型号2
4. 示例：
华为:S5735-L-V2
H3C:S5130S-28P-EI
锐捷:RG-S5750-24GT4XS-P-L"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content, brands)
        except Exception as e:
            print(f"豆包 API 调用失败: {e}")
            return self._get_mock_competitors(product_code, brands)
    
    def _parse_response(self, content: str, brands: List[str]) -> Dict[str, Any]:
        result = {
            'raw_response': content,
            'competitors': []
        }
        
        lines = content.strip().split('\n')
        brand_patterns = {
            '华为': r'华为[：:]\s*([^\s,，、]+)',
            'H3C': r'H3C[：:]\s*([^\s,，、]+)',
            '锐捷': r'锐捷[：:]\s*([^\s,，、]+)'
        }
        
        for brand in brands:
            pattern = brand_patterns.get(brand, r'')
            if pattern:
                match = re.search(pattern, content)
                if match:
                    codes = re.split(r'[,，、\s]+', match.group(1).strip())
                    for code in codes:
                        if code:
                            result['competitors'].append({
                                'brand': brand,
                                'code': code
                            })
        
        return result
    
    def _get_mock_competitors(self, product_code: str, brands: List[str]) -> Dict[str, Any]:
        mock_data = {
            'S5735-L-V2': {
                '华为': [],
                'H3C': ['S5130S-EI'],
                '锐捷': ['RG-S5750V2-L']
            },
            'S5731-L': {
                '华为': [],
                'H3C': ['S5130S-LI'],
                '锐捷': ['RG-S5300-L']
            },
            'S5735-H': {
                '华为': [],
                'H3C': ['S5560X-HI'],
                '锐捷': ['RG-S5750-H']
            },
            'S5130S-EI': {
                '华为': ['S5735-L-V2'],
                'H3C': [],
                '锐捷': ['RG-S5310-E']
            },
            'S5130S-LI': {
                '华为': ['S5731-L'],
                'H3C': [],
                '锐捷': ['RG-S5300-L']
            },
            'S5560X-HI': {
                '华为': ['S5735-H'],
                'H3C': [],
                '锐捷': ['RG-S5750-H']
            },
            'RG-S5750V2-L': {
                '华为': ['S5735-L-V2'],
                'H3C': ['S5130S-LI'],
                '锐捷': []
            },
            'RG-S5310-E': {
                '华为': ['S5735-L-V2'],
                'H3C': ['S5130S-EI'],
                '锐捷': []
            },
            'RG-S5300-L': {
                '华为': ['S5731-L'],
                'H3C': ['S5130S-LI'],
                '锐捷': []
            },
            'RG-S5750-H': {
                '华为': ['S5735-H'],
                'H3C': ['S5560X-HI'],
                '锐捷': []
            },
            'AirEngine 6760': {
                '华为': [],
                'H3C': ['WA6530i', 'WA6628'],
                '锐捷': ['RG-AP880-AR']
            },
            'WA6530i': {
                '华为': ['AirEngine 6760'],
                'H3C': [],
                '锐捷': ['RG-AP820C']
            },
            'RG-AP880-AR': {
                '华为': ['AirEngine 6760'],
                'H3C': ['WA6530i'],
                '锐捷': []
            }
        }
        
        competitors = []
        
        if product_code in mock_data:
            for brand in brands:
                for code in mock_data[product_code].get(brand, []):
                    competitors.append({'brand': brand, 'code': code})
        else:
            default_mapping = {
                '华为': {'H3C': 'S5130S-EI', '锐捷': 'RG-S5310-E'},
                'H3C': {'华为': 'S5735-L-V2', '锐捷': 'RG-S5310-E'},
                '锐捷': {'华为': 'S5735-L-V2', 'H3C': 'S5130S-EI'}
            }
            
            product_brand = None
            if product_code.startswith('S'):
                if '5735' in product_code or '5731' in product_code or '5720' in product_code:
                    product_brand = '华为'
                elif '5130' in product_code or '5560' in product_code or '5800' in product_code:
                    product_brand = 'H3C'
            elif product_code.startswith('RG-'):
                if 'S5750' in product_code or 'S5310' in product_code or 'S5300' in product_code:
                    product_brand = '锐捷'
            elif product_code.startswith('AirEngine'):
                product_brand = '华为'
            elif product_code.startswith('WA'):
                product_brand = 'H3C'
            elif product_code.startswith('RG-AP'):
                product_brand = '锐捷'
            
            if product_brand and product_brand in default_mapping:
                for brand in brands:
                    if brand != product_brand and brand in default_mapping[product_brand]:
                        competitors.append({
                            'brand': brand,
                            'code': default_mapping[product_brand][brand]
                        })
        
        return {
            'raw_response': '(mock数据)',
            'competitors': competitors
        }


class CompetitorMatchValidator:
    def __init__(self):
        self.fetcher = ProductDataFetcher()
        self.evaluator = SimilarityEvaluator()
        self.parser = ProductNamingParser()
        self.doubao = DoubaoClient()
        
        self.all_products_cache = None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        if self.all_products_cache is None:
            self.all_products_cache = self.fetcher.get_all_products_summary()
        return self.all_products_cache
    
    def _is_target_product_type(self, product_code: str) -> bool:
        naming = self.parser.parse(product_code)
        product_type = naming.get('product_type', '')
        details = naming.get('details', {})
        switch_level = details.get('switch_level', '')
        
        if product_type == '无线AP':
            return True
        if product_type == '交换机' and '接入' in switch_level:
            return True
        return False
    
    def get_test_products(self, limit_per_brand=10) -> List[Dict[str, Any]]:
        all_products = self.get_all_products()
        
        by_brand = {}
        for p in all_products:
            brand = self.evaluator._extract_brand(p) or '未知'
            if brand not in by_brand:
                by_brand[brand] = []
            
            code = p.get('product_code', '')
            if self._is_target_product_type(code):
                by_brand[brand].append(p)
        
        print(f"=" * 80)
        print(f"数据库目标产品统计（接入交换机 + 无线AP）")
        print(f"=" * 80)
        for brand, products in sorted(by_brand.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {brand}: {len(products)} 个产品")
        
        test_products = []
        for brand in ['华为', 'H3C', '锐捷']:
            if brand in by_brand:
                products = by_brand[brand][:limit_per_brand]
                for p in products:
                    full_product = self.fetcher.get_product_by_code(p.get('product_code'))
                    if full_product:
                        test_products.append(full_product)
        
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
                    'score': result['total_score'],
                    'breakdown': result['breakdown']
                })
        
        evaluated.sort(key=lambda x: x['score'], reverse=True)
        
        selected = []
        used_brands = set()
        for item in evaluated:
            if len(selected) >= limit:
                break
            brand = item['brand']
            if brand not in used_brands:
                selected.append(item)
                used_brands.add(brand)
        
        remaining_needed = limit - len(selected)
        if remaining_needed > 0:
            for item in evaluated:
                if remaining_needed <= 0:
                    break
                if item not in selected:
                    selected.append(item)
                    remaining_needed -= 1
        
        return selected
    
    def _normalize_code(self, code: str) -> str:
        if not code:
            return ''
        return code.upper().replace('-', '').replace('_', '').replace(' ', '')
    
    def _code_similarity(self, code1: str, code2: str) -> float:
        if not code1 or not code2:
            return 0.0
        
        norm1 = self._normalize_code(code1)
        norm2 = self._normalize_code(code2)
        
        if norm1 == norm2:
            return 1.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _find_best_match(self, target_code: str, local_codes: List[str]) -> Optional[Dict[str, Any]]:
        best_match = None
        best_score = 0.0
        
        for local_code in local_codes:
            similarity = self._code_similarity(target_code, local_code)
            if similarity > best_score:
                best_score = similarity
                best_match = {'code': local_code, 'similarity': similarity}
        
        return best_match
    
    def compare_results(self, target_product: Dict[str, Any], 
                       local_competitors: List[Dict[str, Any]],
                       doubao_result: Dict[str, Any]) -> Dict[str, Any]:
        
        target_code = target_product.get('product_code', '')
        target_name = target_product.get('product_name', '')
        
        local_codes = [c['code'] for c in local_competitors]
        doubao_competitors = doubao_result.get('competitors', [])
        doubao_codes = [c['code'] for c in doubao_competitors]
        
        matched = []
        missed = []
        extra = []
        
        for doubao_comp in doubao_competitors:
            doubao_code = doubao_comp['code']
            doubao_brand = doubao_comp['brand']
            
            best_match = self._find_best_match(doubao_code, local_codes)
            
            if best_match and best_match['similarity'] >= 0.8:
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
                best_doubao_match = self._find_best_match(local_code, doubao_codes)
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
            'local_competitors': [
                {
                    'code': c['code'],
                    'name': c['name'],
                    'brand': c['brand'],
                    'score': c['score']
                } for c in local_competitors
            ],
            'doubao_competitors': doubao_competitors,
            'doubao_raw_response': doubao_result.get('raw_response', ''),
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
    
    def run_tests(self, limit_per_brand: int = 10, sleep_interval: float = 1.0) -> Dict[str, Any]:
        print(f"\n{'=' * 80}")
        print(f"竞品匹配验证测试 - 与豆包结果对比")
        print(f"{'=' * 80}")
        
        test_products = self.get_test_products(limit_per_brand=limit_per_brand)
        print(f"\n选取测试产品数: {len(test_products)}")
        
        all_results = []
        summary = {
            'total_products': len(test_products),
            'total_matched': 0,
            'total_missed': 0,
            'total_extra': 0,
            'avg_precision': 0,
            'avg_recall': 0,
            'avg_f1': 0,
            'by_brand': {}
        }
        
        for i, target in enumerate(test_products, 1):
            target_code = target.get('product_code', '')
            target_name = target.get('product_name', '')
            target_brand = self.evaluator._extract_brand(target)
            
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(test_products)}] 目标产品: {target_name} ({target_code}) [{target_brand}]")
            print(f"{'=' * 80}")
            
            local_competitors = self.match_local_competitors(target, limit=3)
            
            print(f"\n本地匹配结果 ({len(local_competitors)} 个):")
            for j, comp in enumerate(local_competitors, 1):
                print(f"  [{j}] {comp['name']} ({comp['code']}) - {comp['brand']} - {comp['score']}分")
            
            doubao_result = self.doubao.query_competitors(target_name, target_code)
            doubao_competitors = doubao_result.get('competitors', [])
            
            print(f"\n豆包返回结果 ({len(doubao_competitors)} 个):")
            for j, comp in enumerate(doubao_competitors, 1):
                print(f"  [{j}] {comp['code']} - {comp['brand']}")
            
            comparison = self.compare_results(target, local_competitors, doubao_result)
            
            print(f"\n对比分析:")
            print(f"  匹配成功: {len(comparison['matched'])} 个")
            print(f"  遗漏(本地未匹配到但豆包推荐): {len(comparison['missed'])} 个")
            for miss in comparison['missed']:
                print(f"    - {miss['doubao_code']} ({miss['doubao_brand']})")
            print(f"  额外(本地匹配到但豆包未推荐): {len(comparison['extra'])} 个")
            for ext in comparison['extra']:
                print(f"    - {ext['local_code']} ({ext['local_brand']}) - {ext['local_score']}分")
            
            print(f"\n指标:")
            metrics = comparison['metrics']
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1 Score: {metrics['f1_score']:.4f}")
            
            all_results.append(comparison)
            
            summary['total_matched'] += len(comparison['matched'])
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
                    'precision': 0,
                    'recall': 0,
                    'f1': 0
                }
            summary['by_brand'][target_brand]['count'] += 1
            summary['by_brand'][target_brand]['matched'] += len(comparison['matched'])
            summary['by_brand'][target_brand]['missed'] += len(comparison['missed'])
            summary['by_brand'][target_brand]['extra'] += len(comparison['extra'])
            summary['by_brand'][target_brand]['precision'] += metrics['precision']
            summary['by_brand'][target_brand]['recall'] += metrics['recall']
            summary['by_brand'][target_brand]['f1'] += metrics['f1_score']
            
            if i < len(test_products):
                time.sleep(sleep_interval)
        
        if len(test_products) > 0:
            summary['avg_precision'] = round(summary['avg_precision'] / len(test_products), 4)
            summary['avg_recall'] = round(summary['avg_recall'] / len(test_products), 4)
            summary['avg_f1'] = round(summary['avg_f1'] / len(test_products), 4)
        
        for brand_data in summary['by_brand'].values():
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
        for brand, brand_data in summary['by_brand'].items():
            print(f"\n  {brand}:")
            print(f"    测试数: {brand_data['count']}")
            print(f"    匹配数: {brand_data['matched']}")
            print(f"    遗漏数: {brand_data['missed']}")
            print(f"    额外数: {brand_data['extra']}")
            print(f"    Precision: {brand_data['precision']:.4f}")
            print(f"    Recall: {brand_data['recall']:.4f}")
            print(f"    F1: {brand_data['f1']:.4f}")
        
        return {
            'summary': summary,
            'results': all_results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = 'competitor_validation_results.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {filename}")


if __name__ == '__main__':
    validator = CompetitorMatchValidator()
    results = validator.run_tests(limit_per_brand=3)
    validator.save_results(results)
    print(f"\n{'=' * 80}")
    print(f"测试完成")
    print(f"{'=' * 80}")
