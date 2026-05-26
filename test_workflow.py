# 数通产品智能体工作流测试脚本

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5001/api"

def test_greeting():
    """测试问候意图"""
    logger.info("=" * 60)
    logger.info("测试 1: 问候意图")
    logger.info("=" * 60)
    
    payload = {
        "session_id": "test_greeting_001",
        "message": "你好",
        "flag": "y"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    logger.info(f"请求消息: {payload['message']}")
    logger.info(f"响应状态: {response.status_code}")
    logger.info(f"响应消息: {result.get('message', 'N/A')}")
    
    if result.get('intent'):
        logger.info(f"识别意图: {result['intent'].get('intent')}")
        logger.info(f"置信度: {result['intent'].get('confidence')}")
        logger.info(f"路由节点: {result['intent'].get('routed_to')}")
    
    return result

def test_product_introduction():
    """测试产品介绍意图"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 2: 产品介绍意图")
    logger.info("=" * 60)
    
    payload = {
        "session_id": "test_product_intro_001",
        "message": "请为RG-AP820C生成产品介绍",
        "flag": "y"
    }
    
    logger.info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    logger.info(f"响应状态: {response.status_code}")
    logger.info(f"响应消息长度: {len(result.get('message', ''))} 字符")
    logger.info(f"响应消息: {result.get('message', 'N/A')[:200]}...")
    
    if result.get('intent'):
        logger.info(f"识别意图: {result['intent'].get('intent')}")
        logger.info(f"路由节点: {result['intent'].get('routed_to')}")
    
    if result.get('product_data'):
        logger.info(f"产品数据: {result['product_data'].get('product_code')} - {result['product_data'].get('product_name')}")
    
    if result.get('prompt'):
        logger.info(f"Prompt长度: {len(result['prompt'])} 字符")
    
    return result

def test_product_query():
    """测试产品查询意图"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 3: 产品查询意图")
    logger.info("=" * 60)
    
    payload = {
        "session_id": "test_product_query_001",
        "message": "查询产品 RG-AP820",
        "flag": "y"
    }
    
    logger.info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    logger.info(f"响应状态: {response.status_code}")
    logger.info(f"响应消息: {result.get('message', 'N/A')[:200]}...")
    
    if result.get('intent'):
        logger.info(f"识别意图: {result['intent'].get('intent')}")
        logger.info(f"路由节点: {result['intent'].get('routed_to')}")
    
    return result

def test_competitor_analysis():
    """测试竞品分析意图"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 4: 竞品分析意图")
    logger.info("=" * 60)
    
    payload = {
        "session_id": "test_competitor_001",
        "message": "请为RG-AP820C生成竞品分析",
        "flag": "y"
    }
    
    logger.info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    logger.info(f"响应状态: {response.status_code}")
    logger.info(f"响应消息长度: {len(result.get('message', ''))} 字符")
    
    if result.get('intent'):
        logger.info(f"识别意图: {result['intent'].get('intent')}")
        logger.info(f"路由节点: {result['intent'].get('routed_to')}")
    
    if result.get('competitor_data'):
        logger.info(f"竞品数量: {len(result['competitor_data'])}")
    
    return result

def test_general_chat():
    """测试通用聊天意图"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 5: 通用聊天意图")
    logger.info("=" * 60)
    
    payload = {
        "session_id": "test_general_001",
        "message": "你能帮我做什么？",
        "flag": "y"
    }
    
    logger.info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    logger.info(f"响应状态: {response.status_code}")
    logger.info(f"响应消息: {result.get('message', 'N/A')}")
    
    if result.get('intent'):
        logger.info(f"识别意图: {result['intent'].get('intent')}")
        logger.info(f"路由节点: {result['intent'].get('routed_to')}")
    
    return result

def main():
    logger.info("开始测试数通产品智能体工作流")
    logger.info("LangGraph API: http://localhost:5001/api")
    
    try:
        # 测试问候意图
        test_greeting()
        time.sleep(1)
        
        # 测试产品介绍意图
        test_product_introduction()
        time.sleep(1)
        
        # 测试产品查询意图
        test_product_query()
        time.sleep(1)
        
        # 测试竞品分析意图
        test_competitor_analysis()
        time.sleep(1)
        
        # 测试通用聊天意图
        test_general_chat()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("所有测试完成！")
        logger.info("=" * 60)
        
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到 LangGraph 服务，请确保服务正在运行")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
