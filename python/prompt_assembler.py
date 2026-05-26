import logging
import time
import json
from typing import Dict, Any, Optional, List, Tuple

from product_data_fetcher import ProductDataFetcher
from similarity_evaluator import SimilarityEvaluator
from product_naming_parser import ProductNamingParser
from fuzzy_input_handler import FuzzyInputHandler, FuzzyInputResult

logger = logging.getLogger(__name__)


class PromptAssembler:
    """负责意图识别后的数据获取和Prompt拼装"""
    
    def __init__(self, data_fetcher: ProductDataFetcher, similarity_evaluator: SimilarityEvaluator = None, 
                 naming_parser: ProductNamingParser = None, fuzzy_handler: FuzzyInputHandler = None):
        self.data_fetcher = data_fetcher
        self.naming_parser = naming_parser or ProductNamingParser()
        self.similarity_evaluator = similarity_evaluator or SimilarityEvaluator(self.naming_parser)
        self.fuzzy_handler = fuzzy_handler or FuzzyInputHandler(data_fetcher, self.naming_parser, self.similarity_evaluator)
        logger.info("PromptAssembler initialized with naming parser and fuzzy input handler")
    
    def _pre_filter_candidates(self, target_product: Dict[str, Any], candidates_summary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        快速预筛选：根据摘要信息快速过滤明显不相关的产品
        减少需要获取完整数据的产品数量
        """
        target_type = target_product.get('product_type', '').lower()
        target_category = target_product.get('category', '').lower()
        target_brand = self.similarity_evaluator._extract_brand(target_product)
        
        filtered = []
        for candidate in candidates_summary:
            candidate_code = candidate.get('product_code', '')
            target_code = target_product.get('product_code', '')
            
            if candidate_code == target_code:
                continue
            
            candidate_type = candidate.get('product_type', '').lower()
            candidate_category = candidate.get('category', '').lower()
            candidate_brand = self.similarity_evaluator._extract_brand(candidate)
            
            if target_brand and candidate_brand and target_brand == candidate_brand:
                continue
            
            if target_type and candidate_type:
                if target_type != candidate_type:
                    continue
            
            if target_category and candidate_category:
                if target_category != candidate_category:
                    continue
            
            filtered.append(candidate)
        
        return filtered
    
    def _select_competitors_with_brand_diversity(self, evaluated: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        """
        选择竞品时考虑品牌多样性，确保选中的竞品来自不同品牌（如果有足够多的品牌）
        策略：
        1. 先按品牌分组，每组保留最高分的产品
        2. 如果品牌数 >= limit，每个品牌选1个最高分
        3. 如果品牌数 < limit，先用每个品牌的最高分填满，再用次高分补充
        """
        if not evaluated:
            return []
        
        by_brand = {}
        for item in evaluated:
            brand = item.get('brand', '未知') or '未知'
            if brand not in by_brand:
                by_brand[brand] = []
            by_brand[brand].append(item)
        
        for brand in by_brand:
            by_brand[brand].sort(key=lambda x: x['score'], reverse=True)
        
        brands = list(by_brand.keys())
        logger.info("Available brands for competitor selection: %s", brands)
        
        selected = []
        selected_brands = set()
        
        if len(brands) >= limit:
            brand_index = 0
            while len(selected) < limit:
                brand = brands[brand_index % len(brands)]
                if by_brand[brand]:
                    item = by_brand[brand].pop(0)
                    selected.append(item['product'])
                    selected_brands.add(brand)
                brand_index += 1
        else:
            for brand in brands:
                if by_brand[brand]:
                    item = by_brand[brand].pop(0)
                    selected.append(item['product'])
                    selected_brands.add(brand)
            
            while len(selected) < limit:
                for brand in brands:
                    if len(selected) >= limit:
                        break
                    if by_brand[brand]:
                        item = by_brand[brand].pop(0)
                        selected.append(item['product'])
        
        logger.info("Selected competitors with brand diversity (limit=%d)", limit)
        logger.info("  Selected brands: %s", selected_brands)
        
        return selected
    
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
            product_code = product_code.upper()
            logger.info("Product code normalized to uppercase: %s", product_code)
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
                    logger.info("=== Competitor Analysis Data Fetching ===")
                    overall_start = time.time()
                    
                    t1 = time.time()
                    logger.info("Step 1: Fetching all products for similarity evaluation")
                    all_products_summary = self.data_fetcher.get_all_products_summary()
                    t2 = time.time()
                    logger.info("  Total products in database: %d (cost: %.2f ms)", 
                               len(all_products_summary), (t2-t1)*1000)
                    
                    t1 = time.time()
                    logger.info("Step 2: Pre-filtering candidates (by product_type, category, brand)")
                    filtered_candidates = self._pre_filter_candidates(product_data, all_products_summary)
                    t2 = time.time()
                    logger.info("  Candidates after pre-filter: %d -> %d (cost: %.2f ms)", 
                               len(all_products_summary)-1, len(filtered_candidates), (t2-t1)*1000)
                    
                    logger.info("Step 3: Evaluating similarity for competitor selection")
                    target_code = product_data.get('product_code', '')
                    evaluated = []
                    fetch_count = 0
                    eval_start = time.time()
                    
                    for candidate_summary in filtered_candidates:
                        candidate_code = candidate_summary.get('product_code', '')
                        
                        tt1 = time.time()
                        candidate_full = self.data_fetcher.get_product_by_code(candidate_code)
                        tt2 = time.time()
                        fetch_count += 1
                        
                        if not candidate_full:
                            continue
                        
                        result = self.similarity_evaluator.evaluate(product_data, candidate_full)
                        if result['is_competitor']:
                            evaluated.append({
                                'product': candidate_full,
                                'score': result['total_score'],
                                'brand': result.get('candidate_brand', '')
                            })
                    
                    eval_end = time.time()
                    logger.info("  Similarity evaluation completed:")
                    logger.info("    - Full data fetched: %d products", fetch_count)
                    logger.info("    - Qualified competitors: %d", len(evaluated))
                    logger.info("    - Total cost: %.2f ms (avg %.2f ms/fetch)", 
                               (eval_end-eval_start)*1000, 
                               (eval_end-eval_start)*1000/fetch_count if fetch_count > 0 else 0)
                    
                    t1 = time.time()
                    evaluated.sort(key=lambda x: x['score'], reverse=True)
                    
                    competitors = self._select_competitors_with_brand_diversity(evaluated, 3)
                    
                    t2 = time.time()
                    logger.info("Step 4: Sorting and selecting top competitors with brand diversity (cost: %.2f ms)", 
                               (t2-t1)*1000)
                    
                    logger.info("Found %d qualified competitors, selected top %d", 
                               len(evaluated), len(competitors))
                    for i, comp in enumerate(competitors, 1):
                        logger.info("  Competitor %d: %s (%s) - brand: %s",
                                   i, comp.get('product_name'), comp.get('product_code'),
                                   self.similarity_evaluator._extract_brand(comp))
                    
                    overall_end = time.time()
                    logger.info("=== Competitor Analysis Total Cost: %.2f ms ===", 
                               (overall_end-overall_start)*1000)
                    
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
                logger.warning("Product not found for code: %s, trying fuzzy input handling", product_code)
                
                fuzzy_result = self.fuzzy_handler.handle(product_code)
                
                if fuzzy_result.is_fuzzy and fuzzy_result.best_match:
                    logger.info("Fuzzy input handler found best match: %s (confidence: %s, score: %.2f)",
                               fuzzy_result.best_match.product_code,
                               fuzzy_result.confidence_level,
                               fuzzy_result.best_match.match_score)
                    
                    if fuzzy_result.confidence_level == "high":
                        best_code = fuzzy_result.best_match.product_code
                        logger.info("High confidence match, using %s instead of %s", best_code, product_code)
                        
                        fuzzy_product_data = self.data_fetcher.get_product_by_code(best_code)
                        if fuzzy_product_data:
                            context = {
                                "product_data": fuzzy_product_data,
                                "matched_products": [fuzzy_product_data],
                                "has_data": True,
                                "fuzzy_matched": True,
                                "original_input": product_code,
                                "matched_code": best_code,
                                "confidence_level": fuzzy_result.confidence_level
                            }
                            
                            if intent == "product_introduction":
                                prompt = self._build_product_intro_prompt(fuzzy_product_data, message)
                            elif intent == "competitor_analysis":
                                prompt, comp_context = self._handle_competitor_analysis_with_product(fuzzy_product_data, message)
                                context.update(comp_context)
                            elif intent == "product_query":
                                prompt = self._build_product_query_prompt(fuzzy_product_data, message)
                            else:
                                prompt = self._build_product_intro_prompt(fuzzy_product_data, message)
                            
                            logger.info("Prompt assembled with fuzzy matched product (length: %d chars)", len(prompt))
                            logger.info("=== PromptAssembler End (Fuzzy Match Success) ===")
                            return prompt, context
                    
                    if fuzzy_result.needs_user_confirmation:
                        logger.info("Needs user confirmation, generating suggestion message")
                        candidates_data = []
                        for candidate in fuzzy_result.candidates[:5]:
                            candidate_full = self.data_fetcher.get_product_by_code(candidate.product_code)
                            if candidate_full:
                                candidates_data.append(candidate_full)
                        
                        if candidates_data:
                            prompt = self._build_fuzzy_confirmation_prompt(
                                candidates_data, 
                                product_code, 
                                fuzzy_result.confidence_level,
                                message
                            )
                            context = {
                                "product_data": None,
                                "matched_products": candidates_data,
                                "has_data": True,
                                "fuzzy_matched": True,
                                "original_input": product_code,
                                "needs_confirmation": True,
                                "confidence_level": fuzzy_result.confidence_level,
                                "candidates": [c.to_dict() if hasattr(c, 'to_dict') else {
                                    "product_code": c.product_code,
                                    "product_name": c.product_name,
                                    "brand": c.brand,
                                    "category": c.category,
                                    "match_score": c.match_score,
                                    "matched_fields": c.matched_fields
                                } for c in fuzzy_result.candidates[:5]]
                            }
                            logger.info("=== PromptAssembler End (Fuzzy Needs Confirmation) ===")
                            return prompt, context
                
                all_products = self.data_fetcher.search_products(keyword=product_code)
                if all_products:
                    logger.info("Found %d similar products via keyword search", len(all_products))
                    prompt = self._build_similar_products_prompt(all_products, message)
                    context = {
                        "product_data": None,
                        "matched_products": all_products,
                        "has_data": True
                    }
                    logger.info("=== PromptAssembler End (Similar Products via Keyword) ===")
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
    
    def _format_naming_info(self, naming: Dict[str, Any]) -> str:
        if not naming or not naming.get('parsed'):
            return 'N/A'
        
        details = naming.get('details', {})
        parts = []
        
        brand = naming.get('brand', '')
        if brand:
            parts.append(f"品牌: {brand}")
        
        product_type = naming.get('product_type', '')
        if product_type:
            parts.append(f"产品类型: {product_type}")
        
        switch_level = details.get('switch_level', '')
        if switch_level:
            parts.append(f"交换机等级: {switch_level}")
        
        feature_level = details.get('feature_level', '')
        if feature_level:
            feature_name = details.get('feature_name', '')
            parts.append(f"功能等级: {feature_level}" + (f" ({feature_name})" if feature_name else ''))
        
        port_count = details.get('port_count', '')
        if port_count:
            parts.append(f"端口数量: {port_count}")
        
        port_type = details.get('port_type', '')
        if port_type:
            parts.append(f"端口类型: {port_type}")
        
        port_speed = details.get('port_speed', '')
        if port_speed:
            parts.append(f"端口速率: {port_speed}")
        
        if details.get('poe'):
            poe_type = details.get('poe_type', 'PoE')
            parts.append(f"支持PoE: {poe_type}")
        
        hardware_version = details.get('hardware_version', '')
        if hardware_version:
            parts.append(f"硬件版本: {hardware_version}")
        
        wifi_generation = details.get('wifi_generation', '')
        if wifi_generation:
            parts.append(f"WiFi代际: {wifi_generation}")
        
        level = details.get('level', '')
        if level:
            parts.append(f"产品定位: {level}")
        
        form_factor = details.get('form_factor', '')
        if form_factor:
            parts.append(f"产品形态: {form_factor}")
        
        special_feature = details.get('special_feature', '')
        if special_feature:
            special_feature_name = details.get('special_feature_name', '')
            parts.append(f"特殊功能: {special_feature}" + (f" ({special_feature_name})" if special_feature_name else ''))
        
        return '; '.join(parts)
    
    def _build_competitor_analysis_prompt(self, target: Dict[str, Any], competitors: List[Dict[str, Any]], user_message: str) -> str:
        target_name = target.get("product_name", "")
        target_code = target.get("product_code", "")
        target_series = target.get("series", "")
        target_description = target.get("description", "")
        target_specs = target.get("specs_json", "")
        
        target_naming = self.naming_parser.parse(target_code)
        target_brand = target_naming.get('brand') or self.similarity_evaluator._extract_brand(target)
        target_naming_info = self._format_naming_info(target_naming)
        
        competitors_info = ""
        if competitors:
            for i, comp in enumerate(competitors, 1):
                comp_code = comp.get('product_code', '')
                comp_naming = self.naming_parser.parse(comp_code)
                comp_brand = comp_naming.get('brand') or self.similarity_evaluator._extract_brand(comp)
                comp_naming_info = self._format_naming_info(comp_naming)
                
                similarity_result = self.similarity_evaluator.evaluate(target, comp)
                similarity_score = similarity_result.get('total_score', 0)
                similarity_breakdown = similarity_result.get('breakdown', [])
                similarity_details = '; '.join([f"{b['category']}({b['score']}分)" for b in similarity_breakdown if b['score'] > 0])
                
                competitors_info += f"### 竞品{i}: {comp_brand} {comp.get('product_name', '')}\n"
                competitors_info += f"- **产品型号**: {comp_code}\n"
                competitors_info += f"- **产品品牌**: {comp_brand}\n"
                competitors_info += f"- **产品系列**: {comp.get('series', '')}\n"
                competitors_info += f"- **命名解析信息**: {comp_naming_info}\n"
                competitors_info += f"- **与目标产品相似度**: {similarity_score}分\n"
                competitors_info += f"- **相似度匹配项**: {similarity_details if similarity_details else 'N/A'}\n"
                competitors_info += f"- **产品描述**: {comp.get('description', '')}\n"
                competitors_info += f"- **技术规格**: {comp.get('specs_json', '')}\n\n"
        else:
            competitors_info = "无具体竞品信息，请根据行业知识进行分析。\n"
        
        prompt = f"""你是一个资深的数通产品竞争情报分析师，擅长进行专业的竞品对比分析。

## 分析目标
请对 **{target_name} ({target_code})** 进行全面的竞品分析。

---

## 目标产品信息

### 基本信息
- **产品品牌**: {target_brand}
- **产品名称**: {target_name}
- **产品型号**: {target_code}
- **产品系列**: {target_series}

### 命名解析信息（从产品型号自动提取）
{target_naming_info}

### 产品描述
{target_description}

### 技术规格
{target_specs}

---

## 竞品信息

{competitors_info}

---

## 输出格式要求（严格遵守）

请按照以下 Markdown 格式输出分析报告，**不要添加任何额外的说明文字**：

# 竞品分析报告：{target_name}

## 一、市场定位分析

### 1.1 目标市场
（分析目标市场：企业、政府、运营商等）

### 1.2 目标客户群体
（分析目标客户群体：中小企业、大型企业、运营商等）

### 1.3 产品定位
（分析产品在市场中的定位：高端、中端、入门级等，可参考命名解析信息中的产品等级、功能等级、WiFi代际等）

## 二、竞品对比分析

### 2.1 核心参数对比表

| 参数维度 | 目标产品 | 竞品1 | 竞品2 | 竞品3 |
|---------|---------|-------|-------|-------|
| 产品品牌 | | | | |
| 产品型号 | | | | |
| 产品定位 | | | | |
| 产品类型 | | | | |
| 接口规格 | | | | |
| 交换容量 | | | | |
| 转发性能 | | | | |
| 支持协议 | | | | |
| 管理方式 | | | | |

### 2.2 功能特性对比
- **功能特性1**: 目标产品: xx，竞品1: xx，竞品2: xx，竞品3: xx
- **功能特性2**: ...

### 2.3 优劣势分析

| 产品 | 优势 | 劣势 |
|-----|------|------|
| 目标产品 | - 优势1<br>- 优势2 | - 劣势1<br>- 劣势2 |
| 竞品1 | - 优势1<br>- 优势2 | - 劣势1<br>- 劣势2 |
| 竞品2 | - 优势1<br>- 优势2 | - 劣势1<br>- 劣势2 |
| 竞品3 | - 优势1<br>- 优势2 | - 劣势1<br>- 劣势2 |

## 三、SWOT分析

| 维度 | 分析内容 |
|-----|---------|
| **优势 (Strengths)** | - 优势1<br>- 优势2 |
| **劣势 (Weaknesses)** | - 劣势1<br>- 劣势2 |
| **机会 (Opportunities)** | - 机会1<br>- 机会2 |
| **威胁 (Threats)** | - 威胁1<br>- 威胁2 |

## 四、竞争策略建议

### 4.1 差异化策略
- 建议1
- 建议2

### 4.2 市场策略
- 建议1
- 建议2

### 4.3 产品优化建议
- 建议1
- 建议2

## 五、总结

（总结全文，给出核心观点）

---

## 重要要求

1. **严格格式**: 必须按照上述 Markdown 格式输出，标题层级、表格结构必须严格遵守
2. **数据驱动**: 分析必须基于提供的产品数据，避免无根据的猜测
3. **表格完整**: 对比表格必须填充完整，可从技术规格中提取相关参数
4. **客观中立**: 分析要客观，既要说明目标产品的优势，也要指出竞品的长处
5. **专业术语**: 使用正确的网络通信专业术语
6. **无需解释**: 不要添加"以下是分析报告"等说明性文字，直接输出分析内容
7. **表格对齐**: 使用 Markdown 标准表格语法，确保在页面上能正确渲染

---

## 分析提示

- 从技术规格中提取：交换容量、转发性能、接口数量、支持的协议等
- 从产品描述中提取：产品定位、适用场景、核心卖点
- 从命名解析信息中提取：产品等级（核心/汇聚/接入）、功能等级（EI/SI/LI等）、WiFi代际、端口配置、PoE支持等
- 相似度评分可用于判断竞品与目标产品的相似程度，评分越高说明越相似
- 对比维度：性能、功能、可扩展性、管理能力、安全性、成本等
"""
        
        logger.info("Built competitor analysis prompt for %s (%s) with %d competitors (with naming info)", 
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
            r'为([A-Za-z0-9\-]{3,})生成',
            r'(?<![A-Za-z0-9\-])([A-Za-z][A-Za-z0-9\-]{2,})',
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
    
    def _handle_competitor_analysis_with_product(self, product_data: Dict[str, Any], message: str) -> Tuple[str, Dict[str, Any]]:
        logger.info("=== Competitor Analysis Data Fetching (Fuzzy Matched) ===")
        overall_start = time.time()
        
        t1 = time.time()
        logger.info("Step 1: Fetching all products for similarity evaluation")
        all_products_summary = self.data_fetcher.get_all_products_summary()
        t2 = time.time()
        logger.info("  Total products in database: %d (cost: %.2f ms)", 
                   len(all_products_summary), (t2-t1)*1000)
        
        t1 = time.time()
        logger.info("Step 2: Pre-filtering candidates (by product_type, category, brand)")
        filtered_candidates = self._pre_filter_candidates(product_data, all_products_summary)
        t2 = time.time()
        logger.info("  Candidates after pre-filter: %d -> %d (cost: %.2f ms)", 
                   len(all_products_summary)-1, len(filtered_candidates), (t2-t1)*1000)
        
        logger.info("Step 3: Evaluating similarity for competitor selection")
        evaluated = []
        fetch_count = 0
        eval_start = time.time()
        
        for candidate_summary in filtered_candidates:
            candidate_code = candidate_summary.get('product_code', '')
            
            tt1 = time.time()
            candidate_full = self.data_fetcher.get_product_by_code(candidate_code)
            tt2 = time.time()
            fetch_count += 1
            
            if not candidate_full:
                continue
            
            result = self.similarity_evaluator.evaluate(product_data, candidate_full)
            if result['is_competitor']:
                evaluated.append({
                    'product': candidate_full,
                    'score': result['total_score'],
                    'brand': result.get('candidate_brand', '')
                })
        
        eval_end = time.time()
        logger.info("  Similarity evaluation completed:")
        logger.info("    - Full data fetched: %d products", fetch_count)
        logger.info("    - Qualified competitors: %d", len(evaluated))
        logger.info("    - Total cost: %.2f ms (avg %.2f ms/fetch)", 
                   (eval_end-eval_start)*1000, 
                   (eval_end-eval_start)*1000/fetch_count if fetch_count > 0 else 0)
        
        t1 = time.time()
        evaluated.sort(key=lambda x: x['score'], reverse=True)
        
        competitors = self._select_competitors_with_brand_diversity(evaluated, 3)
        
        t2 = time.time()
        logger.info("Step 4: Sorting and selecting top competitors with brand diversity (cost: %.2f ms)", 
                   (t2-t1)*1000)
        
        logger.info("Found %d qualified competitors, selected top %d", 
                   len(evaluated), len(competitors))
        for i, comp in enumerate(competitors, 1):
            logger.info("  Competitor %d: %s (%s) - brand: %s",
                       i, comp.get('product_name'), comp.get('product_code'),
                       self.similarity_evaluator._extract_brand(comp))
        
        overall_end = time.time()
        logger.info("=== Competitor Analysis Total Cost: %.2f ms ===", 
                   (overall_end-overall_start)*1000)
        
        prompt = self._build_competitor_analysis_prompt(product_data, competitors, message)
        context = {
            "competitor_data": competitors,
            "matched_products": [product_data],
        }
        
        return prompt, context
    
    def _build_fuzzy_confirmation_prompt(self, candidates: List[Dict[str, Any]], 
                                        original_input: str, 
                                        confidence_level: str,
                                        user_message: str) -> str:
        product_list = ""
        for i, p in enumerate(candidates, 1):
            product_list += f"{i}. {p.get('product_name', '')} ({p.get('product_code', '')})"
            if p.get('category'):
                product_list += f" - {p['category']}"
            product_list += "\n"
        
        confidence_text = {
            "high": "高置信度",
            "medium": "中等置信度",
            "low": "低置信度"
        }.get(confidence_level, "未知置信度")
        
        prompt = f"""你是一个友好的数通产品助手。

用户查询：{user_message}

用户提供的产品型号 '{original_input}' 没有找到精确匹配，但找到了以下可能的相关产品（{confidence_text}）：
{product_list}

请以友好的方式回复用户，说明没有找到精确匹配的产品，然后列出这些候选产品供用户选择。如果只有一个候选产品，可以询问用户是否指的是这个产品；如果有多个候选产品，请让用户选择或提供更详细的型号信息。

要求：
- 语气友好、专业
- 清晰说明情况
- 引导用户提供更多信息或进行选择"""
        
        logger.info("Built fuzzy confirmation prompt with %d candidates (confidence: %s)", 
                   len(candidates), confidence_level)
        return prompt
