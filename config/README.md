# 自定义配置文件说明

本文档介绍项目中的所有自定义配置文件的路径、参数含义和使用方法。

## 配置文件概览

| 配置文件 | 路径 | 用途 |
|---------|------|------|
| LLM 配置 | `config/llm.yml` | 大语言模型相关配置 |
| 提示词配置 | `config/prompts.yml` | 系统提示词和意图识别关键词 |
| 前端配置 | `config/web-config.js` | 前端页面 API 地址配置 |
| 爬虫配置 | `config/scraper.yml` | 数据采集爬虫相关配置 |
| CORS 配置 | `config/cors.yml` | 跨域资源共享配置 |

---

## 1. LLM 配置 (llm.yml)

**路径**: `config/llm.yml`

**用途**: 配置大语言模型（LLM）的相关参数

### 参数说明

#### llm 配置块

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `default_provider` | string | `"qwen"` | 默认使用的 LLM 提供商 |
| `temperature` | float | `0.7` | 生成文本的随机性（0.0-2.0），值越高越随机 |
| `max_tokens` | int/null | `null` | 最大生成 token 数，null 表示使用默认值 |
| `top_p` | float/null | `null` | Nucleus sampling 参数 |

#### providers 配置块

支持多个 LLM 提供商，每个提供商需要配置以下参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型名称 |
| `base_url` | string | API 基础地址 |
| `api_key_env` | string | 存储 API Key 的环境变量名 |

### 支持的提供商

- **qwen**: 通义千问（阿里云）
- **deepseek**: DeepSeek 模型

### 使用方式

Python 代码通过 `python/config_loader.py` 模块读取配置：

```python
from config_loader import (
    get_default_provider,
    get_llm_temperature,
    get_provider_config,
    get_model_name,
    get_base_url,
    get_api_key
)

# 获取默认提供商
provider = get_default_provider()  # "qwen"

# 获取温度参数
temp = get_llm_temperature()  # 0.7

# 获取提供商配置
qwen_config = get_provider_config('qwen')

# 获取模型名称
model = get_model_name('qwen')  # "qwen-plus"
```

### 环境变量覆盖

配置文件中的值可以通过环境变量覆盖：

- `LLM_PROVIDER` - 覆盖默认提供商
- `QWEN_MODEL` - 覆盖 qwen 模型名称
- `QWEN_BASE_URL` - 覆盖 qwen API 地址
- `DEEPSEEK_MODEL` - 覆盖 deepseek 模型名称
- `DEEPSEEK_BASE_URL` - 覆盖 deepseek API 地址

### 修改后生效

修改此文件后需要**重启 Python 服务**才能生效。

---

## 2. 提示词配置 (prompts.yml)

**路径**: `config/prompts.yml`

**用途**: 配置系统提示词和意图识别关键词

### 参数说明

#### system_prompts 配置块

定义不同场景下的系统提示词：

| 提示词名称 | 适用场景 |
|-----------|---------|
| `product_introduction` | 产品介绍生成 |
| `competitor_analysis` | 竞品分析 |
| `product_query` | 产品查询 |
| `general_chat` | 通用对话 |

#### intent_keywords 配置块

定义意图识别的关键词和参数：

| 意图类型 | 说明 |
|---------|------|
| `greeting` | 问候语 |
| `farewell` | 告别语 |
| `code_query` | 代码查询 |
| `competitor_analysis` | 竞品分析请求 |
| `product_introduction` | 产品介绍请求 |
| `product_query` | 产品查询请求 |
| `data_analysis` | 数据分析请求 |
| `knowledge_query` | 知识查询 |

每个意图配置包含以下参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `keywords` | list | 触发此意图的关键词列表 |
| `confidence` | float | 置信度（0.0-1.0） |
| `reason` | string | 匹配原因 |
| `max_length` | int | 可选，消息最大长度限制 |

### 使用方式

```python
from config_loader import (
    get_system_prompt,
    get_intent_keywords,
    get_all_intent_keywords
)

# 获取系统提示词
prompt = get_system_prompt('product_introduction')

# 获取意图关键词配置
greeting_config = get_intent_keywords('greeting')

# 获取所有意图关键词
all_keywords = get_all_intent_keywords()
```

### 修改后生效

修改此文件后需要**重启 Python 服务**才能生效。

---

## 3. 前端配置 (web-config.js)

**路径**: `config/web-config.js`

**用途**: 配置前端页面的 API 地址

### 参数说明

#### api 配置块

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `javaBaseUrl` | string | `"http://localhost:8080/api"` | Java 后端 API 基础地址 |
| `pythonBaseUrl` | string | `"http://localhost:5001/api"` | Python LLM 服务 API 基础地址 |

#### endpoints 配置块

| 参数 | 类型 | 说明 |
|------|------|------|
| `chat` | string | 聊天接口路径 |
| `collect` | string | 数据采集接口路径 |
| `productData` | string | 产品数据接口路径 |

### 使用方式

在 HTML 页面中引入配置文件：

```html
<script src="../config/web-config.js"></script>
```

然后在 JavaScript 中使用：

```javascript
// 获取 API 地址
const javaApiBase = window.AppConfig.api.javaBaseUrl;
const pythonApiBase = window.AppConfig.api.pythonBaseUrl;

// 完整的 API 地址
const chatUrl = javaApiBase + window.AppConfig.endpoints.chat;
```

### 部署到不同环境

当部署到不同环境（如测试环境、生产环境）时，只需修改此文件中的 `javaBaseUrl` 和 `pythonBaseUrl` 即可：

```javascript
// 生产环境示例
api: {
    javaBaseUrl: 'https://api.example.com/api',
    pythonBaseUrl: 'https://llm.example.com/api'
}
```

### 修改后生效

修改此文件后**刷新浏览器页面**即可生效，无需重新编译。

---

## 4. 爬虫配置 (scraper.yml)

**路径**: `config/scraper.yml`

**用途**: 配置数据采集爬虫的相关参数

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `request_timeout` | int | `30` | 请求超时时间（秒） |
| `request_delay` | int | `1` | 请求之间的延迟（秒） |
| `max_retries` | int | `3` | 最大重试次数 |
| `user_agents` | list | 多个浏览器 UA | User-Agent 列表，爬虫会随机选择 |
| `headers` | dict | 请求头配置 | HTTP 请求头 |

### user_agents 说明

爬虫会从 `user_agents` 列表中随机选择一个 User-Agent 发送请求，这样可以避免被目标网站识别为爬虫。

### 使用方式

配置文件创建完成后，可以通过以下方式读取：

```python
from config_loader import load_config

scraper_config = load_config('scraper')
if scraper_config:
    timeout = scraper_config['scraper']['request_timeout']
    user_agents = scraper_config['scraper']['user_agents']
```

### 修改后生效

修改此文件后需要**重启 Python 爬虫服务**才能生效。

---

## 5. CORS 配置 (cors.yml)

**路径**: `config/cors.yml`

**用途**: 配置跨域资源共享（CORS）相关参数

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `allowed_origins` | list | `["*"]` | 允许的来源域名列表 |
| `allowed_methods` | list | `["GET", "POST", "PUT", "DELETE", "OPTIONS"]` | 允许的 HTTP 方法 |
| `allowed_headers` | list | `["*"]` | 允许的请求头 |
| `max_age` | int | `3600` | 预检请求缓存时间（秒） |
| `allow_credentials` | bool | `false` | 是否允许携带凭证（如 Cookie） |

### 安全建议

在生产环境中，建议将 `allowed_origins` 设置为具体的域名，而不是 `*`：

```yaml
cors:
  allowed_origins:
    - "https://www.example.com"
    - "https://app.example.com"
```

### 修改后生效

修改此文件后需要**重启 Spring Boot 服务**才能生效。

---

## 配置加载器模块

**路径**: `python/config_loader.py`

### 功能说明

配置加载器模块负责：
1. 从 YAML 配置文件读取配置
2. 提供默认值作为 fallback
3. 支持环境变量覆盖
4. 缓存已加载的配置

### 可用函数

| 函数名 | 说明 |
|--------|------|
| `load_config(config_name, reload=False)` | 加载指定名称的配置文件 |
| `get_llm_config()` | 获取完整的 LLM 配置 |
| `get_default_provider()` | 获取默认 LLM 提供商 |
| `get_llm_temperature()` | 获取 temperature 参数 |
| `get_provider_config(provider)` | 获取指定提供商的配置 |
| `get_model_name(provider)` | 获取指定提供商的模型名称 |
| `get_base_url(provider)` | 获取指定提供商的 API 地址 |
| `get_api_key(provider)` | 获取指定提供商的 API Key |
| `get_prompts_config()` | 获取完整的提示词配置 |
| `get_system_prompt(intent_type)` | 获取指定意图的系统提示词 |
| `get_intent_keywords(intent_name)` | 获取指定意图的关键词配置 |
| `get_all_intent_keywords()` | 获取所有意图的关键词配置 |
| `get_scraper_config()` | 获取完整的爬虫配置 |
| `get_scraper_setting(key, default)` | 获取指定的爬虫配置项 |
| `get_random_user_agent()` | 随机获取一个 User-Agent |
| `get_scraper_headers()` | 获取爬虫请求头（包含随机 User-Agent） |
| `get_request_timeout()` | 获取请求超时时间 |
| `get_request_delay()` | 获取请求延迟时间 |
| `get_max_retries()` | 获取最大重试次数 |

---

## 测试文件

所有配置相关的测试文件都在 `test/` 目录下：

| 测试文件 | 用途 |
|---------|------|
| `testLlmConfig.py` | 测试 LLM 配置文件格式和内容 |
| `testConfigLoader.py` | 测试配置加载器功能 |
| `testAppConfigIntegration.py` | 测试 app.py 与配置加载器的集成 |
| `testWebConfig.py` | 测试前端配置文件 |
| `testPromptsConfig.py` | 测试提示词配置 |
| `testIntentRouterConfig.py` | 测试意图路由器的配置集成 |
| `testAdditionalConfigs.py` | 测试其他配置文件 |
| `testFrontendConfigIntegration.py` | 测试前端 HTML 页面与配置的集成 |
| `testScraperConfigIntegration.py` | 测试爬虫代码与配置的集成 |

### 运行测试

```bash
# 运行单个测试
python test\testLlmConfig.py

# 运行所有配置测试
python test\testLlmConfig.py ; python test\testConfigLoader.py ; python test\testAppConfigIntegration.py ; python test\testWebConfig.py ; python test\testPromptsConfig.py ; python test\testIntentRouterConfig.py ; python test\testAdditionalConfigs.py ; python test\testFrontendConfigIntegration.py ; python test\testScraperConfigIntegration.py
```

---

## 修改后的代码文件

以下代码文件已修改为使用配置加载器：

### python/app.py

- 导入 `config_loader` 模块
- 使用 `get_system_prompt()` 替代硬编码的系统提示词
- 使用 `get_llm_temperature()` 替代硬编码的 `temperature=0.7`
- 使用配置加载器获取模型名称、API 地址等参数

### python/intent_router.py

- 导入 `config_loader` 模块
- 在 `__init__` 中调用 `get_all_intent_keywords()` 加载配置
- 使用配置中的关键词和置信度进行意图匹配

### python/config_loader.py

- 新增配置加载器模块
- 提供 LLM、提示词、爬虫等配置的读取函数
- 支持环境变量覆盖
- 支持配置缓存

### collect/base_scraper.py

- 导入 `config_loader` 模块
- 使用 `get_scraper_headers()` 替代硬编码的请求头
- 支持从配置文件读取 User-Agent 列表

### python/requirements.txt

- 添加 `pyyaml>=6.0` 依赖

### 前端 HTML 页面

以下 HTML 页面已修改为使用 `config/web-config.js`：

| 文件 | 修改内容 |
|------|---------|
| `web/chat.html` | 引入 web-config.js，使用 `window.AppConfig.api.javaBaseUrl` |
| `web/product_agent.html` | 引入 web-config.js，使用 `window.AppConfig.api.javaBaseUrl` |
| `web/collect.html` | 引入 web-config.js，使用组合的 Java API 地址 |
| `web/index.html` | 引入 web-config.js，使用 `window.AppConfig.api.pythonBaseUrl` |
| `web/intent_test.html` | 引入 web-config.js，使用 `window.AppConfig.api.pythonBaseUrl` |

---

## 配置文件注释规范

所有配置文件都包含以下注释：

1. 文件头部说明：
   - 文件路径
   - 用途说明
   - 使用说明

2. 每个配置块都有清晰的参数说明

3. 重要的默认值都有文档记录

---

## 注意事项

1. **YAML 格式**: 所有 YAML 配置文件必须符合 YAML 语法规范，缩进使用 2 个空格
2. **环境变量**: 敏感信息（如 API Key）不要直接写在配置文件中，应通过环境变量设置
3. **重启服务**: 修改配置文件后，需要重启对应的服务才能生效
4. **备份**: 修改配置前建议先备份原文件
5. **测试**: 每次修改配置后，应运行对应的测试用例确保配置正确
