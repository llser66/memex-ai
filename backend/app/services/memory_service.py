from sqlalchemy.orm import Session

from app.database.models import (
    UserProfile,
    EventMemory
)


def upsert_profile(
    db: Session,
    key: str,
    value: str
):
    """
    新增或者更新用户画像
    """

    profile = (
        db.query(UserProfile)
        .filter(UserProfile.key == key)
        .first()
    )

    if profile:

        profile.value = value

    else:

        profile = UserProfile(
            key=key,
            value=value
        )

        db.add(profile)

    db.commit()

    db.refresh(profile)

    return profile


def get_all_profiles(db: Session):

    return (
        db.query(UserProfile)
        .all()
    )


def get_profile(
    db: Session,
    key: str
):

    return (
        db.query(UserProfile)
        .filter(UserProfile.key == key)
        .first()
    )


def add_event(
    db: Session,
    event_type: str,
    description: str,
    related_doc: str = None
):

    event = EventMemory(
        event_type=event_type,
        description=description,
        related_doc=related_doc
    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event


def get_recent_events(
    db: Session,
    limit: int = 5
):

    return (
        db.query(EventMemory)
        .order_by(EventMemory.created_at.desc())
        .limit(limit)
        .all()
    )