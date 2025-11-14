"""Local Agent-to-Agent (A2A) bridge between CrewAI and ADK agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from agents.crewai_jd_extractor import CrewAIJDExtractorWorkflow


@dataclass
class LocalA2ABridge:
    """Facilitates A2A-style communication without a remote server."""

    workflow: CrewAIJDExtractorWorkflow
    transport: str = field(default="in-process")

    def request_job_payload(self, *, job_url: str, context_id: str) -> Dict[str, Any]:
        """Send a job extraction task to the CrewAI workflow and return transcript."""
        task_id = f"a2a-{uuid4()}"
        request_packet = {
            "task_id": task_id,
            "context_id": context_id,
            "protocol": "A2A",
            "transport": self.transport,
            "payload": {"job_url": job_url},
            "requested_at": datetime.utcnow().isoformat(),
        }

        result = self.workflow.extract_job_data(job_url)

        response_packet = {
            "task_id": task_id,
            "context_id": context_id,
            "protocol": "A2A",
            "transport": self.transport,
            "payload": result,
            "completed_at": datetime.utcnow().isoformat(),
            "producer": "CrewAI",
            "consumer": "ADK",
        }
        return {"request": request_packet, "response": response_packet}
