from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_or_create_user(session: Session, telegram_id: int) -> models.User:
    user = session.scalar(select(models.User).where(models.User.telegram_id == telegram_id))
    if user:
        return user
    user = models.User(telegram_id=telegram_id)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def reset_assessment(session: Session, user: models.User) -> None:
    user.assessment_completed = False
    user.personality_type = None
    user.assessment_state = {"current_index": 0, "answers": []}
    session.commit()


def save_answer(session: Session, user: models.User, question_index: int, answer_index: int) -> models.User:
    state = user.assessment_state or {"current_index": 0, "answers": []}
    answers = list(state.get("answers", []))

    # Ensure deterministic replacement if user returns to previous question.
    if len(answers) > question_index:
        answers[question_index] = answer_index
    else:
        while len(answers) < question_index:
            answers.append(0)
        answers.append(answer_index)

    state["answers"] = answers
    state["current_index"] = min(question_index + 1, 20)
    user.assessment_state = state
    user.updated_at = datetime.now(tz=timezone.utc)
    session.commit()
    session.refresh(user)
    return user


def complete_assessment(session: Session, user: models.User, personality_type: str) -> None:
    user.assessment_completed = True
    user.personality_type = personality_type
    user.updated_at = datetime.now(tz=timezone.utc)
    session.commit()


def save_generation(
    session: Session,
    user: models.User,
    source_photo_file_id: str,
    variation_level: str,
    prompt: str,
    result_file_id: str,
) -> models.GenerationHistory:
    item = models.GenerationHistory(
        user_id=user.id,
        source_photo_file_id=source_photo_file_id,
        variation_level=variation_level,
        generation_prompt=prompt,
        result_file_id=result_file_id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
