import asyncio
import json
import logging

import httpx
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        _client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=httpx.Timeout(600.0, connect=60.0),
        )
    return _client


async def _chat_completion(messages: list[dict], temperature: float = 0.3) -> str:
    """Shared LLM call with automatic retry on transient failures."""
    client = _get_client()
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,

            )
            return response.choices[0].message.content
        except Exception as e:
            last_err = e
            logger.warning("LLM call attempt %d/%d failed: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
    raise last_err


SYSTEM_PROMPT = """你是Robotaxi乘客反馈分析助手。请根据提供的乘客反馈数据，生成结构化的分析摘要。

请严格按以下JSON格式返回（不要包含markdown代码块标记）：
{
  "major_problems": ["问题1", "问题2", ...],
  "feedback_themes": ["主题1", "主题2", ...],
  "action_suggestions": ["建议1", "建议2", ...],
  "trend_summary": "总体趋势描述"
}

分析要求：
- major_problems: 提取反馈中反映的主要问题（3-5条），按严重程度排序
- feedback_themes: 归纳反馈的核心主题/模式（3-5条）
- action_suggestions: 基于问题和主题，给出具体可执行的改进建议（3-5条）
- trend_summary: 综合分析用户反馈的总体变化趋势，包括评分分布特征、高频问题的集中程度、不同城市/路线的差异表现、以及与服务质量相关的整体走向（2-4句话）
- 使用中文回答
- 保持简洁专业"""


def _build_user_message(feedbacks: list[dict]) -> str:
    lines = [f"以下是{len(feedbacks)}条乘客反馈数据：\n"]
    for i, fb in enumerate(feedbacks, 1):
        lines.append(
            f"{i}. [评分:{fb['rating']}/5] [分类:{fb.get('ai_category') or '未分类'}] "
            f"[城市:{fb['city']}] [路线:{fb['route']}]\n"
            f"   反馈内容：{fb['feedback_text']}"
        )
    return "\n".join(lines)


async def analyze_feedbacks(feedbacks: list[dict]) -> dict:
    """Call LLM to analyze feedback texts. Returns parsed JSON dict."""
    user_message = _build_user_message(feedbacks)

    content = await _chat_completion([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    # Strip markdown code block wrapper if present
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(content)


REPORT_SYSTEM_PROMPT = """你是Robotaxi运营数据分析专家。请根据提供的仪表盘数据，生成一份专业的运营分析报告。

报告要求：
- 使用Markdown格式
- 包含以下章节：概述、关键指标分析、趋势分析、分布分析、工单处理分析、建议与行动项
- 数据驱动：引用具体数字和百分比
- 对比分析：指出异常值和值得关注的变化
- 建议部分要具体可执行
- 使用中文，保持专业简洁
- 不要在报告中使用markdown代码块标记"""

PERIOD_LABELS = {"daily": "日报", "weekly": "周报", "monthly": "月报"}


def _build_report_message(data: dict, period: str) -> str:
    label = PERIOD_LABELS.get(period, period)
    lines = [f"请生成一份Robotaxi运营{label}。以下是当前仪表盘数据：\n"]

    # Overview
    ov = data["overview"]
    lines.append("## 概览指标")
    lines.append(f"- 总反馈数: {ov['total_feedbacks']}")
    lines.append(f"- 今日反馈: {ov['total_today']}")
    lines.append(f"- 本周反馈: {ov['total_this_week']}")
    lines.append(f"- 本月反馈: {ov['total_this_month']}")
    lines.append(f"- 平均评分: {ov['avg_rating']}")
    lines.append(f"- 好评率: {ov['positive_rate']}%")
    lines.append(f"- 差评率: {ov['negative_rate']}%")
    lines.append(f"- 未关闭工单: {ov['open_tickets']}")
    lines.append(f"- SLA达标率: {ov['sla_compliance_rate']}%\n")

    # Trends
    trends = data["trends"]
    lines.append("## 趋势数据")
    for i, point in enumerate(trends["negative_count"]):
        date = point["date"]
        neg = point["value"]
        pos = trends["positive_rate"][i]["value"] if i < len(trends["positive_rate"]) else "N/A"
        avg = trends["avg_rating"][i]["value"] if i < len(trends["avg_rating"]) else "N/A"
        lines.append(f"- {date}: 差评数={neg}, 好评率={pos}%, 平均评分={avg}")
    lines.append("")

    # Distribution
    dist = data["distribution"]
    for key, title in [
        ("by_rating", "评分分布"),
        ("by_category", "反馈类型分布"),
        ("by_city", "城市分布"),
        ("by_route", "路线分布(Top10)"),
        ("by_time_period", "时段分布"),
    ]:
        items = dist.get(key, [])
        if items:
            lines.append(f"## {title}")
            for item in items:
                lines.append(f"- {item['label']}: {item['count']}条 ({item['percentage']}%)")
            lines.append("")

    # Ticket metrics
    tm = data["ticket_metrics"]
    lines.append("## 工单指标")
    for item in tm.get("by_priority", []):
        p = item["label"]
        resolve = tm["avg_resolve_time_hours"].get(p, "N/A")
        sla = tm["sla_compliance_by_priority"].get(p, "N/A")
        lines.append(f"- {p}: {item['count']}个工单, 平均处理时长={resolve}h, SLA达标率={sla}%")
    aging = tm.get("open_tickets_aging", [])
    if aging:
        lines.append("- 未关闭工单老化: " + ", ".join(f"{a['label']}={a['count']}个" for a in aging))

    return "\n".join(lines)


async def generate_dashboard_report(data: dict, period: str) -> str:
    """Call LLM to generate a dashboard analysis report. Returns markdown string."""
    user_message = _build_report_message(data, period)

    content = await _chat_completion([
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    # Strip markdown code block wrapper if present
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return content
