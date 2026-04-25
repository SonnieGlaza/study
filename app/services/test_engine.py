from dataclasses import dataclass

from app.services.personality_formula import calculate_personality

QUESTION_COUNT = 20


@dataclass(frozen=True)
class Question:
    number: int
    text: str
    options: list[str]


@dataclass(frozen=True)
class TestSummary:
    personality_type: str
    summary_text: str
    interior_recommendations: str
    title: str


QUESTIONS: list[Question] = [
    Question(
        number=i + 1,
        text=f"Вопрос {i + 1}: как вы предпочитаете организовывать пространство?",
        options=[
            "Люблю структуру и систему",
            "Предпочитаю гибкость и эксперименты",
            "Ориентируюсь на эстетику и атмосферу",
            "Ставлю практичность на первое место",
        ],
    )
    for i in range(QUESTION_COUNT)
]


def question_by_number(number: int) -> Question:
    idx = max(min(number, QUESTION_COUNT), 1) - 1
    return QUESTIONS[idx]


def summarize_result(answer_indexes: list[int], formula_override: str | None = None) -> TestSummary:
    result = calculate_personality(answer_indexes, formula_override_json=formula_override)
    return TestSummary(
        personality_type=result.personality_type,
        summary_text=result.description,
        interior_recommendations=result.interior_recommendations,
        title=result.title,
    )
