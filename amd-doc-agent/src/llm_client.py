from langchain_openai import ChatOpenAI

from src.util import get_deepseek_api_key

DEEPSEEK_TIMEOUT_SECONDS = 12.0
DEEPSEEK_MAX_RETRIES = 1


def build_deepseek_llm(*, http_client=None) -> ChatOpenAI:
    options = {
        "model": "deepseek-chat",
        "api_key": get_deepseek_api_key(),
        "base_url": "https://api.deepseek.com",
        "temperature": 0,
        "timeout": 12.0,
        "max_retries": 1
    }
    
    if http_client is not None:
        options["http_client"] = http_client
        
    return ChatOpenAI(**options)