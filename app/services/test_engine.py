from dataclasses import dataclass


@dataclass(frozen=True)
class TestResult:
    personality_type: str
    title: str
    description: str
    interior_recommendations: str


PERSONALITY_MAP = {
    "A": "ESTP",
    "B": "INFJ",
    "C": "ENTJ",
    "D": "ISFP",
}


def calculate_personality(answer_codes: list[str]) -> TestResult:
    counters = {"A": 0, "B": 0, "C": 0, "D": 0}
    for code in answer_codes:
        if code in counters:
            counters[code] += 1
    dominant = max(counters, key=counters.get) if answer_codes else "A"
    personality = PERSONALITY_MAP[dominant]

    if personality == "ESTP":
        return TestResult(
            personality_type=personality,
            title="Динамичный реалист",
            description="Вы любите скорость, простоту и функциональность.",
            interior_recommendations=(
                "Подходят тёмные оттенки, прямые линии, контрастные формы, "
                "минимализм и функциональные решения."
            ),
        )
    if personality == "INFJ":
        return TestResult(
            personality_type=personality,
            title="Гармоничный стратег",
            description="Вы цените уединение, смысл и атмосферу.",
            interior_recommendations=(
                "Подходят мягкие фактуры, тёплые нейтральные цвета, "
                "натуральные материалы и уютные световые сценарии."
            ),
        )
    if personality == "ENTJ":
        return TestResult(
            personality_type=personality,
            title="Системный лидер",
            description="Вы мыслите структурно и ориентированы на результат.",
            interior_recommendations=(
                "Подходят чёткая геометрия, премиальные материалы, "
                "эргономичная мебель и технологичные акценты."
            ),
        )
    return TestResult(
        personality_type=personality,
        title="Творческий эстет",
        description="Вы чувствительны к красоте, деталям и настроению.",
        interior_recommendations=(
            "Подходят природные палитры, декор с характером, "
            "живые растения и мягкое рассеянное освещение."
        ),
    )
