"""AdapterFactory — create LLM adapters by backend name.

Uses lazy imports so that missing openai/anthropic packages do not
break ``import ccp``. Import errors are deferred to
``AdapterFactory.create('openai')`` only.
"""

from ccp.integration.llm_adapter import LLMAdapter


class AdapterFactory:
    """Factory for creating LLM adapter instances by backend name."""

    @staticmethod
    def create(backend: str = "mock", **kwargs) -> LLMAdapter:
        """Create and return an LLMAdapter for the given backend.

        Args:
            backend: One of 'mock', 'openai', 'anthropic'.
            **kwargs: Passed directly to the adapter constructor.

        Returns:
            An LLMAdapter instance.

        Raises:
            ValueError: If an unknown backend is requested.
            ImportError: If the required package for the backend is not installed.
        """
        if backend == "mock":
            from ccp.integration.adapters.mock import MockAdapter
            return MockAdapter(**kwargs)
        if backend == "openai":
            from ccp.integration.adapters.openai_adapter import OpenAIAdapter
            return OpenAIAdapter(**kwargs)
        if backend == "anthropic":
            from ccp.integration.adapters.anthropic_adapter import AnthropicAdapter
            return AnthropicAdapter(**kwargs)
        raise ValueError(
            f"Unknown backend: {backend!r}. Choose one of: mock, openai, anthropic"
        )


__all__ = ["AdapterFactory"]
