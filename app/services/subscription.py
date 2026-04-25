from __future__ import annotations

from dataclasses import dataclass

from app.services.getcourse import GetCourseClient


@dataclass(frozen=True)
class SubscriptionSyncResult:
    active: bool
    tier: str


async def is_subscription_active(telegram_user_id: int) -> tuple[bool, str]:
    client = GetCourseClient()
    status = await client.validate_subscription(telegram_user_id=telegram_user_id)
    return status.active, status.plan


async def sync_subscription(repo, telegram_user_id: int) -> SubscriptionSyncResult:
    client = GetCourseClient()
    status = await client.validate_subscription(telegram_user_id=telegram_user_id)
    repo.set_subscription(telegram_user_id=telegram_user_id, active=status.active, tier=status.plan)
    return SubscriptionSyncResult(active=status.active, tier=status.plan)
