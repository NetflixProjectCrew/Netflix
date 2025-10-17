from datetime import datetime, timezone

def can_user_watch(user, movie) -> tuple[bool, str | None, dict]:
    """
    Единая точка бизнес-логики «можно смотреть?».
    Возвращает (ok: bool, reason: str | None, meta: dict)
    """
    if not user.is_authenticated:
        return False, "auth_required", {}

    sub = getattr(user, "subscription", None)
    if sub is None:
        # На всякий случай проверим активную из истории
        active = getattr(user, "subscriptions", None)
        if active and active.filter(status="active", end_date__gt=datetime.now(timezone.utc)).exists():
            return True, None, {}
        return False, "subscription_missing", {}

    if not sub.is_active:
        return False, "subscription_inactive", {}


    return True, None, {}
