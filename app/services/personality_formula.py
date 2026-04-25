from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import settings


@dataclass(frozen=True)
class PersonalityResult:
    personality_type: str
    title: str
    description: str
    interior_recommendations: str
    trait_scores: dict[str, int]
    max_score: int


def _default_formula_path() -> Path:
    return Path(__file__).resolve().parent.parent / "personality_formula.default.json"


def _load_formula_file() -> dict[str, Any]:
    path = (
        Path(settings.personality_formula_path)
        if settings.personality_formula_path
        else _default_formula_path()
    )
    if not path.exists():
        path = _default_formula_path()
    return json.loads(path.read_text(encoding="utf-8"))


def _load_formula_override(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def calculate_personality(answer_indices: list[int], formula_override_json: str | None = None) -> PersonalityResult:
    formula = _load_formula_override(formula_override_json) or _load_formula_file()
    dimensions: list[dict[str, Any]] = formula["dimensions"]
    personality_map: dict[str, dict[str, str]] = formula["personality_map"]

    letters: list[str] = []
    scores: dict[str, int] = {}
    total_max = 0
    for idx, dim in enumerate(dimensions):
        selected = answer_indices[idx] if idx < len(answer_indices) else 0
        selected = min(max(selected, 0), 3)
        score_vector = dim["score_by_option"][selected]
        left, right = dim["letters"][0], dim["letters"][1]
        left_score = int(score_vector.get(left, 0))
        right_score = int(score_vector.get(right, 0))
        scores[left] = scores.get(left, 0) + left_score
        scores[right] = scores.get(right, 0) + right_score
        total_max += max(left_score, right_score)
        letters.append(left if left_score >= right_score else right)

    personality_type = "".join(letters)
    profile = personality_map.get(personality_type) or next(iter(personality_map.values()))
    return PersonalityResult(
        personality_type=personality_type,
        title=profile["title"],
        description=profile["description"],
        interior_recommendations=profile["interior_recommendations"],
        trait_scores=scores,
        max_score=total_max,
    )
