import logging
from typing import Dict, Any, Optional, List, Tuple

from product_data_fetcher import ProductDataFetcher

logger = logging.getLogger(__name__)


class PromptAssembler:
    """负责意图识别后的数据获取和Prompt拼装"""
    
    def __init__(self, data_fetcher: ProductDataFetcher):
        self.data_fetcher = data_fetcher
        logger.info("PromptAssembler initialized")
    
    def assemble_from_message(self, message: str, intent: str, entities: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        根据消息、意图和实体，从数据库获取产品数据，拼装完整prompt
        
        Returns:
            (prompt, context_info) - 拼装好的prompt和上下文信息
        """
        logger.info("=== PromptAssembler Start ===")
        logger.info("Intent: %s", intent)
        logger.info("Message: %s", message)
        logger.info("Entities: %s", entities)
        
        product_code = entities.get("product_code")
        
        if not product_code:
            product_code = self.extract_product_code_from_message(message)
            logger.info("Extracted product code from message: %s", product_code)
        
        if product_code:
            logger.info("Fetching product data for code: %s", product_code)
            product_data = self.data_fetcher.get_product_by_code(product_code)
            
            if product_data:
                logger.info("Product found: %s (%s)", product_data.get("product_name"), product_code)
                
                if intent == "product_introduction":
                    prompt = self._build_product_intro_prompt(product_data, message)
                    context = {
                        "product_data": product_data,
                        "matched_products": [product_data],
                        "has_data": True
                    }
                elif intent == "competitor_analysis":
                    logger.info("Fetching competitors for: %s", product_code)
                    competitors = self.data_fetcher.get_competitors(product_code, limit=3)
                    logger.info("Found %d competitors", len(competitors))
                    prompt = self._build_competitor_analysis_prompt(product_data, competitors, message)
                    context = {
                        "product_data": product_data,
                        "competitor_data": competitors,
                        "matched_products": [product_data],
                        "has_data": True
                    }
                elif intent == "product_query":
                    prompt = self._build_product_query_prompt(product_data, message)
                    context = {
                        "product_data": product_data,
                        "matched_products": [product_data],
                        "has_data": True
                    }
                else:
                    prompt = self._build_product_intro_prompt(product_data, message)
                    context = {
                        "product_data": product_data,
                        "matched_products": [product_data],
                        "has_data": True
                    }
                
                logger.info("Prompt assembled successfully (length: %d chars)", len(prompt))
                logger.info("=== PromptAssembler End (Success) ===")
                return prompt, context
            else:
                logger.warning("Product not found for code: %s", product_code)
                
                all_products = self.data_fetcher.search_products(keyword=product_code)
                if all_products:
                    logger.info("Found %d similar products", len(all_products))
                    prompt = self._build_similar_products_prompt(all_products, message)
                    context = {
                        "product_data": None,
                        "matched_products": all_products,
                        "has_data": True
                    }
                    logger.info("=== PromptAssembler End (Similar Products) ===")
                    return prompt, context
                else:
                    prompt = f"抱歉，我没有找到产品型号为'{product_code}'的产品信息。请检查型号是否正确，或者我可以帮你查询其他产品。"
                    context = {
                        "product_data": None,
                        "matched_products": [],
                        "has_data": False
                    }
                    logger.info("=== PromptAssembler End (Product Not Found) ===")
                    return prompt, context
        else:
            logger.warning("No product code provided")
            
            if intent == "product_query":
                keyword = self.extract_keyword_from_message(message)
                logger.info("Extracted keyword for query: '%s'", keyword)
                products = self.data_fetcher.search_products(keyword=keyword)
                logger.info("Found %d products for keyword '%s'", len(products), keyword)
                
                if products:
                    prompt = self._build_search_results_prompt(products, keyword, message)
                    context = {
                        "product_data": None,
                        "matched_products": products,
                        "has_data": True
                    }
                    logger.info("=== PromptAssembler End (Search Results) ===")
                    return prompt, context
                else:
                    all_products = self.data_fetcher.get_all_products_summary()
                    if all_products:
                        prompt = self._build_all_products_prompt(all_products, message)
                        context = {
                            "product_data": None,
                            "matched_products": all_products,
                            "has_data": True
                        }
                        logger.info("=== PromptAssembler End (All Products) ===")
                        return prompt, context
                    else:
                        prompt = "当前没有可用的产品信息。"
                        context = {"product_data": None, "matched_products": [], "has_data": False}
                        logger.info("=== PromptAssembler End (No Products) ===")
                        return prompt, context
            else:
                prompt = "请提供要查询的产品型号，例如：'请为RG-AP820C生成产品介绍'或'产品介绍 产品型号:S5735-L'"
                context = {"product_data": None, "matched_products": [], "has_data": False}
                logger.info("=== PromptAssembler End (No Product Code) ===")
                return prompt, context
    
    def _build_product_intro_prompt(self, product: Dict[str, Any], user_message: str) -> str:
        product_name = product.get("product_name", "")
        product_code = product.get("product_code", "")
        series = product.get("series", "")
        category = product.get("category", "")
        status = product.get("status", "")
        description = product.get("description", "")
        specs_json = product.get("specs_json", "")
        
        prompt = f"""你是一个专业的数通产品分析师，擅长撰写清晰、有吸引力的产品介绍。

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
        
        logger.info("Built product intro prompt for %s (%s)", product_name, product_code)
        return prompt
    
    def _build_competitor_analysis_prompt(self, target: Dict[str, Any], competitors: List[Dict[str, Any]], user_message: str) -> str:
        target_name = target.get("product_name", "")
        target_code = target.get("product_code", "")
        target_series = target.get("series", "")
        target_description = target.get("description", "")
        target_specs = target.get("specs_json", "")
        
        competitors_info = ""
        if competitors:
            for i, comp in enumerate(competitors, 1):
                competitors_info += f"【竞品{i}】\n"
                competitors_info += f"- 产品名称：{comp.get('product_name', '')}\n"
                competitors_info += f"- 产品型号：{comp.get('product_code', '')}\n"
                competitors_info += f"- 产品系列：{comp.get('series', '')}\n"
                competitors_info += f"- 产品描述：{comp.get('description', '')}\n"
                competitors_info += f"- 技术规格：{comp.get('specs_json', '')}\n\n"
        else:
            competitors_info = "无具体竞品信息，请根据行业知识进行分析。\n"
        
        prompt = f"""你是一个资深的数通产品竞争情报分析师，擅长进行竞品对比分析。

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
        
        logger.info("Built competitor analysis prompt for %s (%s) with %d competitors", 
                   target_name, target_code, len(competitors))
        return prompt
    
    def _build_product_query_prompt(self, product: Dict[str, Any], user_message: str) -> str:
        product_name = product.get("product_name", "")
        product_code = product.get("product_code", "")
        series = product.get("series", "")
        category = product.get("category", "")
        description = product.get("description", "")
        specs_json = product.get("specs_json", "")
        
        prompt = f"""你是一个数通产品专家，擅长介绍和解答产品相关问题。

用户查询：{user_message}

产品信息如下：
- 产品名称：{product_name}
- 产品型号：{product_code}
- 产品系列：{series}
- 产品类别：{category}
- 产品描述：{description}
- 技术规格：{specs_json}

请根据用户的问题，详细介绍该产品。如果用户有具体问题，请针对性回答。"""
        
        logger.info("Built product query prompt for %s (%s)", product_name, product_code)
        return prompt
    
    def _build_similar_products_prompt(self, products: List[Dict[str, Any]], user_message: str) -> str:
        product_list = ""
        for i, p in enumerate(products, 1):
            product_list += f"{i}. {p.get('product_name', '')} ({p.get('product_code', '')})"
            if p.get('category'):
                product_list += f" - {p['category']}"
            product_list += "\n"
        
        prompt = f"""你是一个数通产品专家。

用户查询：{user_message}

没有找到完全匹配的产品，但找到以下相关产品：
{product_list}

请向用户说明没有找到完全匹配的产品，并列出找到的相关产品供参考。"""
        
        logger.info("Built similar products prompt with %d products", len(products))
        return prompt
    
    def _build_search_results_prompt(self, products: List[Dict[str, Any]], keyword: str, user_message: str) -> str:
        product_list = ""
        for i, p in enumerate(products, 1):
            product_list += f"{i}. {p.get('product_name', '')} ({p.get('product_code', '')})"
            if p.get('category'):
                product_list += f" - {p['category']}"
            product_list += "\n"
        
        prompt = f"""你是一个数通产品专家，擅长介绍和解答产品相关问题。

用户查询：{user_message}
搜索关键词：{keyword}

找到以下相关产品（共{len(products)}个）：
{product_list}

请根据用户的问题，详细介绍相关产品。如果用户有具体问题，请针对性回答；如果用户只是查询，请主动提供产品概览。"""
        
        logger.info("Built search results prompt for keyword '%s' with %d products", keyword, len(products))
        return prompt
    
    def _build_all_products_prompt(self, products: List[Dict[str, Any]], user_message: str) -> str:
        product_list = ""
        for i, p in enumerate(products, 1):
            product_list += f"{i}. {p.get('product_name', '')} ({p.get('product_code', '')})"
            if p.get('category'):
                product_list += f" - {p['category']}"
            product_list += "\n"
        
        prompt = f"""你是一个数通产品专家。

用户查询：{user_message}

以下是所有可用产品（共{len(products)}个）：
{product_list}

请向用户介绍这些产品，可以根据产品类别进行分类说明。"""
        
        logger.info("Built all products prompt with %d products", len(products))
        return prompt
    
    def extract_product_code_from_message(self, message: str) -> Optional[str]:
        import re
        patterns = [
            r'产品[型号代码][:：]?\s*([A-Za-z0-9\-]+)',
            r'为([A-Z]{2,}[0-9][A-Za-z0-9\-]*)生成',
            r'([A-Z]{2,}[0-9][A-Za-z0-9\-]*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                extracted = match.group(1)
                logger.info("Product code extracted: %s (pattern: %s)", extracted, pattern)
                return extracted
        return None
    
    def extract_keyword_from_message(self, message: str) -> str:
        import re
        keywords_to_remove = [
            '查询产品', '产品查询', '产品信息', '查看所有产品', '产品列表',
            '查询', '查看', '搜索', '找'
        ]
        keyword = message
        for kw in keywords_to_remove:
            keyword = keyword.replace(kw, '')
        keyword = keyword.strip()
        
        match = re.search(r'[的]?(.+)', keyword)
        if match:
            keyword = match.group(1).strip()
        
        logger.info("Extracted keyword: '%s'", keyword)
        return keyword
