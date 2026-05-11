# llm_runner/model_clients.py
"""
One client class per LLM provider, all using httpx for direct HTTP calls.
No vendor SDKs required — only httpx (already in requirements.txt).

Supported:
  ClaudeClient   — claude-sonnet-4-5        via api.anthropic.com
  GeminiClient   — gemini-2.5-flash          via generativelanguage.googleapis.com
  ChatGPTClient  — gpt-4.1                  via api.openai.com
  DeepSeekClient — deepseek-chat            via api.deepseek.com (OpenAI-compatible)
  MistralClient  — mistral-large-latest     via api.mistral.ai  (OpenAI-compatible)
"""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx

# ── Shared system prompt ──────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are an expert in Bayesian statistics and probability theory. "
    "Solve problems step by step, showing all working. "
    "Always end your response with your final answer on its own line "
    "in the format: ANSWER: <value1>, <value2>, ..."
)

_MAX_TOKENS  = 1024
_TIMEOUT     = 60.0   # seconds per request
_SLEEP_S     = 1.0    # seconds between consecutive requests
_RETRY_WAITS        = [5, 15, 30]          # seconds to wait before attempts 2, 3, then give up
_GEMINI_RETRY_WAITS = [10, 20, 40, 80, 160]  # 5 retries: exponential from 10s (429 backoff)
_GEMINI_SLEEP_S     = 3.0                # default inter-request delay for Gemini; override via --delay

# HTTP status codes that should NOT be retried (client errors)
_NO_RETRY_STATUSES = {400, 401, 403, 404}

# Raised when Gemini daily quota (RPD) is exhausted — not retryable
class GeminiQuotaExhausted(RuntimeError):
    pass


def _gemini_429_body(exc: Exception) -> str:
    """Extract response body from a Gemini 429 HTTPStatusError, or ''."""
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
        try:
            return exc.response.text
        except Exception:
            return ""
    return ""


def _is_gemini_quota_exhausted(exc: Exception) -> bool:
    """True when Gemini signals daily RPD quota gone (not an RPM rate limit)."""
    body = _gemini_429_body(exc)
    if not body:
        return False
    body_lower = body.lower()
    # RPM messages contain "per-minute" or "per minute"
    if "per-minute" in body_lower or "per minute" in body_lower:
        return False
    # RPD messages: RESOURCE_EXHAUSTED without per-minute wording
    return "resource_exhausted" in body_lower or "quota" in body_lower


def _should_retry(exc: Exception) -> bool:
    """Return True if this exception is a retryable error."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code not in _NO_RETRY_STATUSES
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)):
        return True
    return False


def _call_with_retry(
    model_family: str,
    task_id: str,
    request_fn,          # callable() -> httpx.Response
    retry_waits=None,    # override per-client; defaults to _RETRY_WAITS
) -> httpx.Response:
    """Call request_fn with exponential backoff. Max attempts = len(retry_waits) + 1."""
    if retry_waits is None:
        retry_waits = _RETRY_WAITS
    max_attempts = len(retry_waits) + 1
    last_exc: Exception = RuntimeError("unreachable")
    for attempt in range(1, max_attempts + 1):
        try:
            resp = request_fn()
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            # Gemini daily quota exhausted — stop immediately, no point retrying
            if _is_gemini_quota_exhausted(exc):
                raise GeminiQuotaExhausted(
                    "GEMINI_QUOTA_EXHAUSTED: daily RPD limit hit. "
                    "Quota resets at midnight Pacific. Resume tomorrow."
                ) from exc
            if attempt == max_attempts or not _should_retry(exc):
                raise
            wait = retry_waits[attempt - 1]
            body_snippet = _gemini_429_body(exc)[:120]
            extra = f" | body: {body_snippet}" if body_snippet else ""
            print(f"  [RETRY {attempt}/{max_attempts - 1}] {model_family} | {task_id} — waiting {wait}s ({exc}){extra}")
            time.sleep(wait)
    raise last_exc


# ── Base class ────────────────────────────────────────────────────────────────

class BaseModelClient(ABC):
    """Common interface for all LLM clients."""

    model: str       = ""
    model_family: str = ""

    def _empty_result(self, task_id: str, error: str) -> Dict[str, Any]:
        return {
            "model":        self.model,
            "model_family": self.model_family,
            "task_id":      task_id,
            "raw_response": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms":   0.0,
            "error":        error,
        }

    @abstractmethod
    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        ...


# ── Claude ────────────────────────────────────────────────────────────────────

class ClaudeClient(BaseModelClient):
    model        = "claude-sonnet-4-5"
    model_family = "claude"

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")

    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        print(f"  Querying claude on {task_id}...")
        if not self._api_key:
            return self._empty_result(task_id, "ANTHROPIC_API_KEY not set")

        payload = {
            "model":      self.model,
            "max_tokens": _MAX_TOKENS,
            "system":     _SYSTEM_PROMPT,
            "messages":   [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key":         self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        }
        t0 = time.monotonic()
        try:
            resp = _call_with_retry(
                self.model_family, task_id,
                lambda: httpx.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload, headers=headers, timeout=_TIMEOUT,
                ),
            )
            data = resp.json()
            latency_ms = (time.monotonic() - t0) * 1000
            raw = data["content"][0]["text"]
            usage = data.get("usage", {})
            time.sleep(_SLEEP_S)
            return {
                "model":         self.model,
                "model_family":  self.model_family,
                "task_id":       task_id,
                "raw_response":  raw,
                "input_tokens":  usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "latency_ms":    latency_ms,
                "error":         None,
            }
        except Exception as exc:
            time.sleep(_SLEEP_S)
            return self._empty_result(task_id, str(exc))


# ── Gemini ────────────────────────────────────────────────────────────────────

class GeminiClient(BaseModelClient):
    model        = "gemini-2.5-flash"
    model_family = "gemini"

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
        self.delay: float = _GEMINI_SLEEP_S  # inter-request delay; override via runner --delay

    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        print(f"  Querying gemini on {task_id}...")
        if not self._api_key:
            return self._empty_result(task_id, "GEMINI_API_KEY not set")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self._api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 4096,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        t0 = time.monotonic()
        try:
            resp = _call_with_retry(
                self.model_family, task_id,
                lambda: httpx.post(url, json=payload, timeout=_TIMEOUT),
                retry_waits=_GEMINI_RETRY_WAITS,
            )
            data = resp.json()
            latency_ms = (time.monotonic() - t0) * 1000
            raw = (
                data["candidates"][0]["content"]["parts"][0]["text"]
                if data.get("candidates") else ""
            )
            usage = data.get("usageMetadata", {})
            time.sleep(self.delay)
            return {
                "model":         self.model,
                "model_family":  self.model_family,
                "task_id":       task_id,
                "raw_response":  raw,
                "input_tokens":  usage.get("promptTokenCount", 0),
                "output_tokens": usage.get("candidatesTokenCount", 0),
                "latency_ms":    latency_ms,
                "error":         None,
            }
        except GeminiQuotaExhausted as exc:
            # Daily quota gone — propagate up so the runner can stop cleanly
            time.sleep(self.delay)
            raise
        except Exception as exc:
            # Include response body in error message when available
            body = _gemini_429_body(exc)
            err_msg = str(exc)
            if body:
                err_msg = f"{err_msg} | body: {body[:300]}"
            time.sleep(self.delay)
            return self._empty_result(task_id, err_msg)


# ── ChatGPT ───────────────────────────────────────────────────────────────────

class ChatGPTClient(BaseModelClient):
    model        = "gpt-4.1"
    model_family = "chatgpt"

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")

    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        print(f"  Querying chatgpt on {task_id}...")
        if not self._api_key:
            return self._empty_result(task_id, "OPENAI_API_KEY not set")

        payload = {
            "model":      self.model,
            "max_tokens": _MAX_TOKENS,
            "messages": [
                {"role": "system",  "content": _SYSTEM_PROMPT},
                {"role": "user",    "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type":  "application/json",
        }
        t0 = time.monotonic()
        try:
            resp = _call_with_retry(
                self.model_family, task_id,
                lambda: httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload, headers=headers, timeout=_TIMEOUT,
                ),
            )
            data = resp.json()
            latency_ms = (time.monotonic() - t0) * 1000
            raw = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            time.sleep(_SLEEP_S)
            return {
                "model":         self.model,
                "model_family":  self.model_family,
                "task_id":       task_id,
                "raw_response":  raw,
                "input_tokens":  usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "latency_ms":    latency_ms,
                "error":         None,
            }
        except Exception as exc:
            time.sleep(_SLEEP_S)
            return self._empty_result(task_id, str(exc))


# ── DeepSeek ──────────────────────────────────────────────────────────────────

class DeepSeekClient(BaseModelClient):
    model        = "deepseek-chat"
    model_family = "deepseek"

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.environ.get("DEEPSEEK_API_KEY")

    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        print(f"  Querying deepseek on {task_id}...")
        if not self._api_key:
            return self._empty_result(task_id, "DEEPSEEK_API_KEY not set")

        # OpenAI-compatible endpoint
        payload = {
            "model":      self.model,
            "max_tokens": _MAX_TOKENS,
            "messages": [
                {"role": "system",  "content": _SYSTEM_PROMPT},
                {"role": "user",    "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type":  "application/json",
        }
        t0 = time.monotonic()
        try:
            resp = _call_with_retry(
                self.model_family, task_id,
                lambda: httpx.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    json=payload, headers=headers, timeout=_TIMEOUT,
                ),
            )
            data = resp.json()
            latency_ms = (time.monotonic() - t0) * 1000
            raw = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            time.sleep(_SLEEP_S)
            return {
                "model":         self.model,
                "model_family":  self.model_family,
                "task_id":       task_id,
                "raw_response":  raw,
                "input_tokens":  usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "latency_ms":    latency_ms,
                "error":         None,
            }
        except Exception as exc:
            time.sleep(_SLEEP_S)
            return self._empty_result(task_id, str(exc))


# ── Mistral ───────────────────────────────────────────────────────────────────

class MistralClient(BaseModelClient):
    model        = "mistral-large-latest"
    model_family = "mistral"

    def __init__(self) -> None:
        self._api_key: Optional[str] = os.environ.get("MISTRAL_API_KEY")

    def query(self, prompt: str, task_id: str) -> Dict[str, Any]:
        print(f"  Querying mistral on {task_id}...")
        if not self._api_key:
            return self._empty_result(task_id, "MISTRAL_API_KEY not set")

        # OpenAI-compatible endpoint
        payload = {
            "model":      self.model,
            "max_tokens": _MAX_TOKENS,
            "messages": [
                {"role": "system",  "content": _SYSTEM_PROMPT},
                {"role": "user",    "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type":  "application/json",
        }
        t0 = time.monotonic()
        try:
            resp = _call_with_retry(
                self.model_family, task_id,
                lambda: httpx.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    json=payload, headers=headers, timeout=_TIMEOUT,
                ),
            )
            data = resp.json()
            latency_ms = (time.monotonic() - t0) * 1000
            raw = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            time.sleep(_SLEEP_S)
            return {
                "model":         self.model,
                "model_family":  self.model_family,
                "task_id":       task_id,
                "raw_response":  raw,
                "input_tokens":  usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "latency_ms":    latency_ms,
                "error":         None,
            }
        except Exception as exc:
            time.sleep(_SLEEP_S)
            return self._empty_result(task_id, str(exc))


# ── Factory ───────────────────────────────────────────────────────────────────

_CLIENTS = {
    "claude":   ClaudeClient,
    "gemini":   GeminiClient,
    "chatgpt":  ChatGPTClient,
    "deepseek": DeepSeekClient,
    "mistral":  MistralClient,
}


def get_client(name: str) -> BaseModelClient:
    """Instantiate a client by family name ('claude', 'gemini', 'chatgpt', 'deepseek')."""
    name = name.lower().strip()
    if name not in _CLIENTS:
        raise ValueError(f"Unknown model family '{name}'. Choose from: {list(_CLIENTS)}")
    return _CLIENTS[name]()
