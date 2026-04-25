from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    personality_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    quiz_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    quiz_question_index: Mapped[int] = mapped_column(Integer, default=0)
    quiz_scores_json: Mapped[str] = mapped_column(Text, default="{}")
    subscription_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    generations: Mapped[list["GenerationHistory"]] = relationship(back_populates="user")


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_image_file_id: Mapped[str] = mapped_column(String(255))
    intensity: Mapped[str] = mapped_column(String(16))
    result_image_url: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="generations")


class BotConfig(Base):
    __tablename__ = "bot_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    consultant_system_prompt: Mapped[str] = mapped_column(
        Text, default="Ты интерьерный консультант. Отвечай практично и дружелюбно."
    )
    response_style: Mapped[str] = mapped_column(
        String(64), default="professional-friendly"
    )
