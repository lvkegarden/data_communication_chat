import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ProductNamingParser:
    
    H3C_SWITCH_FEATURES = {
        'HI': {'name': '旗舰型', 'level': 'high', 'description': '高端旗舰型，功能最全'},
        'EA': {'name': '增强高级型', 'level': 'high', 'description': '增强高级型'},
        'EI': {'name': '增强型', 'level': 'medium', 'description': '增强型，支持三层功能'},
        'SI': {'name': '标准型', 'level': 'low', 'description': '标准型，弱三层或二层'},
        'LI': {'name': '简化型', 'level': 'basic', 'description': '简化型，二层为主'},
    }
    
    H3C_PORT_TYPES = {
        'GT': {'name': '千兆电口', 'speed': '1G', 'medium': 'copper'},
        'GS': {'name': '千兆光口', 'speed': '1G', 'medium': 'fiber'},
        'SFP': {'name': '千兆SFP光口', 'speed': '1G', 'medium': 'fiber'},
        'S': {'name': '万兆SFP+光口', 'speed': '10G', 'medium': 'fiber'},
        'XS': {'name': '万兆光口', 'speed': '10G', 'medium': 'fiber'},
        'XT': {'name': '万兆电口', 'speed': '10G', 'medium': 'copper'},
        'Q': {'name': '40G QSFP光口', 'speed': '40G', 'medium': 'fiber'},
        'QXS': {'name': '40G光口', 'speed': '40G', 'medium': 'fiber'},
        'T': {'name': '电口', 'speed': '1G', 'medium': 'copper'},
        'P': {'name': 'SFP光口', 'speed': '1G', 'medium': 'fiber'},
        'TP': {'name': '光电复用', 'speed': '1G', 'medium': 'combo'},
        'F': {'name': '全光口', 'speed': '1G', 'medium': 'fiber'},
        'C': {'name': '可扩展模块', 'speed': 'variable', 'medium': 'modular'},
    }
    
    H3C_POE_TYPES = {
        'PWR': {'name': 'PoE远程供电', 'type': 'poe'},
        'HPWR': {'name': '高功率PoE', 'type': 'poe+'},
        'DC': {'name': '直流供电', 'type': 'dc'},
        'AC': {'name': '交流供电', 'type': 'ac'},
    }
    
    RUIJIE_SWITCH_FEATURES = {
        'H': {'name': '高端型', 'level': 'high', 'description': '高端高性能'},
        'E': {'name': '增强型', 'level': 'medium', 'description': '增强型'},
        'S': {'name': '标准型', 'level': 'low', 'description': '标准型'},
        'L': {'name': '简化型', 'level': 'basic', 'description': '简化型'},
        'I': {'name': '智能型', 'level': 'medium', 'description': '智能型'},
    }
    
    RUIJIE_POE_TYPES = {
        'HP': {'name': '全端口POE+供电', 'type': 'poe+'},
        'P': {'name': '全端口PoE供电', 'type': 'poe'},
        'LP': {'name': '部分端口PoE供电', 'type': 'poe_lite'},
        'UP': {'name': '60W/90W超PoE', 'type': 'poe_ultra'},
    }
    
    RUIJIE_AP_FEATURES = {
        'TR': {'name': '三射频', 'feature': 'triple_radio'},
        'AR': {'name': 'AI Radio智能射频', 'feature': 'ai_radio'},
        'R': {'name': 'AI Radio智能射频', 'feature': 'ai_radio'},
        'D': {'name': '内置AI Radio', 'feature': 'ai_radio'},
        'C': {'name': '支持扩展槽', 'feature': 'expansion_slot'},
    }
    
    AP_WIFI_STANDARD = {
        'WiFi 4': {'standard': '802.11n', 'generation': 4},
        'WiFi 5': {'standard': '802.11ac', 'generation': 5},
        'WiFi 6': {'standard': '802.11ax', 'generation': 6},
        'WiFi 7': {'standard': '802.11be', 'generation': 7},
    }
    
    def __init__(self):
        logger.info("ProductNamingParser initialized")
    
    def parse(self, product_code: str, product_type: Optional[str] = None) -> Dict[str, Any]:
        result = {
            'product_code': product_code,
            'product_code_upper': product_code.upper(),
            'brand': self._detect_brand(product_code),
            'product_type': None,
            'parsed': False,
            'details': {}
        }
        
        code_upper = product_code.upper()
        brand = result['brand']
        
        if brand == '华为':
            return self._parse_huawei(code_upper, result)
        elif brand == 'H3C':
            return self._parse_h3c(code_upper, result)
        elif brand == '锐捷':
            return self._parse_ruijie(code_upper, result)
        
        return result
    
    def _detect_brand(self, product_code: str) -> str:
        code_upper = product_code.upper()
        
        if code_upper.startswith('RG-'):
            return '锐捷'
        
        if code_upper.startswith('WA') or code_upper.startswith('WX'):
            return 'H3C'
        
        if 'AIRENGINE' in code_upper:
            return '华为'
        
        if code_upper.startswith('S') and re.match(r'^S\d', code_upper):
            h3c_patterns = ['S5130', 'S5120', 'S5110', 'S5100', 'S5024', 'S5048', 'S5560', 'S5590', 
                           'S5580', 'S5570', 'S5500', 'S5820', 'S5810', 'S5800', 'S6520', 'S6530', 
                           'S6526', 'S6510', 'S6500', 'S6800', 'S6850', 'S6860', 'S6890', 'S6880', 
                           'S6825', 'S6826', 'S6812', 'S6813', 'S6805', 'S6855', 'S6110', 'S6116', 
                           'S6216', 'S9800', 'S9820', 'S9825', 'S9826', 'S9827', 'S9850', 'S9855', 
                           'S9857', 'S9900', 'S1050', 'S1250', 'S12500G', 'S7500', 'S7500X', 'S7600', 
                           'S7000', 'S7300', 'S5300', 'S5170', 'S5175', 'S5135', 'S5000', 'S4620', 
                           'S4500', 'S4320', 'S4300', 'S4200', 'S4100', 'S4000', 'S3600', 'S3210', 
                           'S3110', 'S3100', 'S2600', 'S2100', 'S2126', 'S2000', 'S1850', 'S1800', 
                           'S1750', 'S1650', 'S1600', 'S1550', 'S1526', 'S1500', 'S1300', 'S1200', 
                           'S1248', 'S1224', 'S1000']
            for pattern in h3c_patterns:
                if pattern in code_upper:
                    return 'H3C'
            
            huawei_patterns = ['S2700', 'S2720', 'S2750', 'S3700', 'S5700', 'S5720', 'S5730', 'S5731', 
                              'S5732', 'S5735', 'S5736', 'S5755', 'S6720', 'S6730', 'S6735', 'S7700', 
                              'S7703', 'S7706', 'S7712', 'S8700', 'S9700', 'S1270', 'S12704', 'S12708', 
                              'S12712', 'S16700']
            for pattern in huawei_patterns:
                if pattern in code_upper:
                    return '华为'
            
            series_match = re.match(r'^S(\d+)', code_upper)
            if series_match:
                series = int(series_match.group(1))
                if series >= 10000:
                    if series >= 12500 and series <= 12599:
                        return 'H3C'
                    if series >= 10500 and series <= 10599:
                        return 'H3C'
                    return '华为'
        
        if code_upper.startswith('AP'):
            if 'AIR' in code_upper:
                return '华为'
            
            ap_match = re.match(r'^AP(\d+)', code_upper)
            if ap_match:
                ap_series = int(ap_match.group(1))
                if ap_series >= 1000:
                    return '华为'
            
            return '锐捷'
        
        return '未知'
    
    def _parse_huawei(self, code_upper: str, result: Dict[str, Any]) -> Dict[str, Any]:
        result['brand'] = '华为'
        details = {}
        
        if 'AIR-' in code_upper or 'AIRENGINE' in code_upper:
            result['product_type'] = '无线AP'
            details = self._parse_huawei_ap(code_upper)
        elif code_upper.startswith('S'):
            result['product_type'] = '交换机'
            details = self._parse_huawei_switch(code_upper)
        elif code_upper.startswith('AP'):
            result['product_type'] = '无线AP'
            details = self._parse_huawei_ap(code_upper)
        
        result['details'] = details
        result['parsed'] = len(details) > 0
        return result
    
    def _parse_huawei_switch(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        match = re.match(r'^S(\d+)([A-Z]?)([A-Z]*)(?:-([A-Z0-9]+))?', code_upper)
        if match:
            series_num = match.group(1)
            suffix1 = match.group(2) or ''
            suffix2 = match.group(3) or ''
            extra = match.group(4) or ''
            
            series_num_int = int(series_num) if series_num else 0
            
            if series_num_int >= 16000:
                details['switch_level'] = '核心交换机'
                details['series'] = '框式核心'
            elif series_num_int >= 12000:
                details['switch_level'] = '核心交换机'
                details['series'] = '框式核心'
            elif series_num_int >= 8000:
                details['switch_level'] = '核心/汇聚交换机'
                details['series'] = '框式核心/汇聚'
            elif series_num_int >= 7000:
                details['switch_level'] = '汇聚交换机'
                details['series'] = '框式汇聚'
            elif series_num_int >= 6000:
                details['switch_level'] = '核心/汇聚交换机'
                details['series'] = '盒式核心/汇聚'
            elif series_num_int >= 5000:
                details['switch_level'] = '汇聚/接入交换机'
                details['series'] = '盒式汇聚/接入'
            elif series_num_int >= 3000:
                details['switch_level'] = '接入交换机'
                details['series'] = '盒式接入'
            else:
                details['switch_level'] = '接入交换机'
                details['series'] = '入门接入'
            
            full_suffix = suffix1 + suffix2
            all_check_text = full_suffix + extra + code_upper
            
            if 'HI' in all_check_text:
                details['feature_level'] = 'HI'
                details['feature_name'] = '旗舰型'
            elif 'EI' in all_check_text:
                details['feature_level'] = 'EI'
                details['feature_name'] = '增强型'
            elif 'SI' in all_check_text:
                details['feature_level'] = 'SI'
                details['feature_name'] = '标准型'
            elif 'LI' in all_check_text:
                details['feature_level'] = 'LI'
                details['feature_name'] = '简化型'
            elif '-L-' in code_upper or '-L,' in code_upper + ',' or (extra == 'L'):
                details['feature_level'] = 'LI'
                details['feature_name'] = '简化型'
            elif 'E' in extra and not 'EI' in all_check_text:
                details['feature_level'] = 'EI'
                details['feature_name'] = '增强型'
            elif 'S' in extra and not 'SI' in all_check_text:
                details['feature_level'] = 'SI'
                details['feature_name'] = '标准型'
            
            if 'PWR' in extra or '-P-' in code_upper or '-P,' in code_upper + ',' or (extra and 'P' in extra and len(extra) == 1):
                details['poe'] = True
                details['poe_type'] = 'PoE'
            
            if 'V2' in code_upper:
                details['hardware_version'] = 'V2'
            elif 'V3' in code_upper:
                details['hardware_version'] = 'V3'
        
        return details
    
    def _parse_huawei_ap(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        if 'AIRENGINE' in code_upper:
            match = re.search(r'AIRENGINE\s*(\d+)', code_upper)
            if match:
                series = int(match.group(1))
                details['series'] = f'AirEngine {series}'
                details['series_num'] = series
                
                if series >= 80:
                    details['wifi_generation'] = 'WiFi 6/7'
                    details['level'] = '高端'
                elif series >= 60:
                    details['wifi_generation'] = 'WiFi 6'
                    details['level'] = '中高端'
                else:
                    details['wifi_generation'] = 'WiFi 5'
                    details['level'] = '中端'
        elif code_upper.startswith('AP'):
            match = re.match(r'^AP(\d+)', code_upper)
            if match:
                series = int(match.group(1))
                details['series'] = f'AP{series}'
                details['series_num'] = series
                
                if series >= 9000:
                    details['wifi_generation'] = 'WiFi 7'
                    details['level'] = '旗舰'
                elif series >= 8000:
                    details['wifi_generation'] = 'WiFi 6'
                    details['level'] = '高端'
                elif series >= 7000:
                    details['wifi_generation'] = 'WiFi 6'
                    details['level'] = '中高端'
                elif series >= 6000:
                    details['wifi_generation'] = 'WiFi 6'
                    details['level'] = '中端'
                elif series >= 4000:
                    details['wifi_generation'] = 'WiFi 5'
                    details['level'] = '中端'
                elif series >= 2000:
                    details['wifi_generation'] = 'WiFi 4/5'
                    details['level'] = '入门'
        
        if 'N' in code_upper:
            details['form_factor'] = '面板式'
        elif 'E' in code_upper:
            details['form_factor'] = '室外型'
        else:
            details['form_factor'] = '放装式'
        
        return details
    
    def _parse_h3c(self, code_upper: str, result: Dict[str, Any]) -> Dict[str, Any]:
        result['brand'] = 'H3C'
        details = {}
        
        if code_upper.startswith('WA'):
            result['product_type'] = '无线AP'
            details = self._parse_h3c_ap(code_upper)
        elif code_upper.startswith('WX'):
            result['product_type'] = '无线控制器'
            details = self._parse_h3c_ac(code_upper)
        elif code_upper.startswith('S'):
            result['product_type'] = '交换机'
            details = self._parse_h3c_switch(code_upper)
        
        result['details'] = details
        result['parsed'] = len(details) > 0
        return result
    
    def _parse_h3c_switch(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        match = re.match(r'^S(\d+)([A-Z]*)', code_upper)
        if match:
            series_num = match.group(1)
            suffix = match.group(2) or ''
            
            series_num_int = int(series_num) if series_num else 0
            
            if series_num_int >= 12000:
                details['switch_level'] = '核心交换机'
                details['series'] = '框式核心'
            elif series_num_int >= 10000:
                details['switch_level'] = '核心交换机'
                details['series'] = '框式核心'
            elif series_num_int >= 7000:
                details['switch_level'] = '核心/汇聚交换机'
                details['series'] = '核心/汇聚'
            elif series_num_int >= 6000:
                details['switch_level'] = '汇聚交换机'
                details['series'] = '汇聚'
            elif series_num_int >= 5000:
                details['switch_level'] = '汇聚/接入交换机'
                details['series'] = '汇聚/接入'
            elif series_num_int >= 3000:
                details['switch_level'] = '接入交换机'
                details['series'] = '接入'
            elif series_num_int >= 1000:
                details['switch_level'] = '接入交换机'
                details['series'] = '入门接入'
            else:
                details['switch_level'] = 'SOHO交换机'
                details['series'] = 'SOHO'
            
            if 'PWR' in code_upper:
                details['poe'] = True
                details['poe_type'] = 'PoE'
            elif 'HPWR' in code_upper:
                details['poe'] = True
                details['poe_type'] = '高功率PoE'
            
            for feature in ['HI', 'EA', 'EI', 'SI', 'LI']:
                if feature in code_upper:
                    details['feature_level'] = feature
                    if feature in self.H3C_SWITCH_FEATURES:
                        details['feature_name'] = self.H3C_SWITCH_FEATURES[feature]['name']
                        details['feature_desc'] = self.H3C_SWITCH_FEATURES[feature]['description']
                    break
            
            for port_type in ['XS', 'XT', 'QXS', 'SFP', 'GT', 'GS', 'S', 'Q', 'TP', 'T', 'P', 'F', 'C']:
                if port_type in code_upper:
                    if port_type in self.H3C_PORT_TYPES:
                        details['port_type'] = self.H3C_PORT_TYPES[port_type]['name']
                        details['port_speed'] = self.H3C_PORT_TYPES[port_type]['speed']
                    break
            
            port_match = re.search(r'(\d{2,})(?:[A-Z]{1,3})?', code_upper)
            if port_match:
                port_count = port_match.group(1)
                if port_count.isdigit() and int(port_count) < 100:
                    details['port_count'] = int(port_count)
            
            if 'X' in code_upper and details.get('port_speed') != '10G':
                details['uplink_type'] = '万兆'
            
            if 'V2' in code_upper:
                details['hardware_version'] = 'V2'
            elif 'V3' in code_upper:
                details['hardware_version'] = 'V3'
            elif 'V5' in code_upper:
                details['hardware_version'] = 'V5'
            
            if 'G' in code_upper and series_num_int >= 12000:
                details['uplink_40g'] = True
        
        return details
    
    def _parse_h3c_ap(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        match = re.match(r'^WA(\d+)([A-Z]*)', code_upper)
        if match:
            series = int(match.group(1))
            details['series'] = f'WA{series}'
            details['series_num'] = series
            
            if series >= 6000:
                details['wifi_generation'] = 'WiFi 6/7'
                details['level'] = '高端'
            elif series >= 5000:
                details['wifi_generation'] = 'WiFi 6'
                details['level'] = '中高端'
            elif series >= 4000:
                details['wifi_generation'] = 'WiFi 6'
                details['level'] = '中端'
            elif series >= 2000:
                details['wifi_generation'] = 'WiFi 5'
                details['level'] = '中端'
            else:
                details['wifi_generation'] = 'WiFi 4/5'
                details['level'] = '入门'
        
        if 'N' in code_upper:
            details['form_factor'] = '面板式'
        elif 'E' in code_upper:
            details['form_factor'] = '室外型'
        elif 'F' in code_upper:
            details['form_factor'] = '放装式'
        
        return details
    
    def _parse_h3c_ac(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        match = re.match(r'^WX(\d+)([A-Z]*)', code_upper)
        if match:
            series = int(match.group(1))
            details['series'] = f'WX{series}'
            details['series_num'] = series
            
            if series >= 30000:
                details['level'] = '核心AC'
                details['capacity'] = '大规模'
            elif series >= 20000:
                details['level'] = '核心AC'
                details['capacity'] = '中大规模'
            elif series >= 10000:
                details['level'] = '汇聚AC'
                details['capacity'] = '中等规模'
            elif series >= 5000:
                details['level'] = '接入AC'
                details['capacity'] = '中小规模'
            else:
                details['level'] = '入门AC'
                details['capacity'] = '小规模'
        
        return details
    
    def _parse_ruijie(self, code_upper: str, result: Dict[str, Any]) -> Dict[str, Any]:
        result['brand'] = '锐捷'
        details = {}
        
        if 'AP' in code_upper:
            result['product_type'] = '无线AP'
            details = self._parse_ruijie_ap(code_upper)
        elif 'S' in code_upper:
            result['product_type'] = '交换机'
            details = self._parse_ruijie_switch(code_upper)
        
        result['details'] = details
        result['parsed'] = len(details) > 0
        return result
    
    def _parse_ruijie_switch(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        clean_code = code_upper.replace('RG-', '')
        
        match = re.match(r'^S(\d+)([A-Z]*)', clean_code)
        if match:
            series_num = match.group(1)
            suffix = match.group(2) or ''
            
            series_num_int = int(series_num) if series_num else 0
            
            if series_num_int >= 8000:
                details['switch_level'] = '核心交换机'
                details['series'] = '框式核心'
            elif series_num_int >= 7000:
                details['switch_level'] = '核心/汇聚交换机'
                details['series'] = '核心/汇聚'
            elif series_num_int >= 6000:
                details['switch_level'] = '汇聚交换机'
                details['series'] = '汇聚'
            elif series_num_int >= 5000:
                details['switch_level'] = '汇聚/接入交换机'
                details['series'] = '汇聚/接入'
            elif series_num_int >= 3000:
                details['switch_level'] = '接入交换机'
                details['series'] = '接入'
            elif series_num_int >= 2000:
                details['switch_level'] = '接入交换机'
                details['series'] = '入门接入'
            else:
                details['switch_level'] = 'SOHO交换机'
                details['series'] = 'SOHO'
            
            if 'C' in suffix:
                details['expansion_slot'] = True
                details['modular'] = True
            
            parts = code_upper.split('-')
            feature_found = False
            
            for part in reversed(parts):
                if part in ['H', 'E', 'S', 'L', 'I']:
                    details['feature_level'] = part
                    if part in self.RUIJIE_SWITCH_FEATURES:
                        details['feature_name'] = self.RUIJIE_SWITCH_FEATURES[part]['name']
                        details['feature_desc'] = self.RUIJIE_SWITCH_FEATURES[part]['description']
                    feature_found = True
                    break
            
            if not feature_found:
                for feature in ['-H-', '-E-', '-S-', '-L-', '-I-']:
                    if feature in code_upper:
                        level = feature[1]
                        if 'XS' in code_upper and level == 'S':
                            continue
                        if 'GS' in code_upper and level == 'S':
                            continue
                        if 'GT' in code_upper and level == 'T':
                            continue
                        details['feature_level'] = level
                        if level in self.RUIJIE_SWITCH_FEATURES:
                            details['feature_name'] = self.RUIJIE_SWITCH_FEATURES[level]['name']
                            details['feature_desc'] = self.RUIJIE_SWITCH_FEATURES[level]['description']
                        feature_found = True
                        break
            
            for poe_type in ['HP', 'UP', 'LP', 'P']:
                if poe_type in code_upper:
                    if poe_type in self.RUIJIE_POE_TYPES:
                        details['poe'] = True
                        details['poe_type'] = self.RUIJIE_POE_TYPES[poe_type]['name']
                    break
            
            for port_type in ['QXS', 'XS', 'XT', 'SFP', 'GT', 'GS', 'S', 'Q']:
                if port_type in code_upper:
                    details['port_type'] = port_type
                    break
            
            port_match = re.search(r'(\d{2,})', clean_code)
            if port_match:
                port_count = port_match.group(1)
                if port_count.isdigit() and int(port_count) < 100:
                    details['port_count'] = int(port_count)
        
        return details
    
    def _parse_ruijie_ap(self, code_upper: str) -> Dict[str, Any]:
        details = {}
        
        clean_code = code_upper.replace('RG-', '')
        
        match = re.match(r'^AP(\d+)([A-Z]*)', clean_code)
        if match:
            series = int(match.group(1))
            details['series'] = f'AP{series}'
            details['series_num'] = series
            
            if series >= 900:
                details['wifi_generation'] = 'WiFi 7'
                details['level'] = '旗舰'
            elif series >= 800:
                details['wifi_generation'] = 'WiFi 6/7'
                details['level'] = '高端'
            elif series >= 700:
                details['wifi_generation'] = 'WiFi 6'
                details['level'] = '中高端'
            elif series >= 600:
                details['wifi_generation'] = 'WiFi 6'
                details['level'] = '中端'
            elif series >= 500:
                details['wifi_generation'] = 'WiFi 6'
                details['level'] = '中端'
            elif series >= 400:
                details['wifi_generation'] = 'WiFi 5'
                details['level'] = '中端'
            elif series >= 200:
                details['wifi_generation'] = 'WiFi 4/5'
                details['level'] = '入门'
            else:
                details['wifi_generation'] = 'WiFi 4'
                details['level'] = '入门'
            
            for feature in ['TR', 'AR', 'R', 'D', 'C']:
                if feature in clean_code:
                    if feature in self.RUIJIE_AP_FEATURES:
                        details['special_feature'] = feature
                        details['special_feature_name'] = self.RUIJIE_AP_FEATURES[feature]['name']
                    break
            
            if 'V2' in clean_code:
                details['hardware_version'] = 'V2'
            elif 'V3' in clean_code:
                details['hardware_version'] = 'V3'
        
        return details
    
    def parse_similarity(self, product_a: Dict[str, Any], product_b: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            'same_brand': False,
            'same_type': False,
            'same_level': False,
            'same_series': False,
            'similarity_score': 0,
            'matched_fields': []
        }
        
        if product_a.get('brand') == product_b.get('brand'):
            result['same_brand'] = True
            result['similarity_score'] += 20
            result['matched_fields'].append('品牌相同')
        
        if product_a.get('product_type') == product_b.get('product_type'):
            result['same_type'] = True
            result['similarity_score'] += 30
            result['matched_fields'].append('产品类型相同')
        
        details_a = product_a.get('details', {})
        details_b = product_b.get('details', {})
        
        if details_a.get('switch_level') and details_a.get('switch_level') == details_b.get('switch_level'):
            result['same_level'] = True
            result['similarity_score'] += 25
            result['matched_fields'].append(f'产品等级相同: {details_a.get("switch_level")}')
        
        if details_a.get('series') and details_a.get('series') == details_b.get('series'):
            result['same_series'] = True
            result['similarity_score'] += 15
            result['matched_fields'].append(f'产品系列相同: {details_a.get("series")}')
        
        if details_a.get('feature_level') and details_a.get('feature_level') == details_b.get('feature_level'):
            result['similarity_score'] += 10
            result['matched_fields'].append(f'功能等级相同: {details_a.get("feature_level")}')
        
        if details_a.get('port_count') and details_b.get('port_count'):
            diff = abs(details_a['port_count'] - details_b['port_count'])
            if diff == 0:
                result['similarity_score'] += 15
                result['matched_fields'].append(f'端口数量相同: {details_a["port_count"]}')
            elif diff <= 12:
                result['similarity_score'] += 10
                result['matched_fields'].append(f'端口数量相近: {details_a["port_count"]} vs {details_b["port_count"]}')
        
        if details_a.get('poe') == details_b.get('poe'):
            if details_a.get('poe'):
                result['similarity_score'] += 10
                result['matched_fields'].append('均支持PoE')
        
        return result
