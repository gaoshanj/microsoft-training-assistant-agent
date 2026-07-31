"""Tests for the Microsoft Learn search and learning path recommendation tools."""

import json
from unittest import mock

import pytest

from src.agent.tools.ms_learn_search import (
    get_learning_path_recommendation,
    search_microsoft_learn,
)


@pytest.fixture
def sample_catalog_response():
    """Return a minimal Microsoft Learn catalog API response."""
    return {
        "learningPaths": [
            {
                "uid": f"path-{i}",
                "title": f"Learning Path {i}",
                "summary": "Summary",
                "duration_in_minutes": 60,
                "levels": ["beginner"],
                "roles": ["developer"],
                "products": ["azure"],
            }
            for i in range(12)
        ],
        "modules": [
            {
                "uid": f"module-{i}",
                "title": f"Module {i}",
                "summary": "Summary",
                "duration_in_minutes": 30,
                "levels": ["beginner"],
                "roles": ["developer"],
                "products": ["azure"],
            }
            for i in range(12)
        ],
    }


@mock.patch("src.agent.tools.ms_learn_search.requests.get")
def test_search_microsoft_learn_returns_up_to_ten_each(mock_get, sample_catalog_response):
    """搜索工具每种类型最多返回 10 条结果。"""
    mock_get.return_value.json.return_value = sample_catalog_response
    mock_get.return_value.raise_for_status.return_value = None

    result = search_microsoft_learn("Azure")
    data = json.loads(result)

    assert data["query"] == "Azure"
    assert data["total_results"] == 20
    assert len([r for r in data["results"] if r["type"] == "学习路径"]) == 10
    assert len([r for r in data["results"] if r["type"] == "学习模块"]) == 10


@mock.patch("src.agent.tools.ms_learn_search.requests.get")
def test_search_microsoft_learn_no_results(mock_get):
    """没有结果时返回友好提示。"""
    mock_get.return_value.json.return_value = {}
    mock_get.return_value.raise_for_status.return_value = None

    result = search_microsoft_learn("nonexistent topic")
    data = json.loads(result)

    assert "未找到" in data["message"]
    assert data["results"] == []


def _extract_certifications(result: str) -> list:
    return json.loads(result)["certifications"]


def _extract_stages(result: str) -> list:
    return json.loads(result)["stages"]


def test_learning_path_azure_developer_beginner():
    """Azure 后端开发入门返回 AZ-900 到 AZ-204 的路径。"""
    result = get_learning_path_recommendation("Azure", "后端开发", "入门")
    assert _extract_certifications(result) == ["AZ-900", "AZ-204"]
    assert len(_extract_stages(result)) == 3


def test_learning_path_azure_developer_advanced():
    """Azure 开发高级路径返回 AZ-204 与 AZ-400。"""
    result = get_learning_path_recommendation("Azure", "developer", "高级")
    assert _extract_certifications(result) == ["AZ-204", "AZ-400"]


def test_learning_path_ai_includes_copilot():
    """AI / Copilot 方向推荐 AI-900 与 AI-102。"""
    result = get_learning_path_recommendation("生成式 AI", "AI 工程师", "初级")
    certs = _extract_certifications(result)
    assert "AI-900" in certs
    assert "AI-102" in certs
    stages = _extract_stages(result)
    assert any("Copilot Studio" in topic for stage in stages for topic in stage["topics"])


def test_learning_path_data_includes_fabric():
    """数据工程路径包含 Microsoft Fabric。"""
    result = get_learning_path_recommendation("Azure Data", "数据工程师", "初级")
    certs = _extract_certifications(result)
    assert "DP-900" in certs
    assert "DP-203" in certs
    stages = _extract_stages(result)
    assert any("Microsoft Fabric" in topic for stage in stages for topic in stage["topics"])


def test_learning_path_power_platform_advanced():
    """高级 Power Platform 方向推荐 PL-400 与 PL-600。"""
    result = get_learning_path_recommendation("Power Platform", "开发者", "高级")
    assert _extract_certifications(result) == ["PL-400", "PL-600"]


def test_learning_path_devops():
    """DevOps 方向推荐 AZ-400。"""
    result = get_learning_path_recommendation("DevOps", "DevOps 工程师", "初级")
    assert "AZ-400" in _extract_certifications(result)


def test_learning_path_dotnet():
    """.NET 方向推荐 AZ-204。"""
    result = get_learning_path_recommendation(".NET", "developer", "初级")
    assert _extract_certifications(result) == ["AZ-204"]


def test_learning_path_beginner_default():
    """未命中具体方向时，入门默认推荐 AZ-900。"""
    result = get_learning_path_recommendation("SomeTech", "学生", "入门")
    assert _extract_certifications(result) == ["AZ-900"]


def test_learning_path_non_beginner_default_has_more_stages():
    """非入门默认路径包含更多阶段。"""
    result = get_learning_path_recommendation("SomeTech", "工程师", "初级")
    assert len(_extract_stages(result)) == 3
