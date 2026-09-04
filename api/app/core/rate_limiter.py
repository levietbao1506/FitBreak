import asyncio
import math
import time
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


def get_client_ip(request: Request) -> str:
    """
    Lấy IP thực tế của client, hỗ trợ trường hợp chạy qua Reverse Proxy hoặc Docker container.
    """
    # X-Forwarded-For: <client>, <proxy1>, <proxy2>
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


class SlidingWindowLimiter:
    """
    Bộ quản lý sliding-window in-memory để giới hạn số lượng request theo khung thời gian.
    """
    def __init__(self):
        # Lưu key -> danh sách timestamp các request
        self._records: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()

    async def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        """
        Kiểm tra xem request có được phép hay không.
        Trả về (được phép hay không, số giây cần chờ trước khi thử lại).
        """
        now = time.time()
        window_start = now - window_seconds

        async with self._lock:
            # Dọn dẹp định kỳ mỗi 5 phút để tránh rò rỉ bộ nhớ
            if now - self._last_cleanup > 300:
                self._cleanup(now)
                self._last_cleanup = now

            timestamps = self._records[key]
            # Loại bỏ các timestamp đã nằm ngoài cửa sổ thời gian
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= max_requests:
                oldest_in_window = valid_timestamps[0]
                retry_after = max(1, math.ceil(window_seconds - (now - oldest_in_window)))
                self._records[key] = valid_timestamps
                return False, retry_after

            # Thêm timestamp hiện tại và cho phép đi qua
            valid_timestamps.append(now)
            self._records[key] = valid_timestamps
            return True, 0

    def _cleanup(self, now: float):
        """Xóa các IP không còn hoạt động."""
        keys_to_delete = []
        for key, timestamps in self._records.items():
            valid = [t for t in timestamps if t > (now - 3600)]
            if not valid:
                keys_to_delete.append(key)
            else:
                self._records[key] = valid

        for key in keys_to_delete:
            del self._records[key]


# Instance dùng chung cho toàn bộ app
_limiter = SlidingWindowLimiter()


class RateLimiter:
    """
    FastAPI Dependency để giới hạn rate limit riêng cho từng endpoint cụ thể.
    Ví dụ:
        @app.post("/api/food-suggest", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
    """
    def __init__(self, times: int = 10, seconds: int = 60, scope: Optional[str] = None):
        self.times = times
        self.seconds = seconds
        self.scope = scope

    async def __call__(self, request: Request):
        client_ip = get_client_ip(request)
        scope = self.scope or request.url.path
        key = f"{client_ip}:{scope}"

        allowed, retry_after = await _limiter.is_allowed(key, self.times, self.seconds)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Quá giới hạn yêu cầu ({self.times} lần/{self.seconds}s). Vui lòng thử lại sau {retry_after} giây.",
                headers={"Retry-After": str(retry_after)},
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware giới hạn tần suất request toàn cục cho toàn bộ API.
    Bỏ qua các endpoint tĩnh hoặc tài liệu Swagger/Redoc.
    """
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exempt_paths = {"/docs", "/redoc", "/openapi.json", "/api/health"}

    async def dispatch(self, request: Request, call_next):
        # Bỏ qua các endpoint không cần giới hạn
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        client_ip = get_client_ip(request)
        key = f"global:{client_ip}"

        allowed, retry_after = await _limiter.is_allowed(key, self.max_requests, self.window_seconds)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Quá giới hạn tần suất gọi API. Vui lòng thử lại sau {retry_after} giây.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

