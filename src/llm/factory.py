import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import AIMessage
from openai import OpenAI

load_dotenv()


# Transform input data to OpenAI format
def _normalize_openai_messages(input_data: Any) -> List[Dict[str, str]]:
    # If input is a string
    if isinstance(input_data, str):
        return [{"role": "user", "content": input_data}]

    # If input is a list
    if isinstance(input_data, list):
        normalized: List[Dict[str, str]] = []

        # Loop through each item to normalize
        # item is a LangChain message object
        for item in input_data:
            if isinstance(item, dict) and "role" in item and "content" in item:
                normalized.append({"role": str(item["role"]), "content": str(item["content"])})
                continue

            msg_type = getattr(item, "type", None)
            msg_content = getattr(item, "content", None)
            if msg_type is not None and msg_content is not None:
                # LangChain and OpenAI role are different, so we need to map
                role_map = {
                    "human": "user",
                    "ai": "assistant",
                    "system": "system",
                    "tool": "tool",
                }
                normalized.append({"role": role_map.get(str(msg_type), "user"), "content": str(msg_content)})
                continue

            # If the message type is not found in role_map, default to "user"
            normalized.append({"role": "user", "content": str(item)})

        return normalized

    return [{"role": "user", "content": str(input_data)}]

# custom wrapper class to make DeepSeek/OpenAI-compatible client behave like a LangChain chat model
class OpenAIChatModel:
    def __init__(self, client: OpenAI, model_name: str, temperature: float = 0):
        self._client = client
        self._model_name = model_name
        self._temperature = temperature

    def invoke(self, input_data: Any, **kwargs: Any) -> AIMessage:
        # Normalize input data
        messages = _normalize_openai_messages(input_data)

        # Get temperature
        temperature = kwargs.get("temperature", self._temperature)

        # Send request to model
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            temperature=temperature,
        )

        # Parse response
        content = ""
        if response and getattr(response, "choices", None):
            content = response.choices[0].message.content or ""
        
        # Return LangChain style AIMessage
        return AIMessage(content=content)


def get_llm():
    """
    Factory function to get the configured LLM instance.
    Supports 'dashscope' (Qwen) and 'deepseek' (OpenAI-compatible API).
    """
    provider = os.getenv("LLM_PROVIDER", "dashscope").lower()

    if provider == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in .env")
        return ChatTongyi(
            dashscope_api_key=api_key,
            model_name="qwen-max",
            temperature=0,
        )

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0"))

        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in .env")

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        return OpenAIChatModel(client=client, model_name=model_name, temperature=temperature)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
