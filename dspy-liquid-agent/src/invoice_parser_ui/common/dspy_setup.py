"""DSPy setup utilities for invoice parser."""

import logging
import os
from typing import Any, Dict, Optional


def setup_dspy(model_config: Optional[Dict[str, Any]] = None) -> Any:
    """Setup DSPy language model based on configuration."""

    # Default configuration
    default_config = {
        "provider": "ollama",
        "model": "llama2:7b",
        "base_url": "http://localhost:11434",
        "temperature": 0.1,
        "max_tokens": 1000,
    }

    # Merge with provided config
    config = {**default_config, **(model_config or {})}

    provider = config.get("provider", "ollama")

    try:
        if provider == "ollama":
            import dspy

            # DSPy uses litellm with Ollama - format: 'ollama_chat/<model>'
            model_name = config["model"]
            if not model_name.startswith("ollama_chat/"):
                model_name = f"ollama_chat/{model_name}"

            base_url = config.get("base_url", "http://localhost:11434")

            # Setup DSPy LM with Ollama via litellm
            lm = dspy.LM(
                model=model_name,
                api_base=base_url,
                api_key="ollama",  # Ollama doesn't require a key, but litellm expects this
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 1000),
            )

            return lm

        elif provider == "gemini":
            import dspy

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")

            # DSPy uses litellm for Gemini - format: 'gemini/<model>'
            model_name = config["model"]
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"

            lm = dspy.LM(
                model=model_name,
                api_key=api_key,
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 1000),
            )
            return lm

        elif provider == "openai":
            import dspy
            from dspy.clients import openai

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            client = openai.OpenAI(model=config["model"], api_key=api_key)
            return dspy.LM(client=client)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    except ImportError as e:
        logging.error(f"Failed to import required client for {provider}: {e}")
        raise
    except Exception as e:
        logging.error(f"Failed to setup DSPy for {provider}: {e}")
        raise
