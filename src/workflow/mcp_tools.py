"""Minimal MCP-style tool registry used by the ADK workflow.

This module does not depend on any external MPC server. Instead, it mimics the
Model Context Protocol request/response envelopes so that agents can interact
with tools through a standardised contract while running entirely in-process.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import json
import requests
from pydantic import BaseModel, Field


class MCPToolRequest(BaseModel):
    """Represents a tool invocation in the MCP contract."""

    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    context_id: str


class MCPToolResponse(BaseModel):
    """Normalised response envelope returned by each tool."""

    name: str
    started_at: str
    finished_at: str
    context_id: str
    output: Dict[str, Any]
    telemetry: Dict[str, Any] = Field(default_factory=dict)


@dataclass(slots=True)
class BaseMCPTool:
    """Base class for all lightweight MCP tools used in the workflow."""

    name: str
    description: str

    def invoke(self, request: MCPToolRequest) -> MCPToolResponse:  # pragma: no cover - interface
        raise NotImplementedError


class MCPToolRegistry:
    """Small registry that keeps MCP-style tools discoverable at runtime."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseMCPTool] = {}

    def register(self, tool: BaseMCPTool) -> None:
        self._tools[tool.name] = tool

    def invoke(self, name: str, *, context_id: str, **arguments: Any) -> MCPToolResponse:
        if name not in self._tools:
            raise KeyError(f"MCP tool '{name}' is not registered")

        tool = self._tools[name]
        started_at = datetime.utcnow()
        request = MCPToolRequest(name=name, arguments=arguments, context_id=context_id)
        response = tool.invoke(request)
        return self._normalise_response(
            response=response,
            tool_name=name,
            context_id=context_id,
            fallback_started=started_at,
        )

    def describe(self) -> Dict[str, str]:
        return {name: tool.description for name, tool in self._tools.items()}

    def _normalise_response(
        self,
        *,
        response: Any,
        tool_name: str,
        context_id: str,
        fallback_started: datetime,
    ) -> MCPToolResponse:
        """Coerce arbitrary tool outputs into a MCPToolResponse envelope."""

        if isinstance(response, MCPToolResponse):
            if not response.started_at:
                response.started_at = fallback_started.isoformat()
            if not response.finished_at:
                response.finished_at = datetime.utcnow().isoformat()
            return response

        payload = getattr(response, "output", response)
        telemetry = getattr(response, "telemetry", {"tool": tool_name})
        started_at = getattr(response, "started_at", None) or fallback_started.isoformat()
        finished_at = getattr(response, "finished_at", None) or datetime.utcnow().isoformat()

        if not isinstance(payload, dict):
            payload = {"value": payload}
        if not isinstance(telemetry, dict):
            telemetry = {"tool": tool_name}

        return MCPToolResponse(
            name=tool_name,
            context_id=context_id,
            started_at=started_at,
            finished_at=finished_at,
            output=payload,
            telemetry=telemetry,
        )


class WebFetchTool(BaseMCPTool):
    """Simple HTTP GET tool that surfaces sanitised metadata back to the agent."""

    def __init__(self, timeout: int = 15) -> None:
        super().__init__(
            name="web_fetch",
            description="Fetch raw HTML for a URL and return metadata + truncated content",
        )
        self.timeout = timeout

    def invoke(self, request: MCPToolRequest) -> MCPToolResponse:
        url = request.arguments.get("url")
        if not url:
            raise ValueError("web_fetch requires a URL")

        started = datetime.utcnow()
        try:
            response = requests.get(url, timeout=self.timeout)
            content_preview = response.text[:1000]
            payload = {
                "status_code": response.status_code,
                "content_preview": content_preview,
                "url": url,
            }
        except Exception as exc:  # pragma: no cover - network failures
            payload = {"error": str(exc), "url": url}

        return MCPToolResponse(
            name=self.name,
            context_id=request.context_id,
            started_at=started.isoformat(),
            finished_at=datetime.utcnow().isoformat(),
            output=payload,
            telemetry={"tool": self.name},
        )


class ProfileStoreTool(BaseMCPTool):
    """Loads cached applicant profiles from disk and exposes them via MCP."""

    def __init__(self, profiles_dir: str) -> None:
        super().__init__(
            name="profile_store",
            description="Lookup stored profile JSON payloads by identifier",
        )
        self.profiles_dir = Path(profiles_dir)

    def _resolve_profile_path(self, profile_id: str) -> Optional[Path]:
        if not profile_id:
            return None
        candidates = [
            self.profiles_dir / f"{profile_id}.json",
            self.profiles_dir / profile_id,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def invoke(self, request: MCPToolRequest) -> MCPToolResponse:
        profile_id = request.arguments.get("profile_id")
        path = self._resolve_profile_path(profile_id)
        started = datetime.utcnow()

        if not path:
            payload = {"error": f"Profile '{profile_id}' not found"}
        else:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                payload = {"error": f"Invalid JSON for profile '{profile_id}': {exc}"}

        return MCPToolResponse(
            name=self.name,
            context_id=request.context_id,
            started_at=started.isoformat(),
            finished_at=datetime.utcnow().isoformat(),
            output=payload,
            telemetry={
                "tool": self.name,
                "profile_id": profile_id,
                "path": str(path) if path else None,
            },
        )
