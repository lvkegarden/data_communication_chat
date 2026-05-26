import requests
import re
import json
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from base_scraper import BaseScraper, ProductInfo
from scraper_logger import log


# 华为交换机核心规格数据库（基于公开资料整理）
HUAWEI_SWITCH_SPECS_DB = {
    # 核心交换机
    'S16700': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络、数据中心',
        '交换容量': '43.2Tbps（整机）',
        '包转发率': '11520Mpps',
        '业务插槽数': '4-12个',
        '主控引擎': '2个（冗余）',
        '交换网板': '支持',
        '端口类型': '10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约6000W',
        '尺寸': '442mm×520mm×300mm（8U）',
        '重量': '约45kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN/M-LAG',
    },
    'S12700E': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络',
        '交换容量': '25.6Tbps/槽位',
        '包转发率': '6240Mpps',
        '业务插槽数': '4-12个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约5000W',
        '尺寸': '442mm×520mm×300mm（8U）',
        '重量': '约40kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN/M-LAG',
    },
    'S12700H': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络',
        '交换容量': '25.6Tbps/槽位',
        '包转发率': '6240Mpps',
        '业务插槽数': '4-12个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约5000W',
        '尺寸': '442mm×520mm×300mm（8U）',
        '重量': '约40kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN/M-LAG',
    },
    'S8700': {
        '产品定位': '核心/汇聚交换机',
        '适用场景': '中大型企业、园区网络',
        '交换容量': '10.4Tbps/槽位',
        '包转发率': '3840Mpps',
        '业务插槽数': '4-8个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约4000W',
        '尺寸': '442mm×480mm×260mm（6U）',
        '重量': '约35kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN',
    },
    'S7700': {
        '产品定位': '核心/汇聚交换机',
        '适用场景': '中大型企业、园区网络',
        '交换容量': '4.8Tbps/槽位',
        '包转发率': '1920Mpps',
        '业务插槽数': '2-6个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约2500W',
        '尺寸': '442mm×420mm×175mm（4U）',
        '重量': '约25kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN',
    },
    # 接入交换机
    'S5735-L-V2': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层、桌面接入',
        '交换容量': '336Gbps/1.68Tbps（堆叠）',
        '包转发率': '96Mpps/240Mpps（堆叠）',
        '端口数量': '24/48个GE',
        '上行端口': '4个万兆SFP+',
        '电源': '交流，单电源',
        '最大功耗': '约50W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.2kg',
        '工作温度': '0°C~45°C',
        'PoE': '不支持',
    },
    'S5731-H': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层、高密度场景',
        '交换容量': '336Gbps/1.68Tbps（堆叠）',
        '包转发率': '132Mpps/444Mpps（堆叠）',
        '端口数量': '24/48个GE',
        '上行端口': '4个万兆SFP+',
        '电源': '交流/直流',
        '最大功耗': '约80W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.5kg',
        '工作温度': '0°C~45°C',
        'PoE': '支持（部分型号）',
    },
    'S5731-L': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层、桌面接入',
        '交换容量': '336Gbps/1.68Tbps（堆叠）',
        '包转发率': '102Mpps/336Mpps（堆叠）',
        '端口数量': '24/48个GE',
        '上行端口': '4个万兆SFP+',
        '电源': '交流，单电源',
        '最大功耗': '约60W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.3kg',
        '工作温度': '0°C~45°C',
        'PoE': '不支持',
    },
    'S5755-H': {
        '产品定位': '接入交换机',
        '适用场景': '企业汇聚/接入层',
        '交换容量': '640Gbps/3.2Tbps（堆叠）',
        '包转发率': '168Mpps/960Mpps（堆叠）',
        '端口数量': '48个GE',
        '上行端口': '4个25GE SFP28 + 2个100GE QSFP28',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约150W',
        '尺寸': '442mm×320mm×43.6mm（1U）',
        '重量': '约5.5kg',
        '工作温度': '0°C~45°C',
        'PoE': '支持（部分型号）',
    },
}

# 华为无线AP核心规格数据库
HUAWEI_WLAN_SPECS_DB = {
    'AirEngine5700': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、教室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
        '天线': '内置智能天线',
        '接入终端': '256个',
        '接口': '1个GE电口',
        'PoE': '支持802.3af/at',
        '尺寸': '180mm×180mm×35mm',
        '重量': '约0.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine5760': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、教室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
        '天线': '内置智能天线',
        '接入终端': '256个',
        '接口': '1个GE电口',
        'PoE': '支持802.3af/at',
        '尺寸': '180mm×180mm×35mm',
        '重量': '约0.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine5761': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、教室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
        '天线': '内置智能天线',
        '接入终端': '256个',
        '接口': '1个GE电口',
        'PoE': '支持802.3af/at',
        '尺寸': '180mm×180mm×35mm',
        '重量': '约0.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine5762': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、高密度',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '2.975Gbps',
        '天线': '内置智能天线',
        '接入终端': '384个',
        '接口': '1个GE电口 + 1个GE SFP',
        'PoE': '支持802.3af/at',
        '尺寸': '200mm×200mm×38mm',
        '重量': '约0.7kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine5773': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '企业办公、高密度',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '3.57Gbps',
        '天线': '内置智能天线',
        '接入终端': '384个',
        '接口': '1个2.5GE电口',
        'PoE': '支持802.3at',
        '尺寸': '200mm×200mm×38mm',
        '重量': '约0.8kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine5776': {
        '产品类型': '室外Wi-Fi 6 AP',
        '适用场景': '园区、广场、停车场',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
        '天线': '外置全向天线',
        '接入终端': '256个',
        '接口': '1个GE电口 + 1个GE SFP',
        'PoE': '支持802.3at',
        '尺寸': '300mm×300mm×60mm',
        '重量': '约3.5kg',
        '工作温度': '-40°C~65°C',
    },
    'AirEngine6700': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、会议室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '内置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '220mm×220mm×40mm',
        '重量': '约1kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine6760': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、会议室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '内置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '220mm×220mm×40mm',
        '重量': '约1kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine6761': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、会议室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '内置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '220mm×220mm×40mm',
        '重量': '约1kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine6776': {
        '产品类型': '室外Wi-Fi 6 AP',
        '适用场景': '园区、广场、室外覆盖',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '外置全向天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '350mm×350mm×80mm',
        '重量': '约4kg',
        '工作温度': '-40°C~65°C',
    },
    'AirEngine8700': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '高密度场景、会议厅',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '10.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '1个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '250mm×250mm×45mm',
        '重量': '约1.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine8760': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '高密度场景、会议厅',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '10.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '1个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '250mm×250mm×45mm',
        '重量': '约1.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine8761': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '高密度场景、会议厅',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '10.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '1个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '250mm×250mm×45mm',
        '重量': '约1.5kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine8771': {
        '产品类型': '室外Wi-Fi 6 AP',
        '适用场景': '园区、广场、室外覆盖',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '外置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '350mm×350mm×80mm',
        '重量': '约4kg',
        '工作温度': '-40°C~65°C',
    },
    'AirEngine8776': {
        '产品类型': '室外Wi-Fi 6 AP',
        '适用场景': '园区、广场、室外高密度',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '外置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '350mm×350mm×80mm',
        '重量': '约4.5kg',
        '工作温度': '-40°C~65°C',
    },
    'AirEngine9700': {
        '产品类型': '室内Wi-Fi 6E AP',
        '适用场景': '旗舰场景、高密度',
        '无线标准': 'Wi-Fi 6E (802.11ax)',
        '最大速率': '12.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '2个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '280mm×280mm×50mm',
        '重量': '约2kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine9701': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '旗舰场景、超密集',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '15.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '2个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '280mm×280mm×50mm',
        '重量': '约2kg',
        '工作温度': '0°C~45°C',
    },
    'AirEngine9703': {
        '产品类型': '室内Wi-Fi 6E AP',
        '适用场景': '旗舰场景、高密度',
        '无线标准': 'Wi-Fi 6E (802.11ax)',
        '最大速率': '11.5Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '2个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '280mm×280mm×50mm',
        '重量': '约2kg',
        '工作温度': '0°C~45°C',
    },
    'AC6000': {
        '产品类型': '无线控制器 (AC)',
        '适用场景': '中型企业无线网络',
        '管理AP数': '128个',
        '用户容量': '2048个',
        '接口': '4个GE电口 + 2个GE SFP',
        '电源': '交流',
        '最大功耗': '约50W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约3kg',
        '工作温度': '0°C~45°C',
    },
    'AC6508': {
        '产品类型': '无线控制器 (AC)',
        '适用场景': '中型企业无线网络',
        '管理AP数': '512个',
        '用户容量': '8192个',
        '接口': '8个GE电口 + 4个GE SFP',
        '电源': '交流，1+1冗余',
        '最大功耗': '约100W',
        '尺寸': '442mm×300mm×43.6mm（1U）',
        '重量': '约5kg',
        '工作温度': '0°C~45°C',
    },
    'AC6805': {
        '产品类型': '无线控制器 (AC)',
        '适用场景': '大型企业无线网络',
        '管理AP数': '1024个',
        '用户容量': '16384个',
        '接口': '8个GE电口 + 4个10GE SFP+',
        '电源': '交流，1+1冗余',
        '最大功耗': '约150W',
        '尺寸': '442mm×380mm×43.6mm（1U）',
        '重量': '约7kg',
        '工作温度': '0°C~45°C',
    },
}


class HuaweiScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source="华为",
            base_url="https://e.huawei.com"
        )
        
        self.switch_url = "https://e.huawei.com/cn/products/switches/"
        self.wlan_url = "https://e.huawei.com/cn/products/wlan/"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "交换机": self.switch_url,
            "无线": self.wlan_url
        }
    
    def scrape_category(self, category: str, url: str) -> List[ProductInfo]:
        log(f"[INFO] 开始爬取华为 {category}（从系列详情页提取具体型号）")
        
        products = []
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                log(f"[WARN] 访问失败: HTTP {response.status_code}")
                return products
            
            response.encoding = 'utf-8'
            
            if not response.text or len(response.text) < 500:
                log("[WARN] 响应内容过少，尝试使用 GBK 编码")
                response.encoding = 'gbk'
            
            html = response.text
            
            series_data = self._extract_product_data(html, category)
            log(f"[INFO] 找到 {len(series_data)} 个产品系列")
            
            all_models = {}
            series_with_models = 0
            series_without_models = 0
            
            for series_name, series_info in series_data.items():
                detail_url = series_info.get('detail_url', '') or series_info.get('url', '')
                
                if not detail_url or '/cn/products/' not in detail_url:
                    log(f"[DEBUG] {series_name} 未找到详情页URL，跳过")
                    series_without_models += 1
                    continue
                
                log(f"[INFO] 正在处理系列: {series_name} -> {detail_url}")
                
                try:
                    import time
                    time.sleep(0.2)
                    
                    detail_resp = self.session.get(detail_url, timeout=20)
                    detail_resp.encoding = 'utf-8'
                    
                    log(f"[DEBUG] {series_name} 详情页HTTP状态: {detail_resp.status_code}, 内容长度: {len(detail_resp.text)} 字节")
                    
                    if detail_resp.status_code != 200:
                        log(f"[WARN] {series_name} 详情页访问失败: HTTP {detail_resp.status_code}")
                        series_without_models += 1
                        continue
                    
                    series_desc = self._extract_description_from_detail(series_name, detail_resp.text)
                    if series_desc:
                        series_info['description'] = series_desc
                    
                    models = self._extract_models_from_detail(series_name, detail_resp.text, detail_url)
                    
                    if models:
                        series_with_models += 1
                        for model in models:
                            model_name = model['name']
                            if model_name not in all_models:
                                all_models[model_name] = {
                                    'model_info': model,
                                    'series_info': series_info,
                                }
                                log(f"[DEBUG] 添加具体型号: {model_name} (属于 {series_name})")
                            else:
                                log(f"[DEBUG] 型号已存在，跳过重复: {model_name}")
                    else:
                        series_without_models += 1
                        log(f"[INFO] {series_name} 未找到具体型号，保留作为系列产品")
                        
                        if series_name not in all_models:
                            all_models[series_name] = {
                                'model_info': {
                                    'name': series_name,
                                    'series_name': series_name,
                                    'description': series_info.get('description', ''),
                                    'specs': series_info.get('specs', {}),
                                    'links': series_info.get('links', []),
                                    'url': detail_url,
                                    'detail_url': detail_url,
                                },
                                'series_info': series_info,
                                'is_series': True,
                            }
                    
                except Exception as e:
                    log(f"[ERROR] 处理 {series_name} 时出错: {e}")
                    import traceback
                    log(traceback.format_exc())
                    series_without_models += 1
            
            log(f"[INFO] 系列处理完成: {series_with_models} 个系列有具体型号, {series_without_models} 个系列无具体型号")
            log(f"[INFO] 共收集到 {len(all_models)} 个唯一产品（型号或系列）")
            
            valid_products = 0
            invalid_products = 0
            
            for model_name, data in all_models.items():
                model_info = data.get('model_info', {})
                series_info = data.get('series_info', {})
                is_series = data.get('is_series', False)
                
                if is_series:
                    product = self._create_product_from_series(
                        category, model_name, series_info
                    )
                else:
                    product = self._create_product_from_model(
                        category, model_name, model_info, series_info
                    )
                
                if product:
                    products.append(product)
                    valid_products += 1
                else:
                    invalid_products += 1
            
            if invalid_products > 0:
                log(f"[WARN] 过滤了 {invalid_products} 个无效产品")
            
            log(f"[INFO] 华为{category}最终采集 {valid_products} 个产品")
            
        except Exception as e:
            log(f"[ERROR] 爬取 {category} 时出错: {e}")
            import traceback
            traceback.print_exc()
            log(traceback.format_exc())
        
        return products
    
    def _extract_product_data(self, html: str, category: str) -> Dict[str, Dict[str, Any]]:
        products = {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        if category == "交换机":
            products = self._extract_switch_products(soup)
        elif category == "无线":
            products = self._extract_wlan_products(soup)
        
        return products
    
    def _extract_switch_products(self, soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
        products = {}
        log(f"[DEBUG] 开始提取交换机产品系列")
        
        switch_series_patterns = [
            r'S\d{3,4}[-A-Za-z0-9]*',
            r'CloudEngine\s+S\d{3,4}[-A-Za-z0-9]*',
        ]
        
        html = str(soup)
        log(f"[DEBUG] HTML内容长度: {len(html)} 字节")
        
        total_matches = 0
        for pattern in switch_series_patterns:
            matches = re.findall(pattern, html)
            log(f"[DEBUG] 正则模式 '{pattern}' 匹配到 {len(matches)} 个结果: {matches[:10]}...")
            total_matches += len(matches)
            
            for match in matches:
                clean_name = re.sub(r'CloudEngine\s+', '', match).strip()
                
                if len(clean_name) >= 4:
                    if clean_name not in products:
                        products[clean_name] = {
                            'name': clean_name,
                            'description': '',
                            'features': [],
                            'specs': {},
                            'links': [],
                            'url': '',
                            'detail_url': ''
                        }
                        log(f"[DEBUG] 添加交换机系列: {clean_name} (原始: {match})")
        
        log(f"[DEBUG] 共提取到 {len(products)} 个交换机系列，正则总匹配数: {total_matches}")
        
        self._extract_detail_urls_from_list(soup, products)
        
        self._extract_links_from_soup(soup, products)
        
        self._extract_descriptions_from_soup(soup, products)
        
        self._extract_specs_from_content(html, products)
        
        return products
    
    def _extract_wlan_products(self, soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
        products = {}
        log(f"[DEBUG] 开始提取无线产品系列")
        
        wireless_series_patterns = [
            r'AirEngine\s+\w+',
            r'AP\d{3,4}[-A-Za-z0-9]*',
            r'AC\d{3,4}[-A-Za-z0-9]*',
        ]
        
        html = str(soup)
        log(f"[DEBUG] 无线HTML内容长度: {len(html)} 字节")
        
        total_matches = 0
        for pattern in wireless_series_patterns:
            matches = re.findall(pattern, html)
            log(f"[DEBUG] 无线正则模式 '{pattern}' 匹配到 {len(matches)} 个结果: {matches[:10]}...")
            total_matches += len(matches)
            
            for match in matches:
                clean_name = match.strip()
                if len(clean_name) >= 4:
                    if clean_name not in products:
                        products[clean_name] = {
                            'name': clean_name,
                            'description': '',
                            'features': [],
                            'specs': {},
                            'links': [],
                            'url': '',
                            'detail_url': ''
                        }
                        log(f"[DEBUG] 添加无线系列: {clean_name} (原始: {match})")
        
        log(f"[DEBUG] 共提取到 {len(products)} 个无线系列，正则总匹配数: {total_matches}")
        
        self._extract_detail_urls_from_list(soup, products)
        
        self._extract_links_from_soup(soup, products)
        
        self._extract_descriptions_from_soup(soup, products)
        
        self._extract_specs_from_content(html, products)
        
        return products
    
    def _extract_detail_urls_from_list(self, soup: BeautifulSoup, products: Dict[str, Dict[str, Any]]):
        base_url = "https://e.huawei.com"
        log(f"[DEBUG] 开始提取产品详情页URL，当前产品数: {len(products)}")
        
        url_count = 0
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            if not href.startswith('/cn/products/') or '.pdf' in href.lower():
                continue
            
            full_url = urljoin(base_url, href)
            
            for series_name in list(products.keys()):
                full_series = 'CloudEngine ' + series_name
                if full_series.lower() in text.lower() or series_name.lower() in text.lower():
                    if not products[series_name]['detail_url']:
                        products[series_name]['detail_url'] = full_url
                        products[series_name]['url'] = full_url
                        
                        products[series_name]['links'].insert(0, {
                            'title': f'CloudEngine {series_name} 产品详情',
                            'url': full_url,
                            'type': '产品详情'
                        })
                        url_count += 1
                        log(f"[DEBUG] 为 {series_name} 提取详情页URL (文本匹配): {full_url}")
                        break
                elif series_name.lower() in href.lower():
                    if not products[series_name]['detail_url']:
                        products[series_name]['detail_url'] = full_url
                        products[series_name]['url'] = full_url
                        
                        products[series_name]['links'].insert(0, {
                            'title': f'{series_name} 产品详情',
                            'url': full_url,
                            'type': '产品详情'
                        })
                        url_count += 1
                        log(f"[DEBUG] 为 {series_name} 提取详情页URL (URL匹配): {full_url}")
                        break
        
        no_url_products = [name for name, info in products.items() if not info.get('detail_url')]
        if no_url_products:
            log(f"[DEBUG] 有 {len(no_url_products)} 个产品未提取到详情页URL，尝试构造URL")
            url_count += self._try_construct_detail_urls(no_url_products, products)
        
        no_url_products_final = [name for name, info in products.items() if not info.get('detail_url')]
        if no_url_products_final:
            log(f"[WARN] 以下 {len(no_url_products_final)} 个产品仍未提取到详情页URL: {no_url_products_final}")
        
        log(f"[DEBUG] 共提取 {url_count} 个产品详情页URL")
    
    def _try_construct_detail_urls(self, no_url_products: List[str], products: Dict[str, Dict[str, Any]]) -> int:
        base_url = "https://e.huawei.com"
        count = 0
        
        for series_name in no_url_products:
            series_lower = series_name.lower()
            
            possible_urls = []
            
            if series_lower.startswith('s'):
                possible_urls.extend([
                    f'/cn/products/switches/campus-switches/{series_lower}',
                    f'/cn/products/switches/campus-switches/{series_lower.replace("-", "")}',
                ])
            
            if '-' in series_lower:
                prefix = series_lower.split('-')[0]
                possible_urls.append(f'/cn/products/switches/campus-switches/{prefix}')
            
            possible_urls = list(dict.fromkeys(possible_urls))
            
            for possible_href in possible_urls:
                full_url = urljoin(base_url, possible_href)
                
                try:
                    import time
                    time.sleep(0.1)
                    
                    resp = self.session.get(full_url, timeout=10)
                    
                    if resp.status_code == 200:
                        tables_count = resp.text.count('<table')
                        
                        if tables_count > 0:
                            products[series_name]['detail_url'] = full_url
                            products[series_name]['url'] = full_url
                            
                            products[series_name]['links'].insert(0, {
                                'title': f'{series_name} 产品详情',
                                'url': full_url,
                                'type': '产品详情'
                            })
                            
                            count += 1
                            log(f"[DEBUG] 为 {series_name} 构造并验证详情页URL: {full_url} (表格数: {tables_count})")
                            break
                except Exception as e:
                    log(f"[DEBUG] 尝试访问 {full_url} 失败: {e}")
                    continue
        
        return count
    
    def _extract_descriptions_from_soup(self, soup: BeautifulSoup, products: Dict[str, Dict[str, Any]]):
        log(f"[DEBUG] 开始从列表页提取产品描述，产品数: {len(products)}")
        desc_count = 0
        
        for series_name in products:
            features = []
            description_parts = []
            
            elements = soup.find_all(['p', 'div', 'span', 'li'])
            for elem in elements:
                text = elem.get_text(strip=True)
                if series_name in text:
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    
                    if len(clean_text) > 20 and len(clean_text) < 500:
                        description_parts.append(clean_text)
                    
                    if '•' in text or '·' in text or '-' in text[:3]:
                        feature_lines = text.split('•')
                        for line in feature_lines[1:]:
                            feature = line.strip()
                            if feature and len(feature) > 2:
                                features.append(feature)
            
            if description_parts:
                products[series_name]['description'] = ' '.join(description_parts[:3])
                desc_count += 1
                log(f"[DEBUG] 为 {series_name} 从列表页提取描述: {products[series_name]['description'][:50]}...")
            
            if features:
                products[series_name]['features'] = features[:10]
        
        log(f"[DEBUG] 共为 {desc_count}/{len(products)} 个产品从列表页提取到描述")
    
    def _extract_links_from_soup(self, soup: BeautifulSoup, products: Dict[str, Dict[str, Any]]):
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if not href or href.startswith('#') or href.startswith('javascript'):
                continue
            
            if href.startswith('/'):
                href = urljoin(self.base_url, href)
            
            link_type = self._classify_link(text, href)
            
            for series_name in products:
                series_in_text = series_name in text
                series_in_href = series_name.lower() in href.lower()
                
                if series_in_text or series_in_href:
                    if link_type:
                        link_info = {
                            'title': text[:100] if text else link_type,
                            'url': href[:500],
                            'type': link_type
                        }
                        if link_info not in products[series_name]['links']:
                            products[series_name]['links'].append(link_info)
    
    def _classify_link(self, text: str, href: str) -> str:
        text_lower = text.lower()
        href_lower = href.lower()
        
        if '彩页' in text or 'brochure' in href_lower:
            return '彩页'
        elif '手册' in text or 'manual' in href_lower or 'guide' in href_lower:
            return '手册'
        elif '规格' in text or 'spec' in href_lower:
            return '规格参数'
        elif '白皮书' in text or 'whitepaper' in href_lower:
            return '白皮书'
        elif '了解更多' in text or '详情' in text:
            return '产品详情'
        elif '.pdf' in href_lower:
            return 'PDF文档'
        elif href_lower.endswith('.pdf'):
            return 'PDF文档'
        
        return ''
    
    def _extract_specs_from_content(self, html: str, products: Dict[str, Dict[str, Any]]):
        log(f"[DEBUG] 开始匹配产品规格数据库")
        matched_count = 0
        unmatched_count = 0
        
        for series_name, product_info in products.items():
            specs = {}
            match_source = '未匹配'
            
            normalized_name = series_name.replace('-', '').replace(' ', '')
            
            # 尝试交换机规格库
            for db_key, db_specs in HUAWEI_SWITCH_SPECS_DB.items():
                db_key_normalized = db_key.replace('-', '')
                if db_key_normalized in normalized_name or normalized_name in db_key_normalized:
                    specs.update(db_specs)
                    matched_count += 1
                    match_source = f'交换机库-{db_key}'
                    log(f"[DEBUG] {series_name} 匹配到交换机规格库: {db_key}")
                    break
            
            # 尝试无线AP规格库
            if not specs:
                for db_key, db_specs in HUAWEI_WLAN_SPECS_DB.items():
                    db_key_normalized = db_key.replace('-', '').replace(' ', '')
                    series_normalized = series_name.replace('-', '').replace(' ', '')
                    
                    if (db_key_normalized in series_normalized or 
                        series_normalized.startswith(db_key_normalized) or
                        series_normalized.startswith('AirEngine' + db_key_normalized.replace('AirEngine', ''))):
                        specs.update(db_specs)
                        matched_count += 1
                        match_source = f'无线AP库-{db_key}'
                        log(f"[DEBUG] {series_name} 匹配到无线AP规格库: {db_key}")
                        break
            
            # fallback逻辑
            if not specs:
                if 'S16700' in series_name or 'S12700' in series_name:
                    specs['产品定位'] = '核心交换机'
                    specs['适用场景'] = '大型企业、园区网络'
                    matched_count += 1
                    match_source = 'fallback-S16700/S12700'
                elif 'S8700' in series_name or 'S7700' in series_name:
                    specs['产品定位'] = '核心/汇聚交换机'
                    specs['适用场景'] = '中大型企业、园区网络'
                    matched_count += 1
                    match_source = 'fallback-S8700/S7700'
                elif 'S5735' in series_name or 'S5731' in series_name or 'S5755' in series_name:
                    specs['产品定位'] = '接入交换机'
                    specs['适用场景'] = '企业接入层、桌面接入'
                    matched_count += 1
                    match_source = 'fallback-S5735/S5731/S5755'
                
                if not specs:
                    if 'AirEngine' in series_name:
                        specs['产品类型'] = '无线接入点 (AP)'
                        specs['适用场景'] = '企业无线覆盖'
                        matched_count += 1
                        match_source = 'fallback-AirEngine'
                    elif 'AC' in series_name:
                        specs['产品类型'] = '无线控制器 (AC)'
                        specs['适用场景'] = '企业无线网络管理'
                        matched_count += 1
                        match_source = 'fallback-AC'
                    else:
                        unmatched_count += 1
                        log(f"[WARN] {series_name} 未能匹配任何规格")
            
            specs['品牌'] = '华为'
            specs['系列'] = series_name
            
            if specs:
                product_info['specs'] = specs
        
        log(f"[DEBUG] 规格匹配结果: 匹配 {matched_count} | 未匹配 {unmatched_count} | 总计 {len(products)}")
    
    def _extract_spec_value(self, text: str, keyword: str) -> str:
        try:
            idx = text.find(keyword)
            if idx >= 0:
                end_idx = idx + len(keyword)
                
                if idx + 50 < len(text):
                    snippet = text[end_idx:end_idx + 50]
                    
                    match = re.search(r'[:：]\s*([^，。！？；\n\r]{1,30})', snippet)
                    if match:
                        return match.group(1).strip()
        except:
            pass
        
        return ''
    
    def _fetch_product_details(self, product_data: Dict[str, Dict[str, Any]]):
        import time
        log(f"[DEBUG] ========== 开始抓取产品详情页 ==========")
        log(f"[DEBUG] 需要抓取详情页的产品数: {len(product_data)}")
        
        fetched_count = 0
        failed_count = 0
        skipped_count = 0
        
        for idx, (series_name, product_info) in enumerate(product_data.items(), 1):
            detail_url = product_info.get('detail_url', '') or product_info.get('url', '')
            
            if not detail_url or '/cn/products/' not in detail_url:
                log(f"[DEBUG] [{idx}/{len(product_data)}] {series_name} 未找到详情页URL (detail_url={detail_url})")
                skipped_count += 1
                continue
            
            log(f"[DEBUG] [{idx}/{len(product_data)}] 正在抓取 {series_name} 详情页: {detail_url}")
            
            try:
                response = self.session.get(detail_url, timeout=20)
                response.encoding = 'utf-8'
                
                log(f"[DEBUG] {series_name} 详情页HTTP状态: {response.status_code}, 内容长度: {len(response.text)} 字节")
                
                if response.status_code != 200:
                    log(f"[WARN] {series_name} 详情页访问失败: HTTP {response.status_code}")
                    failed_count += 1
                    continue
                
                desc = self._extract_description_from_detail(series_name, response.text)
                
                if desc:
                    product_info['description'] = desc
                    fetched_count += 1
                    log(f"[OK] {series_name} 提取到描述 (长度={len(desc)}): {desc[:60]}...")
                else:
                    log(f"[WARN] {series_name} 详情页未提取到有效描述")
                    failed_count += 1
                
                time.sleep(0.3)
                
            except Exception as e:
                log(f"[ERROR] {series_name} 详情页抓取失败: {e}")
                failed_count += 1
        
        log(f"[DEBUG] ========== 详情页抓取完成 ==========")
        log(f"[INFO] 成功: {fetched_count} | 失败: {failed_count} | 跳过: {skipped_count} | 总计: {len(product_data)}")
    
    def _extract_models_from_detail(self, series_name: str, html: str, detail_url: str) -> List[Dict[str, Any]]:
        log(f"[DEBUG] {series_name} 开始从详情页提取具体型号")
        
        models_dict = {}
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        log(f"[DEBUG] {series_name} 找到 {len(tables)} 个表格")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            if len(rows) == 0:
                continue
            
            first_row = rows[0]
            header_cells = first_row.find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]
            
            model_columns = []
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if ('cloudengine' in header_lower or 
                    re.search(r's\d{3,4}', header_lower, re.I) or
                    'airengine' in header_lower or
                    re.search(r'ap\d{3,4}', header_lower, re.I) or
                    re.search(r'ac\d{3,4}', header_lower, re.I)):
                    model_columns.append(i)
            
            if len(model_columns) == 0:
                continue
            
            log(f"[DEBUG] {series_name} 表格 #{table_idx} 找到 {len(model_columns)} 个型号列")
            
            table_models = self._split_model_header(headers, model_columns)
            log(f"[DEBUG] {series_name} 表格 #{table_idx} 拆分后共 {len(table_models)} 个型号")
            
            common_specs = self._extract_common_specs(rows)
            log(f"[DEBUG] {series_name} 表格 #{table_idx} 提取到 {len(common_specs)} 个共用规格")
            
            for model_name, model_info in table_models.items():
                col_specs = self._extract_col_specs(rows, model_info['col_index'], len(headers), model_name, table_models)
                
                if model_name not in models_dict:
                    models_dict[model_name] = {
                        'name': model_name,
                        'series_name': series_name,
                        'description': '',
                        'features': [],
                        'specs': {},
                        'links': [],
                        'url': detail_url,
                        'detail_url': detail_url,
                    }
                
                for key, value in common_specs.items():
                    if key not in models_dict[model_name]['specs']:
                        models_dict[model_name]['specs'][key] = value
                
                for key, value in col_specs.items():
                    models_dict[model_name]['specs'][key] = value
        
        models = list(models_dict.values())
        
        if not models:
            regex_patterns = [
                r'S\d{3,4}-[A-Za-z0-9-]{3,}',
                r'S\d{3,4}[A-Z]-[A-Za-z0-9-]{2,}',
                r'AP\d{3,4}-[A-Za-z0-9-]{2,}',
                r'AC\d{3,4}-[A-Za-z0-9-]{2,}',
                r'AirEngine\s+\d+[\w-]*',
            ]
            
            all_matches = []
            for pattern in regex_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    all_matches.extend(matches)
            
            if all_matches:
                unique_models = sorted(list(set(all_matches)))
                log(f"[DEBUG] {series_name} 从正则匹配找到 {len(unique_models)} 个型号")
                
                for model_name in unique_models:
                    clean_name = self._clean_model_name(model_name, series_name)
                    if clean_name and clean_name not in models_dict:
                        models_dict[clean_name] = {
                            'name': clean_name,
                            'series_name': series_name,
                            'description': '',
                            'features': [],
                            'specs': {},
                            'links': [],
                            'url': detail_url,
                            'detail_url': detail_url,
                        }
                        log(f"[DEBUG] {series_name} 正则匹配到具体型号: {clean_name}")
        
        models = list(models_dict.values())
        
        for model in models:
            log(f"[DEBUG] {series_name} 最终提取型号: {model['name']}, 规格数: {len(model['specs'])}")
        
        log(f"[DEBUG] {series_name} 共提取到 {len(models)} 个具体型号")
        return models
    
    def _split_model_header(self, headers: List[str], model_columns: List[int]) -> Dict[str, Dict[str, Any]]:
        table_models = {}
        
        for col_idx in model_columns:
            header_text = headers[col_idx].strip()
            if not header_text:
                continue
            
            model_starts = []
            
            for match in re.finditer(r'CloudEngine\s+', header_text, flags=re.I):
                model_starts.append((match.start(), 'ce'))
            
            for match in re.finditer(r'S\d{3,4}', header_text, flags=re.I):
                model_starts.append((match.start(), 's'))
            
            for match in re.finditer(r'AirEngine\s+', header_text, flags=re.I):
                model_starts.append((match.start(), 'ae'))
            
            for match in re.finditer(r'AP\d{3,4}', header_text, flags=re.I):
                model_starts.append((match.start(), 'ap'))
            
            for match in re.finditer(r'AC\d{3,4}', header_text, flags=re.I):
                model_starts.append((match.start(), 'ac'))
            
            model_starts.sort(key=lambda x: x[0])
            
            found_models = []
            for i, (start, mtype) in enumerate(model_starts):
                next_start = model_starts[i + 1][0] if i + 1 < len(model_starts) else len(header_text)
                candidate = header_text[start:next_start].strip()
                
                candidate = re.sub(r'CloudEngine\s*$', '', candidate).strip()
                candidate = re.sub(r'AirEngine\s*$', '', candidate).strip()
                candidate = candidate.rstrip('：: ,;').strip()
                
                if candidate and re.search(r'\d', candidate):
                    found_models.append(candidate)
            
            unique_models = []
            seen = set()
            for model in found_models:
                if model and model not in seen:
                    seen.add(model)
                    unique_models.append(model)
            
            if len(unique_models) > 0:
                log(f"[DEBUG] 拆分表头 '{header_text[:50]}...' 得到 {len(unique_models)} 个型号: {unique_models}")
                for model_name in unique_models:
                    clean_name = self._clean_model_name(model_name, '')
                    if clean_name:
                        table_models[clean_name] = {
                            'col_index': col_idx,
                            'original_header': header_text,
                            'raw_name': model_name,
                        }
            else:
                clean_name = self._clean_model_name(header_text, '')
                if clean_name:
                    table_models[clean_name] = {
                        'col_index': col_idx,
                        'original_header': header_text,
                        'raw_name': header_text,
                    }
        
        return table_models
    
    def _extract_common_specs(self, rows: List) -> Dict[str, str]:
        common_specs = {}
        
        for row in rows[1:]:
            cells = row.find_all(['th', 'td'])
            if len(cells) < 2:
                continue
            
            param_name = cells[0].get_text(strip=True)
            if not param_name or param_name == '参数':
                continue
            
            all_values = []
            for cell in cells[1:]:
                value = cell.get_text(strip=True)
                value = re.sub(r'\s+', ' ', value).strip()
                if value and value not in ['-', '/', '']:
                    all_values.append(value)
            
            if len(all_values) > 0 and all(v == all_values[0] for v in all_values):
                common_specs[param_name] = all_values[0]
        
        return common_specs
    
    def _extract_col_specs(
        self, 
        rows: List, 
        col_idx: int, 
        total_cols: int,
        model_name: str,
        table_models: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        specs = {}
        
        model_names_in_col = [
            name for name, info in table_models.items() 
            if info.get('col_index') == col_idx
        ]
        
        for row in rows[1:]:
            cells = row.find_all(['th', 'td'])
            if len(cells) < 2:
                continue
            
            param_name = cells[0].get_text(strip=True)
            if not param_name or param_name == '参数':
                continue
            
            if col_idx >= len(cells):
                continue
            
            param_value = cells[col_idx].get_text(strip=True)
            param_value = re.sub(r'\s+', ' ', param_value).strip()
            
            if not param_value or param_value in ['-', '/', '']:
                continue
            
            specific_value = self._extract_model_specific_value(param_value, model_name, model_names_in_col)
            
            if specific_value:
                specs[param_name] = specific_value
        
        return specs
    
    def _extract_model_specific_value(
        self, 
        value_text: str, 
        target_model: str,
        all_models_in_col: List[str]
    ) -> str:
        model_patterns = [
            r'CloudEngine\s+S\d{3,4}[-A-Za-z0-9]+',
            r'AirEngine\s+[\w-]+',
            r'S\d{3,4}[-A-Za-z0-9]+',
            r'AP\d{3,4}[-A-Za-z0-9]+',
            r'AC\d{3,4}[-A-Za-z0-9]+',
        ]
        
        target_clean = re.sub(r'[-\s]', '', target_model.lower())
        
        has_model = False
        for pattern in model_patterns:
            if re.search(pattern, value_text, flags=re.I):
                has_model = True
                break
        
        if not has_model:
            return value_text
        
        all_model_starts = []
        for pattern in model_patterns:
            for match in re.finditer(pattern, value_text, flags=re.I):
                all_model_starts.append((match.start(), match.end(), match.group(0)))
        
        all_model_starts.sort(key=lambda x: x[0])
        
        for i, (start, end, model_name) in enumerate(all_model_starts):
            match_clean = re.sub(r'[-\s]', '', model_name.lower())
            
            if target_clean in match_clean or match_clean in target_clean:
                next_start = all_model_starts[i + 1][0] if i + 1 < len(all_model_starts) else len(value_text)
                candidate = value_text[end:next_start].strip()
                
                candidate = re.sub(r'^[：:，,；;\s]+', '', candidate).strip()
                candidate = re.sub(r'[：:，,；;\s]+$', '', candidate).strip()
                
                if candidate:
                    return candidate
        
        return ''
    
    def _clean_model_name(self, model_raw: str, series_name: str) -> str:
        model_raw = re.sub(r'系列.*', '', model_raw)
        model_raw = re.sub(r'^/|/$', '', model_raw)
        model_raw = re.sub(r'\s+', ' ', model_raw)
        model_raw = model_raw.strip()
        
        if len(model_raw) < 4:
            return ''
        
        if model_raw == series_name:
            return ''
        
        if re.search(r'^[A-Za-z]+$', model_raw):
            return ''
        
        if re.match(r'^[A-Za-z]+[-]?$', model_raw):
            return ''
        
        return model_raw
    
    def _create_product_from_model(
        self,
        category: str,
        model_name: str,
        model_info: Dict[str, Any],
        series_info: Dict[str, Any]
    ) -> ProductInfo:
        if not self._is_valid_model_name(model_name):
            return None
        
        series_name = model_info.get('series_name', model_name)
        
        specs = dict(model_info.get('specs', {}))
        
        for db_key, db_specs in HUAWEI_SWITCH_SPECS_DB.items():
            db_key_normalized = db_key.replace('-', '').replace(' ', '')
            model_normalized = model_name.replace('-', '').replace(' ', '')
            
            if db_key_normalized in model_normalized or model_normalized.startswith(db_key_normalized):
                for key, value in db_specs.items():
                    if key not in specs:
                        specs[key] = value
                break
        
        for db_key, db_specs in HUAWEI_WLAN_SPECS_DB.items():
            db_key_normalized = db_key.replace('-', '').replace(' ', '')
            model_normalized = model_name.replace('-', '').replace(' ', '')
            
            if db_key_normalized in model_normalized or model_normalized.startswith(db_key_normalized):
                for key, value in db_specs.items():
                    if key not in specs:
                        specs[key] = value
                break
        
        specs['品牌'] = '华为'
        specs['产品类型'] = category
        specs['系列'] = series_name
        
        description = model_info.get('description', '') or series_info.get('description', '')
        
        links = model_info.get('links', [])
        series_links = series_info.get('links', [])
        for link in series_links:
            if link not in links:
                links.append(link)
        
        return self.create_product_info(
            product_code=model_name,
            product_name=f"华为 {model_name}",
            product_url=model_info.get('url', ''),
            category=category,
            series=series_name,
            description=description,
            specs=specs,
            links=links
        )
    
    def _is_valid_model_name(self, name: str) -> bool:
        if not name or len(name) < 5:
            return False
        
        if not re.search(r'\d', name):
            return False
        
        invalid_patterns = [
            r'^参数$',
            r'^系列$',
            r'^产品$',
            r'^[A-Za-z]{1,3}$',
            r'^CloudEngine$',
            r'^AirEngine$',
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, name, re.I):
                return False
        
        if '华为' in name or '产品' in name:
            return False
        
        return True
    
    def _extract_description_from_detail(self, series_name: str, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 策略1: meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if content and len(content) > 20:
                log(f"[DEBUG] {series_name} 从meta description提取到描述 (长度={len(content)})")
                return re.sub(r'\s+', ' ', content).strip()
        
        # 策略2: .overview 容器
        overview = soup.select_one('.overview')
        if overview:
            text = overview.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 30:
                log(f"[DEBUG] {series_name} 从.overview容器提取到描述 (长度={len(text)})")
                return text
        
        # 策略3: 描述类CSS选择器
        desc_selectors = [
            '.product-intro', '.product-description', '.intro-text',
            '.product-overview', '.overview-text',
            '.description', '.summary', '.product-brief',
            '[class*="overview"]', '[class*="intro"]', '[class*="description"]',
        ]
        
        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                log(f"[DEBUG] {series_name} 尝试选择器 '{selector}'，找到 {len(elements)} 个元素")
                for elem in elements:
                    text = elem.get_text(strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 30 and len(text) < 2000:
                        log(f"[DEBUG] {series_name} 从 '{selector}' 提取到描述 (长度={len(text)})")
                        return text
        
        # 策略4: h1 + p标签
        h1 = soup.find('h1')
        if h1:
            h1_text = h1.get_text(strip=True)
            if h1_text and len(h1_text) > 5:
                next_elem = h1.find_next_sibling()
                if next_elem and next_elem.name == 'p':
                    p_text = next_elem.get_text(strip=True)
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if len(p_text) > 30:
                        desc = h1_text + '。' + p_text
                        log(f"[DEBUG] {series_name} 从h1+p提取到描述 (长度={len(desc)})")
                        return desc
                log(f"[DEBUG] {series_name} 尝试从h1提取: '{h1_text[:60]}'")
                return h1_text
        
        # 策略5: 从包含关键词的p标签提取
        paragraphs = soup.find_all('p')
        log(f"[DEBUG] {series_name} 页面共有 {len(paragraphs)} 个p标签")
        for p in paragraphs:
            text = p.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            if (text and len(text) > 30 and len(text) < 1000 and
                not re.search(r'Copyright|©|Cookie|隐私|声明|版权|All rights', text)):
                if any(kw in text for kw in ['交换机', '核心', '企业', '园区', '数据中心', '高性能', '无线', 'AP']):
                    log(f"[DEBUG] {series_name} 从p标签提取到描述 (长度={len(text)})")
                    return text
        
        log(f"[DEBUG] {series_name} 所有策略均未提取到有效描述")
        return ''
    
    def _create_product_from_series(
        self, 
        category: str, 
        series_name: str, 
        series_info: Dict[str, Any]
    ) -> ProductInfo:
        if not self._is_valid_series_name(series_name):
            return None
        
        series_name = self._clean_series_name(series_name)
        
        product_code = series_name.replace(' ', '-')
        product_name = f"华为 {series_name} 系列"
        
        specs = series_info.get('specs', {})
        specs['品牌'] = '华为'
        specs['产品类型'] = category
        specs['系列'] = series_name
        
        features = series_info.get('features', [])
        if features:
            specs['主要特性'] = '; '.join(features[:5])
        
        description = series_info.get('description', '')
        if not description and features:
            description = features[0] if features else ''
        
        links = series_info.get('links', [])
        
        return self.create_product_info(
            product_code=product_code,
            product_name=product_name,
            product_url=series_info.get('url', ''),
            category=category,
            series=series_name,
            description=description,
            specs=specs,
            links=links
        )
    
    def _is_valid_series_name(self, name: str) -> bool:
        if not name or len(name) < 3:
            return False
        
        invalid_patterns = [
            r'^Wi$',
            r'^系列$',
            r'^产品$',
            r'^[A-Z]{1,2}$',
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, name):
                return False
        
        if '华为' in name or '产品' in name:
            return False
        
        return True
    
    def _clean_series_name(self, name: str) -> str:
        name = re.sub(r'[^\x20-\x7E\u4e00-\u9fffA-Za-z0-9_-]', '', name)
        
        name = name.replace('ç³', '系列')
        name = name.replace('Â', '')
        name = name.replace('Ã', '')
        
        name = name.strip()
        
        if not name.endswith('系列') and 'AirEngine' in name and not re.search(r'[-]$', name):
            parts = name.split()
            if len(parts) > 1 and re.match(r'^\d', parts[-1]):
                pass
            elif len(parts) > 1 and not re.match(r'^[A-Z]', parts[-1]):
                pass
        
        return name
    
    def scrape_switch_products(self) -> List[ProductInfo]:
        return self.scrape_category("交换机", self.switch_url)
    
    def scrape_wlan_products(self) -> List[ProductInfo]:
        return self.scrape_category("无线", self.wlan_url)


def main():
    scraper = HuaweiScraper()
    
    print("=" * 60)
    print("华为数据采集 - 测试模式")
    print("=" * 60)
    
    result = scraper.scrape_all()
    
    print(f"\n{'=' * 60}")
    print(f"采集完成:")
    print(f"{'=' * 60}")
    print(f"产品总数: {len(result.products)}")
    print(f"成功分类: {result.success_count}")
    print(f"失败分类: {result.failed_count}")
    
    for i, product in enumerate(result.products[:10]):
        print(f"\n  [{i+1}] {product.product_name}")
        print(f"      型号: {product.product_code}")
        print(f"      分类: {product.category}")
        print(f"      系列: {product.series}")
        if product.specs:
            print(f"      规格: {list(product.specs.keys())[:5]}")
        if product.links:
            print(f"      链接数: {len(product.links)}")
    
    return result


if __name__ == "__main__":
    main()
