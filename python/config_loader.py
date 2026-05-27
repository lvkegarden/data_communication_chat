import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONFIG_DIR = os.path.join(_PROJECT_ROOT, 'config')

_config_cache: Dict[str, Any] = {}


def load_config(config_name: str, reload: bool = False) -> Optional[Dict[str, Any]]:
    global _config_cache
    
    if not reload and config_name in _config_cache:
        return _config_cache[config_name]
    
    config_file = os.path.join(_CONFIG_DIR, f'{config_name}.yml')
    
    if not os.path.exists(config_file):
        logger.warning(f"配置文件不存在: {config_file}")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            _config_cache[config_name] = config
            logger.info(f"已加载配置文件: {config_file}")
            return config
    except Exception as e:
        logger.error(f"加载配置文件失败 {config_file}: {e}")
        return None


def get_llm_config() -> Dict[str, Any]:
    config = load_config('llm') or {}
    defaults = {
        'llm': {
            'default_provider': os.getenv('LLM_PROVIDER', 'qwen'),
            'temperature': 0.7,
            'max_tokens': None,
            'top_p': None
        },
        'providers': {
            'qwen': {
                'model': os.getenv('QWEN_MODEL', 'qwen-plus'),
                'base_url': os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                'api_key_env': 'DASHSCOPE_API_KEY'
            },
            'deepseek': {
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
                'api_key_env': 'DEEPSEEK_API_KEY'
            }
        }
    }
    
    if config:
        defaults['llm'].update(config.get('llm', {}))
        for provider, provider_config in config.get('providers', {}).items():
            if provider in defaults['providers']:
                defaults['providers'][provider].update(provider_config)
            else:
                defaults['providers'][provider] = provider_config
    
    return defaults


def get_provider_config(provider: str) -> Optional[Dict[str, Any]]:
    llm_config = get_llm_config()
    return llm_config.get('providers', {}).get(provider)


def get_llm_temperature(provider: str = None) -> float:
    llm_config = get_llm_config()
    return llm_config.get('llm', {}).get('temperature', 0.7)


def get_default_provider() -> str:
    llm_config = get_llm_config()
    return llm_config.get('llm', {}).get('default_provider', 'qwen')


def get_api_key(provider: str) -> Optional[str]:
    provider_config = get_provider_config(provider)
    if not provider_config:
        return None
    
    env_var = provider_config.get('api_key_env')
    if env_var:
        return os.getenv(env_var)
    return None


def get_model_name(provider: str) -> Optional[str]:
    provider_config = get_provider_config(provider)
    return provider_config.get('model') if provider_config else None


def get_base_url(provider: str) -> Optional[str]:
    provider_config = get_provider_config(provider)
    return provider_config.get('base_url') if provider_config else None


def get_prompts_config() -> Dict[str, Any]:
    config = load_config('prompts') or {}
    defaults = {
        'system_prompts': {
            'product_introduction': '你是一个专业的数通产品分析师，擅长撰写清晰、有吸引力的产品介绍。\n请根据提供的产品信息，生成一份专业的产品介绍。',
            'competitor_analysis': '你是一个资深的数通产品竞争情报分析师，擅长进行竞品对比分析。\n请对提供的目标产品和竞品信息进行专业分析。',
            'product_query': '你是一个数通产品专家，擅长介绍和解答产品相关问题。\n请根据查询到的产品信息，为用户提供详细的产品介绍和对比。',
            'general_chat': '你是一个智能对话助手，擅长帮助用户解决各种问题。\n请根据对话历史和用户当前的问题，给出合适的回答。'
        },
        'intent_keywords': {
            'greeting': {
                'keywords': ['你好', 'hi', 'hello', '早上好', '下午好', '晚上好', '嗨'],
                'max_length': 20,
                'confidence': 0.9,
                'reason': '检测到问候语'
            },
            'farewell': {
                'keywords': ['再见', 'bye', '拜拜', '晚安'],
                'max_length': 20,
                'confidence': 0.9,
                'reason': '检测到告别语'
            },
            'code_query': {
                'keywords': ['代码', '程序', '函数', '类', 'bug', '错误', 'python', 'java', 'javascript', 'sql'],
                'confidence': 0.7,
                'reason': '检测到代码相关关键词'
            },
            'competitor_analysis': {
                'keywords': ['竞品分析', '竞争分析', '产品对比', 'competitor analysis', 'generate competitor analysis'],
                'confidence': 0.8,
                'reason': '检测到竞品分析请求'
            },
            'product_introduction': {
                'keywords': ['产品介绍', '产品说明', '产品概述', 'product introduction', 'generate introduction'],
                'confidence': 0.8,
                'reason': '检测到产品介绍请求'
            },
            'product_query': {
                'keywords': ['查询产品', '产品查询', '产品信息', 'query product', 'product list', '查看所有产品', '产品列表'],
                'confidence': 0.7,
                'reason': '检测到产品查询请求'
            },
            'data_analysis': {
                'keywords': ['分析', '统计', '数据', '报表', 'excel', '图表'],
                'confidence': 0.7,
                'reason': '检测到数据分析关键词'
            },
            'knowledge_query': {
                'keywords': ['什么是', '为什么', '怎么回事', '解释', '说明', '原理'],
                'confidence': 0.6,
                'reason': '检测到知识查询'
            }
        }
    }
    
    if config:
        if config.get('system_prompts'):
            defaults['system_prompts'].update(config.get('system_prompts', {}))
        if config.get('intent_keywords'):
            for intent, intent_config in config.get('intent_keywords', {}).items():
                if intent in defaults['intent_keywords']:
                    defaults['intent_keywords'][intent].update(intent_config)
                else:
                    defaults['intent_keywords'][intent] = intent_config
    
    return defaults


def get_system_prompt(intent_type: str) -> str:
    config = get_prompts_config()
    return config.get('system_prompts', {}).get(intent_type, 
           config.get('system_prompts', {}).get('general_chat', ''))


def get_intent_keywords(intent_name: str) -> Optional[Dict[str, Any]]:
    config = get_prompts_config()
    return config.get('intent_keywords', {}).get(intent_name)


def get_all_intent_keywords() -> Dict[str, Any]:
    config = get_prompts_config()
    return config.get('intent_keywords', {})


def get_scraper_config() -> Dict[str, Any]:
    config = load_config('scraper') or {}
    defaults = {
        'scraper': {
            'request_timeout': 30,
            'request_delay': 1,
            'max_retries': 3,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
            ],
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        }
    }
    
    if config:
        if config.get('scraper'):
            defaults['scraper'].update(config.get('scraper', {}))
    
    return defaults


def get_scraper_setting(key: str, default=None):
    config = get_scraper_config()
    return config.get('scraper', {}).get(key, default)


def get_random_user_agent() -> str:
    import random
    config = get_scraper_config()
    user_agents = config.get('scraper', {}).get('user_agents', [])
    if user_agents:
        return random.choice(user_agents)
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


def get_scraper_headers() -> Dict[str, str]:
    config = get_scraper_config()
    headers = dict(config.get('scraper', {}).get('headers', {}))
    headers['User-Agent'] = get_random_user_agent()
    return headers


def get_request_timeout() -> int:
    return get_scraper_setting('request_timeout', 30)


def get_request_delay() -> int:
    return get_scraper_setting('request_delay', 1)


def get_max_retries() -> int:
    return get_scraper_setting('max_retries', 3)
