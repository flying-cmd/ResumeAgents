import os
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from openai import OpenAI

load_dotenv()

DASHSCOPE_PROVIDER_ALIASES = {"dashscope", "qwen", "tongyi"}
DEEPSEEK_PROVIDER_ALIASES = {"deepseek"}
OPENAI_PROVIDER_ALIASES = {"openai"}


def _normalize_openai_messages(input_data: Any) -> List[Dict[str, str]]:
    """Transform different message formats into OpenAI-compatible messages."""
    if isinstance(input_data, str):
        return [{"role": "user", "content": input_data}]

    if isinstance(input_data, list):
        normalized: List[Dict[str, str]] = []

        for item in input_data:
            if isinstance(item, dict) and "role" in item and "content" in item:
                normalized.append({"role": str(item["role"]), "content": str(item["content"])})
                continue

            msg_type = getattr(item, "type", None)
            msg_content = getattr(item, "content", None)
            if msg_type is not None and msg_content is not None:
                role_map = {
                    "human": "user",
                    "ai": "assistant",
                    "system": "system",
                    "tool": "tool",
                }
                normalized.append({"role": role_map.get(str(msg_type), "user"), "content": str(msg_content)})
                continue

            normalized.append({"role": "user", "content": str(item)})

        return normalized

    return [{"role": "user", "content": str(input_data)}]


class OpenAIChatModel:
    """Make an OpenAI-compatible client behave like a LangChain chat model."""

    def __init__(self, client: OpenAI, model_name: str, temperature: float = 0):
        self._client = client
        self._model_name = model_name
        self._temperature = temperature

    def invoke(self, input_data: Any, **kwargs: Any) -> AIMessage:
        messages = _normalize_openai_messages(input_data)
        temperature = kwargs.get("temperature", self._temperature)

        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            temperature=temperature,
        )

        content = ""
        if response and getattr(response, "choices", None):
            content = response.choices[0].message.content or ""

        return AIMessage(content=content)


def _is_truthy(value: str | None, default: bool = False) -> bool:
    """Interpret common string boolean values."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_provider_and_model() -> Tuple[str, str]:
    """
    Resolve the configured provider and model name.

    Supports both of these styles:
    1. Provider + model split:
       LLM_PROVIDER=dashscope
       DASHSCOPE_MODEL=qwen-max
    2. Model name in LLM_PROVIDER:
       LLM_PROVIDER=qwen3.5-flash
    """
    raw_provider = os.getenv("LLM_PROVIDER", "dashscope").strip()
    provider = raw_provider.lower()

    if provider in DASHSCOPE_PROVIDER_ALIASES:
        return "dashscope", os.getenv("DASHSCOPE_MODEL", "qwen-max")
    if provider.startswith("qwen"):
        return "dashscope", raw_provider

    if provider in DEEPSEEK_PROVIDER_ALIASES:
        return "deepseek", os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    if provider.startswith("deepseek"):
        return "deepseek", raw_provider

    if provider in OPENAI_PROVIDER_ALIASES:
        return "openai", os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if provider.startswith("gpt-") or provider.startswith("o1") or provider.startswith("o3") or provider.startswith("o4"):
        return "openai", raw_provider

    raise ValueError(
        "Unsupported LLM_PROVIDER: "
        f"{raw_provider}. Use a provider name like 'dashscope', 'deepseek', or 'openai', "
        "or set it directly to a model name like 'qwen-max', 'deepseek-chat', or 'gpt-4o-mini'."
    )


def get_llm():
    """
    Factory function for the configured LLM instance.

    Supported configurations:
    - DashScope / Qwen
    - DeepSeek (OpenAI-compatible API)
    - OpenAI
    """
    provider, model_name = _resolve_provider_and_model()

    if provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        temperature = float(os.getenv("DASHSCOPE_TEMPERATURE", "0"))
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in .env")

        # Alibaba's current docs recommend the OpenAI-compatible endpoint for Qwen 3.5
        # models, because the native DashScope text-generation route can return `url error`.
        # This app only relies on simple chat completion behavior, so compatible mode is
        # the safest default for DashScope-backed text models.
        use_compatible_mode = _is_truthy(os.getenv("DASHSCOPE_USE_COMPATIBLE_MODE"), default=True)
        if use_compatible_mode:
            base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            return OpenAIChatModel(client=client, model_name=model_name, temperature=temperature)

        from langchain_community.chat_models.tongyi import ChatTongyi

        return ChatTongyi(
            dashscope_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
        )

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0"))

        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in .env")

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        return OpenAIChatModel(client=client, model_name=model_name, temperature=temperature)

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0"))

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        client = OpenAI(
            api_key=api_key,
            base_url=base_url or None,
        )
        return OpenAIChatModel(client=client, model_name=model_name, temperature=temperature)

    raise ValueError(f"Unsupported LLM provider after resolution: {provider}")
