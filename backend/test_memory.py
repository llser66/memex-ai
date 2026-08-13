from app.database.session import SessionLocal
from app.services.memory_service import (
    add_event,
    get_recent_events,
    upsert_profile,
    get_all_profiles
)


db = SessionLocal()


try:

    # 测试用户画像
    upsert_profile(
        db,
        "name",
        "李立晟"
    )

    upsert_profile(
        db,
        "job",
        "AI应用工程师"
    )


    # 测试事件
    add_event(
        db,
        "test",
        "用户测试了Memex记忆系统"
    )


    # 查询画像
    profiles = get_all_profiles(db)

    print("\n用户画像:")

    for profile in profiles:

        print(
            profile.key,
            "=",
            profile.value
        )


    # 查询事件
    events = get_recent_events(
        db,
        limit=5
    )

    print("\n最近事件:")

    for event in events:

        print(
            event.event_type,
            event.description
        )


finally:

    db.close()