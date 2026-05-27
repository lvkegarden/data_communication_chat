import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any

from config_loader import get_all_intent_keywords, get_intent_keywords

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
        self._load_keyword_configs()
        logger.info("IntentRouter initialized")
    
    def _load_keyword_configs(self):
        self.intent_keywords = get_all_intent_keywords()
        logger.info("Loaded intent keywords config for %d intents", len(self.intent_keywords))

    def classify(self, messages: List[Any]) -> IntentResult:
        if not messages:
            logger.warning("No messages provided for classification")
            return IntentResult(IntentType.UNKNOWN, 0.0, "No messages provided")
        
        last_msg = messages[-1]
        content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        content_lower = content.lower()
        
        logger.info("Classifying intent for message (length: %d chars): %s", len(content), content[:100])
        
        intent_order = [
            IntentType.GREETING,
            IntentType.FAREWELL,
            IntentType.COMPETITOR_ANALYSIS,
            IntentType.PRODUCT_INTRODUCTION,
            IntentType.PRODUCT_QUERY,
            IntentType.CODE_QUERY,
            IntentType.DATA_ANALYSIS,
            IntentType.KNOWLEDGE_QUERY
        ]
        
        for intent_type in intent_order:
            intent_name = intent_type.value
            config = self.intent_keywords.get(intent_name)
            
            if not config:
                continue
            
            keywords = config.get('keywords', [])
            max_length = config.get('max_length')
            confidence = config.get('confidence', 0.5)
            reason = config.get('reason', intent_name)
            
            use_lower = intent_name in ['greeting', 'farewell']
            content_to_check = content_lower if use_lower else content
            
            if any(kw in content_to_check for kw in keywords):
                if max_length and len(content) >= max_length:
                    continue
                
                logger.info("Intent matched: %s (confidence: %.1f, reason: %s)", 
                          intent_type.name, confidence, reason)
                return IntentResult(intent_type, confidence, reason)
        
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
