from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.schemas import (
    AdminPromptUpdateRequest,
    AdminMaterialUploadRequest,
    AdminToggleBotRequest,
)
from app.services.repository import Repository

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")
repo = Repository()


def _check_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin token.")


def _ensure_form_admin_token(admin_token: str) -> None:
    if admin_token != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin token.")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, admin_token: str) -> HTMLResponse:
    _ensure_form_admin_token(admin_token)
    config = repo.get_bot_config()
    users = repo.list_users(limit=300)
    materials = repo.list_materials(limit=300)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "admin_token": admin_token,
            "config": config,
            "users": users,
            "materials": materials,
        },
    )


@router.post("/dashboard/config")
def update_config(
    admin_token: str = Form(...),
    enabled: str = Form("off"),
    consultation_system_prompt: str = Form(...),
    response_style: str = Form(...),
    personality_formula_json: str = Form(""),
) -> RedirectResponse:
    _ensure_form_admin_token(admin_token)
    payload = AdminPromptUpdateRequest(
        consultation_system_prompt=consultation_system_prompt,
        response_style=response_style,
    )
    repo.update_bot_config(
        enabled=(enabled == "on"),
        consultation_system_prompt=payload.consultation_system_prompt,
        response_style=payload.response_style,
        personality_formula_json=personality_formula_json or None,
    )
    return RedirectResponse(url=f"/admin/dashboard?admin_token={admin_token}", status_code=303)


@router.post("/dashboard/materials")
def add_material(
    admin_token: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    source_type: str = Form("manual"),
) -> RedirectResponse:
    _ensure_form_admin_token(admin_token)
    payload = AdminMaterialUploadRequest(title=title, content=content, source_type=source_type)
    repo.upsert_material(payload.title, payload.content, payload.source_type)
    return RedirectResponse(url=f"/admin/dashboard?admin_token={admin_token}", status_code=303)


@router.get("/settings", dependencies=[Depends(_check_admin_token)])
def get_settings() -> dict:
    config = repo.get_bot_config()
    return {
        "enabled": config.enabled,
        "consultation_system_prompt": config.consultation_system_prompt,
        "response_style": config.response_style,
        "personality_formula_json": config.personality_formula_json or "",
    }


@router.post("/bot/toggle", dependencies=[Depends(_check_admin_token)])
def toggle_bot(payload: AdminToggleBotRequest) -> dict[str, bool]:
    updated = repo.update_bot_config(enabled=payload.enabled)
    return {"enabled": updated.enabled}


@router.post("/materials", dependencies=[Depends(_check_admin_token)])
def upload_material(payload: AdminMaterialUploadRequest) -> dict:
    item = repo.upsert_material(payload.title, payload.content, payload.source_type)
    return {"id": item.id, "title": item.title}


@router.get("/dialogs/{telegram_user_id}", dependencies=[Depends(_check_admin_token)])
def read_dialogs(telegram_user_id: int) -> list[dict]:
    rows = repo.list_dialog_messages(telegram_user_id=telegram_user_id, limit=200)
    return [
        {"role": row.role, "text": row.text, "created_at": row.created_at.isoformat()}
        for row in rows
    ]


@router.get("/users", dependencies=[Depends(_check_admin_token)])
def read_users() -> list[dict]:
    users = repo.list_users(limit=500)
    result: list[dict] = []
    for user in users:
        result.append(
            {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "full_name": user.full_name,
                "personality_type": user.personality_type,
                "subscription_active": user.subscription_active,
                "subscription_tier": user.subscription_tier,
            }
        )
    return result
