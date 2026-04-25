from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select

from app import models
from app.db import SessionLocal


class Repository:
    def upsert_user(self, telegram_user_id: int, username: str, full_name: str) -> models.User:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if user:
                user.username = username
                user.full_name = full_name
                user.updated_at = datetime.now(tz=timezone.utc)
            else:
                user = models.User(telegram_user_id=telegram_user_id, username=username, full_name=full_name)
                session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user(self, telegram_user_id: int) -> models.User | None:
        with SessionLocal() as session:
            return session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))

    def list_answers(self, telegram_user_id: int) -> list[int]:
        user = self.get_user(telegram_user_id)
        if not user:
            return []
        state = json.loads(user.assessment_state or '{"current_index": 0, "answers": []}')
        return [int(v) for v in state.get("answers", [])]

    def save_answer(self, telegram_user_id: int, question_number: int, selected_option: int) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            state = json.loads(user.assessment_state or '{"current_index": 0, "answers": []}')
            answers = list(state.get("answers", []))
            idx = max(question_number - 1, 0)
            if len(answers) > idx:
                answers[idx] = int(selected_option)
            else:
                while len(answers) < idx:
                    answers.append(0)
                answers.append(int(selected_option))
            state["answers"] = answers
            state["current_index"] = min(question_number + 1, 20)
            user.assessment_state = json.dumps(state, ensure_ascii=False)
            user.updated_at = datetime.now(tz=timezone.utc)
            session.commit()

    def finalize_test(self, telegram_user_id: int, personality_type: str) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            user.completed_test = True
            user.skipped_test = False
            user.personality_type = personality_type
            state = json.loads(user.assessment_state or '{"current_index": 0, "answers": []}')
            state["current_index"] = 20
            user.assessment_state = json.dumps(state, ensure_ascii=False)
            user.updated_at = datetime.now(tz=timezone.utc)
            session.commit()

    def restart_test(self, telegram_user_id: int) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            user.completed_test = False
            user.skipped_test = False
            user.personality_type = None
            user.assessment_state = '{"current_index": 0, "answers": []}'
            user.updated_at = datetime.now(tz=timezone.utc)
            session.commit()

    def set_skipped(self, telegram_user_id: int, skipped: bool) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            user.skipped_test = skipped
            user.updated_at = datetime.now(tz=timezone.utc)
            session.commit()

    def set_subscription(
        self, telegram_user_id: int, active: bool, tier: str | None = None, days: int = 30
    ) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            user.subscription_active = active
            if tier:
                user.subscription_tier = tier
            user.subscription_expires_at = (
                datetime.now(tz=timezone.utc) + timedelta(days=days) if active else None
            )
            user.updated_at = datetime.now(tz=timezone.utc)
            session.commit()

    def add_generation(
        self,
        telegram_user_id: int,
        source_photo_path: str,
        output_photo_path: str,
        intensity: models.GenerationIntensity,
        prompt: str,
        provider_job_id: str | None = None,
    ) -> models.GenerationHistory:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                raise ValueError("User not found")
            item = models.GenerationHistory(
                user_id=user.id,
                source_photo_path=source_photo_path,
                variation_level=intensity.value,
                generation_prompt=prompt,
                result_file_path=output_photo_path,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def list_generations(self, telegram_user_id: int, limit: int = 20) -> list[models.GenerationHistory]:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return []
            stmt = (
                select(models.GenerationHistory)
                .where(models.GenerationHistory.user_id == user.id)
                .order_by(desc(models.GenerationHistory.created_at))
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def add_dialog_message(self, telegram_user_id: int, role: str, text: str) -> None:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return
            session.add(models.DialogMessage(user_id=user.id, role=role, text=text))
            session.commit()

    def list_dialog_messages(self, telegram_user_id: int, limit: int = 100) -> list[models.DialogMessage]:
        with SessionLocal() as session:
            user = session.scalar(select(models.User).where(models.User.telegram_user_id == telegram_user_id))
            if not user:
                return []
            stmt = (
                select(models.DialogMessage)
                .where(models.DialogMessage.user_id == user.id)
                .order_by(desc(models.DialogMessage.created_at))
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def list_users(self, limit: int = 200) -> list[models.User]:
        with SessionLocal() as session:
            stmt = select(models.User).order_by(desc(models.User.updated_at)).limit(limit)
            return list(session.scalars(stmt))

    def add_material(self, title: str, content: str, source_type: str = "manual") -> models.Material:
        with SessionLocal() as session:
            item = models.Material(title=title, content=content, source_type=source_type)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def list_materials(self, limit: int = 200) -> list[models.Material]:
        with SessionLocal() as session:
            stmt = select(models.Material).order_by(desc(models.Material.created_at)).limit(limit)
            return list(session.scalars(stmt))

    def get_bot_config(self) -> models.BotConfig:
        with SessionLocal() as session:
            cfg = session.get(models.BotConfig, 1)
            if cfg:
                return cfg
            cfg = models.BotConfig(id=1)
            session.add(cfg)
            session.commit()
            session.refresh(cfg)
            return cfg

    def update_bot_config(
        self,
        *,
        enabled: bool | None = None,
        consultation_system_prompt: str | None = None,
        response_style: str | None = None,
        personality_formula_json: str | None = None,
    ) -> models.BotConfig:
        with SessionLocal() as session:
            cfg = session.get(models.BotConfig, 1)
            if not cfg:
                cfg = models.BotConfig(id=1)
                session.add(cfg)
            if enabled is not None:
                cfg.enabled = enabled
            if consultation_system_prompt is not None:
                cfg.consultation_system_prompt = consultation_system_prompt
            if response_style is not None:
                cfg.response_style = response_style
            if personality_formula_json is not None:
                cfg.personality_formula_json = personality_formula_json
            session.commit()
            session.refresh(cfg)
            return cfg
