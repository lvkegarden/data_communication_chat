import logging
import json
from typing import Dict, List, Any, Tuple, Optional

from product_naming_parser import ProductNamingParser

logger = logging.getLogger(__name__)


class SimilarityCriteria:
    PRODUCT_TYPE_MATCH = 10
    NAMING_BRAND_MATCH = -100
    NAMING_SWITCH_LEVEL_MATCH = 20
    NAMING_SWITCH_LEVEL_MISMATCH_PENALTY = -15
    NAMING_FEATURE_LEVEL_MATCH = 15
    NAMING_FEATURE_LEVEL_MISMATCH_PENALTY = -10
    NAMING_POE_MATCH = 10
    NAMING_POE_MISMATCH_PENALTY = -5
    NAMING_PORT_COUNT_MATCH = 10
    NAMING_PORT_SPEED_MATCH = 10
    NAMING_FORM_FACTOR_MATCH = 10
    NAMING_WIFI_GENERATION_MATCH = 15
    NAMING_LEVEL_MATCH = 10
    NAMING_SPECIAL_FEATURE_MATCH = 10
    
    CATEGORY_MATCH = 15
    SERIES_PATTERN_MATCH = 30
    KEY_SPEC_SIMILARITY = 20
    TARGET_SCENARIO_MATCH = 10
    MIN_COMPETITOR_SCORE = 50
    SAME_BRAND_PENALTY = 100
    
    SWITCHING_CAPACITY_MATCH = 12
    PACKET_FORWARDING_MATCH = 12
    PORT_COUNT_MATCH = 8
    UPLINK_TYPE_MATCH = 6
    POE_MATCH = 5
    POWER_TYPE_MATCH = 3


class SimilarityEvaluator:
    def __init__(self, naming_parser: ProductNamingParser = None):
        logger.info("SimilarityEvaluator initialized")
        
        self.naming_parser = naming_parser or ProductNamingParser()
        
        self.series_patterns = {
            'S5735-L-V2': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5735': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5720': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5730': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5731': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5732': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5736': {'category': '接入交换机', 'port_range': (24, 48)},
            'RG-S2900': {'category': '接入交换机', 'port_range': (24, 48)},
            'RG-S29': {'category': '接入交换机', 'port_range': (24, 48)},
            'RG-S5750': {'category': '接入交换机', 'port_range': (24, 48)},
            'RG-S5760': {'category': '接入交换机', 'port_range': (24, 48)},
            'RG-S5300': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'RG-S53': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S5130': {'category': '接入交换机', 'port_range': (24, 48)},
            'S51': {'category': '接入交换机', 'port_range': (24, 48)},
            'S5560': {'category': '汇聚/接入交换机', 'port_range': (24, 48)},
            'S5590': {'category': '汇聚/接入交换机', 'port_range': (24, 48)},
            'S5580': {'category': '汇聚/接入交换机', 'port_range': (24, 48)},
            'S5570': {'category': '汇聚/接入交换机', 'port_range': (24, 48)},
            'S5500': {'category': '汇聚/接入交换机', 'port_range': (24, 48)},
            'S5820': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S5800': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S6520': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S6530': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S65': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S6800': {'category': '核心交换机', 'port_range': (48, 96)},
            'S68': {'category': '核心交换机', 'port_range': (48, 96)},
            'RG-S6120': {'category': '核心/汇聚交换机', 'port_range': (48, 96)},
            'RG-S61': {'category': '核心/汇聚交换机', 'port_range': (48, 96)},
            'S5755': {'category': '汇聚交换机', 'port_range': (24, 48)},
            'S6730': {'category': '核心交换机', 'port_range': (48, 96)},
            'S16700': {'category': '核心交换机', 'port_range': (0, 0)},
            'S12700': {'category': '核心交换机', 'port_range': (0, 0)},
            'S8700': {'category': '核心交换机', 'port_range': (0, 0)},
            'RG-S8600': {'category': '核心交换机', 'port_range': (0, 0)},
            'RG-S7800': {'category': '核心交换机', 'port_range': (0, 0)},
            'S12500': {'category': '核心交换机', 'port_range': (0, 0)},
            'S7000': {'category': '核心交换机', 'port_range': (0, 0)},
            'RG-AP8': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-AP7': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-AP6': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-AP5': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-AP4': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-AP2': {'category': '无线AP', 'port_range': (0, 0)},
            'AirEngine 87': {'category': '无线AP', 'port_range': (0, 0)},
            'AirEngine 67': {'category': '无线AP', 'port_range': (0, 0)},
            'AirEngine 97': {'category': 'AC控制器', 'port_range': (0, 0)},
            'AP90': {'category': '无线AP', 'port_range': (0, 0)},
            'AP80': {'category': '无线AP', 'port_range': (0, 0)},
            'AP70': {'category': '无线AP', 'port_range': (0, 0)},
            'AP60': {'category': '无线AP', 'port_range': (0, 0)},
            'AP40': {'category': '无线AP', 'port_range': (0, 0)},
            'WA66': {'category': '无线AP', 'port_range': (0, 0)},
            'WA65': {'category': '无线AP', 'port_range': (0, 0)},
            'WA6': {'category': '无线AP', 'port_range': (0, 0)},
            'WA5': {'category': '无线AP', 'port_range': (0, 0)},
            'WA4': {'category': '无线AP', 'port_range': (0, 0)},
            'RG-WS7': {'category': 'AC控制器', 'port_range': (0, 0)},
            'RG-WS6': {'category': 'AC控制器', 'port_range': (0, 0)},
            'WX55': {'category': 'AC控制器', 'port_range': (0, 0)},
            'WX35': {'category': 'AC控制器', 'port_range': (0, 0)},
            'WX25': {'category': 'AC控制器', 'port_range': (0, 0)},
            'AC68': {'category': 'AC控制器', 'port_range': (0, 0)},
            'AC65': {'category': 'AC控制器', 'port_range': (0, 0)},
        }
        
        self.product_aliases = {
            '华为': ['huawei', 'HUAWEI', '华为'],
            '锐捷': ['ruijie', 'RUIJIE', '锐捷', 'RG'],
            'H3C': ['h3c', 'H3C', '新华三'],
        }

    def evaluate(self, target_product: Dict[str, Any], candidate_product: Dict[str, Any]) -> Dict[str, Any]:
        scores = []
        score_breakdown = []
        
        target_code = target_product.get('product_code', '')
        candidate_code = candidate_product.get('product_code', '')
        
        target_naming = self.naming_parser.parse(target_code)
        candidate_naming = self.naming_parser.parse(candidate_code)
        
        target_brand = target_naming.get('brand') or self._extract_brand(target_product)
        candidate_brand = candidate_naming.get('brand') or self._extract_brand(candidate_product)
        
        if target_brand and candidate_brand and target_brand == candidate_brand:
            logger.info("Same brand detected (%s), penalizing", target_brand)
            return {
                'is_competitor': False,
                'total_score': 0,
                'reason': f'同品牌产品 ({target_brand})，不视为竞品',
                'breakdown': [{'category': '同品牌排除', 'score': -SimilarityCriteria.SAME_BRAND_PENALTY, 'detail': f'{target_brand} vs {candidate_brand}'}],
                'target_naming': target_naming,
                'candidate_naming': candidate_naming
            }
        
        if target_product.get('product_code') == candidate_product.get('product_code'):
            return {
                'is_competitor': False,
                'total_score': 0,
                'reason': '同一产品',
                'breakdown': [],
                'target_naming': target_naming,
                'candidate_naming': candidate_naming
            }
        
        naming_scores, naming_details = self._evaluate_naming_similarity(target_naming, candidate_naming)
        for ns, nd in zip(naming_scores, naming_details):
            scores.append(ns)
            score_breakdown.append(nd)
        
        product_type_score, product_type_detail = self._evaluate_product_type(target_product, candidate_product)
        scores.append(product_type_score)
        score_breakdown.append(product_type_detail)
        
        category_score, category_detail = self._evaluate_category(target_product, candidate_product)
        scores.append(category_score)
        score_breakdown.append(category_detail)
        
        series_score, series_detail = self._evaluate_series_pattern(target_product, candidate_product)
        scores.append(series_score)
        score_breakdown.append(series_detail)
        
        spec_score, spec_detail = self._evaluate_spec_similarity(target_product, candidate_product)
        scores.append(spec_score)
        score_breakdown.append(spec_detail)
        
        scenario_score, scenario_detail = self._evaluate_scenario(target_product, candidate_product)
        scores.append(scenario_score)
        score_breakdown.append(scenario_detail)
        
        total_score = sum(scores)
        is_competitor = total_score >= SimilarityCriteria.MIN_COMPETITOR_SCORE
        
        result = {
            'is_competitor': is_competitor,
            'total_score': total_score,
            'reason': '达到竞品阈值' if is_competitor else '未达到竞品阈值',
            'breakdown': score_breakdown,
            'target_brand': target_brand,
            'candidate_brand': candidate_brand,
            'target_naming': target_naming,
            'candidate_naming': candidate_naming
        }
        
        logger.info("Similarity evaluation (with naming): %s vs %s => score=%d, is_competitor=%s",
                   target_product.get('product_code'),
                   candidate_product.get('product_code'),
                   total_score, is_competitor)
        
        return result

    def _evaluate_naming_similarity(self, target_naming: Dict[str, Any], candidate_naming: Dict[str, Any]) -> Tuple[List[int], List[Dict[str, Any]]]:
        scores = []
        details = []
        
        target_details = target_naming.get('details', {})
        candidate_details = candidate_naming.get('details', {})
        
        target_type = target_naming.get('product_type')
        candidate_type = candidate_naming.get('product_type')
        
        if target_type and candidate_type:
            if target_type == candidate_type:
                scores.append(SimilarityCriteria.PRODUCT_TYPE_MATCH)
                details.append({
                    'category': '命名解析-产品类型匹配',
                    'score': SimilarityCriteria.PRODUCT_TYPE_MATCH,
                    'detail': target_type
                })
            else:
                scores.append(0)
                details.append({
                    'category': '命名解析-产品类型不匹配',
                    'score': 0,
                    'detail': f'{target_type} vs {candidate_type}'
                })
        
        if target_type == '交换机' or candidate_type == '交换机':
            target_switch_level = target_details.get('switch_level')
            candidate_switch_level = candidate_details.get('switch_level')
            
            if target_switch_level and candidate_switch_level:
                if target_switch_level == candidate_switch_level:
                    scores.append(SimilarityCriteria.NAMING_SWITCH_LEVEL_MATCH)
                    details.append({
                        'category': '命名解析-交换机等级匹配',
                        'score': SimilarityCriteria.NAMING_SWITCH_LEVEL_MATCH,
                        'detail': target_switch_level
                    })
                elif self._are_adjacent_switch_levels(target_switch_level, candidate_switch_level):
                    partial = int(SimilarityCriteria.NAMING_SWITCH_LEVEL_MATCH * 0.6)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-交换机等级相近',
                        'score': partial,
                        'detail': f'{target_switch_level} vs {candidate_switch_level}'
                    })
                else:
                    scores.append(SimilarityCriteria.NAMING_SWITCH_LEVEL_MISMATCH_PENALTY)
                    details.append({
                        'category': '命名解析-交换机等级不匹配(惩罚)',
                        'score': SimilarityCriteria.NAMING_SWITCH_LEVEL_MISMATCH_PENALTY,
                        'detail': f'{target_switch_level} vs {candidate_switch_level}'
                    })
            
            target_feature_level = target_details.get('feature_level')
            candidate_feature_level = candidate_details.get('feature_level')
            
            if target_feature_level and candidate_feature_level:
                if target_feature_level == candidate_feature_level:
                    scores.append(SimilarityCriteria.NAMING_FEATURE_LEVEL_MATCH)
                    details.append({
                        'category': '命名解析-功能等级匹配',
                        'score': SimilarityCriteria.NAMING_FEATURE_LEVEL_MATCH,
                        'detail': target_feature_level
                    })
                elif self._are_similar_feature_levels(target_feature_level, candidate_feature_level):
                    partial = int(SimilarityCriteria.NAMING_FEATURE_LEVEL_MATCH * 0.7)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-功能等级相近',
                        'score': partial,
                        'detail': f'{target_feature_level} vs {candidate_feature_level}'
                    })
                elif self._are_adjacent_feature_levels(target_feature_level, candidate_feature_level):
                    level_diff = self._get_feature_level_diff(target_feature_level, candidate_feature_level)
                    if level_diff == 1:
                        partial = int(SimilarityCriteria.NAMING_FEATURE_LEVEL_MATCH * 0.6)
                    else:
                        partial = int(SimilarityCriteria.NAMING_FEATURE_LEVEL_MATCH * 0.5)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-功能等级相近(差' + str(level_diff) + '级)',
                        'score': partial,
                        'detail': f'{target_feature_level} vs {candidate_feature_level}'
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-功能等级不匹配',
                        'score': 0,
                        'detail': f'{target_feature_level} vs {candidate_feature_level}'
                    })
            
            target_poe = target_details.get('poe')
            candidate_poe = candidate_details.get('poe')
            
            if target_poe is not None and candidate_poe is not None:
                if target_poe == candidate_poe:
                    scores.append(SimilarityCriteria.NAMING_POE_MATCH)
                    details.append({
                        'category': '命名解析-PoE支持匹配',
                        'score': SimilarityCriteria.NAMING_POE_MATCH,
                        'detail': '支持PoE' if target_poe else '不支持PoE'
                    })
                else:
                    scores.append(SimilarityCriteria.NAMING_POE_MISMATCH_PENALTY)
                    details.append({
                        'category': '命名解析-PoE支持不匹配(惩罚)',
                        'score': SimilarityCriteria.NAMING_POE_MISMATCH_PENALTY,
                        'detail': f'{"支持" if target_poe else "不支持"} vs {"支持" if candidate_poe else "不支持"}'
                    })
            
            target_port_count = target_details.get('port_count')
            candidate_port_count = candidate_details.get('port_count')
            
            if target_port_count and candidate_port_count:
                if target_port_count == candidate_port_count:
                    scores.append(SimilarityCriteria.NAMING_PORT_COUNT_MATCH)
                    details.append({
                        'category': '命名解析-端口数量匹配',
                        'score': SimilarityCriteria.NAMING_PORT_COUNT_MATCH,
                        'detail': f'{target_port_count}端口'
                    })
                elif abs(target_port_count - candidate_port_count) <= 8:
                    partial = int(SimilarityCriteria.NAMING_PORT_COUNT_MATCH * 0.7)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-端口数量相近',
                        'score': partial,
                        'detail': f'{target_port_count} vs {candidate_port_count}'
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-端口数量不匹配',
                        'score': 0,
                        'detail': f'{target_port_count} vs {candidate_port_count}'
                    })
            
            target_port_speed = target_details.get('port_speed')
            candidate_port_speed = candidate_details.get('port_speed')
            
            if target_port_speed and candidate_port_speed:
                if target_port_speed == candidate_port_speed:
                    scores.append(SimilarityCriteria.NAMING_PORT_SPEED_MATCH)
                    details.append({
                        'category': '命名解析-端口速率匹配',
                        'score': SimilarityCriteria.NAMING_PORT_SPEED_MATCH,
                        'detail': target_port_speed
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-端口速率不匹配',
                        'score': 0,
                        'detail': f'{target_port_speed} vs {candidate_port_speed}'
                    })
        
        if target_type == '无线AP' or candidate_type == '无线AP':
            target_wifi_gen = target_details.get('wifi_generation')
            candidate_wifi_gen = candidate_details.get('wifi_generation')
            
            if target_wifi_gen and candidate_wifi_gen:
                if target_wifi_gen == candidate_wifi_gen:
                    scores.append(SimilarityCriteria.NAMING_WIFI_GENERATION_MATCH)
                    details.append({
                        'category': '命名解析-WiFi代际匹配',
                        'score': SimilarityCriteria.NAMING_WIFI_GENERATION_MATCH,
                        'detail': target_wifi_gen
                    })
                elif self._are_adjacent_wifi_generations(target_wifi_gen, candidate_wifi_gen):
                    partial = int(SimilarityCriteria.NAMING_WIFI_GENERATION_MATCH * 0.6)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-WiFi代际相近',
                        'score': partial,
                        'detail': f'{target_wifi_gen} vs {candidate_wifi_gen}'
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-WiFi代际不匹配',
                        'score': 0,
                        'detail': f'{target_wifi_gen} vs {candidate_wifi_gen}'
                    })
            
            target_level = target_details.get('level')
            candidate_level = candidate_details.get('level')
            
            if target_level and candidate_level:
                if target_level == candidate_level:
                    scores.append(SimilarityCriteria.NAMING_LEVEL_MATCH)
                    details.append({
                        'category': '命名解析-产品定位匹配',
                        'score': SimilarityCriteria.NAMING_LEVEL_MATCH,
                        'detail': target_level
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-产品定位不匹配',
                        'score': 0,
                        'detail': f'{target_level} vs {candidate_level}'
                    })
            
            target_form = target_details.get('form_factor')
            candidate_form = candidate_details.get('form_factor')
            
            if target_form and candidate_form:
                if target_form == candidate_form:
                    scores.append(SimilarityCriteria.NAMING_FORM_FACTOR_MATCH)
                    details.append({
                        'category': '命名解析-产品形态匹配',
                        'score': SimilarityCriteria.NAMING_FORM_FACTOR_MATCH,
                        'detail': target_form
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-产品形态不匹配',
                        'score': 0,
                        'detail': f'{target_form} vs {candidate_form}'
                    })
            
            target_feature = target_details.get('special_feature')
            candidate_feature = candidate_details.get('special_feature')
            
            if target_feature and candidate_feature:
                if target_feature == candidate_feature:
                    scores.append(SimilarityCriteria.NAMING_SPECIAL_FEATURE_MATCH)
                    details.append({
                        'category': '命名解析-特殊功能匹配',
                        'score': SimilarityCriteria.NAMING_SPECIAL_FEATURE_MATCH,
                        'detail': target_feature
                    })
                elif self._are_similar_features(target_feature, candidate_feature):
                    partial = int(SimilarityCriteria.NAMING_SPECIAL_FEATURE_MATCH * 0.7)
                    scores.append(partial)
                    details.append({
                        'category': '命名解析-特殊功能相近',
                        'score': partial,
                        'detail': f'{target_feature} vs {candidate_feature}'
                    })
                else:
                    scores.append(0)
                    details.append({
                        'category': '命名解析-特殊功能不匹配',
                        'score': 0,
                        'detail': f'{target_feature} vs {candidate_feature}'
                    })
        
        return scores, details
    
    def _are_adjacent_switch_levels(self, level_a: str, level_b: str) -> bool:
        hierarchy = ['SOHO交换机', '接入交换机', '汇聚/接入交换机', '汇聚交换机', '核心/汇聚交换机', '核心交换机']
        
        if level_a in hierarchy and level_b in hierarchy:
            idx_a = hierarchy.index(level_a)
            idx_b = hierarchy.index(level_b)
            return abs(idx_a - idx_b) <= 1
        return False
    
    def _are_similar_feature_levels(self, level_a: str, level_b: str) -> bool:
        high_end = {'HI', 'EA', 'H'}
        mid_end = {'EI', 'E', 'I'}
        standard = {'SI', 'S'}
        basic = {'LI', 'L'}
        
        if level_a == level_b:
            return True
        
        if level_a in high_end and level_b in high_end:
            return True
        if level_a in mid_end and level_b in mid_end:
            return True
        if level_a in standard and level_b in standard:
            return True
        if level_a in basic and level_b in basic:
            return True
        
        return False
    
    def _get_feature_level_group(self, level: str) -> int:
        hierarchy = [
            ['HI', 'EA', 'H'],
            ['EI', 'E', 'I'],
            ['SI', 'S'],
            ['LI', 'L'],
        ]
        
        for i, group in enumerate(hierarchy):
            if level in group:
                return i
        return -1
    
    def _get_feature_level_diff(self, level_a: str, level_b: str) -> int:
        group_a = self._get_feature_level_group(level_a)
        group_b = self._get_feature_level_group(level_b)
        
        if group_a == -1 or group_b == -1:
            return 999
        
        return abs(group_a - group_b)
    
    def _are_adjacent_feature_levels(self, level_a: str, level_b: str) -> bool:
        diff = self._get_feature_level_diff(level_a, level_b)
        return diff >= 1 and diff <= 2
    
    def _are_adjacent_wifi_generations(self, gen_a: str, gen_b: str) -> bool:
        adjacent = [
            ('WiFi 5', 'WiFi 6'), ('WiFi 6', 'WiFi 5'),
            ('WiFi 6', 'WiFi 6/7'), ('WiFi 6/7', 'WiFi 6'),
            ('WiFi 6/7', 'WiFi 7'), ('WiFi 7', 'WiFi 6/7'),
        ]
        return (gen_a, gen_b) in adjacent
    
    def _are_similar_features(self, feat_a: str, feat_b: str) -> bool:
        similar = [
            ('AR', 'R'), ('R', 'AR'),
            ('D', 'AR'), ('AR', 'D'),
            ('D', 'R'), ('R', 'D'),
        ]
        return (feat_a, feat_b) in similar
    
    def _extract_brand(self, product: Dict[str, Any]) -> Optional[str]:
        product_name = product.get('product_name', '') or ''
        product_code = product.get('product_code', '') or ''
        specs_json = product.get('specs_json', '') or ''
        vendor_name = product.get('vendor_name', '') or ''
        source = product.get('source', '') or ''
        
        combined_text = f"{product_name} {product_code} {specs_json} {vendor_name} {source}"
        
        naming_result = self.naming_parser.parse(product_code)
        if naming_result.get('brand') and naming_result['brand'] != '未知':
            return naming_result['brand']
        
        if product_name.startswith('锐捷') or 'RG-' in product_code or product_code.startswith('RG'):
            return '锐捷'
        
        if product_name.startswith('华三') or product_name.startswith('H3C'):
            return 'H3C'
        
        if ('WA' in product_code and len(product_code) >= 3) or product_code.startswith('WX'):
            if not (product_code.startswith('WAC') or 'AirEngine' in combined_text):
                return 'H3C'
        
        if product_name.startswith('华为'):
            return '华为'
        
        if 'AirEngine' in combined_text or product_code.startswith('AC'):
            return '华为'
        
        if product_code.startswith('S'):
            if '锐捷' in combined_text or 'RG' in combined_text:
                return '锐捷'
            if '华三' in combined_text or 'H3C' in combined_text:
                return 'H3C'
            if '华为' in combined_text:
                return '华为'
        
        for brand, aliases in self.product_aliases.items():
            for alias in aliases:
                if alias in combined_text or alias.lower() in combined_text.lower():
                    return brand
        
        specs = {}
        if specs_json:
            try:
                specs = json.loads(specs_json) if isinstance(specs_json, str) else specs_json
            except:
                pass
        
        if '品牌' in specs:
            return specs['品牌']
        
        return None

    def _evaluate_product_type(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        target_specs = self._parse_specs(target.get('specs_json', ''))
        candidate_specs = self._parse_specs(candidate.get('specs_json', ''))
        
        target_type = target_specs.get('产品类型') or target.get('product_type') or ''
        candidate_type = candidate_specs.get('产品类型') or candidate.get('product_type') or ''
        
        if target_type and candidate_type and target_type == candidate_type:
            return SimilarityCriteria.PRODUCT_TYPE_MATCH, {
                'category': '产品类型匹配',
                'score': SimilarityCriteria.PRODUCT_TYPE_MATCH,
                'detail': f'{target_type}'
            }
        
        return 0, {'category': '产品类型不匹配', 'score': 0, 'detail': f'{target_type} vs {candidate_type}'}

    def _evaluate_category(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        target_category = target.get('category', '') or self._extract_category(target)
        candidate_category = candidate.get('category', '') or self._extract_category(candidate)
        
        if target_category and candidate_category:
            if target_category == candidate_category:
                return SimilarityCriteria.CATEGORY_MATCH, {
                    'category': '产品类别匹配',
                    'score': SimilarityCriteria.CATEGORY_MATCH,
                    'detail': f'{target_category}'
                }
        
        return 0, {'category': '产品类别不匹配', 'score': 0, 'detail': f'{target_category} vs {candidate_category}'}

    def _evaluate_series_pattern(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        target_code = target.get('product_code', '')
        candidate_code = candidate.get('product_code', '')
        
        if not target_code or not candidate_code:
            return 0, {'category': '系列模式匹配', 'score': 0, 'detail': '缺少产品型号'}
        
        target_pattern_info = None
        for pattern, info in self.series_patterns.items():
            if pattern in target_code:
                target_pattern_info = info
                break
        
        candidate_pattern_info = None
        for pattern, info in self.series_patterns.items():
            if pattern in candidate_code:
                candidate_pattern_info = info
                break
        
        if target_pattern_info and candidate_pattern_info:
            if target_pattern_info.get('category') == candidate_pattern_info.get('category'):
                return SimilarityCriteria.SERIES_PATTERN_MATCH, {
                    'category': '系列定位匹配',
                    'score': SimilarityCriteria.SERIES_PATTERN_MATCH,
                    'detail': f'{target_pattern_info.get("category")}'
                }
        
        return 0, {'category': '系列模式匹配', 'score': 0, 'detail': '定位不同'}

    def _evaluate_spec_similarity(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        target_specs = self._parse_specs(target.get('specs_json', ''))
        candidate_specs = self._parse_specs(candidate.get('specs_json', ''))
        
        if not target_specs or not candidate_specs:
            return 0, {'category': '规格相似度', 'score': 0, 'detail': '缺少规格数据'}
        
        score = 0
        matched_fields = []
        detail_breakdown = []
        
        target_cap = self._parse_numeric_spec(target_specs.get('交换容量', ''))
        candidate_cap = self._parse_numeric_spec(candidate_specs.get('交换容量', ''))
        if target_cap and candidate_cap:
            ratio = min(target_cap, candidate_cap) / max(target_cap, candidate_cap)
            if ratio >= 0.95:
                score += SimilarityCriteria.SWITCHING_CAPACITY_MATCH
                matched_fields.append('交换容量完全匹配')
                detail_breakdown.append(f'交换容量完全匹配: {target_cap} vs {candidate_cap}')
            elif ratio >= 0.8:
                partial = int(SimilarityCriteria.SWITCHING_CAPACITY_MATCH * 0.7)
                score += partial
                matched_fields.append('交换容量相似')
                detail_breakdown.append(f'交换容量相似({ratio:.1%}): {partial}分')
            elif ratio >= 0.6:
                partial = int(SimilarityCriteria.SWITCHING_CAPACITY_MATCH * 0.4)
                score += partial
                matched_fields.append('交换容量部分相似')
                detail_breakdown.append(f'交换容量部分相似({ratio:.1%}): {partial}分')
        
        target_pps = self._parse_numeric_spec(target_specs.get('包转发率', ''))
        candidate_pps = self._parse_numeric_spec(candidate_specs.get('包转发率', ''))
        if target_pps and candidate_pps:
            ratio = min(target_pps, candidate_pps) / max(target_pps, candidate_pps)
            if ratio >= 0.95:
                score += SimilarityCriteria.PACKET_FORWARDING_MATCH
                matched_fields.append('包转发率完全匹配')
                detail_breakdown.append(f'包转发率完全匹配: {target_pps} vs {candidate_pps}')
            elif ratio >= 0.8:
                partial = int(SimilarityCriteria.PACKET_FORWARDING_MATCH * 0.7)
                score += partial
                matched_fields.append('包转发率相似')
                detail_breakdown.append(f'包转发率相似({ratio:.1%}): {partial}分')
            elif ratio >= 0.6:
                partial = int(SimilarityCriteria.PACKET_FORWARDING_MATCH * 0.4)
                score += partial
                matched_fields.append('包转发率部分相似')
                detail_breakdown.append(f'包转发率部分相似({ratio:.1%}): {partial}分')
        
        target_ports = target_specs.get('端口数量', '')
        candidate_ports = candidate_specs.get('端口数量', '')
        if target_ports and candidate_ports:
            target_count = self._extract_port_count(target_ports)
            candidate_count = self._extract_port_count(candidate_ports)
            if target_count and candidate_count:
                if target_count == candidate_count:
                    score += SimilarityCriteria.PORT_COUNT_MATCH
                    matched_fields.append('端口数量完全匹配')
                    detail_breakdown.append(f'端口数量完全匹配: {target_ports}')
                elif abs(target_count - candidate_count) <= 12:
                    partial = int(SimilarityCriteria.PORT_COUNT_MATCH * 0.6)
                    score += partial
                    matched_fields.append('端口数量相近')
                    detail_breakdown.append(f'端口数量相近: {target_count} vs {candidate_count}')
            elif target_ports == candidate_ports:
                score += SimilarityCriteria.PORT_COUNT_MATCH
                matched_fields.append('端口数量完全匹配')
                detail_breakdown.append(f'端口数量完全匹配: {target_ports}')
        
        target_uplink = target_specs.get('上行端口', '')
        candidate_uplink = candidate_specs.get('上行端口', '')
        if target_uplink and candidate_uplink:
            target_type = self._extract_uplink_type(target_uplink)
            candidate_type = self._extract_uplink_type(candidate_uplink)
            if target_type and candidate_type:
                if target_type == candidate_type:
                    score += SimilarityCriteria.UPLINK_TYPE_MATCH
                    matched_fields.append('上行端口类型匹配')
                    detail_breakdown.append(f'上行端口类型匹配: {target_type}')
                elif set(target_type) & set(candidate_type):
                    partial = int(SimilarityCriteria.UPLINK_TYPE_MATCH * 0.5)
                    score += partial
                    matched_fields.append('上行端口部分匹配')
                    detail_breakdown.append(f'上行端口部分匹配: {partial}分')
        
        target_poe = str(target_specs.get('PoE', '')).lower()
        candidate_poe = str(candidate_specs.get('PoE', '')).lower()
        if target_poe and candidate_poe:
            target_supports = '支持' in target_poe or '是' in target_poe or 'true' in target_poe
            candidate_supports = '支持' in candidate_poe or '是' in candidate_poe or 'true' in candidate_poe
            if target_supports == candidate_supports:
                score += SimilarityCriteria.POE_MATCH
                matched_fields.append('PoE支持匹配')
                detail_breakdown.append(f'PoE支持匹配: {"支持" if target_supports else "不支持"}')
        
        target_power = str(target_specs.get('电源', '')).lower()
        candidate_power = str(candidate_specs.get('电源', '')).lower()
        if target_power and candidate_power:
            target_redundant = '冗余' in target_power or '双电源' in target_power
            candidate_redundant = '冗余' in candidate_power or '双电源' in candidate_power
            target_ac = '交流' in target_power or 'ac' in target_power
            candidate_ac = '交流' in candidate_power or 'ac' in candidate_power
            
            if target_redundant == candidate_redundant:
                score += SimilarityCriteria.POWER_TYPE_MATCH
                matched_fields.append('电源配置匹配')
                detail_breakdown.append(f'电源配置匹配: {"冗余" if target_redundant else "单电源"}')
            elif target_ac == candidate_ac:
                partial = int(SimilarityCriteria.POWER_TYPE_MATCH * 0.5)
                score += partial
                matched_fields.append('电源类型部分匹配')
                detail_breakdown.append(f'电源类型部分匹配: {partial}分')
        
        detail_text = '; '.join(detail_breakdown) if detail_breakdown else ', '.join(matched_fields) if matched_fields else '无匹配规格'
        
        return score if score > 0 else 0, {
            'category': '规格相似度',
            'score': score,
            'detail': detail_text
        }

    def _evaluate_scenario(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        target_specs = self._parse_specs(target.get('specs_json', ''))
        candidate_specs = self._parse_specs(candidate.get('specs_json', ''))
        
        target_scenario = target_specs.get('适用场景', '')
        candidate_scenario = candidate_specs.get('适用场景', '')
        
        if target_scenario and candidate_scenario:
            target_keywords = set(self._extract_keywords(target_scenario))
            candidate_keywords = set(self._extract_keywords(candidate_scenario))
            common = target_keywords & candidate_keywords
            if common:
                return SimilarityCriteria.TARGET_SCENARIO_MATCH, {
                    'category': '适用场景匹配',
                    'score': SimilarityCriteria.TARGET_SCENARIO_MATCH,
                    'detail': f'共享关键词: {", ".join(common)}'
                }
        
        return 0, {'category': '适用场景匹配', 'score': 0, 'detail': '无相同场景关键词'}

    def _extract_category(self, product: Dict[str, Any]) -> str:
        specs = self._parse_specs(product.get('specs_json', ''))
        if specs.get('产品类型'):
            return specs['产品类型']
        if specs.get('产品定位'):
            return specs['产品定位']
        return ''

    def _parse_specs(self, specs_json: Any) -> Dict[str, Any]:
        if not specs_json:
            return {}
        if isinstance(specs_json, dict):
            return specs_json
        try:
            return json.loads(specs_json)
        except:
            return {}

    def _parse_numeric_spec(self, spec_value: str) -> Optional[float]:
        try:
            import re
            num_match = re.search(r'[\d.]+', spec_value)
            if num_match:
                return float(num_match.group())
        except:
            pass
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        keywords = ['企业', '园区', '数据中心', '接入层', '汇聚层', '核心层', '医疗', '零售', '矿业', '互联网', '金融', '政府', '教育']
        return [kw for kw in keywords if kw in text]
    
    def _extract_port_count(self, port_str: str) -> Optional[int]:
        import re
        match = re.search(r'(\d+)\s*/\s*(\d+)|(\d+)', port_str)
        if match:
            if match.group(1) and match.group(2):
                return int(match.group(2))
            elif match.group(3):
                return int(match.group(3))
        return None
    
    def _extract_uplink_type(self, uplink_str: str) -> List[str]:
        uplink_types = []
        uplink_str_lower = uplink_str.lower()
        
        if '40g' in uplink_str_lower or '40gbps' in uplink_str_lower or 'qsfp+' in uplink_str_lower:
            uplink_types.append('40G')
        elif '25g' in uplink_str_lower or '25gbps' in uplink_str_lower or 'sfp28' in uplink_str_lower:
            uplink_types.append('25G')
        elif '万兆' in uplink_str or '10g' in uplink_str_lower or '10gbps' in uplink_str_lower or 'sfp+' in uplink_str_lower:
            uplink_types.append('10G')
        elif '千兆' in uplink_str or '1g' in uplink_str_lower or '1gbps' in uplink_str_lower:
            uplink_types.append('1G')
        
        if not uplink_types:
            if 'sfp+' in uplink_str_lower:
                uplink_types.append('10G')
            elif 'sfp' in uplink_str_lower:
                uplink_types.append('1G')
        
        return uplink_types

    def find_competitors(self, target_product: Dict[str, Any], all_products: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        logger.info("Finding competitors for: %s", target_product.get('product_code'))
        logger.info("Total candidates: %d", len(all_products))
        
        evaluated = []
        for candidate in all_products:
            result = self.evaluate(target_product, candidate)
            if result['is_competitor']:
                evaluated.append({
                    'product': candidate,
                    'score': result['total_score'],
                    'breakdown': result['breakdown'],
                    'brand': result.get('candidate_brand', '')
                })
        
        evaluated.sort(key=lambda x: x['score'], reverse=True)
        selected = evaluated[:limit]
        
        logger.info("Found %d competitors (scored >= %d)", len(selected), SimilarityCriteria.MIN_COMPETITOR_SCORE)
        for i, comp in enumerate(selected, 1):
            logger.info("  Competitor %d: %s (%s) - score: %d, brand: %s",
                       i, comp['product'].get('product_name'),
                       comp['product'].get('product_code'),
                       comp['score'], comp['brand'])
        
        return [comp['product'] for comp in selected]
