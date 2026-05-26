import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from product_naming_parser import ProductNamingParser
import json


def test_huawei_switch():
    parser = ProductNamingParser()
    
    test_cases = [
        'S5735-L-V2',
        'S5735-L48T4X-A',
        'S5736-S48T4XC',
        'S6730-H48X6C',
        'S7703',
        'S8700-4',
        'S12708',
        'S16700-4',
        'S5720-52X-PWR-SI',
        'S5735-L24T4S-A-V2',
    ]
    
    print('=' * 80)
    print('华为交换机命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_h3c_switch():
    parser = ProductNamingParser()
    
    test_cases = [
        'S5130S-28P-EI',
        'S5130S-52P-PWR-EI',
        'S5130S-28S-EI',
        'S5560X-54C-EI',
        'S5560X-30F-EI',
        'S5820V2-54QS-GE',
        'S6520X-54QC-EI',
        'S12508G-AF',
        'S10508X',
    ]
    
    print('\n' + '=' * 80)
    print('H3C交换机命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_ruijie_switch():
    parser = ProductNamingParser()
    
    test_cases = [
        'RG-S5750-48GT4XS-E',
        'RG-S5750-24GT4XS-P-L',
        'RG-S5750V2-48GT4XS-L',
        'RG-S5760C-48GT4XS-X',
        'RG-S6120-48XS4QXS-L',
        'RG-S7510',
        'RG-S8610',
        'RG-S2910-24GT4SFP-UP-H',
        'RG-S2928G-E',
    ]
    
    print('\n' + '=' * 80)
    print('锐捷交换机命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_huawei_ap():
    parser = ProductNamingParser()
    
    test_cases = [
        'AirEngine 8760-X1-PRO',
        'AirEngine 6760-X1',
        'AirEngine 5760-51',
        'AirEngine 6760R-51',
        'AP8050DN',
        'AP6750-10T',
        'AP4050DN-E',
        'AP2050DN',
    ]
    
    print('\n' + '=' * 80)
    print('华为无线AP命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_h3c_ap():
    parser = ProductNamingParser()
    
    test_cases = [
        'WA6530',
        'WA6628',
        'WA6520-FIT',
        'WA6320-C-FIT',
        'WA6522-HI',
        'WA5530-SI',
        'WA5320-EI',
        'WA5530-LI',
        'WA2620E-FIT',
    ]
    
    print('\n' + '=' * 80)
    print('H3C无线AP命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_ruijie_ap():
    parser = ProductNamingParser()
    
    test_cases = [
        'RG-AP9860',
        'RG-AP880(TR)',
        'RG-AP850-I',
        'RG-AP840(AR)',
        'RG-AP780',
        'RG-AP730(TR)',
        'RG-AP680-AR',
        'RG-AP620-H(D)',
        'RG-AP520',
        'RG-AP420',
    ]
    
    print('\n' + '=' * 80)
    print('锐捷无线AP命名规则解析测试')
    print('=' * 80)
    
    for code in test_cases:
        result = parser.parse(code)
        print(f'\n产品型号: {code}')
        print(f'  品牌: {result["brand"]}')
        print(f'  产品类型: {result["product_type"]}')
        print(f'  解析状态: {result["parsed"]}')
        print(f'  详细信息: {json.dumps(result["details"], ensure_ascii=False, indent=2)}')
    
    return True


def test_brand_detection():
    parser = ProductNamingParser()
    
    test_cases = [
        ('S5735-L-V2', '华为'),
        ('S5720-52X-PWR-SI', '华为'),
        ('S6730-H48X6C', '华为'),
        ('S5130S-28P-EI', 'H3C'),
        ('S5560X-54C-EI', 'H3C'),
        ('RG-S5750-48GT4XS-E', '锐捷'),
        ('AirEngine 8760-X1-PRO', '华为'),
        ('WA6530', 'H3C'),
        ('RG-AP880(TR)', '锐捷'),
    ]
    
    print('\n' + '=' * 80)
    print('品牌识别测试')
    print('=' * 80)
    
    all_pass = True
    for code, expected_brand in test_cases:
        result = parser.parse(code)
        actual_brand = result["brand"]
        status = 'PASS' if actual_brand == expected_brand else 'FAIL'
        if actual_brand != expected_brand:
            all_pass = False
        print(f'{status}: {code} -> {actual_brand} (期望: {expected_brand})')
    
    print(f'\n品牌识别测试结果: {"全部通过" if all_pass else "存在失败"}')
    return all_pass


def test_similarity_comparison():
    parser = ProductNamingParser()
    
    product_a = parser.parse('S5735-L-V2')
    product_b = parser.parse('S5130S-28P-EI')
    product_c = parser.parse('RG-S5750-48GT4XS-E')
    
    print('\n' + '=' * 80)
    print('产品相似性比较测试')
    print('=' * 80)
    
    print(f'\n产品A (华为): {product_a["product_code"]}')
    print(f'  品牌: {product_a["brand"]}')
    print(f'  类型: {product_a["product_type"]}')
    print(f'  详细: {product_a["details"]}')
    
    print(f'\n产品B (H3C): {product_b["product_code"]}')
    print(f'  品牌: {product_b["brand"]}')
    print(f'  类型: {product_b["product_type"]}')
    print(f'  详细: {product_b["details"]}')
    
    print(f'\n产品C (锐捷): {product_c["product_code"]}')
    print(f'  品牌: {product_c["brand"]}')
    print(f'  类型: {product_c["product_type"]}')
    print(f'  详细: {product_c["details"]}')
    
    similarity_ab = parser.parse_similarity(product_a, product_b)
    similarity_ac = parser.parse_similarity(product_a, product_c)
    similarity_bc = parser.parse_similarity(product_b, product_c)
    
    print(f'\n产品A vs 产品B (华为 vs H3C):')
    print(f'  同品牌: {similarity_ab["same_brand"]}')
    print(f'  同类型: {similarity_ab["same_type"]}')
    print(f'  相似度评分: {similarity_ab["similarity_score"]}')
    print(f'  匹配字段: {similarity_ab["matched_fields"]}')
    
    print(f'\n产品A vs 产品C (华为 vs 锐捷):')
    print(f'  同品牌: {similarity_ac["same_brand"]}')
    print(f'  同类型: {similarity_ac["same_type"]}')
    print(f'  相似度评分: {similarity_ac["similarity_score"]}')
    print(f'  匹配字段: {similarity_ac["matched_fields"]}')
    
    print(f'\n产品B vs 产品C (H3C vs 锐捷):')
    print(f'  同品牌: {similarity_bc["same_brand"]}')
    print(f'  同类型: {similarity_bc["same_type"]}')
    print(f'  相似度评分: {similarity_bc["similarity_score"]}')
    print(f'  匹配字段: {similarity_bc["matched_fields"]}')
    
    return True


def main():
    print('产品命名规则解析模块测试\n')
    
    test_huawei_switch()
    test_h3c_switch()
    test_ruijie_switch()
    test_huawei_ap()
    test_h3c_ap()
    test_ruijie_ap()
    test_brand_detection()
    test_similarity_comparison()
    
    print('\n' + '=' * 80)
    print('测试完成')
    print('=' * 80)


if __name__ == '__main__':
    main()
