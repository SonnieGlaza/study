from __future__ import annotations

import httpx

from app.config import settings


class GetCourseService:
    async def has_active_subscription(self, telegram_user_id: int) -> bool:
        """
        Stub for GetCourse integration.
        Replace with real endpoint and auth contract from заказчик.
        """
        if not settings.getcourse_api_url or not settings.getcourse_api_token:
            return False

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{settings.getcourse_api_url}/subscriptions/check",
                params={"telegram_id": telegram_user_id},
                headers={"Authorization": f"Bearer {settings.getcourse_api_token}"},
            )
            if response.status_code != 200:
                return False
            payload = response.json()
            return bool(payload.get("active", False))
