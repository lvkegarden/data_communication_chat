from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from typing import Dict, List, Any, TypedDict, Annotated, Optional
import operator
import os
import re
import logging
import time
from dotenv import load_dotenv
import json

from intent_router import IntentRouter, IntentResult, IntentType
from intent import register_intent_routes
from product_data_fetcher import ProductDataFetcher
from prompt_assembler import PromptAssembler
from prompt_builder import PromptBuilder

load_dotenv(override=False)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
LANGGRAPH_PORT = int(os.getenv("LANGGRAPH_PORT", 5001))

CURRENT_MODEL_NAME = QWEN_MODEL if LLM_PROVIDER == "qwen" else DEEPSEEK_MODEL


def get_llm(provider=None):
    if provider is None:
        provider = LLM_PROVIDER
    
    logger.info("Initializing LLM client")
    logger.info("Selected LLM provider: %s", provider)
    
    if provider == "deepseek":
        env_key = os.environ.get("DEEPSEEK_API_KEY")
        dotenv_key_used = env_key is None and DEEPSEEK_API_KEY is not None
        
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-deepseek-api-key-here" or "xxxxxxxx" in DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY environment variable is not properly configured")
            raise ValueError("DEEPSEEK_API_KEY environment variable is not properly configured. "
                            "Please set it as a system environment variable or in the .env file.")
        
        key_source = "system environment variable" if env_key else ".env file"
        logger.info("DEEPSEEK_API_KEY loaded from: %s", key_source)
        logger.info("LLM client initialized with DeepSeek model: %s", DEEPSEEK_MODEL)
        logger.info("DeepSeek API base URL: %s", DEEPSEEK_BASE_URL)
        
        return ChatOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            temperature=0.7
        )
    else:
        env_key = os.environ.get("DASHSCOPE_API_KEY")
        dotenv_key_used = env_key is None and DASHSCOPE_API_KEY is not None
        
        if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your-dashscope-api-key-here" or "xxxxxxxx" in DASHSCOPE_API_KEY:
            logger.error("DASHSCOPE_API_KEY environment variable is not properly configured")
            raise ValueError("DASHSCOPE_API_KEY environment variable is not properly configured. "
                            "Please set it as a system environment variable or in the .env file.")
        
        key_source = "system environment variable" if env_key else ".env file"
        logger.info("DASHSCOPE_API_KEY loaded from: %s", key_source)
        logger.info("LLM client initialized with Qwen model: %s", QWEN_MODEL)
        logger.info("Qwen API base URL: %s", QWEN_BASE_URL)
        
        return ChatOpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=QWEN_BASE_URL,
            model=QWEN_MODEL,
            temperature=0.7
        )


def get_model_name(provider=None):
    if provider is None:
        provider = LLM_PROVIDER
    return DEEPSEEK_MODEL if provider == "deepseek" else QWEN_MODEL


llm = get_llm()
intent_router = IntentRouter(llm)
data_fetcher = ProductDataFetcher()
prompt_assembler = PromptAssembler(data_fetcher)

register_intent_routes(app, llm)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    intent_result: IntentResult
    next_node: str
    session_id: str
    model_provider: str
    product_data: Optional[Dict[str, Any]]
    competitor_data: Optional[List[Dict[str, Any]]]
    prompt: Optional[str]
    generated_content: Optional[str]


class SessionData:
    def __init__(self, messages: List[BaseMessage], model_provider: str):
        self.messages = messages
        self.model_provider = model_provider


sessions: Dict[str, SessionData] = {}


def build_system_prompt(intent_type: str) -> str:
    if intent_type == "product_introduction":
        return """你是一个专业的数通产品分析师，擅长撰写清晰、有吸引力的产品介绍。
请根据提供的产品信息，生成一份专业的产品介绍。"""
    elif intent_type == "competitor_analysis":
        return """你是一个资深的数通产品竞争情报分析师，擅长进行竞品对比分析。
请对提供的目标产品和竞品信息进行专业分析。"""
    elif intent_type == "product_query":
        return """你是一个数通产品专家，擅长介绍和解答产品相关问题。
请根据查询到的产品信息，为用户提供详细的产品介绍和对比。"""
    else:
        return """你是一个智能对话助手，擅长帮助用户解决各种问题。
请根据对话历史和用户当前的问题，给出合适的回答。"""


def route_to_system_prompt(intent_type: str) -> str:
    mapping = {
        "product_introduction": "product_introduction",
        "competitor_analysis": "competitor_analysis",
        "product_query": "product_query",
        "code_query": "code_expert",
        "data_analysis": "data_analyst",
        "knowledge_query": "knowledge_agent",
    }
    return mapping.get(intent_type, "general_chat")


def extract_product_code_from_message(message: str) -> Optional[str]:
    logger.info("Extracting product code from message: %s", message[:50])
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
    logger.info("No product code found in message")
    return None


def intent_classification_node(state: AgentState) -> Dict[str, Any]:
    messages = state["messages"]
    user_message = messages[-1].content if messages else ""
    
    logger.info("=== Intent Classification Start ===")
    logger.info("User message: %s", user_message)
    logger.info("Session ID: %s", state.get("session_id", "unknown"))
    
    start_time = time.time()
    intent_result = intent_router.classify(messages)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: Intent Classification ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Model: Global intent_router (qwen)")
    
    logger.info("Intent classified: %s (confidence: %.2f, reason: %s)", 
                intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent),
                intent_result.confidence,
                intent_result.reason)
    
    extracted_code = extract_product_code_from_message(user_message)
    if extracted_code:
        extracted_code = extracted_code.upper()
        intent_result.entities["product_code"] = extracted_code
        logger.info("Product code added to entities: %s", extracted_code)
    
    next_node = intent_router.route_to_next_node(intent_result)
    
    logger.info("Routed to node: %s", next_node)
    logger.info("=== Intent Classification End (total: %.2f ms) ===", elapsed * 1000)
    
    return {
        "intent_result": intent_result,
        "next_node": next_node
    }


def route_by_intent(state: AgentState) -> str:
    next_node = state["next_node"]
    logger.info("Routing by intent to: %s", next_node)
    return next_node


def simple_response_node(state: AgentState) -> Dict[str, Any]:
    intent = state["intent_result"].intent
    logger.info("=== Simple Response Node ===")
    logger.info("Intent: %s", intent.value if hasattr(intent, 'value') else str(intent))
    
    if intent == IntentType.GREETING:
        response = AIMessage(content="你好！我是数通产品智能助手，可以帮你查询产品信息、生成产品介绍或进行竞品分析。有什么可以帮你的吗？")
        logger.info("Generated greeting response")
    elif intent == IntentType.FAREWELL:
        response = AIMessage(content="再见！如果还有产品相关的问题，随时来找我。")
        logger.info("Generated farewell response")
    else:
        response = AIMessage(content="好的，我收到了你的消息。")
        logger.info("Generated simple response")
    
    logger.info("=== Simple Response Node End ===")
    return {"messages": [response]}


def get_current_llm(state: AgentState):
    model_provider = state.get("model_provider", LLM_PROVIDER)
    logger.info("=== get_current_llm ===")
    logger.info("  Requested model_provider: %s", model_provider)
    logger.info("  Default LLM_PROVIDER: %s", LLM_PROVIDER)
    
    start_time = time.time()
    llm = get_llm(model_provider)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: LLM Initialization ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Actual LLM model: %s", llm.model_name if hasattr(llm, 'model_name') else 'unknown')
    logger.info("  Actual LLM base_url: %s", llm.base_url if hasattr(llm, 'base_url') else 'unknown')
    return llm


def general_chat_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== General Chat Node ===")
    system_prompt = build_system_prompt("general_chat")
    
    current_llm = get_current_llm(state)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    logger.info("Invoking LLM for general chat")
    
    start_time = time.time()
    response = current_llm.invoke(messages)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: General Chat LLM Call ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== General Chat Node End (total: %.2f ms) ===", elapsed * 1000)
    return {"messages": [response]}


def code_expert_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Code Expert Node ===")
    system_prompt = build_system_prompt("code_query")
    
    current_llm = get_current_llm(state)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    logger.info("Invoking LLM for code expert")
    
    start_time = time.time()
    response = current_llm.invoke(messages)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: Code Expert LLM Call ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Code Expert Node End (total: %.2f ms) ===", elapsed * 1000)
    return {"messages": [response]}


def data_analyst_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Data Analyst Node ===")
    system_prompt = build_system_prompt("data_analysis")
    
    current_llm = get_current_llm(state)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    logger.info("Invoking LLM for data analyst")
    
    start_time = time.time()
    response = current_llm.invoke(messages)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: Data Analyst LLM Call ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Data Analyst Node End (total: %.2f ms) ===", elapsed * 1000)
    return {"messages": [response]}


def knowledge_agent_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Knowledge Agent Node ===")
    system_prompt = build_system_prompt("knowledge_query")
    
    current_llm = get_current_llm(state)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    logger.info("Invoking LLM for knowledge agent")
    
    start_time = time.time()
    response = current_llm.invoke(messages)
    elapsed = time.time() - start_time
    
    logger.info("=== PERF: Knowledge Agent LLM Call ===")
    logger.info("  Cost: %.2f ms", elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Knowledge Agent Node End (total: %.2f ms) ===", elapsed * 1000)
    return {"messages": [response]}


def product_introduction_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Product Introduction Node Start ===")
    user_message = state["messages"][-1].content if state["messages"] else ""
    intent_result = state["intent_result"]
    
    intent_value = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
    entities = intent_result.entities
    
    logger.info("Assembling prompt for product introduction")
    
    prompt_start = time.time()
    prompt, context = prompt_assembler.assemble_from_message(user_message, intent_value, entities)
    prompt_elapsed = time.time() - prompt_start
    
    logger.info("=== PERF: Product Intro Prompt Assembly ===")
    logger.info("  Cost: %.2f ms", prompt_elapsed * 1000)
    logger.info("  Has data: %s", context.get("has_data"))
    logger.info("  Product data count: %d", len(context.get("product_data", [])) if isinstance(context.get("product_data"), list) else 0)
    
    if not context.get("has_data"):
        response = AIMessage(content=prompt)
        logger.info("=== Product Introduction Node End (No Data, total: %.2f ms) ===", prompt_elapsed * 1000)
        return {"messages": [response], "prompt": prompt}
    
    system_prompt = build_system_prompt("product_introduction")
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    current_llm = get_current_llm(state)
    logger.info("Invoking LLM for product introduction (prompt length: %d chars)", len(prompt))
    
    llm_start = time.time()
    response = current_llm.invoke(messages)
    llm_elapsed = time.time() - llm_start
    
    total_elapsed = prompt_elapsed + llm_elapsed
    
    logger.info("=== PERF: Product Intro LLM Call ===")
    logger.info("  Cost: %.2f ms", llm_elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Product Introduction Node End (Success, total: %.2f ms) ===", total_elapsed * 1000)
    
    return {
        "messages": [response],
        "product_data": context.get("product_data"),
        "prompt": prompt,
        "generated_content": response.content
    }


def competitor_analysis_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Competitor Analysis Node Start ===")
    user_message = state["messages"][-1].content if state["messages"] else ""
    intent_result = state["intent_result"]
    
    intent_value = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
    entities = intent_result.entities
    
    logger.info("Assembling prompt for competitor analysis")
    
    prompt_start = time.time()
    prompt, context = prompt_assembler.assemble_from_message(user_message, intent_value, entities)
    prompt_elapsed = time.time() - prompt_start
    
    logger.info("=== PERF: Competitor Analysis Prompt Assembly ===")
    logger.info("  Cost: %.2f ms", prompt_elapsed * 1000)
    logger.info("  Has data: %s", context.get("has_data"))
    logger.info("  Product data count: %d", len(context.get("product_data", [])) if isinstance(context.get("product_data"), list) else 0)
    logger.info("  Competitor data count: %d", len(context.get("competitor_data", [])) if isinstance(context.get("competitor_data"), list) else 0)
    
    if not context.get("has_data"):
        response = AIMessage(content=prompt)
        logger.info("=== Competitor Analysis Node End (No Data, total: %.2f ms) ===", prompt_elapsed * 1000)
        return {"messages": [response], "prompt": prompt}
    
    system_prompt = build_system_prompt("competitor_analysis")
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    current_llm = get_current_llm(state)
    logger.info("Invoking LLM for competitor analysis (prompt length: %d chars)", len(prompt))
    
    llm_start = time.time()
    response = current_llm.invoke(messages)
    llm_elapsed = time.time() - llm_start
    
    total_elapsed = prompt_elapsed + llm_elapsed
    
    logger.info("=== PERF: Competitor Analysis LLM Call ===")
    logger.info("  Cost: %.2f ms", llm_elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Competitor Analysis Node End (Success, total: %.2f ms) ===", total_elapsed * 1000)
    
    return {
        "messages": [response],
        "product_data": context.get("product_data"),
        "competitor_data": context.get("competitor_data"),
        "prompt": prompt,
        "generated_content": response.content
    }


def product_query_node(state: AgentState) -> Dict[str, Any]:
    logger.info("=== Product Query Node Start ===")
    user_message = state["messages"][-1].content if state["messages"] else ""
    intent_result = state["intent_result"]
    
    intent_value = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
    entities = intent_result.entities
    
    logger.info("Assembling prompt for product query")
    
    prompt_start = time.time()
    prompt, context = prompt_assembler.assemble_from_message(user_message, intent_value, entities)
    prompt_elapsed = time.time() - prompt_start
    
    logger.info("=== PERF: Product Query Prompt Assembly ===")
    logger.info("  Cost: %.2f ms", prompt_elapsed * 1000)
    logger.info("  Has data: %s", context.get("has_data"))
    logger.info("  Matched products count: %d", len(context.get("matched_products", [])) if isinstance(context.get("matched_products"), list) else 0)
    
    if not context.get("has_data"):
        response = AIMessage(content=prompt)
        logger.info("=== Product Query Node End (No Data, total: %.2f ms) ===", prompt_elapsed * 1000)
        return {"messages": [response], "prompt": prompt}
    
    system_prompt = build_system_prompt("product_query")
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    current_llm = get_current_llm(state)
    logger.info("Invoking LLM for product query (prompt length: %d chars)", len(prompt))
    
    llm_start = time.time()
    response = current_llm.invoke(messages)
    llm_elapsed = time.time() - llm_start
    
    total_elapsed = prompt_elapsed + llm_elapsed
    
    logger.info("=== PERF: Product Query LLM Call ===")
    logger.info("  Cost: %.2f ms", llm_elapsed * 1000)
    logger.info("  Model: %s", current_llm.model_name if hasattr(current_llm, 'model_name') else 'unknown')
    logger.info("  Response length: %d chars", len(response.content) if hasattr(response, 'content') else 0)
    
    logger.info("LLM response received (length: %d chars)", len(response.content) if hasattr(response, 'content') else 0)
    logger.info("=== Product Query Node End (Success, total: %.2f ms) ===", total_elapsed * 1000)
    
    return {
        "messages": [response],
        "product_data": context.get("product_data"),
        "competitor_data": context.get("matched_products") if len(context.get("matched_products", [])) > 1 else None,
        "prompt": prompt,
        "generated_content": response.content
    }


def build_langgraph_workflow():
    logger.info("Building LangGraph workflow")
    workflow = StateGraph(AgentState)
    
    workflow.add_node("intent_classification", intent_classification_node)
    workflow.add_node("simple_response", simple_response_node)
    workflow.add_node("general_chat", general_chat_node)
    workflow.add_node("code_expert", code_expert_node)
    workflow.add_node("data_analyst", data_analyst_node)
    workflow.add_node("knowledge_agent", knowledge_agent_node)
    workflow.add_node("product_introduction", product_introduction_node)
    workflow.add_node("competitor_analysis", competitor_analysis_node)
    workflow.add_node("product_query", product_query_node)
    
    workflow.add_edge(START, "intent_classification")
    
    workflow.add_conditional_edges(
        "intent_classification",
        route_by_intent,
        {
            "simple_response": "simple_response",
            "general_chat": "general_chat",
            "code_expert": "code_expert",
            "data_analyst": "data_analyst",
            "knowledge_agent": "knowledge_agent",
            "product_introduction": "product_introduction",
            "competitor_analysis": "competitor_analysis",
            "product_query": "product_query"
        }
    )
    
    workflow.add_edge("simple_response", END)
    workflow.add_edge("general_chat", END)
    workflow.add_edge("code_expert", END)
    workflow.add_edge("data_analyst", END)
    workflow.add_edge("knowledge_agent", END)
    workflow.add_edge("product_introduction", END)
    workflow.add_edge("competitor_analysis", END)
    workflow.add_edge("product_query", END)
    
    compiled = workflow.compile()
    logger.info("LangGraph workflow compiled successfully")
    return compiled


workflow_app = build_langgraph_workflow()


def build_preview_payload(session_id: str, user_message: str, flag: str, intent_info: Optional[Dict], 
                         assembled_prompt: Optional[str], model_provider: str, 
                         product_data: Optional[Dict] = None, competitor_data: Optional[List] = None):
    api_messages = []
    if assembled_prompt:
        system_prompt = build_system_prompt(intent_info.get("intent", "general_chat") if intent_info else "general_chat")
        api_messages.append({"role": "system", "content": system_prompt})
        api_messages.append({"role": "user", "content": assembled_prompt})
    else:
        api_messages.append({"role": "system", "content": build_system_prompt("general_chat")})
        api_messages.append({"role": "user", "content": user_message})
    
    payload = {
        "session_id": session_id,
        "message": user_message,
        "flag": flag,
        "model_provider": model_provider,
        "model_name": get_model_name(model_provider),
        "api_request": {
            "model": get_model_name(model_provider),
            "messages": api_messages
        },
    }
    
    if intent_info:
        payload["intent"] = intent_info
    
    if product_data:
        payload["product_data"] = product_data
    if competitor_data:
        payload["competitor_data"] = competitor_data
    
    return json.dumps(payload, ensure_ascii=False, indent=2)


@app.route('/api/chat', methods=['POST'])
def chat():
    logger.info("=== Chat API Request Start ===")
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        user_message = data.get('message', '')
        flag = data.get('flag', 'y')
        model_provider = data.get('model_provider', LLM_PROVIDER)
        
        logger.info("Session ID: %s", session_id)
        logger.info("User message: %s", user_message)
        logger.info("Flag: %s", flag)
        logger.info("Model provider: %s", model_provider)
        
        if not user_message:
            logger.warning("Message is empty")
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        if session_id not in sessions:
            logger.info("New session created: %s", session_id)
            sessions[session_id] = SessionData(messages=[], model_provider=model_provider)
        else:
            sessions[session_id].model_provider = model_provider
        
        if flag == 'n':
            logger.info("=== Preview Mode: Fast Path (No LLM Call) ===")
            return handle_preview_mode(session_id, user_message, model_provider)
        
        logger.info("=== Full Mode: Full Workflow Execution ===")
        
        user_msg = HumanMessage(content=user_message)
        sessions[session_id].messages.append(user_msg)
        
        logger.info("Initializing workflow state")
        logger.info("=== Workflow State Initialization ===")
        logger.info("  model_provider set to: %s", model_provider)
        logger.info("  model_name to return: %s", get_model_name(model_provider))
        initial_state: AgentState = {
            "messages": sessions[session_id].messages.copy(),
            "intent_result": None,
            "next_node": "",
            "session_id": session_id,
            "model_provider": model_provider,
            "product_data": None,
            "competitor_data": None,
            "prompt": None,
            "generated_content": None
        }
        logger.info("=== Workflow State Details ===")
        logger.info("  initial_state['model_provider']: %s", initial_state.get('model_provider'))
        
        logger.info("Invoking LangGraph workflow")
        result = workflow_app.invoke(initial_state)
        logger.info("Workflow execution completed")
        
        last_message = result["messages"][-1]
        
        intent_info = None
        if result.get("intent_result"):
            ir = result["intent_result"]
            intent_info = {
                "intent": ir.intent.value if hasattr(ir.intent, 'value') else str(ir.intent),
                "confidence": ir.confidence,
                "reason": ir.reason,
                "entities": ir.entities,
                "routed_to": result.get("next_node", "")
            }
            logger.info("Intent info: %s", json.dumps(intent_info, ensure_ascii=False))
        
        assembled_prompt = result.get("prompt")
        product_data = result.get("product_data")
        competitor_data = result.get("competitor_data")
        
        sessions[session_id].messages.append(last_message)
        
        extra_data = {}
        if assembled_prompt:
            extra_data["prompt"] = assembled_prompt
            logger.info("Prompt included in response (length: %d chars)", len(assembled_prompt))
        if product_data:
            extra_data["product_data"] = product_data
            logger.info("Product data included in response")
        if competitor_data:
            extra_data["competitor_data"] = competitor_data
            logger.info("Competitor data included in response (%d items)", len(competitor_data))
        if result.get("generated_content"):
            extra_data["generated_content"] = result["generated_content"]
            logger.info("Generated content included (length: %d chars)", len(result["generated_content"]))
        
        logger.info("Sending response (message length: %d chars)", len(last_message.content) if hasattr(last_message, 'content') else 0)
        logger.info("=== Chat API Request End (Success) ===")
        
        return jsonify({
            "success": True,
            "message": last_message.content if hasattr(last_message, 'content') else str(last_message),
            "session_id": session_id,
            "intent": intent_info,
            "model_provider": model_provider,
            "model_name": get_model_name(model_provider),
            "preview": build_preview_payload(
                session_id, user_message, 'y', intent_info,
                assembled_prompt, model_provider, product_data, competitor_data
            ),
            **extra_data
        })
    
    except Exception as e:
        logger.error("=== Chat API Request Error ===")
        logger.error("Error: %s", str(e), exc_info=True)
        logger.error("=== Chat API Request End (Error) ===")
        return jsonify({"success": False, "error": str(e)}), 500


def handle_preview_mode(session_id: str, user_message: str, model_provider: str):
    """
    预览模式的快速路径：只执行意图识别和 prompt 拼装，不调用 LLM
    """
    import time
    from langchain_core.messages import HumanMessage
    
    overall_start = time.time()
    
    logger.info("--- Preview Mode Step 1: Intent Recognition ---")
    t1 = time.time()
    messages = [HumanMessage(content=user_message)]
    intent_result = intent_router.classify(messages)
    
    extracted_code = extract_product_code_from_message(user_message)
    if extracted_code:
        extracted_code = extracted_code.upper()
        intent_result.entities["product_code"] = extracted_code
        logger.info("Product code added to entities: %s", extracted_code)
    
    t2 = time.time()
    
    intent_value = intent_result.intent.value if hasattr(intent_result.intent, 'value') else str(intent_result.intent)
    entities = intent_result.entities
    
    intent_info = {
        "intent": intent_value,
        "confidence": intent_result.confidence,
        "reason": intent_result.reason,
        "entities": entities
    }
    
    logger.info("  Intent: %s (cost: %.2f ms)", 
               intent_result.intent, (t2-t1)*1000)
    
    logger.info("--- Preview Mode Step 2: Prompt Assembly ---")
    t1 = time.time()
    assembled_prompt, context = prompt_assembler.assemble_from_message(
        user_message, intent_value, entities
    )
    t2 = time.time()
    logger.info("  Prompt length: %d chars (cost: %.2f ms)", 
               len(assembled_prompt), (t2-t1)*1000)
    
    product_data = context.get("product_data")
    competitor_data = context.get("competitor_data")
    
    logger.info("--- Preview Mode Step 3: Build Response ---")
    preview_payload = build_preview_payload(
        session_id, user_message, 'n', intent_info,
        assembled_prompt, model_provider, product_data, competitor_data
    )
    
    overall_end = time.time()
    logger.info("=== Preview Mode Total Cost: %.2f ms ===", (overall_end-overall_start)*1000)
    
    return jsonify({
        "success": True,
        "message": "",
        "session_id": session_id,
        "model_provider": model_provider,
        "model_name": get_model_name(model_provider),
        "preview": preview_payload
    })


@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    logger.info("=== Get History Request ===")
    logger.info("Session ID: %s", session_id)
    
    if session_id not in sessions:
        logger.warning("Session not found: %s", session_id)
        return jsonify({"success": False, "error": "Session not found"}), 404
    
    session_data = sessions[session_id]
    history = []
    for msg in session_data.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        history.append({"role": role, "content": msg.content})
    
    logger.info("History retrieved: %d messages", len(history))
    logger.info("Model provider: %s", session_data.model_provider)
    logger.info("=== Get History Request End ===")
    
    return jsonify({
        "success": True, 
        "history": history, 
        "session_id": session_id,
        "model_provider": session_data.model_provider,
        "model_name": get_model_name(session_data.model_provider)
    })


if __name__ == '__main__':
    logger.info("Starting LangGraph server on port %d", LANGGRAPH_PORT)
    logger.info("Intent API available at: http://localhost:%d/api/intent/", LANGGRAPH_PORT)
    logger.info("Test page: file:///d:/project/ai/localrest/web/intent_test.html")
    print(f"Starting LangGraph server on port {LANGGRAPH_PORT}...")
    print(f"Intent API available at: http://localhost:{LANGGRAPH_PORT}/api/intent/")
    print(f"Test page: file:///d:/project/ai/localrest/web/intent_test.html")
    app.run(host='0.0.0.0', port=LANGGRAPH_PORT, debug=False)
