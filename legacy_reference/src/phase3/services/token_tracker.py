import time
from datetime import datetime, date
from threading import Lock
from ..config import settings

class TokenTracker:
    def __init__(self):
        self._lock = Lock()
        self._daily_usage: int = 0
        self._last_reset: date = datetime.now().date()
        self.budget_limit = settings.TOKEN_BUDGET_DAILY
        
    def _check_reset(self) -> None:
        """Reset usage if it's a new day."""
        today = datetime.now().date()
        if today > self._last_reset:
            self._daily_usage = 0
            self._last_reset = today
            
    def record_usage(self, tokens: int) -> None:
        """Add tokens to daily total."""
        with self._lock:
            self._check_reset()
            self._daily_usage += tokens
            
    def check_budget(self, estimated_tokens: int = 0) -> bool:
        """Verify if budget allows usage."""
        with self._lock:
            self._check_reset()
            # If we don't have enough budget for the estimated request
            if self._daily_usage + estimated_tokens > self.budget_limit:
                return False
            return True
            
    def get_usage_stats(self) -> dict:
        """Retrieve current statistics."""
        with self._lock:
            self._check_reset()
            return {
                "daily_usage": self._daily_usage,
                "daily_limit": self.budget_limit,
                "remaining": max(0, self.budget_limit - self._daily_usage),
                "last_reset": self._last_reset.isoformat()
            }

# Singleton instance
tracker = TokenTracker()
