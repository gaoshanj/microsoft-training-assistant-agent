"""Microsoft Learn 平台搜索工具 — 通过 Catalog API 查询培训资源。"""

import json
from typing import Annotated

import requests
from agent_framework import tool
from pydantic import Field


@tool(name="search_microsoft_learn", description="在 Microsoft Learn 上搜索培训资源（课程、学习模块、学习路径）。")
def search_microsoft_learn(
    query: Annotated[str, Field(description="搜索关键词，例如 'Azure 存储'、'机器学习'、'Power BI'")],
    content_type: Annotated[
        str,
        Field(
            description="内容类型过滤：all（默认，全部类型）、learningPath（学习路径）、module（单个学习模块）"
        ),
    ] = "all",
    locale: Annotated[
        str,
        Field(description="语言区域：zh-cn（简体中文，默认）或 en-us（英文）"),
    ] = "zh-cn",
) -> str:
    """在 Microsoft Learn 上搜索培训资源（课程、学习模块、学习路径）。"""
    url = "https://learn.microsoft.com/api/catalog/"
    params: dict = {"term": query, "locale": locale}
    if content_type != "all":
        params["type"] = content_type

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"搜索请求失败: {exc}", "results": []}, ensure_ascii=False)

    results: list = []
    max_results = 10

    for lp in data.get("learningPaths", [])[:max_results]:
        results.append({
            "type": "学习路径",
            "title": lp.get("title", ""),
            "summary": lp.get("summary", ""),
            "url": lp.get("url") or f"https://learn.microsoft.com/training/paths/{lp.get('uid', '')}",
            "duration_minutes": lp.get("duration_in_minutes", 0),
            "levels": lp.get("levels", []),
            "roles": lp.get("roles", []),
            "products": lp.get("products", []),
        })

    for mod in data.get("modules", [])[:max_results]:
        results.append({
            "type": "学习模块",
            "title": mod.get("title", ""),
            "summary": mod.get("summary", ""),
            "url": mod.get("url") or f"https://learn.microsoft.com/training/modules/{mod.get('uid', '')}",
            "duration_minutes": mod.get("duration_in_minutes", 0),
            "levels": mod.get("levels", []),
            "roles": mod.get("roles", []),
            "products": mod.get("products", []),
        })

    if not results:
        return json.dumps(
            {"message": f"未找到关于 '{query}' 的培训资源，请尝试更换关键词。", "results": []},
            ensure_ascii=False,
        )

    return json.dumps(
        {"query": query, "total_results": len(results), "results": results},
        ensure_ascii=False,
        indent=2,
    )


@tool(
    name="get_learning_path_recommendation",
    description="根据技术方向、工作角色和经验水平推荐结构化学习路径。",
)
def get_learning_path_recommendation(
    technology: Annotated[
        str,
        Field(
            description="技术领域，例如 Azure、Azure DevOps、Power Platform、Microsoft 365、Azure AI、Azure Data、Security"
        ),
    ],
    role: Annotated[
        str,
        Field(description="工作角色，例如 开发者、管理员、数据工程师、AI 工程师、安全工程师、业务分析师、架构师、学生"),
    ],
    experience_level: Annotated[
        str,
        Field(description="经验水平：入门（零基础）、初级（有一定基础）或 高级（寻求专家认证）"),
    ],
) -> str:
    """根据技术方向、工作角色和经验水平推荐结构化学习路径。"""
    tech = technology.lower()
    role_lower = role.lower()
    level_lower = experience_level.lower()

    paths: dict = {
        "technology": technology,
        "role": role,
        "experience_level": experience_level,
        "stages": [],
        "certifications": [],
        "recommended_search_terms": [],
    }

    is_beginner = level_lower in ["入门", "beginner", "零基础"]
    is_advanced = level_lower in ["高级", "advanced", "专家"]

    if "azure" in tech and any(k in role_lower for k in ["开发", "developer", "dev", "后端", "frontend", "前端"]):
        if is_beginner:
            paths["stages"] = [
                {"stage": "第一阶段：Azure 基础（2-4 周）", "topics": ["云计算概念", "Azure 核心服务", "Azure 定价和支持"], "certification": "AZ-900"},
                {"stage": "第二阶段：开发基础（4-6 周）", "topics": ["Azure App Service", "Azure Functions", "Azure Storage", "Azure SQL"], "certification": ""},
                {"stage": "第三阶段：开发者认证（6-8 周）", "topics": ["容器化与 AKS", "消息队列", "API Management", "监控与诊断"], "certification": "AZ-204"},
            ]
            paths["certifications"] = ["AZ-900", "AZ-204"]
            paths["recommended_search_terms"] = ["Azure developer", "Azure App Service", "Azure Functions Python"]
        else:
            paths["stages"] = [
                {"stage": "第一阶段：高级开发（4-6 周）", "topics": ["微服务架构", "Azure Kubernetes Service", "Event-driven 架构"], "certification": "AZ-204"},
                {"stage": "第二阶段：DevOps 集成（4-6 周）", "topics": ["Azure DevOps", "GitHub Actions", "CI/CD 流水线"], "certification": "AZ-400"},
            ]
            paths["certifications"] = ["AZ-204", "AZ-400"]
            paths["recommended_search_terms"] = ["AKS microservices", "Azure DevOps pipeline", "Azure architecture"]

    elif "azure" in tech and any(k in role_lower for k in ["管理", "admin", "运维", "ops", "system"]):
        paths["stages"] = [
            {"stage": "第一阶段：Azure 基础（2-4 周）", "topics": ["Azure 门户", "资源管理", "Microsoft Entra ID"], "certification": "AZ-900"},
            {"stage": "第二阶段：管理员核心（6-8 周）", "topics": ["虚拟机", "虚拟网络", "存储管理", "Azure Monitor", "备份与恢复"], "certification": "AZ-104"},
        ]
        paths["certifications"] = ["AZ-900", "AZ-104"]
        paths["recommended_search_terms"] = ["Azure administrator", "Azure virtual network", "Azure Monitor"]

    elif any(k in tech for k in ["ai", "人工智能", "机器学习", "ml", "copilot", "生成式 ai", "generative ai"]) or any(k in role_lower for k in ["ai", "数据科学", "data scientist", "prompt engineer"]):
        paths["stages"] = [
            {"stage": "第一阶段：AI 基础（2-3 周）", "topics": ["AI 概念", "Azure AI 服务概览", "负责任 AI"], "certification": "AI-900"},
            {"stage": "第二阶段：AI 工程（6-8 周）", "topics": ["Azure OpenAI", "Azure AI Search", "Azure AI Vision", "Azure AI Language", "Azure Bot Service"], "certification": "AI-102"},
            {"stage": "第三阶段：高级 AI（选修）", "topics": ["Azure Machine Learning", "MLOps", "生成式 AI 应用开发", "Copilot Studio"], "certification": ""},
        ]
        paths["certifications"] = ["AI-900", "AI-102"]
        paths["recommended_search_terms"] = ["Azure OpenAI", "Azure AI services", "responsible AI", "Copilot Studio"]

    elif any(k in tech for k in ["data", "数据", "fabric", "synapse", "databricks"]) or any(k in role_lower for k in ["数据", "data engineer", "数据分析师", "data analyst"]):
        paths["stages"] = [
            {"stage": "第一阶段：数据基础（2-3 周）", "topics": ["数据概念", "Azure 数据服务概览", "关系型与非关系型数据库"], "certification": "DP-900"},
            {"stage": "第二阶段：数据工程（6-8 周）", "topics": ["Azure Synapse Analytics", "Azure Data Factory", "Azure Data Lake", "Azure Databricks", "Microsoft Fabric"], "certification": "DP-203"},
            {"stage": "第三阶段：数据库管理（可选）", "topics": ["Azure SQL Database", "Azure Cosmos DB", "性能调优"], "certification": "DP-300"},
        ]
        paths["certifications"] = ["DP-900", "DP-203"]
        paths["recommended_search_terms"] = ["Azure Synapse Analytics", "Azure Data Factory", "Azure Databricks", "Microsoft Fabric"]

    elif any(k in tech for k in ["power platform", "power apps", "power bi", "power automate"]):
        if is_advanced:
            paths["stages"] = [
                {"stage": "第一阶段：Power Platform 解决方案架构（4-6 周）", "topics": ["Power Apps 高级开发", "Power Automate 高级流程", "Dataverse 建模", "ALM"], "certification": "PL-400"},
                {"stage": "第二阶段：Power Platform 架构师（6-8 周）", "topics": ["企业级解决方案设计", "安全与治理", "集成模式", "性能优化"], "certification": "PL-600"},
            ]
            paths["certifications"] = ["PL-400", "PL-600"]
            paths["recommended_search_terms"] = ["Power Apps advanced", "Dataverse ALM", "Power Platform architecture"]
        else:
            paths["stages"] = [
                {"stage": "第一阶段：Power Platform 基础（1-2 周）", "topics": ["Power Platform 概述", "Power Apps 基础", "Power Automate 基础", "Power BI 基础"], "certification": "PL-900"},
                {"stage": "第二阶段：实战应用（4-6 周）", "topics": ["Canvas App 开发", "Model-driven App", "自动化流程设计", "数据可视化仪表板"], "certification": "PL-200"},
            ]
            paths["certifications"] = ["PL-900", "PL-200"]
            paths["recommended_search_terms"] = ["Power Apps canvas app", "Power Automate workflow", "Power BI dashboard"]

    elif any(k in tech for k in ["m365", "microsoft 365", "teams", "sharepoint", "exchange"]):
        paths["stages"] = [
            {"stage": "第一阶段：M365 基础（1-2 周）", "topics": ["Microsoft 365 服务概览", "Teams 协作", "SharePoint 基础"], "certification": "MS-900"},
            {"stage": "第二阶段：M365 管理（4-6 周）", "topics": ["用户和组管理", "Teams 管理员", "Exchange Online", "安全与合规"], "certification": "MS-700"},
        ]
        paths["certifications"] = ["MS-900", "MS-700"]
        paths["recommended_search_terms"] = ["Microsoft Teams administration", "Microsoft 365 administrator", "SharePoint Online"]

    elif any(k in tech for k in ["security", "安全", "零信任", "defender", "sentinel", "entra"]):
        paths["stages"] = [
            {"stage": "第一阶段：安全基础（1-2 周）", "topics": ["安全、合规与身份概念", "Microsoft Entra ID 基础", "Azure 安全基础"], "certification": "SC-900"},
            {"stage": "第二阶段：安全运营（6-8 周）", "topics": ["Microsoft Defender", "Microsoft Sentinel", "零信任架构"], "certification": "SC-200"},
            {"stage": "第三阶段：身份与访问管理（可选）", "topics": ["Microsoft Entra ID", "条件访问", "特权身份管理"], "certification": "SC-300"},
        ]
        paths["certifications"] = ["SC-900", "SC-200"]
        paths["recommended_search_terms"] = ["Microsoft Defender", "Microsoft Sentinel", "zero trust Azure", "Microsoft Entra ID"]

    elif any(k in tech for k in ["devops", "github", "cicd", "ci/cd"]):
        paths["stages"] = [
            {"stage": "第一阶段：DevOps 基础（2-3 周）", "topics": ["DevOps 文化与实践", "源代码管理", "CI/CD 概念"], "certification": "AZ-900"},
            {"stage": "第二阶段：Azure DevOps 与 GitHub Actions（4-6 周）", "topics": ["Azure Pipelines", "GitHub Actions", "容器化部署", "基础设施即代码"], "certification": "AZ-400"},
        ]
        paths["certifications"] = ["AZ-900", "AZ-400"]
        paths["recommended_search_terms"] = ["Azure DevOps pipeline", "GitHub Actions Azure", "Infrastructure as Code"]

    elif any(k in tech for k in ["dotnet", ".net", "c#", "csharp", "asp.net"]):
        paths["stages"] = [
            {"stage": "第一阶段：.NET 基础（2-4 周）", "topics": ["C# 语言基础", ".NET 运行时与类库", "面向对象编程"], "certification": ""},
            {"stage": "第二阶段：Azure 上的 .NET 开发（4-6 周）", "topics": ["Azure App Service 部署 .NET", "Azure Functions .NET", "Azure SQL 与 EF Core", "容器化 .NET 应用"], "certification": "AZ-204"},
        ]
        paths["certifications"] = ["AZ-204"]
        paths["recommended_search_terms"] = [".NET on Azure", "Azure App Service .NET", "Azure Functions C#"]

    elif any(k in role_lower for k in ["架构", "architect", "solution"]):
        paths["stages"] = [
            {"stage": "前提条件", "topics": ["建议先取得 AZ-104（管理员）或 AZ-204（开发者）认证"], "certification": "AZ-104 / AZ-204"},
            {"stage": "架构师核心（8-10 周）", "topics": ["Azure 解决方案设计", "高可用与灾备", "安全架构", "成本优化", "网络设计"], "certification": "AZ-305"},
        ]
        paths["certifications"] = ["AZ-104", "AZ-305"]
        paths["recommended_search_terms"] = ["Azure solution architecture", "Azure Well-Architected Framework"]

    elif is_beginner:
        paths["stages"] = [
            {"stage": "第一阶段：云计算基础（1-2 周）", "topics": ["云计算概念", "Azure 核心服务", "Azure 门户基础操作"], "certification": "AZ-900"},
            {"stage": "第二阶段：根据角色深化（自选）", "topics": ["开发者 → AZ-204", "管理员 → AZ-104", "数据工程师 → DP-203", "AI 工程师 → AI-102"], "certification": ""},
        ]
        paths["certifications"] = ["AZ-900"]
        paths["recommended_search_terms"] = ["Azure fundamentals", "Microsoft Learn Azure"]

    else:
        paths["stages"] = [
            {"stage": "第一阶段：云计算基础（1-2 周）", "topics": ["云计算概念", "Azure 核心服务", "Azure 门户基础操作"], "certification": "AZ-900"},
            {"stage": "第二阶段：根据角色深化（自选）", "topics": ["开发者 → AZ-204", "管理员 → AZ-104", "数据工程师 → DP-203", "AI 工程师 → AI-102", "安全工程师 → SC-200"], "certification": ""},
            {"stage": "第三阶段：进阶认证方向（可选）", "topics": ["架构师 → AZ-305", "DevOps → AZ-400", "数据库管理 → DP-300"], "certification": ""},
        ]
        paths["certifications"] = ["AZ-900"]
        paths["recommended_search_terms"] = ["Azure fundamentals", "Microsoft Learn Azure", "Azure certification"]

    paths["tips"] = [
        "优先完成 Microsoft Learn 上的免费官方学习路径",
        "使用 Microsoft Learn 沙盒环境动手实践，无需付费",
        "通过 Microsoft 官方练习题和模拟考试巩固备考",
        "加入微软学习社区与其他学习者交流",
    ]

    return json.dumps(paths, ensure_ascii=False, indent=2)
