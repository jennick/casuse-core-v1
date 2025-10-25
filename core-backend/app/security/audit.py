import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

log = logging.getLogger("app.audit")

def audit_event(event: str, user: Optional[str] = None, detail: Optional[Dict[str, Any]] = None, level: str = "INFO"):
    payload = {
        "event": event,
        "user": user or "anonymous",
        "detail": detail or {},
        "ts": datetime.now(timezone.utc).isoformat()
    }
    msg = json.dumps(payload, ensure_ascii=False)
    if level == "ERROR":
        log.error(msg)
    elif level == "WARNING":
        log.warning(msg)
    else:
        log.info(msg)
