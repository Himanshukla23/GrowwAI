import time
from collections import deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..config import settings

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        # In-memory store: IP -> deque of request timestamps
        self.requests: dict[str, deque[float]] = {}
        
    async def dispatch(self, request: Request, call_next):
        # Only rate limit Phase 3 API paths, ignore health checks
        if not request.url.path.startswith("/phase3/") or request.url.path.endswith("/health"):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Initialize deque for new IPs
        if client_ip not in self.requests:
            self.requests[client_ip] = deque()
            
        req_history = self.requests[client_ip]
        
        # Remove requests older than 1 minute (60 seconds)
        while req_history and req_history[0] < now - 60:
            req_history.popleft()
            
        # Check against limit
        if len(req_history) >= self.rate_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests", 
                    "detail": f"Rate limit exceeded: {self.rate_limit} requests per minute."
                }
            )
            
        # Record request
        req_history.append(now)
        
        return await call_next(request)
