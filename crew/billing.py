"""Flexprice usage metering: one event per completed work item."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import httpx

BASE = os.getenv("FLEXPRICE_BASE_URL", "https://us.api.flexprice.io/v1")


async def record_usage(work_item: str, project: str = "demo-project", role: str = "sentinel") -> str:
    key = os.getenv("FLEXPRICE_API_KEY")
    if not key:
        return "Flexprice not configured (no FLEXPRICE_API_KEY); usage not recorded."
    body = {
        "event_name": os.getenv("FLEXPRICE_EVENT_NAME", "agent_task_completed"),
        "external_customer_id": os.environ["FLEXPRICE_CUSTOMER_ID"],
        "event_id": str(uuid.uuid4()),
        "source": "studio-crew",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "properties": {"project": project, "work_item": work_item, "role": role},
    }
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(f"{BASE}/events", json=body, headers={"x-api-key": key})
        return f"Flexprice usage event {r.status_code}: {r.text[:200]}"
    except httpx.HTTPError as e:
        return f"Flexprice call failed: {e}"
