import redis
from fastapi.testclient import TestClient

import main


def test_ask_returns_cached_answer(monkeypatch):
    # Replace real dependencies with lightweight test substitutes.
    monkeypatch.setitem(
        main.app.dependency_overrides,
        main.get_redis_client,
        lambda: None
    )

    # Simulate an existing cached response.
    monkeypatch.setattr(
        main,
        "get_cache",
        lambda client, question: {
            "answer": "This is a test answer.",
            "question": question,
            "sources": ["test_document.pdf"],
        },
    )

    with TestClient(main.app) as client:
        response = client.post(
            "/ask",
            json={"question": "What is Bootgen?"},
        )

        assert response.status_code == 200
        assert response.json()["answer"] == "This is a test answer."
        assert response.json()["sources"] == ["test_document.pdf"]

def test_ask_succeeds_when_redis_unavailable(monkeypatch):
    # Replace external dependencies with test substitutes.
    monkeypatch.setitem(
        main.app.dependency_overrides,
        main.get_redis_client,
        lambda: None
    )
    monkeypatch.setattr(
        main,
        "get_rag_components",
        lambda: (None, [], None)
    )

    # Simulate Redis connection failures.
    def redis_unavailable(*args, **kwargs):
        raise redis.exceptions.ConnectionError(
            "Redis is unavailable"
        )

    monkeypatch.setattr(main, "get_cache", redis_unavailable)
    monkeypatch.setattr(
        main,
        "retrieve_multilingual",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        main,
        "ask_with_context",
        lambda chain, question, docs: "Mock answer",
    )
    monkeypatch.setattr(main, "set_cache", redis_unavailable)

    with TestClient(main.app) as client:
        response = client.post(
            "/ask",
            json={"question": "What is Bootgen?"},
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Mock answer"
    assert response.json()["question"] == "What is Bootgen?"
    

def test_ask_returns_safe_error_when_rag_fails(monkeypatch):
    # Override the real dependencies.
    monkeypatch.setitem(
        main.app.dependency_overrides,
        main.get_redis_client,
        lambda: None
    )
    monkeypatch.setattr(
        main,
        "get_rag_components",
        lambda: (None, [], None)
    )

    # Simulate a cache miss.
    monkeypatch.setattr(
        main,
        "get_cache",
        lambda client, question: None,
    )

    # Simulate an unexpected failure during answer generation.
    def fail_to_answer(chain, question, docs):
        raise RuntimeError("Internal implementation details")

    monkeypatch.setattr(main, "retrieve_multilingual", lambda *a, **kw: [])
    monkeypatch.setattr(main, "ask_with_context", fail_to_answer)

    with TestClient(main.app) as client:
        response = client.post(
            "/ask",
            json={"question": "What is Bootgen?"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert "Internal implementation details" not in response.text


def test_health_ready_returns_503_when_rag_fails(monkeypatch):
    def fail_to_initialize():
        raise RuntimeError("Vector store unavailable")

    monkeypatch.setattr(
        main,
        "get_rag_components",
        fail_to_initialize,
    )

    with TestClient(main.app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "Service not ready"
    assert "Vector store unavailable" not in response.text
