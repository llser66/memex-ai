from datetime import datetime, timedelta
from pathlib import Path
from app.database.session import SessionLocal
from app.services.memory_service import get_events_between, get_all_profiles
from app.rag.generator import get_client  # 复用 DeepSeek client

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_weekly_report() -> str:
    """生成本周周报，返回文件路径"""
    today = datetime.now()
    week_start = datetime(today.year, today.month, today.day) - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    db = SessionLocal()
    try:
        events = get_events_between(db, week_start, week_end)
        profiles = get_all_profiles(db)
    finally:
        db.close()

    memory_context = "用户画像：\n"
    for p in profiles:
        memory_context += f"- {p.key}: {p.value}\n"
    memory_context += "\n近期事件：\n"
    for e in events:
        memory_context += f"- [{e.created_at.strftime('%Y-%m-%d')}] {e.description}\n"

    week_end_display = week_end - timedelta(days=1)

    prompt = f"""请根据以下用户信息，生成本周（{week_start.strftime('%Y-%m-%d')} 至 {week_end_display.strftime('%Y-%m-%d')}）的工作周报。要求：
1. 使用 Markdown 格式，包含“本周工作概述”“重点成果”“遇到的问题”“下周计划”四个部分。
2. 内容要结合用户画像和事件记忆，不要编造。
3. 如果事件较少，可以写“暂无”。

用户信息：
{memory_context}
"""

    response = get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    report_content = response.choices[0].message.content

    filename = f"weekly_report_{today.strftime('%Y%m%d')}.md"
    file_path = OUTPUT_DIR / filename
    file_path.write_text(report_content, encoding="utf-8")
    return str(file_path)
