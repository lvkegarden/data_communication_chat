import sys
import json
sys.path.insert(0, 'd:/project/ai/localrest/python')

from prompt_assembler import PromptAssembler


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
                "description": "华为S5735-L-V2系列交换机是企业级接入层交换机，适用于中型企业网络建设。具备智能堆叠、简易运维等特性，支持丰富的网络功能。",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps/3.36Tbps",
                    "包转发率": "108Mpps/126Mpps",
                    "端口数量": "24/48个千兆以太网端口",
                    "产品类型": "交换机",
                    "功能等级": "LI",
                    "硬件版本": "V2"
                })
            },
            {
                "product_code": "S5735-L48T4X-A",
                "product_name": "华为 S5735-L48T4X-A 交换机",
                "category": "接入交换机",
                "series": "S5735",
                "source": "华为",
                "status": "在售",
                "description": "华为S5735-L48T4X-A是企业级接入层交换机，48个千兆电口，4个万兆光口。",
                "specs_json": json.dumps({
                    "交换容量": "336Gbps/3.36Tbps",
                    "包转发率": "108Mpps/126Mpps",
                    "端口数量": "48个千兆电口+4个万兆光口",
                    "产品类型": "交换机"
                })
            },
            {
                "product_code": "S5735-S-V2",
                "product_name": "华为 S5735-S-V2 系列交换机",
                "category": "汇聚交换机",
                "series": "S5735",
                "source": "华为",
                "status": "在售",
                "description": "华为S5735-S-V2系列交换机是企业级汇聚层交换机，支持更丰富的功能。",
                "specs_json": json.dumps({
                    "交换容量": "598Gbps/5.98Tbps",
                    "包转发率": "222Mpps/273Mpps",
                    "产品类型": "交换机",
                    "功能等级": "EI"
                })
            }
        ]
    
    def get_product_by_code(self, code):
        for p in self.mock_products:
            if p['product_code'].upper() == code.upper():
                return p
        return None
    
    def get_all_products_summary(self):
        return [
            {
                "product_code": p["product_code"],
                "product_name": p["product_name"],
                "category": p["category"],
                "series": p["series"],
                "brand": p.get("source", "未知")
            }
            for p in self.mock_products
        ]
    
    def search_products(self, keyword):
        results = []
        keyword = keyword.upper()
        for p in self.mock_products:
            if keyword in p["product_code"].upper() or keyword in p["product_name"].upper():
                results.append(p)
        return results


data_fetcher = MockProductDataFetcher()

print('=' * 80)
print('测试1：完整型号 S5735-L-V2 的处理流程')
print('=' * 80)

assembler = PromptAssembler(data_fetcher)

prompt, context = assembler.assemble_from_message(
    'S5735-L-V2 产品介绍',
    'product_introduction',
    {'product_code': 'S5735-L-V2'}
)

print('\n是否有数据:', context.get('has_data'))
print('是否模糊匹配:', context.get('fuzzy_matched'))

if context.get('product_data'):
    pd = context['product_data']
    print('\n传递给 LLM 的产品信息：')
    print('  产品型号:', pd.get('product_code'))
    print('  产品名称:', pd.get('product_name'))
    print('  产品系列:', pd.get('series'))
    print('  产品类别:', pd.get('category'))
    desc = pd.get('description', '')
    specs = pd.get('specs_json', '')
    print('  描述长度:', len(desc), '字符')
    print('  规格长度:', len(specs), '字符')
    if desc:
        print('  描述预览:', desc[:100], '...')

print('\nPrompt 长度:', len(prompt), '字符')
print('\n--- Prompt 预览（前800字符）---')
print(prompt[:800])

print('\n\n' + '=' * 80)
print('测试2：模糊型号 S5735-L 的处理流程')
print('=' * 80)

prompt2, context2 = assembler.assemble_from_message(
    'S5735-L 产品介绍',
    'product_introduction',
    {'product_code': 'S5735-L'}
)

print('\n是否有数据:', context2.get('has_data'))
print('是否模糊匹配:', context2.get('fuzzy_matched'))
print('原始输入:', context2.get('original_input'))
print('匹配型号:', context2.get('matched_code'))
print('置信度:', context2.get('confidence_level'))

if context2.get('product_data'):
    pd = context2['product_data']
    print('\n传递给 LLM 的产品信息：')
    print('  产品型号:', pd.get('product_code'))
    print('  产品名称:', pd.get('product_name'))
    print('  产品系列:', pd.get('series'))
    desc = pd.get('description', '')
    specs = pd.get('specs_json', '')
    print('  描述长度:', len(desc), '字符')
    print('  规格长度:', len(specs), '字符')
