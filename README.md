# Microsoft Training Assistant Agent

基于 **Microsoft Agent Framework** 与 **Azure AI Foundry** 构建的微软培训助手。它可以回答微软技术问题、搜索 Microsoft Learn 培训资源、推荐学习路径、提供认证考试信息，并跟踪学员学习进度。

---

## 功能特性

- **技术问答**：回答 Azure、Microsoft 365、Power Platform、Security、Azure AI/Data 等领域的问题。
- **资源搜索**：调用 Microsoft Learn Catalog API 搜索课程、模块、学习路径。
- **学习路径推荐**：根据用户的技术方向、工作角色和经验水平推荐结构化学习路线。
- **认证信息查询**：返回常见微软认证（AZ-900、AZ-104、AI-102、DP-203 等）的考试详情与备考计划。
- **进度跟踪**：记录学员学习进度，并基于已有进度生成个性化下一步学习建议。

---

## 技术栈

- **Python 3.10+**
- **Microsoft Agent Framework** (`agent-framework`)
- **Azure AI Foundry Chat Client** (`agent_framework.foundry.FoundryChatClient`)
- **Azure Identity** (`azure-identity`，支持 DefaultAzureCredential / Azure CLI / Managed Identity）
- **Pydantic** 用于工具参数描述
- **Rich** 用于命令行美化

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/gaoshanj/microsoft-training-assistant-agent.git
cd microsoft-training-assistant-agent
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例文件：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# Azure AI Foundry 项目端点
# 格式：https://<resource-name>.services.ai.azure.com
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com

# 模型部署名称
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 4. 登录 Azure

```bash
az login
```

确保你的账号在 Azure AI Foundry 项目中具有 **Azure AI Developer** 或更高权限。

### 5. 启动助手

```bash
python -m src.app
```

输入问题即可开始对话，例如：

```text
我想学习 Azure，我是一名后端开发，有经验但想考认证，有什么建议？
请帮我搜索 Azure Functions 的中文学习资源。
我要考 AI-102，给我一份 8 周备考计划。
记录我的进度：已完成 AZ-900 云计算概念模块。
查看我的学习进度并制定下一步计划。
```

输入 `exit`、`quit` 或 `退出` 结束对话。

---

## 项目结构

```text
microsoft-training-assistant-agent/
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 依赖
├── README.md                 # 项目说明
└── src/
    ├── app.py                # 命令行交互入口
    ├── agent/
    │   ├── training_agent.py # Agent 封装与初始化
    │   └── tools/            # 工具函数
    │       ├── ms_learn_search.py   # Microsoft Learn 搜索与学习路径
    │       ├── certifications.py    # 认证考试信息
    │       └── progress.py          # 学习进度记录
```

---

## 智能体工具一览

| 工具名 | 说明 |
| --- | --- |
| `search_microsoft_learn` | 搜索 Microsoft Learn 课程与模块 |
| `get_learning_path_recommendation` | 按技术/角色/水平推荐学习路径 |
| `get_certification_info` | 查询微软认证考试详情 |
| `get_exam_preparation_tips` | 根据备考周数生成备考计划 |
| `record_learning_progress` | 记录学员学习进度 |
| `get_learning_progress` | 查询学员学习进度 |
| `generate_personalized_study_plan` | 基于进度生成下一步学习建议 |

---

## 扩展建议

- 接入 **Azure AI Search** 索引企业内部培训资料。
- 使用 **Azure Cosmos DB** 替代本地 JSON 文件保存学习进度。
- 部署为 **Azure Container App** 或 **Azure Functions**，提供 Web / Teams Bot 接口。
- 集成更多工具，如考试预约、课程推荐评分等。

---

## 许可证

[MIT License](LICENSE)
