"""用户画像和历史事件 API。"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.database.session import SessionLocal
from app.services.memory_service import (
    delete_profile,
    get_all_profiles,
    get_recent_events,
    upsert_profile,
)


router = APIRouter(prefix="/memory", tags=["个人记忆"])


class ProfileRequest(BaseModel):
    value: str = Field(min_length=1, max_length=500)


def _serialize_profile(profile):
    return {
        "key": profile.key,
        "value": profile.value,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def _serialize_event(event):
    return {
        "id": event.id,
        "event_type": event.event_type,
        "description": event.description,
        "related_doc": event.related_doc,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.get("/summary")
def memory_summary(limit: int = Query(default=8, ge=1, le=100)):
    db = SessionLocal()
    try:
        return {
            "profiles": [_serialize_profile(profile) for profile in get_all_profiles(db)],
            "events": [_serialize_event(event) for event in get_recent_events(db, limit=limit)],
        }
    finally:
        db.close()


@router.put("/profiles/{key}")
def save_profile(key: str, request: ProfileRequest):
    key = key.strip()
    value = request.value.strip()
    if not key or len(key) > 100:
        raise HTTPException(status_code=422, detail="记忆名称不能为空且不能超过 100 个字符。")
    if not value:
        raise HTTPException(status_code=422, detail="记忆内容不能为空。")

    db = SessionLocal()
    try:
        profile = upsert_profile(db, key, value)
        return _serialize_profile(profile)
    finally:
        db.close()


@router.delete("/profiles/{key}")
def remove_profile(key: str):
    db = SessionLocal()
    try:
        profile = delete_profile(db, key)
        if not profile:
            raise HTTPException(status_code=404, detail="没有找到这条记忆。")
        return {"key": key, "deleted": True}
    finally:
        db.close()
