"""Microsoft 认证考试信息工具 — 返回常见微软认证的考试概览与备考建议。"""

import json
from typing import Annotated

from agent_framework import tool
from pydantic import Field

_CERTIFICATIONS = {
    "AZ-900": {
        "name": "Microsoft Azure Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "销售", "经理", "非技术人员"],
        "skills_measured": ["云计算概念", "Azure 架构和服务", "Azure 管理和治理", "安全、合规和身份"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: AZ-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-fundamentals",
    },
    "AZ-104": {
        "name": "Microsoft Azure Administrator",
        "level": "中级",
        "target_audience": ["Azure 管理员", "系统管理员", "运维工程师"],
        "skills_measured": ["管理 Azure 身份和治理", "实现和管理存储", "部署和管理计算资源", "配置和管理虚拟网络", "监控和维护 Azure 资源"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、案例分析",
        },
        "recommended_courses": ["Microsoft Learn: AZ-104 管理员路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-administrator",
    },
    "AZ-204": {
        "name": "Azure Developer Associate",
        "level": "中级",
        "target_audience": ["开发者", "云应用开发者", "DevOps 工程师"],
        "skills_measured": ["开发 Azure 计算解决方案", "开发 Azure 存储", "实现 Azure 安全", "监控、故障排除和优化 Azure 解决方案", "连接并消费 Azure 和第三方服务"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、代码场景",
        },
        "recommended_courses": ["Microsoft Learn: AZ-204 开发者路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-developer",
    },
    "AZ-305": {
        "name": "Azure Solutions Architect Expert",
        "level": "高级",
        "target_audience": ["解决方案架构师", "云架构师", "技术负责人"],
        "skills_measured": ["设计身份、治理和监控解决方案", "设计数据存储解决方案", "设计业务连续性和灾难恢复", "设计基础设施解决方案"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、案例分析",
        },
        "recommended_courses": ["Microsoft Learn: AZ-305 架构师路径"],
        "prerequisite": "建议先取得 AZ-104 或 AZ-204",
        "url": "https://learn.microsoft.com/credentials/certifications/azure-solutions-architect",
    },
    "AZ-400": {
        "name": "Azure DevOps Engineer Expert",
        "level": "高级",
        "target_audience": ["DevOps 工程师", "发布工程师", "SRE"],
        "skills_measured": ["配置流程和沟通", "设计和实现源代码管理", "设计和实现生成和发布管道", "开发安全合规计划", "实现检测策略"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、案例分析",
        },
        "recommended_courses": ["Microsoft Learn: AZ-400 DevOps 路径"],
        "prerequisite": "需先取得 AZ-104 或 AZ-204",
        "url": "https://learn.microsoft.com/credentials/certifications/devops-engineer",
    },
    "AI-900": {
        "name": "Azure AI Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "业务用户", "产品经理", "开发者"],
        "skills_measured": ["描述 AI 工作负载和考虑因素", "描述 Azure 机器学习的基础", "描述计算机视觉功能", "描述自然语言处理功能", "描述生成式 AI 功能"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: AI-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-ai-fundamentals",
    },
    "AI-102": {
        "name": "Azure AI Engineer Associate",
        "level": "中级",
        "target_audience": ["AI 工程师", "数据科学家", "应用开发者"],
        "skills_measured": ["规划和设计 Azure AI 解决方案", "实现计算机视觉解决方案", "实现自然语言处理解决方案", "实现知识挖掘解决方案", "实现生成式 AI 解决方案"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、案例分析",
        },
        "recommended_courses": ["Microsoft Learn: AI-102 路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-ai-engineer",
    },
    "DP-900": {
        "name": "Microsoft Azure Data Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "数据分析师", "数据库管理员"],
        "skills_measured": ["描述核心数据概念", "识别 Azure 中的关系数据服务", "识别 Azure 中的半结构化和非关系型数据服务", "描述 Azure 中的数据分析负载"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: DP-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-data-fundamentals",
    },
    "DP-203": {
        "name": "Azure Data Engineer Associate",
        "level": "中级",
        "target_audience": ["数据工程师", "BI 开发者", "数据架构师"],
        "skills_measured": ["设计和实现数据存储", "设计和开发数据处理", "设计、实现和监控数据平台", "优化数据解决方案"],
        "exam_details": {
            "duration_minutes": 120,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、拖拽、案例分析",
        },
        "recommended_courses": ["Microsoft Learn: DP-203 数据工程师路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/azure-data-engineer",
    },
    "SC-900": {
        "name": "Microsoft Security, Compliance, and Identity Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "安全从业者", "合规人员"],
        "skills_measured": ["描述安全、合规和身份概念", "描述 Microsoft Entra 的功能", "描述 Microsoft 安全解决方案的功能", "描述 Microsoft 合规解决方案的功能"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: SC-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/security-compliance-and-identity-fundamentals",
    },
    "MS-900": {
        "name": "Microsoft 365 Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "业务用户", "IT 经理"],
        "skills_measured": ["描述 Microsoft 365 应用和服务", "描述 Microsoft 365 的安全、合规、隐私和信任", "描述 Microsoft 365 定价和支持"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: MS-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/microsoft-365-fundamentals",
    },
    "PL-900": {
        "name": "Microsoft Power Platform Fundamentals",
        "level": "入门",
        "target_audience": ["初学者", "业务用户", "公民开发者"],
        "skills_measured": ["描述 Power Platform 业务价值", "描述 Power Platform 的核心组件", "展示 Power BI 的功能", "描述 Power Apps 的功能", "展示 Power Automate 的功能"],
        "exam_details": {
            "duration_minutes": 60,
            "question_count": "约 40-60 题",
            "passing_score": "700 / 1000",
            "format": "单选、多选、判断、拖拽",
        },
        "recommended_courses": ["Microsoft Learn: PL-900 备考路径"],
        "url": "https://learn.microsoft.com/credentials/certifications/power-platform-fundamentals",
    },
}


@tool(name="get_certification_info", description="查询微软认证考试的详细信息。")
def get_certification_info(
    exam_code: Annotated[
        str,
        Field(description="考试代码，例如 AZ-900、AI-102、DP-203"),
    ],
) -> str:
    """查询微软认证考试的详细信息。"""
    key = exam_code.upper().strip()
    cert = _CERTIFICATIONS.get(key)
    if not cert:
        known = ", ".join(sorted(_CERTIFICATIONS.keys()))
        return json.dumps(
            {
                "error": f"暂不支持考试代码 '{exam_code}'，请检查代码是否正确。",
                "supported_exams": known,
            },
            ensure_ascii=False,
            indent=2,
        )

    result = {"exam_code": key}
    result.update(cert)
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool(name="get_exam_preparation_tips", description="根据考试代码和可用备考周数，生成个性化备考计划。")
def get_exam_preparation_tips(
    exam_code: Annotated[
        str,
        Field(description="考试代码，例如 AZ-900、AI-102"),
    ],
    weeks_available: Annotated[
        int,
        Field(description="可用于备考的周数"),
    ],
) -> str:
    """根据考试代码和可用备考周数，生成个性化备考计划。"""
    key = exam_code.upper().strip()
    cert = _CERTIFICATIONS.get(key)
    if not cert:
        return json.dumps(
            {"error": f"暂不支持考试代码 '{exam_code}'。", "supported_exams": list(_CERTIFICATIONS.keys())},
            ensure_ascii=False,
            indent=2,
        )

    if weeks_available < 1:
        weeks_available = 1

    skills = cert.get("skills_measured", [])
    num_skills = len(skills) if skills else 4
    effective_weeks = min(weeks_available, num_skills)
    skills_per_week = max(1, num_skills // effective_weeks) if effective_weeks > 0 else 1

    weekly_plan: list = []
    for week in range(1, weeks_available + 1):
        if week <= effective_weeks:
            start = (week - 1) * skills_per_week
            end = start + skills_per_week
            if week == effective_weeks:
                end = num_skills
            week_skills = skills[start:end] if skills else ["复习上周内容"]
            tasks = [
                f"学习/复习: {', '.join(week_skills)}",
                "完成对应 Microsoft Learn 模块与动手实验",
                "记录错题与知识点盲区",
            ]
        else:
            tasks = [
                "复习已学技能点，强化记忆",
                "完成 Microsoft Learn 复习模块与动手实验",
                "刷题练习，查漏补缺",
            ]
        weekly_plan.append(
            {
                "week": week,
                "focus": f"第 {week} 周",
                "tasks": tasks,
                "hours_per_week": "建议 6-10 小时" if cert.get("level") != "入门" else "建议 3-6 小时",
            }
        )

    weekly_plan[-1]["tasks"].append("完成 1-2 套官方模拟考试，查漏补缺")

    return json.dumps(
        {
            "exam_code": key,
            "exam_name": cert.get("name"),
            "level": cert.get("level"),
            "weeks_available": weeks_available,
            "weekly_plan": weekly_plan,
            "recommended_resources": cert.get("recommended_courses", []),
            "official_url": cert.get("url"),
            "preparation_tips": [
                "先通读官方考试大纲（Skills Measured），明确考核范围",
                "优先完成 Microsoft Learn 上的免费学习路径，理论结合动手实验",
                "使用官方模拟考试熟悉题型和时间分配",
                "建立错题本，针对薄弱环节反复练习",
                "考前一周重点复习官方文档和考试大纲",
                "考试前一天保证充足睡眠，保持平稳心态",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
