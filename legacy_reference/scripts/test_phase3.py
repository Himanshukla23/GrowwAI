import sys
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import specific components to test
from src.phase3.services.token_tracker import tracker
from src.phase3.middleware.rate_limiter import RateLimiterMiddleware

def test_token_tracker():
    """Test token budget limits."""
    print("--- Testing Token Tracker ---")
    
    # Store old budget
    old_limit = tracker.budget_limit
    
    # Set artificial small budget
    tracker.budget_limit = 5000
    tracker._daily_usage = 0
    
    # Add usage
    tracker.record_usage(2000)
    print(f"Usage after 2000: {tracker.get_usage_stats()}")
    assert tracker.check_budget(1000) is True, "Budget should allow 1000 more"
    
    # Exhaust budget
    tracker.record_usage(3000)
    print(f"Usage after full exhaustion: {tracker.get_usage_stats()}")
    assert tracker.check_budget(500) is False, "Budget should reject if exhausted"
    
    # Restore
    tracker.budget_limit = old_limit
    print("✓ Token tracker test passed\n")

if __name__ == "__main__":
    try:
        test_token_tracker()
        print("All manual mock tests passed!")
        print("Note: To fully test Phase 3, run the FastAPI server and hit the /phase3/ endpoints or run pytest if configured.")
    except AssertionError as e:
        print(f"Test failed: {e}")
