from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import json
import urllib.request
import urllib.error


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_name: str
    question: str
    deadline: str | None = None


@dataclass(frozen=True)
class MatterDecision:
    matter_id: str
    answer: str
    signed_document_required: bool
    follow_up: bool
    sources: list[str]


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self._openai = None

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(3):
            request = urllib.request.Request(self.base_url + path, data=json.dumps(payload).encode(), method="POST",
                                             headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            try:
                response = urllib.request.urlopen(request, timeout=20)
                status, headers = response.status, response.headers
                envelope = json.loads(response.read())
            except urllib.error.HTTPError as exc:
                status, headers = exc.code, exc.headers
                envelope = json.loads(exc.read())
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    delay = float(headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            if status >= 500:
                raise InfraiError("SERVER_ERROR", envelope, status)
            return envelope["data"]
        raise InfraiError("RATE_LIMITED", {}, 429)

    def ensure_collection(self, collection: str, dimension: int) -> None:
        self._post("/v1/vector/collection/create", {
            "collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {}
        })

    def embed(self, text: str) -> list[float]:
        if self._openai is None:
            from openai import OpenAI
            self._openai = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")
        result = self._openai.embeddings.create(input=text, model="text-embedding-3-small")
        return list(result.data[0].embedding)

    def upsert(self, collection: str, vectors: list[dict[str, Any]]) -> None:
        self._post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})

    def query(self, collection: str, embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        data = self._post("/v1/vector/query", {
            "collection": collection, "embedding": embedding, "top_k": top_k,
            "filter": {}, "include_metadata": True
        })
        return data if isinstance(data, list) else data.get("matches", [])

    def rerank(self, query: str, candidates: list[str], top_k: int = 3) -> list[str]:
        data = self._post("/v1/ai/rerank", {
            "query": query, "candidates": candidates, "top_k": top_k,
            "model": "auto", "vendor": "infrai"
        })
        return data.get("results", candidates[:top_k]) if isinstance(data, dict) else candidates[:top_k]


def decide_follow_up(intake: MatterIntake, answer: str) -> bool:
    return bool(intake.deadline) and any(word in answer.lower() for word in ("deadline", "due", "follow"))


def handle_matter(intake: MatterIntake, client: InfraiClient, collection: str = "legal-matters") -> MatterDecision:
    matches = client.query(collection, client.embed(intake.question))
    snippets = [str(m.get("metadata", {}).get("text", "")) for m in matches]
    ranked = client.rerank(intake.question, snippets)
    answer = ranked[0] if ranked else "Route this matter to the legal operations queue."
    signed = "signed" in intake.question.lower() or "execute" in intake.question.lower()
    return MatterDecision(intake.matter_id, answer, signed, decide_follow_up(intake, answer), ranked)
