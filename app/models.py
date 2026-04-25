from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class GenerationIntensity(str, Enum):
    light = "light"
    medium = "medium"
    strong = "strong"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(128), default="")
    full_name: Mapped[str] = mapped_column(String(255), default="")
    personality_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    completed_test: Mapped[bool] = mapped_column(Boolean, default=False)
    skipped_test: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_state: Mapped[str] = mapped_column(
        Text, default='{"current_index": 0, "answers": []}'
    )
    subscription_active: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_tier: Mapped[str] = mapped_column(String(32), default="free")
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generations: Mapped[list["GenerationHistory"]] = relationship(back_populates="user")
    dialog_messages: Mapped[list["DialogMessage"]] = relationship(back_populates="user")


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_photo_path: Mapped[str] = mapped_column(String(512))
    variation_level: Mapped[str] = mapped_column(String(16))
    generation_prompt: Mapped[str] = mapped_column(Text)
    result_file_path: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="generations")


class DialogMessage(Base):
    __tablename__ = "dialog_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="dialog_messages")


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(64), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BotConfig(Base):
    __tablename__ = "bot_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    consultation_system_prompt: Mapped[str] = mapped_column(
        Text, default="Ты интерьерный консультант. Отвечай практично и дружелюбно."
    )
    response_style: Mapped[str] = mapped_column(String(64), default="professional-friendly")
    personality_formula_json: Mapped[str] = mapped_column(Text, default="{}")
