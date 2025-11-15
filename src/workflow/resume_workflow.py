"""ADK-based resume workflow orchestrator with MCP tooling and A2A bridge."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

# Import from installed google-adk package
from google.genai import types
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.apps.app import App
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner

from agents.content_alignment_agent import ContentAlignmentAgent
from agents.ats_optimizer_agent import ATSOptimizerAgent
from agents.latex_formatter_agent import LaTeXFormatterAgent
from agents.profile_rag_agent import ProfileRAGAgent
from agents.jd_extractor_agent import JDExtractorAgent
from agents.crewai_jd_extractor import CrewAIJDExtractorWorkflow
from workflow.context_store import WorkflowContextStore
from workflow.mcp_tools import MCPToolRegistry, WebFetchTool, ProfileStoreTool
from workflow.a2a_bridge import LocalA2ABridge


class WorkflowMonitorEntry(BaseModel):
    stage: str
    status: str
    timestamp: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class WorkflowMonitor:
    """Collects callback-style telemetry for each workflow stage."""

    def __init__(self) -> None:
        self.entries: List[WorkflowMonitorEntry] = []

    def record(self, stage: str, status: str, payload: Dict[str, Any]) -> WorkflowMonitorEntry:
        entry = WorkflowMonitorEntry(
            stage=stage,
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            payload=payload,
        )
        self.entries.append(entry)
        return entry


class WorkflowResult(BaseModel):
    success: bool
    context_id: str
    latex_file_path: Optional[str]
    job_data: Optional[Dict[str, Any]]
    profile_data: Optional[Dict[str, Any]]
    aligned_data: Optional[Dict[str, Any]]
    optimized_data: Optional[Dict[str, Any]]
    execution_time: Dict[str, float] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    monitor_log: List[WorkflowMonitorEntry] = Field(default_factory=list)
    a2a_transcript: Dict[str, Any] = Field(default_factory=dict)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)


class ResumeStageAgent(BaseAgent):
    """Wraps imperative handlers so they can run as ADK agents."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        context_store: WorkflowContextStore,
        monitor: WorkflowMonitor,
        shared_state: Dict[str, Any],
        context_key: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, description=description)
        # Use a private attribute to avoid Pydantic field restrictions on BaseAgent.
        self._handler = handler
        self._context_store = context_store
        self._monitor = monitor
        self._context_key = context_key
        self._shared_state = shared_state

    async def _run_async_impl(self, ctx):  # type: ignore[override]
        shared = self._shared_state
        ctx.session.state["shared_state"] = shared
        start_time = datetime.utcnow()
        try:
            output = self._handler(shared)
            normalised = _normalise_payload(output)
            if self._context_key:
                shared[self._context_key] = normalised
                self._persist_context(shared, {self._context_key: normalised})
            duration = (datetime.utcnow() - start_time).total_seconds()
            shared.setdefault("execution_time", {})[self.name] = duration
            shared.setdefault("step_order", []).append(self.name)
            shared.setdefault("intermediate_results", {})[self.name] = normalised
            self._monitor.record(self.name, "success", {"duration": duration})
            yield self._build_event(ctx, normalised, "success", duration)
        except Exception as exc:
            error_msg = f"{self.name} failed: {exc}"
            shared.setdefault("errors", []).append(error_msg)
            self._monitor.record(self.name, "error", {"message": error_msg})
            yield self._build_event(ctx, {"error": str(exc)}, "error", 0.0)
            raise

    def _build_event(self, ctx, payload: Dict[str, Any], status: str, duration: float) -> Event:
        content = types.Content(
            role=self.name,
            parts=[types.Part(text=json.dumps({"status": status, "payload": payload, "duration": duration}, default=str))],
        )
        return Event(invocation_id=ctx.invocation_id, author=self.name, content=content)

    def _persist_context(self, shared: Dict[str, Any], payload: Dict[str, Any]) -> None:
        context_id = shared.get("context_id")
        if not context_id:
            return
        try:
            self._context_store.update_context(context_id, **payload)
        except Exception as exc:  # pragma: no cover - guard rail
            logging.getLogger(__name__).warning("Context persistence failed: %s", exc)


def _normalise_payload(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _normalise_payload(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_normalise_payload(v) for v in data]
    if isinstance(data, set):
        return sorted(_normalise_payload(v) for v in data)
    return data


class ResumeWorkflow:
    """Primary entry point used by Streamlit app and tests."""

    def __init__(
        self,
        template_path: str = "templates/resume_template.tex",
        output_directory: str = "output",
        rag_database_path: str = "data/profiles",
    ) -> None:
        self.template_path = template_path
        self.output_directory = output_directory
        self.rag_database_path = rag_database_path

        os.makedirs(self.output_directory, exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self.context_store = WorkflowContextStore()
        self.jd_agent = JDExtractorAgent()
        self.rag_agent = ProfileRAGAgent(db_path=self.rag_database_path)
        self.alignment_agent = ContentAlignmentAgent()
        self.ats_agent = ATSOptimizerAgent()
        self.latex_agent = LaTeXFormatterAgent(
            template_path=self.template_path,
            output_directory=self.output_directory,
        )
        self.crewai_workflow = CrewAIJDExtractorWorkflow(verbose=False)

        self.mcp_registry = MCPToolRegistry()
        self.mcp_registry.register(WebFetchTool())
        self.mcp_registry.register(ProfileStoreTool(self.rag_database_path))

    def run_workflow(
        self,
        job_url: str,
        profile_id: str,
        return_intermediate_results: bool = False,
    ) -> WorkflowResult:
        monitor = WorkflowMonitor()
        bridge = LocalA2ABridge(self.crewai_workflow)
        context_entry = self.context_store.create_context(job_url=job_url, profile_id=profile_id)

        shared_state = {
            "job_url": job_url,
            "profile_id": profile_id,
            "context_id": context_entry.context_id,
            "warnings": [],
            "errors": [],
            "execution_time": {},
        }

        runner = self._build_runner(monitor, bridge, shared_state)
        asyncio.run(self._execute_runner(runner, shared_state))

        final_shared = shared_state
        
        # Build intermediate results with expected keys for UI
        intermediate_for_ui = {}
        if return_intermediate_results:
            intermediate_for_ui = {
                "job_data": final_shared.get("job_data"),
                "profile_data": final_shared.get("profile_data"),
                "aligned_data": final_shared.get("aligned_data"),
                "optimized_data": final_shared.get("optimized_data"),
            }
        
        result = WorkflowResult(
            success=len(final_shared.get("errors", [])) == 0,
            context_id=context_entry.context_id,
            latex_file_path=final_shared.get("latex_file_path"),
            job_data=final_shared.get("job_data"),
            profile_data=final_shared.get("profile_data"),
            aligned_data=final_shared.get("aligned_data"),
            optimized_data=final_shared.get("optimized_data"),
            execution_time=final_shared.get("execution_time", {}),
            warnings=final_shared.get("warnings", []),
            errors=final_shared.get("errors", []),
            monitor_log=monitor.entries,
            a2a_transcript=final_shared.get("a2a_transcript", {}),
            intermediate_results=intermediate_for_ui,
        )

        self.context_store.update_context(
            context_entry.context_id,
            final_result=result.model_dump(mode="json"),
        )
        return result

    def _build_runner(
        self,
        monitor: WorkflowMonitor,
        bridge: LocalA2ABridge,
        shared_state: Dict[str, Any],
    ) -> InMemoryRunner:
        stages = [
            ResumeStageAgent(
                name="extract_job_data",
                description="Use CrewAI via A2A to gather job description",
                handler=lambda shared: self._handle_job_extraction(shared, bridge),
                context_store=self.context_store,
                monitor=monitor,
                shared_state=shared_state,
                context_key="job_data",
            ),
            ResumeStageAgent(
                name="retrieve_profile",
                description="Fetch applicant profile via MCP tools and RAG",
                handler=self._handle_profile_retrieval,
                context_store=self.context_store,
                monitor=monitor,
                shared_state=shared_state,
                context_key="profile_data",
            ),
            ResumeStageAgent(
                name="align_content",
                description="Align applicant content with job requirements",
                handler=self._handle_alignment,
                context_store=self.context_store,
                monitor=monitor,
                shared_state=shared_state,
                context_key="aligned_data",
            ),
            ResumeStageAgent(
                name="optimize_ats",
                description="Perform ATS optimisation",
                handler=self._handle_ats,
                context_store=self.context_store,
                monitor=monitor,
                shared_state=shared_state,
                context_key="optimized_data",
            ),
            ResumeStageAgent(
                name="generate_latex",
                description="Render LaTeX resume",
                handler=self._handle_latex,
                context_store=self.context_store,
                monitor=monitor,
                shared_state=shared_state,
                context_key="latex_file_path",
            ),
        ]
        root_agent = SequentialAgent(name="resume_workflow", sub_agents=stages)
        app = App(name="resume_optimizer_adk", root_agent=root_agent)
        return InMemoryRunner(app=app)

    def _handle_job_extraction(self, shared: Dict[str, Any], bridge: LocalA2ABridge) -> Dict[str, Any]:
        context_id = shared["context_id"]
        job_url = shared["job_url"]
        transcript = bridge.request_job_payload(job_url=job_url, context_id=context_id)
        shared["a2a_transcript"] = transcript
        job_payload = transcript.get("response", {}).get("payload", {})
        if job_payload.get("error"):
            job_payload = self.jd_agent.extract_job_data(job_url)
        fetch_meta = self.mcp_registry.invoke("web_fetch", context_id=context_id, url=job_url)
        shared.setdefault("tool_outputs", {})["web_fetch"] = fetch_meta.output
        job_payload.setdefault("metadata", {})["web_fetch"] = fetch_meta.output
        return job_payload

    def _handle_profile_retrieval(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        context_id = shared["context_id"]
        profile_id = shared["profile_id"]
        profile_snapshot = self.mcp_registry.invoke("profile_store", context_id=context_id, profile_id=profile_id)
        shared.setdefault("tool_outputs", {})["profile_store"] = profile_snapshot.output
        job_data = shared.get("job_data") or {}
        
        # Get RAG-enhanced profile data
        profile_data = self.rag_agent.retrieve_relevant_profile(job_data)
        
        # Merge with uploaded profile data if available
        if profile_snapshot.output and not profile_snapshot.output.get("error"):
            uploaded_profile = profile_snapshot.output
            profile_data["raw_profile"] = uploaded_profile
            
            # Ensure critical fields from uploaded resume are used
            for key in ["name", "email", "phone", "skills", "experience", "education", "projects", "summary"]:
                if key in uploaded_profile and uploaded_profile[key]:
                    if key not in profile_data or not profile_data[key]:
                        profile_data[key] = uploaded_profile[key]
        
        self.logger.info(f"Profile retrieval completed. Keys: {list(profile_data.keys())}")
        return profile_data

    def _handle_alignment(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        job_data = shared.get("job_data") or {}
        profile_data = shared.get("profile_data") or {}
        
        aligned = self.alignment_agent.align_content(job_data, profile_data)
        
        # Double-check critical fields are preserved
        for key in ["name", "email", "phone", "skills", "experience", "education", "projects"]:
            if not aligned.get(key) and profile_data.get(key):
                aligned[key] = profile_data[key]
        
        self.logger.info(f"Content alignment completed. Has name: {bool(aligned.get('name'))}, skills count: {len(aligned.get('skills', []))}")
        return aligned

    def _handle_ats(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        aligned = shared.get("aligned_data") or {}
        profile_data = shared.get("profile_data") or {}
        
        # Ensure aligned data has complete profile information before optimization
        for key in ["name", "email", "phone", "summary", "skills", "experience", "education", "projects"]:
            if not aligned.get(key) and profile_data.get(key):
                aligned[key] = profile_data[key]
        
        optimized = self.ats_agent.optimize_resume(aligned)
        
        # Verify critical fields after optimization
        for key in ["name", "email", "phone"]:
            if not optimized.get(key) and aligned.get(key):
                optimized[key] = aligned[key]
        
        self.logger.info(f"ATS optimization completed. Has name: {bool(optimized.get('name'))}, ATS score: {optimized.get('ats_analysis', {}).get('ats_score', 'N/A')}")
        return optimized

    def _handle_latex(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        optimized = shared.get("optimized_data") or {}
        profile_data = shared.get("profile_data") or {}
        aligned_data = shared.get("aligned_data") or {}
        
        # Build complete resume data for LaTeX generation
        # Priority: optimized > aligned > profile (newest wins)
        latex_input = {**profile_data, **aligned_data, **optimized}
        
        # Log what we're sending to LaTeX
        self.logger.info(f"Generating LaTeX. Has name: {bool(latex_input.get('name'))}, email: {bool(latex_input.get('email'))}, skills count: {len(latex_input.get('skills', []))}, experience count: {len(latex_input.get('experience', []))}")
        
        context_id = shared.get("context_id", "resume")
        output_name = f"{context_id}.tex"
        
        # Use the merged latex_input instead of just optimized
        latex_path = self.latex_agent.generate_latex_resume(latex_input, output_filename=output_name)
        shared["latex_file_path"] = latex_path
        return latex_path

    async def _execute_runner(self, runner: InMemoryRunner, shared_state: Dict[str, Any]):
        user_id = "resume-user"
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            state={"shared_state": shared_state},
        )
        payload = types.Content(
            role="user",
            parts=[types.Part(text=json.dumps({"intent": "optimize_resume"}))],
        )
        async for _event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=payload,
        ):
            continue
