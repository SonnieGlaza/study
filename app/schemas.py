from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AdminToggleBotRequest(BaseModel):
    enabled: bool


class AdminPromptUpdateRequest(BaseModel):
    consultation_system_prompt: str


class AdminMaterialUploadRequest(BaseModel):
    title: str
    content: str
    source_type: str = "manual"


class UserDialogMessage(BaseModel):
    role: str
    text: str
    created_at: datetime


class UserDialogView(BaseModel):
    user_id: int
    messages: list[UserDialogMessage]


class VisualizationRequest(BaseModel):
    user_id: int
    photo_file_id: str
    strength: str
    meta: dict[str, Any] | None = None
