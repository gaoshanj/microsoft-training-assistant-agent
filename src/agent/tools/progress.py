"""学员进度跟踪工具 — 用本地 JSON 文件保存简单的学习记录。"""

import json
import os
from datetime import datetime, timezone

DEFAULT_DB_PATH = "learning_progress.json"


def _load_db(path: str = DEFAULT_DB_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: dict, path: str = DEFAULT_DB_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_learning_progress(user_id: str, topic: str, status: str, notes: str = "") -> str:
    """记录学员某项学习内容的进度。

    当用户希望保存学习进度、课程完成状态或学习笔记时调用此函数。

    Args:
        user_id: 学员唯一标识，例如邮箱前缀、工号或昵称。
        topic: 学习主题，例如 "AZ-900 云计算概念"、"Azure Functions 入门"。
        status: 学习状态，"未开始"、"进行中"、"已完成"。
        notes: 可选的学习笔记或心得。

    Returns:
        JSON 字符串，确认记录结果。
    """
    db = _load_db()
    user_record = db.setdefault(user_id, {"records": []})

    entry = {
        "topic": topic,
        "status": status,
        "notes": notes,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # 更新已有主题
    existing = next((r for r in user_record["records"] if r["topic"] == topic), None)
    if existing:
        existing.update(entry)
    else:
        user_record["records"].append(entry)

    _save_db(db)
    return json.dumps(
        {"user_id": user_id, "message": "学习进度已记录", "entry": entry},
        ensure_ascii=False,
        indent=2,
    )


def get_learning_progress(user_id: str) -> str:
    """查询某位学员的学习进度。

    当用户希望查看自己或他人的学习记录、学习状态时调用此函数。

    Args:
        user_id: 学员唯一标识。

    Returns:
        JSON 字符串，包含学员的学习记录、完成率统计等。
    """
    db = _load_db()
    user_record = db.get(user_id)
    if not user_record:
        return json.dumps(
            {"user_id": user_id, "message": "暂无学习记录", "records": []},
            ensure_ascii=False,
            indent=2,
        )

    records = user_record.get("records", [])
    total = len(records)
    completed = sum(1 for r in records if r.get("status") == "已完成")
    in_progress = sum(1 for r in records if r.get("status") == "进行中")

    return json.dumps(
        {
            "user_id": user_id,
            "total_topics": total,
            "completed": completed,
            "in_progress": in_progress,
            "completion_rate": round(completed / total, 2) if total else 0,
            "records": records,
        },
        ensure_ascii=False,
        indent=2,
    )


def generate_personalized_study_plan(user_id: str) -> str:
    """根据学员当前进度生成个性化下一步学习建议。

    当用户希望基于已有进度获得下一步学习建议时调用此函数。

    Args:
        user_id: 学员唯一标识。

    Returns:
        JSON 字符串，包含基于进度的推荐下一步行动。
    """
    db = _load_db()
    user_record = db.get(user_id)
    if not user_record or not user_record.get("records"):
        return json.dumps(
            {
                "user_id": user_id,
                "message": "暂无学习记录，请先记录一些学习目标或进度。",
                "next_steps": ["告诉我你想学习的技术方向和目标认证，我帮你制定学习路径。"],
            },
            ensure_ascii=False,
            indent=2,
        )

    records = user_record["records"]
    completed = [r for r in records if r.get("status") == "已完成"]
    in_progress = [r for r in records if r.get("status") == "进行中"]
    not_started = [r for r in records if r.get("status") == "未开始"]

    next_steps: list = []
    if in_progress:
        next_steps.append(f"继续完成进行中的内容：{', '.join(r['topic'] for r in in_progress)}")
    if not_started:
        next_steps.append(f"开始学习尚未开始的内容：{', '.join(r['topic'] for r in not_started[:3])}")
    if completed and not (in_progress or not_started):
        next_steps.append("你已经完成当前计划，可以告诉我下一步想攻克哪门认证或技术方向。")

    return json.dumps(
        {
            "user_id": user_id,
            "summary": {
                "completed": len(completed),
                "in_progress": len(in_progress),
                "not_started": len(not_started),
            },
            "next_steps": next_steps,
            "tip": "保持规律学习节奏，每周至少完成一个学习模块。",
        },
        ensure_ascii=False,
        indent=2,
    )
