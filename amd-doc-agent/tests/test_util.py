import pytest

from src.util import get_deepseek_api_key


def test_get_deepseek_api_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    assert get_deepseek_api_key() == "test-key"


def test_missing_deepseek_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        get_deepseek_api_key()