import os
import redis
from typing import Protocol, Optional
from fastapi import Request, HTTPException, Depends

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_pool = redis.ConnectionPool.from_url(redis_url, decode_responses=True)

class CacheProtocol(Protocol):
    def increment(self, key: str) -> int: ...
    def set_expire(self, key: str, seconds: int) -> None: ...
    def get_value(self, key: str) -> Optional[str]: ...
    def set_value(self, key: str, value: str, seconds: int) -> None: ...

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(connection_pool=redis_pool)

    def increment(self, key: str) -> int:
        try:
            return self.client.incr(key)
        except Exception:
            return 1 

    def set_expire(self, key: str, seconds: int) -> None:
        try:
            self.client.expire(key, seconds)
        except Exception:
            pass

    def get_value(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception:
            return None 

    def set_value(self, key: str, value: str, seconds: int) -> None:
        try:
            self.client.setex(key, seconds, value)
        except Exception:
            pass

def get_cache() -> CacheProtocol:
    return RedisCache()

class IPRateLimiter:
    def __init__(self, requests_per_minute: int = 20):
        self.limit = requests_per_minute

    def __call__(self, request: Request, cache: CacheProtocol = Depends(get_cache)):
        ip = request.headers.get("X-Real-IP") or request.client.host or "127.0.0.1"
        key = f"rate_limit:{ip}"

        current_requests = cache.increment(key)
        if current_requests == 1:
            cache.set_expire(key, 60)

        if current_requests > self.limit:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests - NO BOTS ALLOWED",
                headers={"Retry-After": "60"}
            )