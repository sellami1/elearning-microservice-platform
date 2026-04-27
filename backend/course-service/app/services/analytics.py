from __future__ import annotations

import json
import logging
from urllib import error, request
from uuid import UUID

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def record_course_event(event_path: str, course_id: UUID, token: str) -> bool:
    url = f"{settings.analytics_service_url.rstrip('/')}{event_path}"
    payload = json.dumps({"course_id": str(course_id)}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    analytics_request = request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with request.urlopen(analytics_request, timeout=settings.analytics_request_timeout_seconds) as response:
            response.read()
        return True
    except error.HTTPError as exc:
        logger.warning(
            "Analytics event rejected for course_id=%s event_path=%s status=%s",
            course_id,
            event_path,
            exc.code,
        )
    except error.URLError as exc:
        logger.warning(
            "Analytics service unavailable for course_id=%s event_path=%s error=%s",
            course_id,
            event_path,
            exc.reason,
        )
    except Exception as exc:
        logger.warning(
            "Analytics event failed for course_id=%s event_path=%s error=%s",
            course_id,
            event_path,
            exc,
        )

    return False


def record_course_view(course_id: UUID, token: str) -> bool:
    return record_course_event("/events/view", course_id, token)


def record_course_enroll(course_id: UUID, token: str) -> bool:
    return record_course_event("/events/enroll", course_id, token)