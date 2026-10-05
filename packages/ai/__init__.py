"""AI package — LLM client, guardrails, RAG, embeddings, context assembly, agents.

`ai.agents` is resolved LAZILY (see `__getattr__` below). It used to be imported
eagerly on line 1, which meant a single unimportable agent module took down the
whole AI layer: `import ai` raised, so embeddings, rag, client and guardrails
all stopped being importable too. The hot paths (`ai.prompt_loader.prompts`,
`ai.client.llm`) stay eager and unaffected.
"""

from .embeddings import EmbeddingService, get_embedding_service
from .rag import RAGPipeline, get_rag, ChunkingPipeline
from .context_engine import ContextEngine, NEEDS_MAP, ContextSectionConfig, AGENT_SECTION_CONFIGS
from .prompt_loader import PromptLoader, PromptLoaderError, PromptEntry, prompts
from .client import LLMClient, llm, LLMError, LLMTimeoutError, LLMRateLimitError, LLMProviderUnavailableError
from .guardrails import Guardrails, guardrails
from .observability import AIObservability, observability

__all__ = [
    "EmbeddingService",
    "get_embedding_service",
    "RAGPipeline",
    "get_rag",
    "ChunkingPipeline",
    "ContextEngine",
    "NEEDS_MAP",
    "ContextSectionConfig",
    "AGENT_SECTION_CONFIGS",
    "PromptLoader",
    "PromptLoaderError",
    "PromptEntry",
    "prompts",
    "LLMClient",
    "llm",
    "LLMError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMProviderUnavailableError",
    "Guardrails",
    "guardrails",
    "AIObservability",
    "observability",
    "agents",
]


def __getattr__(name: str):
    """Resolve `ai.agents` on first access (PEP 562).

    Every agent module imports Supabase, httpx and the prompt loader, so pulling
    the sub-package in at `import ai` time coupled the entire AI layer to the
    health of all eleven agent modules. Deferring it means a broken agent now
    fails only the code that actually touches it, and `ai.agents.<x>` keeps
    working for everyone else. `import ai.agents` and `from ai.agents import y`
    are unaffected — they go through the normal submodule machinery.
    """
    if name == "agents":
        import importlib

        module = importlib.import_module(f"{__name__}.agents")
        globals()["agents"] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals()) + ["agents"])
