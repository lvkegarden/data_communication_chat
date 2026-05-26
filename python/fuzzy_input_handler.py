import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from product_naming_parser import ProductNamingParser
from similarity_evaluator import SimilarityEvaluator
from product_data_fetcher import ProductDataFetcher

logger = logging.getLogger(__name__)


@dataclass
class FuzzyMatchResult:
    product_code: str
    product_name: str
    brand: str
    category: str
    match_score: float
    match_reason: str
    matched_fields: List[str]


@dataclass
class FuzzyInputResult:
    is_fuzzy: bool
    original_input: str
    parsed_info: Dict[str, Any]
    candidates: List[FuzzyMatchResult]
    best_match: Optional[FuzzyMatchResult]
    confidence_level: str
    needs_user_confirmation: bool
    suggested_message: str


class FuzzyInputHandler:
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.60
    LOW_CONFIDENCE_THRESHOLD = 0.30

    def __init__(self, data_fetcher: ProductDataFetcher = None, 
                 naming_parser: ProductNamingParser = None,
                 similarity_evaluator: SimilarityEvaluator = None):
        self.data_fetcher = data_fetcher or ProductDataFetcher()
        self.naming_parser = naming_parser or ProductNamingParser()
        self.similarity_evaluator = similarity_evaluator or SimilarityEvaluator(self.naming_parser)
        logger.info("FuzzyInputHandler initialized")

    def handle(self, input_text: str) -> FuzzyInputResult:
        logger.info("Processing fuzzy input: %s", input_text[:50])
        
        parsed_info = self._parse_fuzzy_input(input_text)
        is_fuzzy = self._is_fuzzy_input(parsed_info, input_text)
        
        if not is_fuzzy:
            logger.info("Input is not fuzzy, returning direct match result")
            return FuzzyInputResult(
                is_fuzzy=False,
                original_input=input_text,
                parsed_info=parsed_info,
                candidates=[],
                best_match=None,
                confidence_level="direct",
                needs_user_confirmation=False,
                suggested_message=""
            )
        
        logger.info("Input is fuzzy, searching for candidates")
        candidates = self._find_candidates(parsed_info)
        
        if not candidates:
            logger.warning("No candidates found for fuzzy input")
            return FuzzyInputResult(
                is_fuzzy=True,
                original_input=input_text,
                parsed_info=parsed_info,
                candidates=[],
                best_match=None,
                confidence_level="none",
                needs_user_confirmation=True,
                suggested_message=f"抱歉，我没有找到与'{input_text}'相关的产品。请提供更详细的产品型号信息。"
            )
        
        candidates.sort(key=lambda x: x.match_score, reverse=True)
        
        best_match = candidates[0] if candidates else None
        confidence_level = self._calculate_confidence(best_match)
        needs_user_confirmation = confidence_level != "high"
        
        suggested_message = self._generate_suggestion(candidates, confidence_level, input_text)
        
        logger.info("Found %d candidates, best match: %s (score: %.2f, confidence: %s)",
                   len(candidates), 
                   best_match.product_code if best_match else "None",
                   best_match.match_score if best_match else 0,
                   confidence_level)
        
        return FuzzyInputResult(
            is_fuzzy=True,
            original_input=input_text,
            parsed_info=parsed_info,
            candidates=candidates,
            best_match=best_match,
            confidence_level=confidence_level,
            needs_user_confirmation=needs_user_confirmation,
            suggested_message=suggested_message
        )

    def _parse_fuzzy_input(self, input_text: str) -> Dict[str, Any]:
        parsed = {
            'original': input_text,
            'product_code_candidate': None,
            'brand': None,
            'product_type': None,
            'series_pattern': None,
            'is_partial': False,
            'keywords': []
        }
        
        clean_input = input_text.upper().strip()
        
        brand_patterns = {
            '华为': ['华为', 'HUAWEI', 'AIR-ENGINE'],
            'H3C': ['H3C', '华三', '新华三'],
            '锐捷': ['锐捷', 'RUIJIE', 'RG-']
        }
        
        for brand, patterns in brand_patterns.items():
            for pattern in patterns:
                if pattern.upper() in clean_input:
                    parsed['brand'] = brand
                    break
            if parsed['brand']:
                break
        
        type_patterns = {
            '交换机': ['交换机', 'SWITCH', 'SW'],
            '无线AP': ['AP', '无线', 'WIFI', 'WLan', 'ACCESS POINT'],
            '无线控制器': ['AC', '控制器', 'WLC', '无线控制']
        }
        
        for ptype, patterns in type_patterns.items():
            for pattern in patterns:
                if pattern.upper() in clean_input:
                    parsed['product_type'] = ptype
                    break
            if parsed['product_type']:
                break
        
        code_match = re.search(r'([A-Z]+[A-Z0-9\-]*)', clean_input)
        if code_match:
            code_candidate = code_match.group(1)
            if len(code_candidate) >= 2:
                parsed['product_code_candidate'] = code_candidate
                
                naming_result = self.naming_parser.parse(code_candidate)
                if naming_result.get('brand') and naming_result['brand'] != '未知':
                    parsed['brand'] = naming_result['brand']
                if naming_result.get('product_type'):
                    parsed['product_type'] = naming_result['product_type']
                
                if not self._is_complete_model(code_candidate, naming_result):
                    parsed['is_partial'] = True
                    parsed['series_pattern'] = self._extract_series_pattern(code_candidate)
        
        keywords = re.findall(r'[A-Za-z0-9]+', input_text)
        parsed['keywords'] = [kw for kw in keywords if len(kw) >= 2]
        
        logger.info("Parsed fuzzy input: %s", parsed)
        return parsed

    def _is_complete_model(self, code: str, naming_result: Dict[str, Any]) -> bool:
        if len(code) < 6:
            return False
        
        details = naming_result.get('details', {})
        code_upper = code.upper()
        
        if naming_result.get('product_type') == '交换机':
            if code.startswith('S') and re.match(r'^S\d+$', code):
                return False
            
            if re.search(r'L\d+[T|P|S]', code_upper):
                return True
            
            if code_upper.endswith(('-EI', '-SI', '-LI', '-HI', '-EA', '-V2', '-V3', '-PWR', '-AC', '-DC')):
                return True
            
            if code.count('-') >= 2 and len(code) >= 12:
                return True
            
            if details.get('port_count') and details.get('feature_level'):
                return True
            
            return False
        
        if naming_result.get('product_type') == '无线AP':
            if 'AIRENGINE' in code_upper and re.search(r'AIRENGINE\s*\d+', code_upper):
                if re.search(r'-X[0-9]+', code_upper) or re.search(r'PRO', code_upper):
                    return True
            
            if code_upper.startswith('RG-AP') and re.search(r'\(TR\)|\(AR\)|\(D\)|\(C\)|\(E\)|\(I\)$', code_upper):
                return True
            
            if code_upper.startswith('WA') and code_upper.endswith(('FIT', 'HI', 'SI', 'EI', 'LI')):
                return True
            
            if len(code) >= 12:
                if details.get('form_factor'):
                    return True
            
            return False
        
        if naming_result.get('parsed') and len(code) >= 12:
            return True
        
        return False

    def _extract_series_pattern(self, code: str) -> str:
        match = re.match(r'^([A-Z]+\d+)', code.upper())
        if match:
            return match.group(1)
        
        match = re.match(r'^(RG-[A-Z]+\d+)', code.upper())
        if match:
            return match.group(1)
        
        return code.upper()

    def _is_fuzzy_input(self, parsed_info: Dict[str, Any], original_input: str) -> bool:
        if parsed_info.get('is_partial'):
            return True
        
        code_candidate = parsed_info.get('product_code_candidate')
        if code_candidate:
            if len(code_candidate) < 5:
                return True
            if len(code_candidate) == 5 and re.match(r'^[A-Z]+\d{2,}$', code_candidate):
                return True
        
        if parsed_info.get('brand') and not parsed_info.get('product_code_candidate'):
            return True
        
        if parsed_info.get('product_type') and not parsed_info.get('product_code_candidate'):
            return True
        
        if len(parsed_info.get('keywords', [])) > 0 and not parsed_info.get('product_code_candidate'):
            return True
        
        return False

    def _find_candidates(self, parsed_info: Dict[str, Any]) -> List[FuzzyMatchResult]:
        candidates = []
        
        all_products = self.data_fetcher.get_all_products_summary()
        logger.info("Total products in database: %d", len(all_products))
        
        for product in all_products:
            match_score, matched_fields = self._calculate_match_score(product, parsed_info)
            
            if match_score > 0:
                candidates.append(FuzzyMatchResult(
                    product_code=product.get('product_code', ''),
                    product_name=product.get('product_name', ''),
                    brand=self.similarity_evaluator._extract_brand(product),
                    category=product.get('category', ''),
                    match_score=match_score,
                    match_reason=', '.join(matched_fields) if matched_fields else '部分匹配',
                    matched_fields=matched_fields
                ))
        
        candidates = [c for c in candidates if c.match_score >= self.LOW_CONFIDENCE_THRESHOLD]
        
        if len(candidates) > 10:
            candidates.sort(key=lambda x: x.match_score, reverse=True)
            candidates = candidates[:10]
        
        return candidates

    def _calculate_match_score(self, product: Dict[str, Any], parsed_info: Dict[str, Any]) -> Tuple[float, List[str]]:
        score = 0.0
        matched_fields = []
        total_weight = 0.0
        
        product_code = product.get('product_code', '').upper()
        product_name = product.get('product_name', '')
        category = product.get('category', '').lower()
        series = product.get('series', '')
        
        product_brand = self.similarity_evaluator._extract_brand(product)
        product_naming = self.naming_parser.parse(product.get('product_code', ''))
        product_type = product_naming.get('product_type')
        
        code_candidate = parsed_info.get('product_code_candidate')
        is_partial_match = code_candidate and product_code != code_candidate
        
        if parsed_info.get('brand'):
            total_weight += 30
            if product_brand == parsed_info['brand']:
                score += 30
                matched_fields.append(f'品牌匹配: {parsed_info["brand"]}')
            elif product_brand:
                score -= 10
        
        if parsed_info.get('product_type'):
            total_weight += 25
            if product_type == parsed_info['product_type']:
                score += 25
                matched_fields.append(f'产品类型匹配: {parsed_info["product_type"]}')
            elif category and parsed_info['product_type'].lower() in category:
                score += 20
                matched_fields.append(f'产品类别匹配: {category}')
        
        if parsed_info.get('series_pattern'):
            total_weight += 35
            series_pattern = parsed_info['series_pattern']
            
            if product_code.startswith(series_pattern):
                if is_partial_match:
                    score += 25
                    matched_fields.append(f'型号前缀匹配: {series_pattern}')
                else:
                    score += 35
                    matched_fields.append(f'型号前缀精确匹配: {series_pattern}')
            elif series_pattern in product_code:
                if is_partial_match:
                    score += 20
                    matched_fields.append(f'型号包含匹配: {series_pattern}')
                else:
                    score += 28
                    matched_fields.append(f'型号包含匹配: {series_pattern}')
            elif series and series_pattern in series:
                score += 15
                matched_fields.append(f'系列匹配: {series}')
        
        if code_candidate:
            total_weight += 50
            
            if product_code == code_candidate:
                score += 50
                matched_fields.append('型号完全匹配')
            elif product_code.startswith(code_candidate):
                score += 28
                matched_fields.append(f'型号前缀匹配: {code_candidate}')
            elif code_candidate in product_code:
                score += 18
                matched_fields.append(f'型号包含匹配: {code_candidate}')
            
            code_similarity = self._calculate_code_similarity(code_candidate, product_code)
            if code_similarity > 0.6 and code_similarity < 1.0:
                similarity_score = int(15 * code_similarity)
                score += similarity_score
                matched_fields.append(f'型号相似度: {int(code_similarity*100)}%')
        
        keywords = parsed_info.get('keywords', [])
        if code_candidate:
            keywords = [kw for kw in keywords if kw.upper() not in code_candidate]
        
        for keyword in keywords:
            keyword_upper = keyword.upper()
            if keyword_upper in product_code:
                score += 3
                matched_fields.append(f'关键词匹配: {keyword}')
            elif keyword in product_name:
                score += 2
                matched_fields.append(f'名称关键词: {keyword}')
        
        max_score = max(total_weight, 50)
        normalized_score = min(score / max_score, 1.0) if max_score > 0 else 0
        
        if is_partial_match and normalized_score > 0.9:
            normalized_score = 0.82
        
        return normalized_score, matched_fields

    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        if not code1 or not code2:
            return 0.0
        
        code1 = code1.upper()
        code2 = code2.upper()
        
        if code1 == code2:
            return 1.0
        
        if code2.startswith(code1) or code1.startswith(code2):
            return 0.9
        
        common_chars = set(code1) & set(code2)
        all_chars = set(code1) | set(code2)
        
        if all_chars:
            return len(common_chars) / len(all_chars) * 0.5
        
        return 0.0

    def _calculate_confidence(self, best_match: Optional[FuzzyMatchResult]) -> str:
        if not best_match:
            return "none"
        
        score = best_match.match_score
        
        if score >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        elif score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return "medium"
        elif score >= self.LOW_CONFIDENCE_THRESHOLD:
            return "low"
        
        return "none"

    def _generate_suggestion(self, candidates: List[FuzzyMatchResult], 
                           confidence_level: str, 
                           original_input: str) -> str:
        if confidence_level == "high" and candidates:
            best = candidates[0]
            return f"我找到一个高置信度的匹配产品：{best.product_name} ({best.product_code})。是否需要我为您介绍这个产品？"
        
        if confidence_level == "medium" and len(candidates) >= 1:
            suggestion = f"我找到多个与'{original_input}'相关的产品，请您选择：\n"
            for i, candidate in enumerate(candidates[:5], 1):
                suggestion += f"{i}. {candidate.product_name} ({candidate.product_code}) - {candidate.category}\n"
            suggestion += "\n请告诉我您想了解哪个产品，或者提供更详细的型号信息。"
            return suggestion
        
        if confidence_level == "low" and len(candidates) >= 1:
            suggestion = f"以下是可能与'{original_input}'相关的产品：\n"
            for i, candidate in enumerate(candidates[:5], 1):
                suggestion += f"{i}. {candidate.product_name} ({candidate.product_code})\n"
            suggestion += "\n这些产品的匹配度较低，请提供更详细的产品型号以获得更精确的结果。"
            return suggestion
        
        return f"抱歉，我没有找到与'{original_input}'相关的产品。请提供更详细的产品型号信息。"

    def get_confidence_levels(self) -> Dict[str, Dict[str, Any]]:
        return {
            "high": {
                "threshold": self.HIGH_CONFIDENCE_THRESHOLD,
                "description": "高置信度，自动使用最佳匹配",
                "needs_confirmation": False
            },
            "medium": {
                "threshold": self.MEDIUM_CONFIDENCE_THRESHOLD,
                "description": "中等置信度，需要用户确认",
                "needs_confirmation": True
            },
            "low": {
                "threshold": self.LOW_CONFIDENCE_THRESHOLD,
                "description": "低置信度，建议用户提供更多信息",
                "needs_confirmation": True
            },
            "none": {
                "threshold": 0,
                "description": "无匹配结果",
                "needs_confirmation": True
            }
        }
