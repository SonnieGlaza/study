from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.schemas import (
    AdminSettingsRead,
    AdminSettingsUpdate,
    BotToggleRequest,
    BotToggleResponse,
    UserDialogRead,
)
from app.services.repository import (
    get_dialog_messages,
    get_or_create_admin_settings,
    update_admin_settings,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _check_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin token.")


@router.get("/settings", response_model=AdminSettingsRead, dependencies=[Depends(_check_admin_token)])
def read_settings(db: Session = Depends(get_db)) -> AdminSettingsRead:
    cfg = get_or_create_admin_settings(db)
    return AdminSettingsRead.model_validate(cfg, from_attributes=True)


@router.patch("/settings", response_model=AdminSettingsRead, dependencies=[Depends(_check_admin_token)])
def patch_settings(payload: AdminSettingsUpdate, db: Session = Depends(get_db)) -> AdminSettingsRead:
    cfg = update_admin_settings(
        db,
        system_prompt=payload.system_prompt,
        response_style=payload.response_style,
        consultation_logic=payload.consultation_logic,
    )
    return AdminSettingsRead.model_validate(cfg, from_attributes=True)


@router.post("/bot/toggle", response_model=BotToggleResponse, dependencies=[Depends(_check_admin_token)])
def toggle_bot(payload: BotToggleRequest, db: Session = Depends(get_db)) -> BotToggleResponse:
    cfg = update_admin_settings(db, bot_enabled=payload.enabled)
    return BotToggleResponse(enabled=cfg.bot_enabled)


@router.get(
    "/dialogs/{telegram_user_id}",
    response_model=list[UserDialogRead],
    dependencies=[Depends(_check_admin_token)],
)
def read_dialogs(telegram_user_id: int, db: Session = Depends(get_db)) -> list[UserDialogRead]:
    rows = get_dialog_messages(db, telegram_user_id=telegram_user_id, limit=200)
    return [UserDialogRead.model_validate(row, from_attributes=True) for row in rows]
