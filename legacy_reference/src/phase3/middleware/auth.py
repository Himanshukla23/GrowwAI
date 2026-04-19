from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..config import settings

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.api_key = settings.API_AUTH_TOKEN
        # If API key is empty, auth is essentially disabled (development mode)
        self.auth_enabled = bool(self.api_key)
        
    async def dispatch(self, request: Request, call_next):
        # If auth is disabled, allow all
        if not self.auth_enabled:
            return await call_next(request)
            
        # Allow open access to non-phase3 paths and health checks
        if not request.url.path.startswith("/phase3/") or request.url.path.endswith("/health"):
            return await call_next(request)
            
        # Check X-API-Key header
        provided_key = request.headers.get("X-API-Key")
        if provided_key != self.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized", 
                    "detail": "Invalid or missing X-API-Key header"
                }
            )
            
        return await call_next(request)
