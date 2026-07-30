"""Microsoft Training Assistant Agent — 基于 Azure AI Foundry Agent Service 的培训助手。

主要能力：
- 回答微软技术问题（Azure、M365、Power Platform、Security、AI 等）
- 调用 Microsoft Learn Catalog API 搜索培训资源
- 推荐结构化学习路径与微软认证
- 记录与跟踪学员学习进度
"""

from __future__ import annotations

import json
import os
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from .tools.certifications import get_certification_info, get_exam_preparation_tips
from .tools.ms_learn_search import get_learning_path_recommendation, search_microsoft_learn
from .tools.progress import (
    generate_personalized_study_plan,
    get_learning_progress,
    record_learning_progress,
)

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
AGENT_ID = os.getenv("AGENT_ID")

_SYSTEM_INSTRUCTION = """你是一名专业的微软培训助手，擅长帮助学员学习微软云技术、完成认证考试并规划职业发展。

## 角色与语气
- 友好、耐心、专业，用中文回答（除非用户明确使用其他语言）。
- 回答尽量简洁、结构化，使用 Markdown 列表或表格帮助阅读。
- 对不确定的内容坦诚说明，不编造信息。

## 能力
1. 回答 Azure、Microsoft 365、Power Platform、Microsoft Security、Azure AI / Data 等技术问题。
2. 调用工具搜索 Microsoft Learn 培训资源（课程、模块、学习路径）。
3. 根据用户技术方向、角色和经验水平推荐系统学习路径。
4. 提供微软认证考试信息（考试范围、题型、备考资源）。
5. 根据可用备考时间制定备考计划。
6. 记录和跟踪学员学习进度，并基于进度给出下一步建议。

## 工具使用原则
- 当用户询问“学什么”“如何入门”“推荐学习资源”时，使用 search_microsoft_learn 或 get_learning_path_recommendation。
- 当用户提到具体认证考试代码（如 AZ-900、AI-102）时，使用 get_certification_info 和 get_exam_preparation_tips。
- 当用户要求“记录进度”“保存学习状态”“制定下一步计划”时，使用 progress 相关工具。
- 工具返回 JSON 后，用自然语言为用户总结关键信息，不要直接粘贴原始 JSON。

## 示例引导
- 用户说“我想学 Azure” → 先询问用户角色（开发者/管理员/数据/AI）和经验水平，再推荐路径。
- 用户说“我要考 AZ-104” → 给出考试信息、备考计划，并推荐 Microsoft Learn 资源。
"""


_USER_FUNCTIONS = {
    "search_microsoft_learn": search_microsoft_learn,
    "get_learning_path_recommendation": get_learning_path_recommendation,
    "get_certification_info": get_certification_info,
    "get_exam_preparation_tips": get_exam_preparation_tips,
    "record_learning_progress": record_learning_progress,
    "get_learning_progress": get_learning_progress,
    "generate_personalized_study_plan": generate_personalized_study_plan,
}


class TrainingAgent:
    """包装 Azure AI Foundry Agent Service 的培训助手客户端。"""

    def __init__(self) -> None:
        if not PROJECT_ENDPOINT:
            raise RuntimeError("环境变量 PROJECT_ENDPOINT 未设置。请参照 .env.example 配置。")

        self.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=DefaultAzureCredential(),
        )

        function_tool = FunctionTool(_USER_FUNCTIONS)
        self.toolset = ToolSet()
        self.toolset.add(function_tool)

        # 支持复用已有 agent
        if AGENT_ID:
            self.agent = self.project_client.agents.get_agent(AGENT_ID)
        else:
            self.agent = self.project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT_NAME,
                name="microsoft-training-assistant",
                instructions=_SYSTEM_INSTRUCTION,
                toolset=self.toolset,
            )

        self.project_client.agents.enable_auto_function_calls(toolset=self.toolset)

    def create_thread(self) -> str:
        """创建一个新的对话线程，返回 thread_id。"""
        thread = self.project_client.agents.threads.create()
        return thread.id

    def send_message(self, thread_id: str, user_message: str) -> str:
        """发送用户消息并返回助手的回复文本。"""
        self.project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )

        run = self.project_client.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=self.agent.id,
            toolset=self.toolset,
        )

        if run.status == "failed":
            error = run.last_error or "未知错误"
            raise RuntimeError(f"Agent run failed: {error}")

        # 取最后一条 assistant 文本消息
        messages = list(self.project_client.agents.messages.list(thread_id=thread_id).data)
        for message in reversed(messages):
            if message.role == "assistant" and message.content:
                for item in message.content:
                    if item.type == "text":
                        return item.text.value

        return "（助手未返回文本内容）"

    def close(self) -> None:
        """关闭底层 HTTP 客户端。"""
        self.project_client.close()


def create_training_agent() -> TrainingAgent:
    """工厂函数：创建并返回一个已配置好的 TrainingAgent 实例。"""
    return TrainingAgent()


def quick_ask(question: str) -> str:
    """一次性提问的便捷函数，不保留多轮对话上下文。"""
    agent = create_training_agent()
    try:
        thread_id = agent.create_thread()
        return agent.send_message(thread_id, question)
    finally:
        agent.close()


if __name__ == "__main__":
    print(quick_ask("请介绍 AZ-900 考试，并给我一份 4 周备考计划。"))
