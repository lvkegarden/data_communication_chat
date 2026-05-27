# LocalREST - 数通产品专业智能体

一个基于大语言模型的数通产品专业智能体系统，采用现代技术栈构建，为用户提供产品咨询、竞品分析等智能化服务。

## 项目简介

本项目是一个学习型项目，旨在探索如何将大语言模型（LLM）与传统企业应用相结合，为数据通信领域提供智能化服务。使用 Trae IDE 进行开发，采用多技术栈协同工作的架构设计。

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐       │
│  │ HTML页面    │  │ Android端   │  │ 聊天界面         │       │
│  │ (web/)      │  │ (android/)  │  │ (chat.html)      │       │
│  └────────────┘  └────────────┘  └──────────────────┘       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│                        服务层                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Spring Boot 服务 (端口 8080)              │   │
│  │  - RESTful API 接口                                  │   │
│  │  - 数据持久化 (JPA + SQLite)                          │   │
│  │  - 业务逻辑处理                                       │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                               │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │         Python LangGraph 服务 (端口 5001)            │   │
│  │  - 流程编排 (LangGraph)                              │   │
│  │  - 意图识别与路由                                     │   │
│  │  - 大模型调用                                        │   │
│  └─────────────────────────┬───────────────────────────┘   │
└────────────────────────────│───────────────────────────────┘
                             │ API调用
┌────────────────────────────▼───────────────────────────────┐
│                        LLM 层                               │
│  ┌──────────────┐          ┌───────────────────┐           │
│  │ 通义千问 API  │          │ DeepSeek API      │           │
│  │ (qwen-plus)  │          │ (deepseek-chat)   │           │
│  └──────────────┘          └───────────────────┘           │
└────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|-----|------|------|
| **前端** | HTML/CSS/JavaScript | 轻量级聊天界面，跨平台兼容 |
| **移动端** | Android (Java) | 原生 Android 应用 |
| **后端** | Spring Boot 3.2.5 | RESTful API 服务，Java 17 |
| **数据持久化** | JPA + SQLite | 嵌入式数据库，无需额外部署 |
| **流程编排** | LangGraph 0.1.19 | 多智能体工作流编排 |
| **LLM 集成** | LangChain 0.2.14 | 大模型调用框架 |
| **Python 服务** | Flask 2.3.3 | LLM 服务接口 |
| **LLM 提供商** | 通义千问 / DeepSeek | 支持双LLM 提供商配置 |
| **开发工具** | Trae IDE | 智能编程助手 |

## 核心功能

### 1. 智能对话
- 自然语言交互的聊天界面
- 支持多种消息类型
- 上下文记忆与管理

### 2. 产品咨询
- 产品规格查询
- 产品参数对比
- 产品型号识别

### 3. 竞品分析
- 多品牌产品对比
- 参数差异分析
- 优势劣势评估

### 4. 数据采集
- 多厂商产品数据爬取（华为、H3C、锐捷等）
- 自动规格参数提取
- 数据清洗与标准化

### 5. 意图识别
- 智能意图分类
- 动态路由到对应处理逻辑
- 可配置的关键词规则

## 项目结构

```
localrest/
├── android/              # Android 原生应用
├── collect/              # 数据采集模块（爬虫）
│   ├── base_scraper.py   # 爬虫基类
│   ├── huawei_scraper.py # 华为数据采集
│   ├── h3c_scraper.py    # H3C数据采集
│   └── ruijie_scraper.py # 锐捷数据采集
├── config/               # 配置文件目录
│   ├── llm.yml           # LLM 配置
│   ├── prompts.yml       # 提示词配置
│   ├── web-config.js     # 前端配置
│   └── README.md         # 配置说明文档
├── data/                 # 数据目录
├── doc/                  # 文档目录
├── langgraph/            # LangGraph 流程编排（新版本）
│   ├── app.py            # Flask 应用入口
│   ├── intent_router.py  # 意图路由器
│   ├── prompt_builder.py # 提示词构建器
│   └── requirements.txt  # Python 依赖
├── python/               # Python 服务（传统版本）
│   ├── app.py            # Flask 应用入口
│   ├── intent_router.py  # 意图路由器
│   ├── prompt_builder.py # 提示词构建器
│   └── requirements.txt  # Python 依赖
├── service/              # Spring Boot 源码（主编译目录）
│   └── com/example/localrestservice/
│       ├── controller/   # 控制器层
│       ├── service/      # 服务层
│       ├── repository/   # 数据访问层
│       ├── entity/       # 实体类
│       └── dto/          # 数据传输对象
├── test/                 # 测试目录
├── web/                  # 前端页面
│   ├── chat.html         # 聊天页面
│   ├── product_agent.html # 产品代理页面
│   ├── collect.html      # 数据采集页面
│   └── index.html        # 入口页面
├── pom.xml               # Maven 配置
└── run.bat               # Windows 启动脚本
```

> **重要提示**：本项目的 Java 源码目录是 `service/`，不是 `src/main/java/`。`pom.xml` 已配置 `<sourceDirectory>service</sourceDirectory>`。

## 快速开始

### 环境要求

- Java 17+
- Python 3.10+
- Maven 3.6+
- Windows 操作系统（当前脚本）

### 配置步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd localrest
```

2. **配置环境变量（必须）**

> ⚠️ **重要提示**：以下环境变量必须正确配置，否则 Python 服务无法启动，LLM 相关功能将完全不可用。

在 `python/` 和 `langgraph/` 目录下创建 `.env` 文件，配置至少一个 LLM 提供商的 API Key：

```env
# 通义千问 API Key（阿里云）- 可选但推荐配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# DeepSeek API Key - 可选但推荐配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Java 后端 API 地址（可选，默认使用本地地址）
JAVA_API_URL=http://localhost:8080/api/product-data

# Python 服务端口（可选，默认 5001）
LANGGRAPH_PORT=5001
```

**环境变量说明**：

| 环境变量 | 是否必须 | 说明 |
|---------|---------|------|
| `DASHSCOPE_API_KEY` | ⭐ 必须配置其一 | 通义千问 API Key，从阿里云获取 |
| `DEEPSEEK_API_KEY` | ⭐ 必须配置其一 | DeepSeek API Key，从 DeepSeek 官网获取 |
| `JAVA_API_URL` | 可选 | Java 后端产品数据 API 地址，默认为 `http://localhost:8080/api/product-data` |
| `LANGGRAPH_PORT` | 可选 | Python 服务端口，默认为 `5001` |

**获取 API Key**：

- **通义千问**：访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/) 获取
- **DeepSeek**：访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取

> 💡 **建议**：为了获得最佳体验和稳定性，建议同时配置两个 API Key。系统默认使用通义千问（qwen-plus），但可以随时切换到 DeepSeek。

**配置验证**：

- 如果 API Key 未配置或格式不正确，Python 服务启动时会抛出错误：
  ```
  ValueError: DASHSCOPE_API_KEY environment variable is not properly configured.
  Please set it as a system environment variable or in the .env file.
  ```

3. **安装 Python 依赖**

```bash
# 安装 Python 服务依赖
cd python
pip install -r requirements.txt

# 或使用 LangGraph 版本
cd langgraph
pip install -r requirements.txt
```

4. **启动服务**

```bash
# Windows
run.bat
```

或者手动启动：

```bash
# 启动 Python 服务（端口 5001）
cd python
python app.py

# 另开终端启动 Spring Boot（端口 8080）
mvn spring-boot:run
```

5. **访问应用**

- 聊天页面：http://localhost:8080/chat.html
- 产品代理：http://localhost:8080/product_agent.html
- 数据采集：http://localhost:8080/collect.html

## 配置说明

项目所有配置文件位于 `config/` 目录下，以下是各配置文件的详细说明：

| 配置文件 | 路径 | 用途 | 修改后生效方式 |
|---------|------|------|---------------|
| LLM 配置 | `config/llm.yml` | 大语言模型相关配置（提供商、模型、API地址等） | 重启 Python 服务 |
| 提示词配置 | `config/prompts.yml` | 系统提示词和意图识别关键词 | 重启 Python 服务 |
| 前端配置 | `config/web-config.js` | 前端页面 API 地址配置 | 刷新浏览器页面 |
| 爬虫配置 | `config/scraper.yml` | 数据采集爬虫相关配置 | 重启 Python 爬虫服务 |
| CORS 配置 | `config/cors.yml` | 跨域资源共享配置 | 重启 Spring Boot 服务 |

---

### 1. LLM 配置（config/llm.yml）

**用途**：配置大语言模型（LLM）的相关参数

> ⚠️ **必须配置 API Key**：本配置文件中的 `api_key_env` 指定了从哪个环境变量读取 API Key。
> 请确保 `DASHSCOPE_API_KEY` 或 `DEEPSEEK_API_KEY` 环境变量已正确配置，否则 LLM 服务将无法启动。

**配置示例**：

```yaml
llm:
  default_provider: "qwen"
  temperature: 0.7
  max_tokens: null
  top_p: null

providers:
  qwen:
    model: "qwen-plus"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key_env: "DASHSCOPE_API_KEY"  # ⭐ 必须配置对应的环境变量
    
  deepseek:
    model: "deepseek-chat"
    base_url: "https://api.deepseek.com/v1"
    api_key_env: "DEEPSEEK_API_KEY"   # ⭐ 必须配置对应的环境变量
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `default_provider` | string | 默认使用的 LLM 提供商（"qwen" 或 "deepseek"） |
| `temperature` | float | 生成文本的随机性（0.0-2.0），值越高越随机 |
| `max_tokens` | int/null | 最大生成 token 数，null 表示使用默认值 |
| `top_p` | float/null | Nucleus sampling 参数 |
| `api_key_env` | string | **关键**：从哪个环境变量读取 API Key |

**支持的 LLM 提供商**：
- **qwen**：通义千问（阿里云），模型 `qwen-plus`，需要配置 `DASHSCOPE_API_KEY`
- **deepseek**：DeepSeek 模型，模型 `deepseek-chat`，需要配置 `DEEPSEEK_API_KEY`

**环境变量覆盖**：
- `LLM_PROVIDER` - 覆盖默认提供商
- `DASHSCOPE_API_KEY` - ⭐ **必须配置**：通义千问 API Key
- `DEEPSEEK_API_KEY` - ⭐ **必须配置**：DeepSeek API Key
- `QWEN_MODEL` - 覆盖 qwen 模型名称
- `QWEN_BASE_URL` - 覆盖 qwen API 地址
- `DEEPSEEK_MODEL` - 覆盖 deepseek 模型名称
- `DEEPSEEK_BASE_URL` - 覆盖 deepseek API 地址

---

### 2. 提示词配置（config/prompts.yml）

**用途**：配置系统提示词和意图识别关键词

**配置结构**：

```yaml
system_prompts:
  product_introduction: "产品介绍生成场景的系统提示词..."
  competitor_analysis: "竞品分析场景的系统提示词..."
  product_query: "产品查询场景的系统提示词..."
  general_chat: "通用对话场景的系统提示词..."

intent_keywords:
  greeting:
    keywords: ["你好", "您好", "hi", "hello"]
    confidence: 0.9
    reason: "用户问候"
    max_length: 50
  competitor_analysis:
    keywords: ["对比", "竞品", "差异", "哪个好"]
    confidence: 0.8
    reason: "用户请求竞品分析"
```

**系统提示词场景**：

| 提示词名称 | 适用场景 |
|-----------|---------|
| `product_introduction` | 产品介绍生成 |
| `competitor_analysis` | 竞品分析 |
| `product_query` | 产品查询 |
| `general_chat` | 通用对话 |

**意图类型**：

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

---

### 3. 前端配置（config/web-config.js）

**用途**：配置前端页面的 API 地址

**配置示例**：

```javascript
window.AppConfig = {
    api: {
        javaBaseUrl: "http://localhost:8080/api",
        pythonBaseUrl: "http://localhost:5001/api"
    },
    endpoints: {
        chat: "/chat",
        collect: "/collect",
        productData: "/product-data"
    }
};
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `javaBaseUrl` | string | Java 后端 API 基础地址（Spring Boot 服务） |
| `pythonBaseUrl` | string | Python LLM 服务 API 基础地址 |
| `endpoints.chat` | string | 聊天接口路径 |
| `endpoints.collect` | string | 数据采集接口路径 |
| `endpoints.productData` | string | 产品数据接口路径 |

**部署到不同环境**：

当部署到不同环境（如测试环境、生产环境）时，只需修改 `javaBaseUrl` 和 `pythonBaseUrl`：

```javascript
// 生产环境示例
api: {
    javaBaseUrl: 'https://api.example.com/api',
    pythonBaseUrl: 'https://llm.example.com/api'
}
```

---

### 4. 爬虫配置（config/scraper.yml）

**用途**：配置数据采集爬虫的相关参数

**配置示例**：

```yaml
scraper:
  request_timeout: 30
  request_delay: 1
  max_retries: 3
  user_agents:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ..."
  headers:
    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    Accept-Language: "zh-CN,zh;q=0.9,en;q=0.8"
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `request_timeout` | int | 请求超时时间（秒） |
| `request_delay` | int | 请求之间的延迟（秒） |
| `max_retries` | int | 最大重试次数 |
| `user_agents` | list | 多个浏览器 UA，爬虫会随机选择以避免被识别 |
| `headers` | dict | HTTP 请求头配置 |

---

### 5. CORS 配置（config/cors.yml）

**用途**：配置跨域资源共享（CORS）相关参数

**配置示例**：

```yaml
cors:
  allowed_origins:
    - "*"
  allowed_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  allowed_headers:
    - "*"
  max_age: 3600
  allow_credentials: false
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `allowed_origins` | list | 允许的来源域名列表 |
| `allowed_methods` | list | 允许的 HTTP 方法 |
| `allowed_headers` | list | 允许的请求头 |
| `max_age` | int | 预检请求缓存时间（秒） |
| `allow_credentials` | bool | 是否允许携带凭证（如 Cookie） |

**安全建议**：在生产环境中，建议将 `allowed_origins` 设置为具体的域名：

```yaml
cors:
  allowed_origins:
    - "https://www.example.com"
    - "https://app.example.com"
```

---

### 配置加载器模块

Python 代码通过 `python/config_loader.py` 模块读取配置，提供以下功能：

1. 从 YAML 配置文件读取配置
2. 提供默认值作为 fallback
3. 支持环境变量覆盖
4. 缓存已加载的配置

**常用函数**：

| 函数名 | 说明 |
|--------|------|
| `load_config(config_name, reload=False)` | 加载指定名称的配置文件 |
| `get_default_provider()` | 获取默认 LLM 提供商 |
| `get_llm_temperature()` | 获取 temperature 参数 |
| `get_provider_config(provider)` | 获取指定提供商的配置 |
| `get_system_prompt(intent_type)` | 获取指定意图的系统提示词 |
| `get_all_intent_keywords()` | 获取所有意图的关键词配置 |
| `get_scraper_setting(key, default)` | 获取指定的爬虫配置项 |
| `get_random_user_agent()` | 随机获取一个 User-Agent |

---

### 注意事项

1. **YAML 格式**：所有 YAML 配置文件必须符合 YAML 语法规范，缩进使用 2 个空格
2. **环境变量**：敏感信息（如 API Key）不要直接写在配置文件中，应通过环境变量设置
3. **重启服务**：修改配置文件后，需要重启对应的服务才能生效
4. **备份**：修改配置前建议先备份原文件

更多配置详情请参考 [config/README.md](config/README.md)。

## API 接口

### Spring Boot 服务（8080端口）

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/chat` | POST | 聊天对话 |
| `/api/product/query` | GET/POST | 产品查询 |
| `/api/product/competitor-analysis` | POST | 竞品分析 |
| `/api/product/introduction` | POST | 产品介绍生成 |
| `/api/collect` | POST | 数据采集 |

### Python 服务（5001端口）

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/chat` | POST | LLM 对话处理 |
| `/api/intent` | POST | 意图识别 |
| `/api/product-data` | POST | 产品数据处理 |

## 开发说明

### 项目规范

1. **Java 源码位置**：所有 Java 代码放在 `service/` 目录下，`src/main/java/` 目录下的代码不会被编译
2. **测试文件**：所有测试文件放在 `test/` 目录下，按驼峰命名规则 `testXXX` 命名
3. **配置文件**：敏感信息不提交到版本库，通过环境变量配置

### 重新编译与重启

- 修改 Java 代码或静态资源：执行 `mvn clean compile` 后重启 Spring Boot 服务
- 修改 Python 代码：必须重启 Python 服务（端口 5001）才能生效
- 执行 `run.bat` 会同时重启 Python 和 Spring Boot 两个服务

## 学习资源

本项目是一个学习尝试项目，探索以下主题：

- **LLM 应用开发**：如何将大语言模型集成到企业应用中
- **LangGraph 工作流**：多智能体协作与流程编排
- **RAG 技术**：检索增强生成的实际应用
- **多模态交互**：文本理解与结构化数据处理
- **Trae IDE 使用**：AI 辅助编程的最佳实践

## 注意事项

### 关键配置

| 配置项 | 重要性 | 说明 |
|-------|--------|------|
| `DASHSCOPE_API_KEY` | ⭐⭐⭐ 必须 | 通义千问 API Key，二选一即可 |
| `DEEPSEEK_API_KEY` | ⭐⭐⭐ 必须 | DeepSeek API Key，二选一即可 |
| `JAVA_API_URL` | ⭐⭐ 推荐 | Java 后端产品数据接口地址 |
| `config/web-config.js` | ⭐⭐ 推荐 | 前端 API 地址配置 |

> ⚠️ **特别强调**：`DASHSCOPE_API_KEY` 或 `DEEPSEEK_API_KEY` 必须至少配置一个，否则：
> - Python 服务无法正常启动
> - 所有 LLM 相关功能（智能对话、产品咨询、竞品分析等）完全不可用
> - 服务启动时会抛出 `ValueError` 错误

### 其他注意事项

1. **API 调用优化**：聊天页面只有点击提交按钮才触发 API 调用，尽量减少不必要的调用
2. **数据安全**：API Key 等敏感信息通过环境变量管理，不要提交到版本库
3. **生产环境**：CORS 配置建议指定具体域名，而非使用 `*`
4. **配置文件修改后生效方式**：
   - 修改 `.env` 环境变量：需重启 Python 服务
   - 修改 `config/llm.yml`：需重启 Python 服务
   - 修改 `config/cors.yml`：需重启 Spring Boot 服务
   - 修改 `config/web-config.js`：刷新浏览器即可

## ⚠️ 重要法律声明与合规要求

### 数据采集模块合规说明

本项目中的 `collect/` 目录包含数据采集相关代码，**仅供技术研究和教育目的使用**。

#### 使用前提

使用本项目的用户必须遵守以下规定：

1. **法律法规遵守**：必须遵守中华人民共和国相关法律法规，包括但不限于：
   - 《网络数据安全管理条例》
   - 《中华人民共和国网络安全法》
   - 《中华人民共和国数据安全法》
   - 《中华人民共和国反不正当竞争法》

2. **目标网站合规**：
   - 尊重目标网站的 `robots.txt` 协议
   - 遵守目标网站的服务条款（Terms of Service）
   - 不得绕过或突破目标网站的反爬虫技术保护措施
   - 不得干扰目标网站的正常运行

3. **数据使用限制**：
   - 不得将爬取的数据用于商业用途
   - 不得侵犯他人的知识产权
   - 不得泄露或出售爬取的个人信息
   - 爬取的数据仅供个人学习研究使用

#### 代码中已有的保护措施

本项目爬虫代码已包含以下合规设计：

| 保护措施 | 位置 | 说明 |
|---------|------|------|
| 请求延迟 | `config/scraper.yml` | `request_delay: 1` 秒，避免对目标服务器造成压力 |
| 请求超时 | `config/scraper.yml` | `request_timeout: 30` 秒 |
| 最大重试 | `config/scraper.yml` | `max_retries: 3` 次 |
| User-Agent 轮换 | `config/scraper.yml` | 随机选择浏览器 UA，避免被识别为恶意爬虫 |

### 免责声明

> **重要提示**：
>
> 1. 本项目作者不对任何使用本代码造成的任何法律后果承担责任。
> 2. 使用本代码前请确保已获得目标网站的明确授权。
> 3. 如因使用本代码导致任何法律纠纷，由使用者自行承担全部责任。
> 4. 本项目不包含任何已爬取的数据，数据采集代码仅用于演示技术实现。
> 5. 强烈建议在实际使用前咨询专业法律顾问。

### 建议

| 建议 | 说明 |
|-----|------|
| **仅供学习** | 本项目仅用于学习和研究，不建议用于生产环境 |
| **获取授权** | 如需爬取商业网站数据，请先获取官方授权 |
| **私有仓库** | 建议将此代码存放在私有仓库中，而非公开仓库 |
| **法律咨询** | 有疑问请咨询专业律师 |

---

## 许可证

本项目仅供学习和研究使用，禁止用于任何非法用途。

---

> 本项目使用 [Trae IDE](https://trae.cn) 开发，探索 AI 辅助编程的无限可能。
