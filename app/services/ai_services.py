from dataclasses import dataclass


@dataclass
class VisualGenerationResult:
    image_url: str
    prompt_used: str


class InteriorVisualizerService:
    def generate(self, photo_file_id: str, personality_type: str, change_level: str) -> VisualGenerationResult:
        # Stub implementation. Replace with real provider integration.
        prompt = (
            f"Reimagine room based on MBTI={personality_type}, "
            f"change_level={change_level}, source_photo={photo_file_id}"
        )
        return VisualGenerationResult(
            image_url=f"https://example.com/generated/{photo_file_id}_{change_level}.jpg",
            prompt_used=prompt,
        )


class ConsultantService:
    def answer(self, question: str, personality_type: str | None = None) -> str:
        # Stub RAG + LLM answer.
        if personality_type:
            return (
                f"С учётом вашего типа {personality_type}, рекомендую: {question}. "
                "Подборка основана на внутренних материалах (режим-заглушка)."
            )
        return (
            f"Рекомендация по запросу: {question}. "
            "Ответ сформирован на основе внутренних материалов (режим-заглушка)."
        )
