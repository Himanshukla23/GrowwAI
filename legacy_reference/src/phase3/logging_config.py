import logging
import json
import sys
from datetime import datetime
from .config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        # Add any extra kwargs passed to logger
        if hasattr(record, "extra_info"):
            log_obj.update(record.extra_info)
            
        return json.dumps(log_obj)

def setup_logging():
    logger = logging.getLogger("phase3")
    
    # Only setup once
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Log to stdout for container environments
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Don't propagate to root logger if we want strict JSON output
    logger.propagate = False
    
    return logger

logger = setup_logging()
