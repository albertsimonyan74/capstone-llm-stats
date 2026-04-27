"""
User Study — parallel 5-model comparison
POST /api/user-study        : submit question → parallel responses from all 5 models
POST /api/user-study/vote   : record user preference
GET  /api/user-study/results: aggregate voting statistics
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

router = APIRouter()

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = DATA_DIR / "user_study_results.json"

SYSTEM_PROMPT = (
    "You are an expert in Bayesian statistics and probability theory. "
    "The user has a question about Bayesian or inferential statistics. "
    "Provide a clear, educational response that: "
    "(1) directly answers the question, "
    "(2) shows the mathematical reasoning with formulas where relevant, "
    "(3) interprets the result in plain language, "
    "(4) states key assumptions and caveats. "
    "Be thorough but accessible to a graduate statistics student."
)

MODEL_COLORS = {
    "claude":   "#00CED1",
    "chatgpt":  "#7FFFD4",
    "gemini":   "#FF6B6B",
    "deepseek": "#4A90D9",
    "mistral":  "#A78BFA",
}

TIMEOUT = 60.0


# ── Schemas ───────────────────────────────────────────────────────────────────
class ModelResponse(BaseModel):
    model_id: str
    model_name: str
    response: str
    latency_ms: float
    error: Optional[str] = None
    supports_vision: bool = True
    color: str = "#8BAFC0"


class StudyResponse(BaseModel):
    session_id: str
    question: str
    responses: list[ModelResponse]
    timestamp: str


class VoteRequest(BaseModel):
    session_id: str
    question: str
    voted_model: str
    reason: Optional[str] = None
    had_image: bool = False


# ── Rate limiter (10 req/hr per IP) ───────────────────────────────────────────
_rate_store: dict[str, list[float]] = defaultdict(list)

def _check_rate(ip: str, limit: int = 10, window: int = 3600) -> bool:
    now = time.time()
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < window]
    if len(_rate_store[ip]) >= limit:
        return False
    _rate_store[ip].append(now)
    return True


# ── Async model callers — httpx REST, no SDK ──────────────────────────────────
async def call_claude(question: str, image_b64: Optional[str], media_type: str) -> ModelResponse:
    start = time.time()
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return ModelResponse(model_id="claude", model_name="Claude Sonnet 4.6",
                             response="", latency_ms=0, error="ANTHROPIC_API_KEY not set",
                             color=MODEL_COLORS["claude"])
    content: list = []
    if image_b64:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": image_b64},
        })
    content.append({"type": "text", "text": question})
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-sonnet-4-6", "max_tokens": 1024,
                      "system": SYSTEM_PROMPT,
                      "messages": [{"role": "user", "content": content}]},
            )
            r.raise_for_status()
            text = r.json()["content"][0]["text"]
        return ModelResponse(model_id="claude", model_name="Claude Sonnet 4.6", response=text,
                             latency_ms=round((time.time() - start) * 1000, 1),
                             color=MODEL_COLORS["claude"])
    except Exception as e:
        return ModelResponse(model_id="claude", model_name="Claude Sonnet 4.6",
                             response="", latency_ms=round((time.time() - start) * 1000, 1),
                             error=str(e)[:200], color=MODEL_COLORS["claude"])


async def call_gpt4(question: str, image_b64: Optional[str], media_type: str) -> ModelResponse:
    start = time.time()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return ModelResponse(model_id="chatgpt", model_name="GPT-4.1",
                             response="", latency_ms=0, error="OPENAI_API_KEY not set",
                             color=MODEL_COLORS["chatgpt"])
    content: list = []
    if image_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{image_b64}"},
        })
    content.append({"type": "text", "text": question})
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "gpt-4.1", "max_tokens": 1024,
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": content}]},
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
        return ModelResponse(model_id="chatgpt", model_name="GPT-4.1", response=text,
                             latency_ms=round((time.time() - start) * 1000, 1),
                             color=MODEL_COLORS["chatgpt"])
    except Exception as e:
        return ModelResponse(model_id="chatgpt", model_name="GPT-4.1",
                             response="", latency_ms=round((time.time() - start) * 1000, 1),
                             error=str(e)[:200], color=MODEL_COLORS["chatgpt"])


async def call_gemini(question: str, image_b64: Optional[str], media_type: str) -> ModelResponse:
    start = time.time()
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return ModelResponse(model_id="gemini", model_name="Gemini 2.5 Flash",
                             response="", latency_ms=0, error="GEMINI_API_KEY not set",
                             color=MODEL_COLORS["gemini"])
    parts: list = []
    if image_b64:
        parts.append({"inline_data": {"mime_type": media_type, "data": image_b64}})
    parts.append({"text": question})
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/gemini-2.5-flash:generateContent?key={key}")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(url, json={
                "contents": [{"parts": parts}],
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig": {"maxOutputTokens": 1024},
            })
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return ModelResponse(model_id="gemini", model_name="Gemini 2.5 Flash", response=text,
                             latency_ms=round((time.time() - start) * 1000, 1),
                             color=MODEL_COLORS["gemini"])
    except Exception as e:
        return ModelResponse(model_id="gemini", model_name="Gemini 2.5 Flash",
                             response="", latency_ms=round((time.time() - start) * 1000, 1),
                             error=str(e)[:200], color=MODEL_COLORS["gemini"])


async def call_deepseek(question: str, image_b64: Optional[str], _media_type: str) -> ModelResponse:
    start = time.time()
    if image_b64:
        return ModelResponse(model_id="deepseek", model_name="DeepSeek-V3",
                             response="", latency_ms=0, error="vision_not_supported",
                             supports_vision=False, color=MODEL_COLORS["deepseek"])
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        return ModelResponse(model_id="deepseek", model_name="DeepSeek-V3",
                             response="", latency_ms=0, error="DEEPSEEK_API_KEY not set",
                             supports_vision=False, color=MODEL_COLORS["deepseek"])
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "max_tokens": 1024,
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": question}]},
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
        return ModelResponse(model_id="deepseek", model_name="DeepSeek-V3", response=text,
                             latency_ms=round((time.time() - start) * 1000, 1),
                             supports_vision=False, color=MODEL_COLORS["deepseek"])
    except Exception as e:
        return ModelResponse(model_id="deepseek", model_name="DeepSeek-V3",
                             response="", latency_ms=round((time.time() - start) * 1000, 1),
                             error=str(e)[:200], supports_vision=False, color=MODEL_COLORS["deepseek"])


async def call_mistral(question: str, image_b64: Optional[str], _media_type: str) -> ModelResponse:
    start = time.time()
    if image_b64:
        return ModelResponse(model_id="mistral", model_name="Mistral Large",
                             response="", latency_ms=0, error="vision_not_supported",
                             supports_vision=False, color=MODEL_COLORS["mistral"])
    key = os.environ.get("MISTRAL_API_KEY", "")
    if not key:
        return ModelResponse(model_id="mistral", model_name="Mistral Large",
                             response="", latency_ms=0, error="MISTRAL_API_KEY not set",
                             supports_vision=False, color=MODEL_COLORS["mistral"])
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "mistral-large-latest", "max_tokens": 1024,
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": question}]},
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
        return ModelResponse(model_id="mistral", model_name="Mistral Large", response=text,
                             latency_ms=round((time.time() - start) * 1000, 1),
                             supports_vision=False, color=MODEL_COLORS["mistral"])
    except Exception as e:
        return ModelResponse(model_id="mistral", model_name="Mistral Large",
                             response="", latency_ms=round((time.time() - start) * 1000, 1),
                             error=str(e)[:200], supports_vision=False, color=MODEL_COLORS["mistral"])


# ── Endpoints ──────────────────────────────────────────────────────────────────
@router.post("/api/user-study", response_model=StudyResponse)
async def submit_question(
    request: Request,
    question: str = Form(...),
    image: Optional[UploadFile] = File(None),
):
    ip = request.client.host if request.client else "unknown"
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="Rate limit: 10 requests/hour per IP")

    q = question.strip()
    if len(q) < 5:
        raise HTTPException(status_code=400, detail="Question too short (min 5 chars)")
    if len(q) > 2000:
        raise HTTPException(status_code=400, detail="Question too long (max 2000 chars)")

    image_b64: Optional[str] = None
    media_type = "image/jpeg"
    if image and image.filename:
        img_bytes = await image.read()
        if len(img_bytes) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 5 MB)")
        ct = image.content_type or "image/jpeg"
        if ct not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
            raise HTTPException(status_code=400, detail=f"Unsupported image type: {ct}")
        media_type = ct
        image_b64 = base64.b64encode(img_bytes).decode()

    results = await asyncio.gather(
        call_claude(q, image_b64, media_type),
        call_gpt4(q, image_b64, media_type),
        call_gemini(q, image_b64, media_type),
        call_deepseek(q, image_b64, media_type),
        call_mistral(q, image_b64, media_type),
        return_exceptions=False,
    )

    return StudyResponse(
        session_id=str(uuid.uuid4())[:8],
        question=q,
        responses=list(results),
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/api/user-study/vote")
async def submit_vote(vote: VoteRequest):
    record = {
        "session_id":  vote.session_id,
        "timestamp":   datetime.utcnow().isoformat(),
        "question":    vote.question[:200],
        "voted_model": vote.voted_model,
        "reason":      vote.reason or "",
        "had_image":   vote.had_image,
    }
    existing: list = []
    if RESULTS_PATH.exists():
        try:
            existing = json.loads(RESULTS_PATH.read_text())
        except Exception:
            existing = []
    existing.append(record)
    RESULTS_PATH.write_text(json.dumps(existing, indent=2))
    return {"status": "recorded", "session_id": vote.session_id}


@router.get("/api/user-study/results")
async def get_study_results():
    if not RESULTS_PATH.exists():
        return {"total_votes": 0, "vote_distribution": {}}
    try:
        records = json.loads(RESULTS_PATH.read_text())
    except Exception:
        return {"total_votes": 0, "vote_distribution": {}}
    dist: dict[str, int] = defaultdict(int)
    for r in records:
        dist[r.get("voted_model", "?")] += 1
    return {
        "total_votes": len(records),
        "vote_distribution": dict(sorted(dist.items(), key=lambda x: -x[1])),
    }
