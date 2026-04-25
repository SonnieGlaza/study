from datetime import datetime

from pydantic import BaseModel


class AdminToggleBotRequest(BaseModel):
    enabled: bool


class AdminPromptUpdateRequest(BaseModel):
    consultation_system_prompt: str
    response_style: str


class AdminFormulaUpdateRequest(BaseModel):
    personality_formula_json: str


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
    telegram_user_id: int
    username: str
    full_name: str
    messages: list[UserDialogMessage]
