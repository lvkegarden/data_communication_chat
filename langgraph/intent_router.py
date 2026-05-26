import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class IntentType(Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    GENERAL_CHAT = "general_chat"
    CODE_QUERY = "code_query"
    DATA_ANALYSIS = "data_analysis"
    KNOWLEDGE_QUERY = "knowledge_query"
    PRODUCT_INTRODUCTION = "product_introduction"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    PRODUCT_QUERY = "product_query"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float
    reason: str
    entities: Dict[str, Any] = field(default_factory=dict)


class IntentRouter:
    def __init__(self, llm=None):
        self.llm = llm
        logger.info("IntentRouter initialized")

    def classify(self, messages: List[Any]) -> IntentResult:
        if not messages:
            logger.warning("No messages provided for classification")
            return IntentResult(IntentType.UNKNOWN, 0.0, "No messages provided")
        
        last_msg = messages[-1]
        content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        content_lower = content.lower()
        
        logger.info("Classifying intent for message (length: %d chars): %s", len(content), content[:100])
        
        if any(g in content_lower for g in ['你好', 'hi', 'hello', '早上好', '下午好', '晚上好', '嗨']) and len(content) < 20:
            logger.info("Intent matched: GREETING (confidence: 0.9)")
            return IntentResult(IntentType.GREETING, 0.9, "检测到问候语")
        
        if any(f in content_lower for f in ['再见', 'bye', '拜拜', '晚安']) and len(content) < 20:
            logger.info("Intent matched: FAREWELL (confidence: 0.9)")
            return IntentResult(IntentType.FAREWELL, 0.9, "检测到告别语")
        
        if any(c in content for c in ['代码', '程序', '函数', '类', 'bug', '错误', 'python', 'java', 'javascript', 'sql']):
            logger.info("Intent matched: CODE_QUERY (confidence: 0.7)")
            return IntentResult(IntentType.CODE_QUERY, 0.7, "检测到代码相关关键词")
        
        if any(d in content for d in ['分析', '统计', '数据', '报表', 'excel', '图表']):
            logger.info("Intent matched: DATA_ANALYSIS (confidence: 0.7)")
            return IntentResult(IntentType.DATA_ANALYSIS, 0.7, "检测到数据分析关键词")
        
        if any(k in content for k in ['什么是', '为什么', '怎么回事', '解释', '说明', '原理']):
            logger.info("Intent matched: KNOWLEDGE_QUERY (confidence: 0.6)")
            return IntentResult(IntentType.KNOWLEDGE_QUERY, 0.6, "检测到知识查询")
        
        if any(p in content for p in ['产品介绍', '产品说明', '产品概述', 'product introduction', 'generate introduction']):
            logger.info("Intent matched: PRODUCT_INTRODUCTION (confidence: 0.8)")
            return IntentResult(IntentType.PRODUCT_INTRODUCTION, 0.8, "检测到产品介绍请求")
        
        if any(c in content for c in ['竞品分析', '竞争分析', '产品对比', 'competitor analysis', 'generate competitor analysis']):
            logger.info("Intent matched: COMPETITOR_ANALYSIS (confidence: 0.8)")
            return IntentResult(IntentType.COMPETITOR_ANALYSIS, 0.8, "检测到竞品分析请求")
        
        if any(q in content for q in ['查询产品', '产品查询', '产品介绍', '产品信息', 'query product', 'product list', '查看所有产品', '产品列表']):
            logger.info("Intent matched: PRODUCT_QUERY (confidence: 0.7)")
            return IntentResult(IntentType.PRODUCT_QUERY, 0.7, "检测到产品查询请求")
        
        logger.info("Intent matched: GENERAL_CHAT (confidence: 0.5, default)")
        return IntentResult(IntentType.GENERAL_CHAT, 0.5, "通用聊天")

    def route_to_next_node(self, intent_result: IntentResult) -> str:
        intent = intent_result.intent
        intent_value = intent.value if hasattr(intent, 'value') else str(intent)
        
        logger.info("Routing intent '%s' to next node", intent_value)
        
        if intent in [IntentType.GREETING, IntentType.FAREWELL]:
            logger.info("Route result: simple_response")
            return "simple_response"
        elif intent == IntentType.CODE_QUERY:
            logger.info("Route result: code_expert")
            return "code_expert"
        elif intent == IntentType.DATA_ANALYSIS:
            logger.info("Route result: data_analyst")
            return "data_analyst"
        elif intent == IntentType.KNOWLEDGE_QUERY:
            logger.info("Route result: knowledge_agent")
            return "knowledge_agent"
        elif intent == IntentType.PRODUCT_INTRODUCTION:
            logger.info("Route result: product_introduction")
            return "product_introduction"
        elif intent == IntentType.COMPETITOR_ANALYSIS:
            logger.info("Route result: competitor_analysis")
            return "competitor_analysis"
        elif intent == IntentType.PRODUCT_QUERY:
            logger.info("Route result: product_query")
            return "product_query"
        else:
            logger.info("Route result: general_chat (default)")
            return "general_chat"
