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


class BrowserDoubaoClient:
    """
    使用浏览器访问豆包进行竞品分析
    """
    
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.llm_available = False
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            self.llm_available = True
        except ImportError:
            print("警告：openai库未安装，使用mock数据")
            self.llm_available = False
    
    def query_competitors(self, product_name: str, product_code: str, brands: List[str] = ['华为', 'H3C', '锐捷'] ) -> Dict[str, Any]:
        """
        查询竞品
        """
        if not self.llm_available or not self.api_key or self.api_key == "your-dashscope-api-key-here":
            return self._get_mock_competitors(product_code, brands)
        
        # 解析目标品牌
        target_brand = self._guess_brand(product_code)
        
        brands_str = '、'.join(brands)
        query = f"{product_name} (型号: {product_code}) 产品 竞品分析，给出 {brands_str} 三个品牌的竞品名称"
        
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

        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            print(f"\n豆包原始返回内容:\n{content}")
            return self._parse_response(content, brands, product_code)
        except Exception as e:
            print(f"豆包API调用失败: {e}")
            return self._get_mock_competitors(product_code, brands)
    
    def _parse_response(self, content: str, brands: List[str], target_code: str = None) -> Dict[str, Any]:
        """
        解析豆包的响应
        """
        result = {
            'raw_response': content,
            'competitors': []
        }
        
        # 解析目标品牌
        target_brand = self._guess_brand(target_code) if target_code else None
        
        # 尝试匹配各种格式
        brand_patterns = {
            '华为': r'华为[：:]\s*([^\n]+)',
            'H3C': r'H3C[：:]\s*([^\n]+)',
            '锐捷': r'锐捷[：:]\s*([^\n]+)'
        }
        
        for brand in brands:
            # 跳过目标品牌
            if target_brand and brand == target_brand:
                continue
                
            pattern = brand_patterns.get(brand, '')
            if pattern:
                matches = re.findall(pattern, content)
                for code_list in matches:
                    # 处理逗号分隔的多个型号
                    codes = re.split(r'[,，]', code_list.strip())
                    for code in codes:
                        code = code.strip()
                        if code:
                            result['competitors'].append({
                                'brand': brand,
                                'code': code
                            })
        
        # 如果没有找到，尝试更宽松的匹配
        if not result['competitors']:
            lines = content.strip().split('\n')
            for line in lines:
                for brand in brands:
                    # 跳过目标品牌
                    if target_brand and brand == target_brand:
                        continue
                        
                    if brand in line:
                        # 提取型号
                        code_match = re.search(r'[^\s，、：:]*S\d+[^\s，、：:]*|[^\s，、：:]*RG-[^\s，、：:]*|[^\s，、：:]*WA\d+[^\s，、：:]*|[^\s，、：:]*AirEngine[^\s，、：:]*', line)
                        if code_match:
                            code = code_match.group(0).strip()
                            if code:
                                result['competitors'].append({
                                    'brand': brand,
                                    'code': code
                                })
        
        return result
    
    def _guess_brand(self, product_code: str) -> str:
        """
        猜测产品品牌
        """
        if product_code.startswith('S'):
            if '5735' in product_code or '5731' in product_code or '5720' in product_code:
                return '华为'
            elif '5130' in product_code or '5560' in product_code or '5800' in product_code:
                return 'H3C'
        elif product_code.startswith('RG-'):
            return '锐捷'
        elif product_code.startswith('AirEngine'):
            return '华为'
        elif product_code.startswith('WA'):
            return 'H3C'
        return '未知'
    
    def _get_mock_competitors(self, product_code: str, brands: List[str]) -> Dict[str, Any]:
        """
        获取mock竞品数据
        """
        mock_data = {
            'S5735-L-V2': {
                '华为': [],
                'H3C': ['S5130S-EI', 'S5130S-HI-G', 'S5800'],
                '锐捷': ['RG-S5760-X', 'RG-S5310-E', 'RG-S5300-L']
            },
            'S5130S-EI': {
                '华为': ['S5735-L-V2', 'S5731-H'],
                'H3C': [],
                '锐捷': ['RG-S5310-E', 'RG-S5750V2-L']
            },
            'RG-S5310-E': {
                '华为': ['S5735-L-V2', 'S5731-H'],
                'H3C': ['S5130S-EI', 'S5800'],
                '锐捷': []
            }
        }
        
        # 解析目标品牌
        target_brand = self._guess_brand(product_code)
        
        competitors = []
        
        if product_code in mock_data:
            for brand in brands:
                # 跳过目标品牌
                if target_brand and brand == target_brand:
                    continue
                    
                for code in mock_data[product_code].get(brand, []):
                    competitors.append({'brand': brand, 'code': code})
        else:
            # 默认映射
            default_mapping = {
                '华为': {'H3C': 'S5130S-EI', '锐捷': 'RG-S5310-E'},
                'H3C': {'华为': 'S5735-L-V2', '锐捷': 'RG-S5310-E'},
                '锐捷': {'华为': 'S5735-L-V2', 'H3C': 'S5130S-EI'}
            }
            
            product_brand = target_brand
            
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


class CompetitorComparisonTest:
    """
    竞品分析对比测试
    """
    
    def __init__(self):
        self.fetcher = ProductDataFetcher()
        self.evaluator = SimilarityEvaluator()
        self.parser = ProductNamingParser()
        self.doubao = BrowserDoubaoClient()
        self.all_products = None
    
    def get_all_products(self):
        """
        获取所有产品
        """
        if self.all_products is None:
            self.all_products = self.fetcher.get_all_products_summary()
        return self.all_products
    
    def is_target_product_type(self, product_code: str) -> bool:
        """
        判断是否是目标产品类型（接入交换机、无线AP）
        """
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
        """
        从数据库中抽取测试产品
        """
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
    
    def match_local_competitors(self, target_product: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        本地匹配竞品
        """
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
            final_result.extend(products[:2])  # 每个品牌最多2个
        
        final_result.sort(key=lambda x: x['score'], reverse=True)
        return final_result[:limit]
    
    def normalize_code(self, code: str) -> str:
        """
        标准化产品型号
        """
        if not code:
            return ''
        return code.upper().replace('-', '').replace('_', '').replace(' ', '')
    
    def code_similarity(self, code1: str, code2: str) -> float:
        """
        计算产品型号相似度
        """
        if not code1 or not code2:
            return 0.0
        
        norm1 = self.normalize_code(code1)
        norm2 = self.normalize_code(code2)
        
        if norm1 == norm2:
            return 1.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def compare_results(self, target_product: Dict[str, Any], 
                       local_competitors: List[Dict[str, Any]],
                       doubao_competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对比本地匹配和豆包结果
        """
        target_code = target_product.get('product_code', '')
        target_name = target_product.get('product_name', '')
        
        local_codes = [c['code'] for c in local_competitors]
        
        matched = []
        missed = []
        extra = []
        
        for doubao_comp in doubao_competitors:
            doubao_code = doubao_comp['code']
            doubao_brand = doubao_comp['brand']
            
            best_match = None
            best_score = 0.0
            for local_code in local_codes:
                similarity = self.code_similarity(doubao_code, local_code)
                if similarity > best_score:
                    best_score = similarity
                    best_match = {'code': local_code, 'similarity': similarity}
            
            if best_match and best_match['similarity'] >= 0.55:
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
                best_doubao_match = None
                best_doubao_score = 0.0
                for dc in doubao_competitors:
                    similarity = self.code_similarity(local_code, dc['code'])
                    if similarity > best_doubao_score:
                        best_doubao_score = similarity
                        best_doubao_match = {'code': dc['code'], 'similarity': similarity}
                
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
    
    def run_tests(self, test_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        运行所有测试
        """
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
            target_brand = self.evaluator._extract_brand(target_product)
            
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(test_products)}] 目标产品: {target_name} ({target_code}) [{target_brand}]")
            print(f"{'=' * 80}")
            
            local_competitors = self.match_local_competitors(target_product, limit=5)
            
            print(f"\n本地匹配结果 ({len(local_competitors)} 个):")
            for j, comp in enumerate(local_competitors, 1):
                print(f"  [{j}] {comp['name']} ({comp['code']}) - {comp['brand']} - {comp['score']}分")
            
            doubao_result = self.doubao.query_competitors(target_name, target_code)
            doubao_competitors = doubao_result.get('competitors', [])
            
            print(f"\n豆包返回结果 ({len(doubao_competitors)} 个):")
            for j, comp in enumerate(doubao_competitors, 1):
                print(f"  [{j}] {comp['code']} - {comp['brand']}")
            
            if doubao_competitors:
                comparison = self.compare_results(target_product, local_competitors, doubao_competitors)
                
                print(f"\n对比分析:")
                print(f"  匹配成功: {len(comparison['matched'])} 个")
                print(f"  遗漏: {len(comparison['missed'])} 个")
                if comparison['missed']:
                    for miss in comparison['missed']:
                        print(f"    - {miss['doubao_code']} ({miss['doubao_brand']})")
                print(f"  额外: {len(comparison['extra'])} 个")
                if comparison['extra']:
                    for ext in comparison['extra']:
                        print(f"    - {ext['local_code']} ({ext['local_brand']}) - {ext['local_score']}分")
                
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
        
        return {
            'summary': summary,
            'results': all_results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = 'doubao_comparison_results.json'):
        """
        保存结果
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {filename}")


def main():
    """
    主函数
    """
    test = CompetitorComparisonTest()
    
    print(f"\n{'=' * 80}")
    print(f"豆包竞品分析对比测试")
    print(f"{'=' * 80}")
    
    # 抽取测试产品（每个品牌10个，接入交换机和无线AP）
    test_products = test.extract_test_products(limit_per_brand=10)
    
    print(f"\n{'=' * 80}")
    print(f"测试产品列表")
    print(f"{'=' * 80}")
    for i, product in enumerate(test_products, 1):
        print(f"[{i}] {product.get('product_name')} ({product.get('product_code')})")
    
    if test_products:
        results = test.run_tests(test_products)
        test.save_results(results)
    
    print(f"\n{'=' * 80}")
    print(f"测试完成")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
