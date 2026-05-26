import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    
    @staticmethod
    def build_product_introduction_prompt(product: Dict[str, Any]) -> str:
        product_name = product.get("product_name", "")
        product_code = product.get("product_code", "")
        series = product.get("series", "")
        category = product.get("category", "")
        status = product.get("status", "")
        description = product.get("description", "")
        specs_json = product.get("specs_json", "")
        
        logger.info("Building product introduction prompt for: %s (%s)", product_name, product_code)
        logger.info("Product fields - series: %s, category: %s, status: %s", series, category, status)
        logger.info("Description length: %d chars, specs_json length: %d chars", 
                   len(description), len(specs_json))
        
        prompt = f"""你是一个专业的产品分析师，擅长撰写清晰、有吸引力的产品介绍。

请根据以下产品信息，生成一份专业的产品介绍：

【产品名称】{product_name}
【产品型号】{product_code}
【产品系列】{series}
【产品类别】{category}
【产品状态】{status}
【产品描述】{description}
【技术规格】{specs_json}

请按照以下结构输出：
1. 产品概述（100-200字）
2. 核心卖点（3-5条）
3. 技术亮点（3-5条）
4. 适用场景（2-4个）
5. 总结

要求：
- 语言专业、简洁
- 突出产品优势和差异化特点
- 使用技术术语但要易于理解
- 适合B2B营销场景"""
        
        logger.info("Product introduction prompt built successfully (length: %d chars)", len(prompt))
        return prompt

    @staticmethod
    def build_competitor_analysis_prompt(target_product: Dict[str, Any], competitors: list) -> str:
        target_name = target_product.get("product_name", "")
        target_code = target_product.get("product_code", "")
        target_series = target_product.get("series", "")
        target_description = target_product.get("description", "")
        target_specs = target_product.get("specs_json", "")
        
        logger.info("Building competitor analysis prompt for: %s (%s)", target_name, target_code)
        logger.info("Number of competitors: %d", len(competitors))
        
        competitors_info = ""
        if competitors:
            for i, comp in enumerate(competitors, 1):
                comp_name = comp.get('product_name', '')
                comp_code = comp.get('product_code', '')
                logger.info("Competitor %d: %s (%s)", i, comp_name, comp_code)
                competitors_info += f"【竞品{i}】\n"
                competitors_info += f"- 产品名称：{comp_name}\n"
                competitors_info += f"- 产品型号：{comp_code}\n"
                competitors_info += f"- 产品系列：{comp.get('series', '')}\n"
                competitors_info += f"- 产品描述：{comp.get('description', '')}\n"
                competitors_info += f"- 技术规格：{comp.get('specs_json', '')}\n\n"
        else:
            logger.info("No competitors provided, using placeholder")
            competitors_info = "无具体竞品信息，请根据行业知识进行分析。\n"
        
        prompt = f"""你是一个资深的竞争情报分析师，擅长进行竞品对比分析。

请对以下产品进行全面的竞品分析：

【目标产品】
- 产品名称：{target_name}
- 产品型号：{target_code}
- 产品系列：{target_series}
- 产品描述：{target_description}
- 技术规格：{target_specs}

【竞品信息】
{competitors_info}

请按照以下结构输出分析报告：
1. 市场定位分析
   - 目标市场
   - 目标客户群体
   - 产品定位

2. 竞品对比分析
   - 功能对比
   - 技术参数对比
   - 价格对比（如可获取）
   - 优劣势对比

3. SWOT分析
   - 优势（Strengths）
   - 劣势（Weaknesses）
   - 机会（Opportunities）
   - 威胁（Threats）

4. 竞争策略建议
   - 差异化策略
   - 市场策略
   - 产品优化建议

5. 总结

要求：
- 分析客观、数据驱动
- 提供具体的对比维度
- 给出可执行的建议
- 使用表格进行对比（如适用）
- 适合企业决策参考"""
        
        logger.info("Competitor analysis prompt built successfully (length: %d chars)", len(prompt))
        return prompt

    @staticmethod
    def build_product_query_prompt(keyword: str, products: list) -> str:
        logger.info("Building product query prompt for keyword: '%s' (products: %d)", keyword, len(products))
        
        if not products:
            logger.info("No products found for keyword: '%s'", keyword)
            return f"抱歉，我没有找到与'{keyword}'相关的产品信息。请尝试其他关键词。"
        
        product_list = ""
        for i, p in enumerate(products, 1):
            p_name = p.get('product_name', '')
            p_code = p.get('product_code', '')
            p_category = p.get('category', '')
            logger.info("Product %d: %s (%s) - %s", i, p_name, p_code, p_category)
            product_list += f"{i}. {p_name} ({p_code})"
            if p_category:
                product_list += f" - {p_category}"
            product_list += "\n"
        
        prompt = f"""你是一个数通产品专家，擅长介绍和解答产品相关问题。

用户查询关键词：{keyword}

找到以下相关产品：
{product_list}

请根据用户的问题，详细介绍相关产品。如果用户有具体问题，请针对性回答；如果用户只是查询，请主动提供产品概览。"""
        
        logger.info("Product query prompt built successfully (length: %d chars)", len(prompt))
        return prompt
