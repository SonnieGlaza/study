from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.config import settings
from app.models import GenerationIntensity
from app.services.file_storage import ensure_dir
from app.services.rag import RAGService


@dataclass
class GeneratedImage:
    output_path: str
    prompt_used: str
    provider_job_id: str | None


def _encode_image(path: str) -> tuple[str, str]:
    file_path = Path(path)
    encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8")
    mime = mimetypes.guess_type(file_path.name)[0] or "image/jpeg"
    return encoded, mime


def _build_generation_prompt(
    personality_type: str | None, intensity: GenerationIntensity, extra_instruction: str | None = None
) -> str:
    persona_part = f"personality={personality_type}" if personality_type else "personality=unknown"
    style = settings.visual_style_rules
    prompt = (
        f"Interior redesign, {persona_part}, intensity={intensity.value}. "
        f"Use these style rules: {style}. Keep room geometry realistic."
    )
    if extra_instruction:
        prompt += f" Extra task: {extra_instruction}."
    return prompt


def generate_interior_image(
    input_photo_path: str, personality_type: str | None, intensity: GenerationIntensity
) -> GeneratedImage:
    prompt = _build_generation_prompt(personality_type, intensity)
    output_dir = ensure_dir("storage/generated")
    output_path = output_dir / f"gen_{Path(input_photo_path).stem}_{intensity.value}.jpg"

    if not settings.image_api_url or not settings.image_api_key:
        output_path.write_bytes(Path(input_photo_path).read_bytes())
        return GeneratedImage(output_path=str(output_path), prompt_used=prompt, provider_job_id=None)

    image_b64, mime = _encode_image(input_photo_path)
    payload = {
        "image_base64": image_b64,
        "image_mime": mime,
        "prompt": prompt,
        "strength": intensity.value,
    }
    headers = {"Authorization": f"Bearer {settings.image_api_key}"}
    with httpx.Client(timeout=settings.provider_timeout_seconds) as client:
        response = client.post(settings.image_api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    output_b64 = data.get("output_image_base64")
    if output_b64:
        output_path.write_bytes(base64.b64decode(output_b64))
    else:
        output_path.write_bytes(Path(input_photo_path).read_bytes())
    return GeneratedImage(
        output_path=str(output_path),
        prompt_used=prompt,
        provider_job_id=data.get("job_id"),
    )


def visualize_object_on_wall(input_photo_path: str, object_name: str) -> str:
    prompt = _build_generation_prompt(
        personality_type=None,
        intensity=GenerationIntensity.medium,
        extra_instruction=f"place suitable {object_name} on wall with realistic proportions",
    )
    output_dir = ensure_dir("storage/consultation_generated")
    output_path = output_dir / f"{Path(input_photo_path).stem}_{object_name}.jpg"
    if not settings.image_api_url or not settings.image_api_key:
        output_path.write_bytes(Path(input_photo_path).read_bytes())
        return str(output_path)

    image_b64, mime = _encode_image(input_photo_path)
    payload = {
        "image_base64": image_b64,
        "image_mime": mime,
        "prompt": prompt,
        "strength": "medium",
    }
    headers = {"Authorization": f"Bearer {settings.image_api_key}"}
    with httpx.Client(timeout=settings.provider_timeout_seconds) as client:
        response = client.post(settings.image_api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    if data.get("output_image_base64"):
        output_path.write_bytes(base64.b64decode(data["output_image_base64"]))
    else:
        output_path.write_bytes(Path(input_photo_path).read_bytes())
    return str(output_path)


def ask_consultant(question: str, image_path: str | None = None, personality_type: str | None = None) -> str:
    rag = RAGService()
    snippets = rag.search(question)
    context = "\n".join(f"- {s}" for s in snippets) if snippets else "Нет релевантного контекста."

    if not settings.llm_api_url or not settings.llm_api_key:
        prefix = f"С учетом психотипа {personality_type}. " if personality_type else ""
        image_note = " Фото проанализировано." if image_path else ""
        return (
            f"{prefix}Рекомендация: {question}.{image_note}\n"
            f"Контекст базы знаний:\n{context}"
        )

    payload = {
        "system_prompt": settings.consultant_system_prompt_default,
        "question": question,
        "personality_type": personality_type,
        "knowledge_context": snippets,
        "response_style": "professional-friendly",
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    with httpx.Client(timeout=settings.provider_timeout_seconds) as client:
        response = client.post(settings.llm_api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    return data.get("answer", "Не удалось получить ответ от LLM-провайдера.")
