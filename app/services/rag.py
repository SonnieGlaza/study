from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import settings


@dataclass(frozen=True)
class RagChunk:
    source_title: str
    snippet: str
    score: float


class RagService:
    async def retrieve(self, query: str, limit: int = 5) -> list[RagChunk]:
        if not settings.rag_api_url:
            return []
        payload = {"query": query, "top_k": limit}
        headers = {"Authorization": f"Bearer {settings.rag_api_key}"} if settings.rag_api_key else {}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(settings.rag_api_url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        items = data.get("results", [])
        chunks: list[RagChunk] = []
        for item in items:
            chunks.append(
                RagChunk(
                    source_title=str(item.get("title", "internal-material")),
                    snippet=str(item.get("snippet", "")),
                    score=float(item.get("score", 0.0)),
                )
            )
        return chunks
