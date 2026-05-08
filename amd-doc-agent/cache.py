import redis
import json
import os

def normalize_question(question: str) -> str:
    return question.lower().strip()

def get_cache(r: redis.Redis, question: str):
    cached_question =r.get(normalize_question(question))

    if cached_question:
        print("Cache Hit!")
        return json.loads(cached_question)

    return None

def set_cache(r: redis.Redis, question: str, response: dict, ttl: int = 3600):
    r.setex(normalize_question(question), ttl, json.dumps(response))