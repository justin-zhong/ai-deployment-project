import httpx
import pytest
from openai import APITimeoutError

from src.llm_client import (
    DEEPSEEK_MAX_RETRIES,
    DEEPSEEK_TIMEOUT_SECONDS,
    build_deepseek_llm,
)


def test_deepseek_client_configuration(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    llm = build_deepseek_llm()

    assert llm.request_timeout == DEEPSEEK_TIMEOUT_SECONDS
    assert llm.max_retries == DEEPSEEK_MAX_RETRIES
    assert llm.model_name == "deepseek-chat"

def test_retries_transient_server_error(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(
                500,
                json={
                    "error": {
                        "message": "Temporary server failure",
                        "type": "server_error",
                        "code": "server_error",
                    }
                },
                request=request,
            )

        # Simulated successful Chat Completions response.
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1700000000,
                "model": "deepseek-chat",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Mock answer",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 2,
                    "total_tokens": 3,
                },
            },
            request=request,
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler)
    ) as http_client:
        llm = build_deepseek_llm(http_client=http_client)
        result = llm.invoke("Say hello.")

    assert attempts == 2
    assert result.content == "Mock answer"

def test_timeout_is_retried_once_then_fails(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        raise httpx.ReadTimeout(
            "Simulated timeout",
            request=request,
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler)
    ) as http_client:
        llm = build_deepseek_llm(http_client=http_client)

        with pytest.raises(APITimeoutError):
            llm.invoke("Say hello.")

    assert attempts == 2