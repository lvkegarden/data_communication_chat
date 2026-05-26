import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from fuzzy_input_handler import FuzzyInputHandler, FuzzyInputResult, FuzzyMatchResult
from product_naming_parser import ProductNamingParser
from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator


class MockProductDataFetcher:
    def __init__(self):
        self.mock_products = [
            {
                "product_code": "S5735-L-V2",
                "product_name": "华为 S5735-L-V2 系列交换机",
                "category": "接入交换机",
                "series": "S5735",
                "source": "华为",
                "status": "在售",
                "description": "华为S5735-L-V2系列交换机是企业级接入层交换机",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps/3.36Tbps",
                    "包转发率": "108Mpps/126Mpps",
                    "端口数量": "24/48个千兆以太网端口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "S5735-L48T4X-A",
                "product_name": "华为 S5735-L48T4X-A 交换机",
                "category": "接入交换机",
                "series": "S5735",
                "source": "华为",
                "status": "在售",
                "description": "华为S5735-L48T4X-A是企业级接入层交换机，48个千兆电口，4个万兆光口",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps/3.36Tbps",
                    "包转发率": "108Mpps/126Mpps",
                    "端口数量": "48个千兆电口+4个万兆光口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "S5735-L24T4S-A-V2",
                "product_name": "华为 S5735-L24T4S-A-V2 交换机",
                "category": "接入交换机",
                "series": "S5735",
                "source": "华为",
                "status": "在售",
                "description": "华为S5735-L24T4S-A-V2是企业级接入层交换机",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps/3.36Tbps",
                    "包转发率": "108Mpps/126Mpps",
                    "端口数量": "24个千兆电口+4个千兆光口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "S5130S-28P-EI",
                "product_name": "H3C S5130S-28P-EI 交换机",
                "category": "接入交换机",
                "series": "S5130",
                "source": "H3C",
                "status": "在售",
                "description": "H3C S5130S-28P-EI是企业级接入层交换机",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps",
                    "包转发率": "96Mpps",
                    "端口数量": "24个千兆电口+4个千兆光口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "RG-S5750-48GT4XS-E",
                "product_name": "锐捷 RG-S5750-48GT4XS-E 交换机",
                "category": "接入交换机",
                "series": "S5750",
                "source": "锐捷",
                "status": "在售",
                "description": "锐捷RG-S5750-48GT4XS-E是企业级接入层交换机",
                "specs_json": json.dumps({
                    "交换容量": "598Gbps/5.98Tbps",
                    "包转发率": "168Mpps",
                    "端口数量": "48个千兆电口+4个万兆光口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "RG-AP880(TR)",
                "product_name": "锐捷 RG-AP880(TR) 无线AP",
                "category": "无线AP",
                "series": "AP880",
                "source": "锐捷",
                "status": "在售",
                "description": "锐捷RG-AP880(TR)是三射频WiFi 6无线接入点",
                "specs_json": json.dumps({
                    "WiFi标准": "WiFi 6",
                    "射频数量": "三射频",
                    "产品类型": "无线AP"
                })
            },
            {
                "product_code": "AirEngine 8760-X1-PRO",
                "product_name": "华为 AirEngine 8760-X1-PRO 无线AP",
                "category": "无线AP",
                "series": "AirEngine 8700",
                "source": "华为",
                "status": "在售",
                "description": "华为AirEngine 8760-X1-PRO是高端WiFi 6无线接入点",
                "specs_json": json.dumps({
                    "WiFi标准": "WiFi 6",
                    "产品类型": "无线AP"
                })
            },
            {
                "product_code": "WA6530",
                "product_name": "H3C WA6530 无线AP",
                "category": "无线AP",
                "series": "WA6500",
                "source": "H3C",
                "status": "在售",
                "description": "H3C WA6530是企业级WiFi 6无线接入点",
                "specs_json": json.dumps({
                    "WiFi标准": "WiFi 6",
                    "产品类型": "无线AP"
                })
            }
        ]
    
    def get_product_by_code(self, product_code: str):
        for product in self.mock_products:
            if product["product_code"] == product_code:
                return product
        return None
    
    def search_products(self, keyword: str = None, category: str = None, source: str = None):
        results = []
        for product in self.mock_products:
            match = True
            if keyword:
                keyword_upper = keyword.upper()
                if (keyword_upper not in product["product_code"].upper() and
                    keyword_upper not in product["product_name"].upper() and
                    keyword_upper not in product.get("category", "").upper()):
                    match = False
            if category:
                if category not in product.get("category", ""):
                    match = False
            if source:
                if source not in product.get("source", ""):
                    match = False
            if match:
                results.append(product)
        return results
    
    def get_all_products_summary(self):
        return self.mock_products
    
    def get_competitors(self, product_code: str, limit: int = 3):
        return []


def test_fuzzy_input_detection():
    print("\n" + "=" * 80)
    print("测试1：模糊输入检测")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    test_cases = [
        ("S5735", True, "部分型号，应该检测为模糊输入"),
        ("S5735-L-V2", False, "完整型号，不应该检测为模糊输入"),
        ("华为交换机", True, "只有品牌和类型，应该检测为模糊输入"),
        ("S5130", True, "部分型号，应该检测为模糊输入"),
        ("RG-AP880", True, "部分型号，应该检测为模糊输入"),
        ("AirEngine", True, "只有品牌标识，应该检测为模糊输入"),
    ]
    
    all_pass = True
    for input_text, expected_is_fuzzy, description in test_cases:
        result = handler.handle(input_text)
        actual = result.is_fuzzy
        status = "PASS" if actual == expected_is_fuzzy else "FAIL"
        if actual != expected_is_fuzzy:
            all_pass = False
        print(f"{status}: '{input_text}' -> is_fuzzy={actual} (期望: {expected_is_fuzzy}) - {description}")
    
    return all_pass


def test_fuzzy_match_scoring():
    print("\n" + "=" * 80)
    print("测试2：模糊匹配评分")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    test_cases = [
        ("S5735", "应该匹配华为S5735系列产品"),
        ("S5130", "应该匹配H3C S5130系列产品"),
        ("RG-AP880", "应该匹配锐捷AP880系列产品"),
        ("AirEngine", "应该匹配华为AirEngine系列产品"),
    ]
    
    all_pass = True
    for input_text, description in test_cases:
        result = handler.handle(input_text)
        print(f"\n输入: '{input_text}' - {description}")
        print(f"  解析信息: {result.parsed_info}")
        print(f"  是否模糊: {result.is_fuzzy}")
        print(f"  置信度: {result.confidence_level}")
        print(f"  候选数量: {len(result.candidates)}")
        
        if result.candidates:
            print(f"  最佳匹配: {result.best_match.product_code} ({result.best_match.product_name})")
            print(f"  匹配分数: {result.best_match.match_score:.2f}")
            print(f"  匹配字段: {result.best_match.matched_fields}")
        
        if result.is_fuzzy and len(result.candidates) == 0:
            print(f"  WARNING: 检测到模糊输入但没有找到候选")
            all_pass = False
    
    return all_pass


def test_confidence_levels():
    print("\n" + "=" * 80)
    print("测试3：置信度级别")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    levels = handler.get_confidence_levels()
    for level, info in levels.items():
        print(f"\n置信度级别: {level}")
        print(f"  阈值: {info['threshold']}")
        print(f"  描述: {info['description']}")
        print(f"  需要确认: {info['needs_confirmation']}")
    
    return True


def test_suggested_messages():
    print("\n" + "=" * 80)
    print("测试4：建议消息生成")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    test_cases = [
        "S5735",
        "S5130",
        "华为交换机",
        "不存在的型号",
    ]
    
    for input_text in test_cases:
        result = handler.handle(input_text)
        print(f"\n输入: '{input_text}'")
        print(f"  置信度: {result.confidence_level}")
        print(f"  需要确认: {result.needs_user_confirmation}")
        print(f"  建议消息:")
        print(f"    {result.suggested_message[:100]}..." if len(result.suggested_message) > 100 else f"    {result.suggested_message}")
    
    return True


def test_parsed_info_extraction():
    print("\n" + "=" * 80)
    print("测试5：解析信息提取")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    test_cases = [
        ("S5735", {"product_type": "交换机", "brand": "华为"}),
        ("S5130S", {"product_type": "交换机", "brand": "H3C"}),
        ("RG-AP880", {"product_type": "无线AP", "brand": "锐捷"}),
        ("华为交换机", {"product_type": "交换机", "brand": "华为"}),
        ("AirEngine", {"brand": "华为"}),
    ]
    
    all_pass = True
    for input_text, expected in test_cases:
        result = handler.handle(input_text)
        parsed = result.parsed_info
        
        print(f"\n输入: '{input_text}'")
        print(f"  解析到的品牌: {parsed.get('brand')}")
        print(f"  解析到的类型: {parsed.get('product_type')}")
        print(f"  系列模式: {parsed.get('series_pattern')}")
        print(f"  型号候选: {parsed.get('product_code_candidate')}")
        print(f"  关键词: {parsed.get('keywords')}")
        
        if expected.get('brand') and parsed.get('brand') != expected.get('brand'):
            print(f"  FAIL: 品牌不匹配，期望: {expected.get('brand')}")
            all_pass = False
        
        if expected.get('product_type') and parsed.get('product_type') != expected.get('product_type'):
            print(f"  FAIL: 产品类型不匹配，期望: {expected.get('product_type')}")
            all_pass = False
    
    return all_pass


def test_mixed_strategy():
    print("\n" + "=" * 80)
    print("测试6：混合策略（高置信度自动匹配，低置信度需要确认）")
    print("=" * 80)
    
    handler = FuzzyInputHandler(
        data_fetcher=MockProductDataFetcher(),
        naming_parser=ProductNamingParser(),
        similarity_evaluator=SimilarityEvaluator()
    )
    
    test_cases = [
        ("S5735-L-V2", "direct", False, "完整型号，直接匹配"),
        ("S5735-L48T4X-A", "direct", False, "完整型号，直接匹配"),
        ("S5735", None, None, "部分型号，根据匹配度决定"),
        ("S5130", None, None, "部分型号，根据匹配度决定"),
        ("华为", None, True, "只有品牌，需要更多信息"),
    ]
    
    all_pass = True
    for input_text, expected_confidence, expected_needs_confirm, description in test_cases:
        result = handler.handle(input_text)
        
        print(f"\n输入: '{input_text}' - {description}")
        print(f"  是否模糊: {result.is_fuzzy}")
        print(f"  置信度级别: {result.confidence_level}")
        print(f"  需要用户确认: {result.needs_user_confirmation}")
        print(f"  候选数量: {len(result.candidates)}")
        
        if expected_confidence == "direct":
            if result.is_fuzzy:
                print(f"  FAIL: 期望直接匹配，但检测为模糊输入")
                all_pass = False
            else:
                print(f"  PASS: 直接匹配（非模糊输入）")
        elif expected_needs_confirm is not None:
            if result.needs_user_confirmation != expected_needs_confirm:
                print(f"  WARN: 确认需求不同，期望: {expected_needs_confirm}, 实际: {result.needs_user_confirmation}")
            else:
                print(f"  PASS: 确认需求符合预期")
        else:
            print(f"  INFO: 部分型号，置信度级别: {result.confidence_level}")
            if result.confidence_level == "high":
                print(f"  INFO: 高置信度匹配，将自动使用最佳匹配")
            elif result.confidence_level == "medium":
                print(f"  INFO: 中等置信度匹配，需要用户确认")
    
    return all_pass


def main():
    print("\n" + "=" * 80)
    print("模糊输入处理模块测试")
    print("=" * 80)
    
    results = []
    
    results.append(("模糊输入检测", test_fuzzy_input_detection()))
    results.append(("模糊匹配评分", test_fuzzy_match_scoring()))
    results.append(("置信度级别", test_confidence_levels()))
    results.append(("建议消息生成", test_suggested_messages()))
    results.append(("解析信息提取", test_parsed_info_extraction()))
    results.append(("混合策略", test_mixed_strategy()))
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    all_pass = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"总体结果: {'全部通过' if all_pass else '存在失败'}")
    print("=" * 80)


if __name__ == '__main__':
    main()
