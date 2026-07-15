"""Embedding service with Ollama nomic-embed-text (default) and OpenAI text-embedding-ada-002 (fallback)."""

import asyncio
import hashlib
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import httpx
from config.core.config import settings
from shared.utils.logger import logger
from shared.utils.retry import CircuitBreaker, CircuitBreakerOpenError


class EmbeddingError(Exception):
    pass


class EmbeddingProviderUnavailableError(EmbeddingError):
    pass


class EmbeddingAllProvidersExhaustedError(EmbeddingError):
    pass


@dataclass
class EmbeddingResult:
    embedding: List[float]
    provider: str
    model: str
    dimensions: int
    duration_ms: float


class EmbeddingService:
    def __init__(
        self,
        ollama_base_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        use_local: Optional[bool] = None,
        model: Optional[str] = None,
        openai_model: Optional[str] = None,
        cache_size: int = 1000,
        cache_ttl: int = 3600,
        batch_concurrency: int = 4,
    ):
        self.ollama_base = ollama_base_url or settings.ollama_base_url
        self.openai_key = openai_api_key or getattr(settings, "openai_api_key", None)
        self.use_local = use_local if use_local is not None else settings.use_local_ai
        self.model = model or "nomic-embed-text"
        self.openai_model = openai_model or "text-embedding-ada-002"

        self.batch_concurrency = batch_concurrency
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max = cache_size
        self._cache_ttl = cache_ttl
        self._stats = {"hits": 0, "misses": 0, "ollama_calls": 0, "openai_calls": 0, "fallbacks": 0}

        self.ollama_timeout = getattr(settings, "ollama_timeout", 30)
        self.openai_timeout = 30

        self.ollama_circuit = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=(httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError),
        )
        self.openai_circuit = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=120,
            expected_exception=(httpx.RequestError, httpx.HTTPStatusError, asyncio.TimeoutError),
        )

    def _cache_key(self, text: str, model: str) -> str:
        raw = f"{text}:{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _check_cache(self, text: str, model: str) -> Optional[List[float]]:
        key = self._cache_key(text, model)
        entry = self._cache.get(key)
        if entry and time.time() - entry["time"] < self._cache_ttl:
            self._stats["hits"] += 1
            return entry["embedding"]
        self._stats["misses"] += 1
        return None

    def _set_cache(self, text: str, model: str, embedding: List[float]):
        if len(self._cache) >= self._cache_max:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k]["time"])
            del self._cache[oldest]
        key = self._cache_key(text, model)
        self._cache[key] = {"embedding": embedding, "time": time.time()}

    def _get_providers(self) -> List[tuple[str, str, Callable]]:
        providers = []
        if self.use_local:
            providers.append(("ollama", self.model, self._call_ollama))
        if self.openai_key:
            providers.append(("openai", self.openai_model, self._call_openai))
        if not providers:
            providers.append(("ollama", self.model, self._call_ollama))
        return providers

    async def generate_embedding(self, text: str, preferred_model: Optional[str] = None) -> List[float]:
        if not text or not text.strip():
            return [0.0] * 768

        model = preferred_model or self.model
        cached = self._check_cache(text, model)
        if cached is not None:
            logger.debug("Embedding cache hit", text_len=len(text), model=model)
            return cached

        providers = self._get_providers()
        last_error: Optional[Exception] = None

        for provider_name, provider_model, provider_fn in providers:
            effective_model = preferred_model if provider_name == "openai" and preferred_model else provider_model
            try:
                start = time.time()
                result = await provider_fn(text, effective_model)
                duration_ms = (time.time() - start) * 1000
                logger.info(
                    "Embedding generated",
                    provider=provider_name,
                    model=effective_model,
                    dims=len(result),
                    duration_ms=round(duration_ms, 1),
                    text_len=len(text),
                )
                self._set_cache(text, effective_model, result)
                return result
            except (EmbeddingProviderUnavailableError, CircuitBreakerOpenError) as e:
                logger.warn("Embedding provider unavailable", provider=provider_name, error=str(e))
                last_error = e
                self._stats["fallbacks"] += 1
            except Exception as e:
                logger.warn("Embedding provider error", provider=provider_name, error=str(e))
                last_error = e
                self._stats["fallbacks"] += 1

        logger.error("All embedding providers exhausted", last_error=str(last_error))
        zero_vec = [0.0] * 768
        self._set_cache(text, model, zero_vec)
        return zero_vec

    async def generate_embeddings(
        self, texts: List[str], preferred_model: Optional[str] = None
    ) -> List[List[float]]:
        if not texts:
            return []

        uncached_indices: List[int] = []
        uncached_texts: List[str] = []
        results: List[Optional[List[float]]] = [None] * len(texts)

        model = preferred_model or self.model
        for i, text in enumerate(texts):
            cached = self._check_cache(text, model)
            if cached is not None:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if not uncached_texts:
            return [r for r in results if r is not None]

        if self.use_local:
            embeddings = await self._ollama_embed_batch(uncached_texts, model)
        elif self.openai_key:
            embeddings = await self._openai_embed_batch(uncached_texts, self.openai_model)
        else:
            embeddings = await self._ollama_embed_batch(uncached_texts, model)

        for idx, emb in zip(uncached_indices, embeddings):
            results[idx] = emb
            self._set_cache(uncached_texts[uncached_indices.index(idx)], model, emb)

        return [r for r in results if r is not None]

    async def _call_ollama(self, text: str, model: str) -> List[float]:
        if self.ollama_circuit.state == "open":
            raise CircuitBreakerOpenError("Ollama circuit breaker is OPEN")
        async with httpx.AsyncClient(timeout=self.ollama_timeout) as client:
            resp = await client.post(
                f"{self.ollama_base}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            if resp.status_code == 404:
                raise EmbeddingProviderUnavailableError(f"Model {model} not found in Ollama")
            resp.raise_for_status()
            self._stats["ollama_calls"] += 1
            return resp.json()["embedding"]

    async def _call_openai(self, text: str, model: str) -> List[float]:
        if self.openai_circuit.state == "open":
            raise CircuitBreakerOpenError("OpenAI circuit breaker is OPEN")
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.openai_timeout) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                json={"input": text, "model": model},
                headers=headers,
            )
            resp.raise_for_status()
            self._stats["openai_calls"] += 1
            return resp.json()["data"][0]["embedding"]

    async def _ollama_embed_batch(self, texts: List[str], model: str) -> List[List[float]]:
        sem = asyncio.Semaphore(self.batch_concurrency)

        async def _single(t: str) -> List[float]:
            async with sem:
                try:
                    return await self._call_ollama(t, model)
                except Exception as e:
                    logger.warn("Batch embedding failed for text", error=str(e), text_len=len(t))
                    return [0.0] * 768

        return await asyncio.gather(*[_single(t) for t in texts])

    async def _openai_embed_batch(self, texts: List[str], model: str) -> List[List[float]]:
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=self.openai_timeout) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    json={"input": texts, "model": model},
                    headers=headers,
                )
                resp.raise_for_status()
                self._stats["openai_calls"] += 1
                data = resp.json()["data"]
                return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]
        except Exception as e:
            logger.error("OpenAI batch embedding failed", error=str(e))
            return [[0.0] * 1536 for _ in texts]

    def clear_cache(self):
        self._cache.clear()

    def invalidate_cache(self, text: Optional[str] = None, model: Optional[str] = None):
        if text and model:
            key = self._cache_key(text, model)
            self._cache.pop(key, None)
        elif text:
            to_delete = [k for k in self._cache if k.startswith(hashlib.sha256(f"{text}:".encode()).hexdigest()[:16])]
            for k in to_delete:
                del self._cache[k]
        else:
            self._cache.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        total = self._stats["hits"] + self._stats["misses"]
        return {
            "cache_hits": self._stats["hits"],
            "cache_misses": self._stats["misses"],
            "cache_hit_rate": round(self._stats["hits"] / total * 100, 1) if total else 0.0,
            "cache_size": len(self._cache),
            "ollama_calls": self._stats["ollama_calls"],
            "openai_calls": self._stats["openai_calls"],
            "fallbacks": self._stats["fallbacks"],
            "default_dimensions": 768,
        }


_embedding_instance: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_instance
    if _embedding_instance is None:
        try:
            _embedding_instance = EmbeddingService()
        except Exception:
            _embedding_instance = EmbeddingService(
                ollama_base_url="http://localhost:11434",
                openai_api_key=None,
                use_local=True,
            )
    return _embedding_instance
