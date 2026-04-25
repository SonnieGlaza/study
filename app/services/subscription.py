from __future__ import annotations

from app.services.getcourse import GetCourseClient


async def is_subscription_active(telegram_user_id: int) -> tuple[bool, str]:
    client = GetCourseClient()
    status = await client.fetch_subscription_status(telegram_user_id=telegram_user_id)
    return status.is_active, status.tariff
