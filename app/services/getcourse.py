from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

from app.config import settings


@dataclass
class SubscriptionStatus:
    active: bool
    plan: str
    expires_at: datetime | None
    raw: dict


class GetCourseClient:
    def __init__(self) -> None:
        self.base_url = settings.getcourse_api_url.rstrip("/")
        self.api_key = settings.getcourse_api_key
        self.account = settings.getcourse_account_name

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def validate_subscription(self, telegram_user_id: int) -> SubscriptionStatus:
        if not self.base_url:
            return SubscriptionStatus(active=False, plan="free", expires_at=None, raw={})

        url = f"{self.base_url}/subscriptions/status"
        params = {"telegram_id": telegram_user_id}
        if self.account:
            params["account_name"] = self.account
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params, headers=self._headers())
            response.raise_for_status()
            payload = response.json()

        expires_raw = payload.get("expires_at")
        expires_at = None
        if expires_raw:
            expires_at = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))

        return SubscriptionStatus(
            active=bool(payload.get("active", False)),
            plan=str(payload.get("plan", "free")),
            expires_at=expires_at,
            raw=payload,
        )

    async def sync_client(self, telegram_user_id: int, username: str, full_name: str) -> dict:
        if not self.base_url:
            return {}
        url = f"{self.base_url}/clients/sync"
        body = {
            "telegram_id": telegram_user_id,
            "username": username,
            "full_name": full_name,
            "account_name": self.account,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, json=body, headers=self._headers())
            response.raise_for_status()
            return response.json()
