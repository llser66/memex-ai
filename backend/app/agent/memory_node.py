from app.database.session import SessionLocal
from app.services.memory_service import get_recent_events, get_all_profiles

def memory_node(state: dict) -> dict:
    db = SessionLocal()
    try:
        events = get_recent_events(db, limit=5)
        profiles = get_all_profiles(db)

        events_data = [
            {
                "created_at": event.created_at,
                "event_type": event.event_type,
                "description": event.description,
                "related_doc": event.related_doc,
            }
            for event in events
        ]
        profiles_data = [
            {"key": profile.key, "value": profile.value}
            for profile in profiles
        ]
    finally:
        db.close()

    memory_context = ""
    if profiles_data:
        memory_context += "\n用户画像：\n"
        for p in profiles_data:
            memory_context += f"- {p['key']}: {p['value']}\n"
    if events_data:
        memory_context += "\n用户历史事件：\n"
        for e in events_data:
            memory_context += f"- 时间：{e['created_at']}\n"
            memory_context += f"  类型：{e['event_type']}\n"
            memory_context += f"  描述：{e['description']}\n"
            if e['related_doc']:
                memory_context += f"  关联文档：{e['related_doc']}\n"

    return {
        "memory_context": memory_context,
        "next_node": "generate"
    }