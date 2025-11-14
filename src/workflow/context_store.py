"""Shared workflow context storage utilities.

This module provides a light-weight context store that persists the
intermediate artifacts produced by the resume optimization workflow so
that other frameworks (CrewAI, ADK, etc.) can reuse them easily.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WorkflowContextModel(BaseModel):
    """Structured snapshot of a workflow execution."""

    context_id: str
    job_url: str
    profile_id: str
    job_data: Optional[Dict[str, Any]] = None
    profile_data: Optional[Dict[str, Any]] = None
    aligned_data: Optional[Dict[str, Any]] = None
    optimized_data: Optional[Dict[str, Any]] = None
    latex_file_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowContextStore:
    """Persists and retrieves workflow contexts on disk."""

    def __init__(self, base_dir: str = "data/workflow_context") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Context lifecycle helpers
    # ------------------------------------------------------------------
    def create_context(self, job_url: str, profile_id: str) -> WorkflowContextModel:
        """Create a new context skeleton for a workflow run."""
        context = WorkflowContextModel(
            context_id=str(uuid.uuid4()),
            job_url=job_url,
            profile_id=profile_id,
            metadata={},
        )
        self._write(context)
        return context

    def load_context(self, context_id: str) -> WorkflowContextModel:
        """Load an existing context from disk."""
        path = self._path(context_id)
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return WorkflowContextModel(**raw)

    def update_context(self, context_id: str, **fields: Any) -> WorkflowContextModel:
        """Update a context with the provided fields and persist it."""
        context = self.load_context(context_id)
        updates = {k: v for k, v in fields.items() if v is not None}
        for key, value in updates.items():
            if key == "metadata" and isinstance(value, dict):
                context.metadata.update(value)
            elif hasattr(context, key):
                setattr(context, key, value)
        self._write(context)
        return context

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _path(self, context_id: str) -> Path:
        return self.base_dir / f"{context_id}.json"

    def _write(self, context: WorkflowContextModel) -> None:
        path = self._path(context.context_id)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(context.model_dump(), handle, indent=2)


__all__ = ["WorkflowContextModel", "WorkflowContextStore"]
