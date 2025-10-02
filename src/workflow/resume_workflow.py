"""
Resume Workflow Orchestration using LangGraph.

This module contains the ResumeWorkflow class that orchestrates all agents
in the multi-agent resume optimization pipeline using LangGraph for
workflow management and state coordination.
"""

import os
import logging
from typing import Dict, Any, Optional, TypedDict, Annotated
from datetime import datetime
import traceback

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from langchain_core.messages import BaseMessage
except ImportError as e:
    print(f"Warning: LangGraph dependencies not available: {e}")
    print("Please install with: pip install langgraph langchain langchain-core")
    # Create mock classes for development
    class StateGraph:
        def __init__(self, state_schema): pass
        def add_node(self, name, func): pass
        def add_edge(self, from_node, to_node): pass
        def set_entry_point(self, node): pass
        def compile(self): return MockCompiledGraph()
    
    class MockCompiledGraph:
        def invoke(self, state): return {}
    
    END = "END"
    def add_messages(x, y): return x + y
    class BaseMessage: pass

# Import our agents
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.jd_extractor_agent import JDExtractorAgent
from agents.profile_rag_agent import ProfileRAGAgent
from agents.content_alignment_agent import ContentAlignmentAgent
from agents.ats_optimizer_agent import ATSOptimizerAgent
from agents.latex_formatter_agent import LaTeXFormatterAgent


class WorkflowState(TypedDict):
    """
    State schema for the resume optimization workflow.
    
    This class defines the shared state that gets passed between
    all agents in the workflow pipeline.
    """
    # Input parameters
    job_url: str
    profile_id: str
    
    # Agent outputs
    job_data: Optional[Dict[str, Any]]
    profile_data: Optional[Dict[str, Any]]
    aligned_data: Optional[Dict[str, Any]]
    optimized_data: Optional[Dict[str, Any]]
    latex_file_path: Optional[str]
    
    # Workflow metadata
    current_step: str
    step_count: int
    errors: list
    warnings: list
    execution_time: Dict[str, float]
    
    # Messages for LangGraph compatibility
    messages: Annotated[list[BaseMessage], add_messages]


class ResumeWorkflow:
    """
    LangGraph-based workflow orchestrator for resume optimization.
    
    This class coordinates the execution of all agents in the proper sequence,
    manages state between agents, handles errors, and provides comprehensive
    logging of the entire process.
    """
    
    def __init__(
        self,
        template_path: str = "templates/resume_template.tex",
        output_directory: str = "output",
        rag_database_path: str = "data/profiles",
        enable_logging: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize the ResumeWorkflow.
        
        Args:
            template_path: Path to LaTeX template file
            output_directory: Directory for output files
            rag_database_path: Path to RAG database
            enable_logging: Whether to enable detailed logging
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.template_path = template_path
        self.output_directory = output_directory
        self.rag_database_path = rag_database_path
        
        # Setup logging
        if enable_logging:
            self._setup_logging(log_level)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self._initialize_agents()
        
        # Build the workflow graph
        self.workflow_graph = self._build_workflow_graph()
        
        self.logger.info("ResumeWorkflow initialized successfully")
    
    def _setup_logging(self, log_level: str) -> None:
        """
        Setup comprehensive logging for the workflow.
        
        Args:
            log_level: Logging level to use
        """
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/resume_workflow_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Log the log file location
        print(f"Workflow logging to: {os.path.abspath(log_file)}")
    
    def _initialize_agents(self) -> None:
        """
        Initialize all agents used in the workflow.
        """
        try:
            self.jd_agent = JDExtractorAgent()
            self.rag_agent = ProfileRAGAgent(db_path=self.rag_database_path)
            self.alignment_agent = ContentAlignmentAgent()
            self.ats_agent = ATSOptimizerAgent()
            self.latex_agent = LaTeXFormatterAgent(
                template_path=self.template_path,
                output_directory=self.output_directory
            )
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def _build_workflow_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow graph.
        
        Returns:
            Compiled LangGraph workflow
        """
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("extract_job_data", self._extract_job_data_node)
        workflow.add_node("retrieve_profile", self._retrieve_profile_node)
        workflow.add_node("align_content", self._align_content_node)
        workflow.add_node("optimize_ats", self._optimize_ats_node)
        workflow.add_node("generate_latex", self._generate_latex_node)
        
        # Define the workflow edges (sequence)
        workflow.set_entry_point("extract_job_data")
        workflow.add_edge("extract_job_data", "retrieve_profile")
        workflow.add_edge("retrieve_profile", "align_content")
        workflow.add_edge("align_content", "optimize_ats")
        workflow.add_edge("optimize_ats", "generate_latex")
        workflow.add_edge("generate_latex", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def _extract_job_data_node(self, state: WorkflowState) -> WorkflowState:
        """
        LangGraph node for job data extraction.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Step 1/5: Extracting job data from URL: {state['job_url']}")
            state["current_step"] = "extract_job_data"
            state["step_count"] = 1
            
            # Extract job data
            job_data = self.jd_agent.extract_job_data(state["job_url"])
            
            if not job_data or job_data.get("error"):
                error_msg = f"Failed to extract job data: {job_data.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            state["job_data"] = job_data
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            state["execution_time"]["extract_job_data"] = execution_time
            
            self.logger.info(f"[SUCCESS] Job data extracted successfully in {execution_time:.2f}s")
            self.logger.info(f"  Job Title: {job_data.get('job_title', 'N/A')}")
            self.logger.info(f"  Company: {job_data.get('company', 'N/A')}")
            self.logger.info(f"  Keywords: {len(job_data.get('keywords', []))} found")
            
        except Exception as e:
            error_msg = f"Error in job data extraction: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            state["errors"].append(error_msg)
        
        return state
    
    def _retrieve_profile_node(self, state: WorkflowState) -> WorkflowState:
        """
        LangGraph node for profile data retrieval.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Step 2/5: Retrieving profile data for ID: {state['profile_id']}")
            state["current_step"] = "retrieve_profile"
            state["step_count"] = 2
            
            # Check if job data is available
            if not state.get("job_data"):
                error_msg = "No job data available for profile retrieval"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            # Retrieve profile data
            profile_data = self.rag_agent.retrieve_relevant_profile(
                state["job_data"], 
                state["profile_id"]
            )
            
            if not profile_data or profile_data.get("error"):
                error_msg = f"Failed to retrieve profile data: {profile_data.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            state["profile_data"] = profile_data
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            state["execution_time"]["retrieve_profile"] = execution_time
            
            self.logger.info(f"[SUCCESS] Profile data retrieved successfully in {execution_time:.2f}s")
            self.logger.info(f"  Profile ID: {profile_data.get('profile_id', 'N/A')}")
            self.logger.info(f"  Relevance Score: {profile_data.get('relevance_score', 'N/A')}")
            
            # Log relevant sections found
            relevant_data = profile_data.get("relevant_data", {})
            if relevant_data:
                sections = list(relevant_data.keys())
                self.logger.info(f"  Relevant Sections: {', '.join(sections)}")
            
        except Exception as e:
            error_msg = f"Error in profile retrieval: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            state["errors"].append(error_msg)
        
        return state
    
    def _align_content_node(self, state: WorkflowState) -> WorkflowState:
        """
        LangGraph node for content alignment.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Step 3/5: Aligning content with job requirements")
            state["current_step"] = "align_content"
            state["step_count"] = 3
            
            # Check if required data is available
            if not state.get("job_data") or not state.get("profile_data"):
                error_msg = "Missing job data or profile data for content alignment"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            # Align content
            aligned_data = self.alignment_agent.align_content(
                state["job_data"],
                state["profile_data"]
            )
            
            if not aligned_data or aligned_data.get("error"):
                error_msg = f"Failed to align content: {aligned_data.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            state["aligned_data"] = aligned_data
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            state["execution_time"]["align_content"] = execution_time
            
            self.logger.info(f"[SUCCESS] Content aligned successfully in {execution_time:.2f}s")
            
            # Log alignment statistics
            alignment_score = aligned_data.get("alignment_analysis", {}).get("overall_score", 0)
            matched_keywords = aligned_data.get("alignment_analysis", {}).get("matched_keywords", [])
            
            self.logger.info(f"  Alignment Score: {alignment_score:.1%}")
            self.logger.info(f"  Matched Keywords: {len(matched_keywords)}")
            
            # Log aligned sections
            aligned_sections = aligned_data.get("aligned_sections", {})
            if aligned_sections:
                sections = list(aligned_sections.keys())
                self.logger.info(f"  Aligned Sections: {', '.join(sections)}")
            
        except Exception as e:
            error_msg = f"Error in content alignment: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            state["errors"].append(error_msg)
        
        return state
    
    def _optimize_ats_node(self, state: WorkflowState) -> WorkflowState:
        """
        LangGraph node for ATS optimization.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Step 4/5: Optimizing for ATS compatibility")
            state["current_step"] = "optimize_ats"
            state["step_count"] = 4
            
            # Check if aligned data is available
            if not state.get("aligned_data"):
                error_msg = "No aligned data available for ATS optimization"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            # Optimize for ATS
            optimized_data = self.ats_agent.optimize_resume(state["aligned_data"])
            
            if not optimized_data or optimized_data.get("error"):
                error_msg = f"Failed to optimize for ATS: {optimized_data.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            state["optimized_data"] = optimized_data
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            state["execution_time"]["optimize_ats"] = execution_time
            
            self.logger.info(f"[SUCCESS] ATS optimization completed in {execution_time:.2f}s")
            
            # Log ATS analysis results
            ats_analysis = optimized_data.get("ats_analysis", {})
            ats_score = ats_analysis.get("ats_score", 0)
            category = ats_analysis.get("category", "Unknown")
            
            self.logger.info(f"  ATS Score: {ats_score}/100 ({category})")
            
            # Log optimization details
            keyword_density = ats_analysis.get("keyword_density", 0)
            section_completeness = ats_analysis.get("section_completeness", 0)
            formatting_score = ats_analysis.get("formatting_score", 0)
            
            self.logger.info(f"  Keyword Density: {keyword_density:.1%}")
            self.logger.info(f"  Section Completeness: {section_completeness:.1%}")
            self.logger.info(f"  Formatting Score: {formatting_score:.1%}")
            
            # Log suggestions and auto-fixes
            suggestions = ats_analysis.get("suggestions", [])
            if suggestions:
                self.logger.info(f"  Suggestions: {len(suggestions)} provided")
                for i, suggestion in enumerate(suggestions[:3], 1):  # Show first 3
                    self.logger.info(f"    {i}. {suggestion}")
            
            auto_fixes = optimized_data.get("auto_fixes_applied", [])
            if auto_fixes:
                self.logger.info(f"  Auto-fixes Applied: {len(auto_fixes)}")
                for fix in auto_fixes[:3]:  # Show first 3
                    self.logger.info(f"    - {fix}")
            
        except Exception as e:
            error_msg = f"Error in ATS optimization: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            state["errors"].append(error_msg)
        
        return state
    
    def _generate_latex_node(self, state: WorkflowState) -> WorkflowState:
        """
        LangGraph node for LaTeX generation.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("Step 5/5: Generating LaTeX resume")
            state["current_step"] = "generate_latex"
            state["step_count"] = 5
            
            # Check if optimized data is available
            if not state.get("optimized_data"):
                error_msg = "No optimized data available for LaTeX generation"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            # Generate custom filename
            profile_id = state["profile_id"]
            job_title = state.get("job_data", {}).get("job_title", "position")
            # Clean job title for filename
            clean_job_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_job_title = clean_job_title.replace(' ', '_').lower()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{profile_id}_{clean_job_title}_{timestamp}.tex"
            
            # Generate LaTeX resume
            latex_file_path = self.latex_agent.generate_latex_resume(
                state["optimized_data"],
                filename
            )
            
            if not latex_file_path or not os.path.exists(latex_file_path):
                error_msg = "Failed to generate LaTeX file"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
            
            state["latex_file_path"] = latex_file_path
            
            # Log success
            execution_time = (datetime.now() - start_time).total_seconds()
            state["execution_time"]["generate_latex"] = execution_time
            
            self.logger.info(f"[SUCCESS] LaTeX resume generated successfully in {execution_time:.2f}s")
            
            # Log file details
            absolute_path = os.path.abspath(latex_file_path)
            file_size = os.path.getsize(latex_file_path)
            
            self.logger.info(f"  File Path: {absolute_path}")
            self.logger.info(f"  File Size: {file_size:,} bytes")
            
            # Validate Overleaf compatibility
            try:
                with open(latex_file_path, 'r', encoding='utf-8') as f:
                    latex_content = f.read()
                
                validation = self.latex_agent.validate_overleaf_compatibility(latex_content)
                
                if validation['is_compatible']:
                    self.logger.info("  [COMPATIBLE] Overleaf compatible")
                else:
                    self.logger.warning("  [WARNING] Potential Overleaf compatibility issues")
                
                if validation['warnings']:
                    for warning in validation['warnings']:
                        self.logger.warning(f"    - {warning}")
                        state["warnings"].append(warning)
                
            except Exception as validation_error:
                warning_msg = f"Could not validate Overleaf compatibility: {validation_error}"
                self.logger.warning(warning_msg)
                state["warnings"].append(warning_msg)
            
        except Exception as e:
            error_msg = f"Error in LaTeX generation: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            state["errors"].append(error_msg)
        
        return state
    
    def run_workflow(
        self, 
        job_url: str, 
        profile_id: str,
        return_intermediate_results: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete resume optimization workflow.
        
        Args:
            job_url: URL of the job description to optimize for
            profile_id: ID of the applicant profile to use
            return_intermediate_results: Whether to include intermediate results
            
        Returns:
            Dictionary containing workflow results and final LaTeX file path
        """
        workflow_start_time = datetime.now()
        
        self.logger.info("=" * 60)
        self.logger.info("STARTING RESUME OPTIMIZATION WORKFLOW")
        self.logger.info("=" * 60)
        self.logger.info(f"Job URL: {job_url}")
        self.logger.info(f"Profile ID: {profile_id}")
        self.logger.info(f"Timestamp: {workflow_start_time}")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            job_url=job_url,
            profile_id=profile_id,
            job_data=None,
            profile_data=None,
            aligned_data=None,
            optimized_data=None,
            latex_file_path=None,
            current_step="initializing",
            step_count=0,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        try:
            # Execute the workflow
            final_state = self.workflow_graph.invoke(initial_state)
            
            # Calculate total execution time
            total_time = (datetime.now() - workflow_start_time).total_seconds()
            final_state["execution_time"]["total"] = total_time
            
            # Log workflow completion
            self.logger.info("=" * 60)
            if final_state["errors"]:
                self.logger.error("WORKFLOW COMPLETED WITH ERRORS")
                self.logger.error(f"Errors encountered: {len(final_state['errors'])}")
                for error in final_state["errors"]:
                    self.logger.error(f"  - {error}")
            else:
                self.logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            
            if final_state["warnings"]:
                self.logger.warning(f"Warnings: {len(final_state['warnings'])}")
                for warning in final_state["warnings"]:
                    self.logger.warning(f"  - {warning}")
            
            self.logger.info(f"Total Execution Time: {total_time:.2f} seconds")
            
            # Log step-by-step timing
            self.logger.info("Step Execution Times:")
            for step, time_taken in final_state["execution_time"].items():
                if step != "total":
                    self.logger.info(f"  {step}: {time_taken:.2f}s")
            
            if final_state["latex_file_path"]:
                self.logger.info(f"Final LaTeX File: {final_state['latex_file_path']}")
                self.logger.info("Ready for Overleaf upload!")
            
            self.logger.info("=" * 60)
            
            # Prepare return data
            result = {
                "success": len(final_state["errors"]) == 0,
                "latex_file_path": final_state["latex_file_path"],
                "errors": final_state["errors"],
                "warnings": final_state["warnings"],
                "execution_time": final_state["execution_time"],
                "workflow_metadata": {
                    "job_url": job_url,
                    "profile_id": profile_id,
                    "total_steps": 5,
                    "completed_steps": final_state["step_count"],
                    "timestamp": workflow_start_time.isoformat()
                }
            }
            
            # Include intermediate results if requested
            if return_intermediate_results:
                result["intermediate_results"] = {
                    "job_data": final_state.get("job_data"),
                    "profile_data": final_state.get("profile_data"),
                    "aligned_data": final_state.get("aligned_data"),
                    "optimized_data": final_state.get("optimized_data")
                }
            
            return result
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return {
                "success": False,
                "latex_file_path": None,
                "errors": [error_msg],
                "warnings": [],
                "execution_time": {"total": (datetime.now() - workflow_start_time).total_seconds()},
                "workflow_metadata": {
                    "job_url": job_url,
                    "profile_id": profile_id,
                    "total_steps": 5,
                    "completed_steps": 0,
                    "timestamp": workflow_start_time.isoformat()
                }
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get the current status and configuration of the workflow.
        
        Returns:
            Dictionary containing workflow status information
        """
        return {
            "workflow_name": "ResumeOptimizationWorkflow",
            "version": "1.0.0",
            "agents": {
                "jd_extractor": "JDExtractorAgent",
                "profile_rag": "ProfileRAGAgent", 
                "content_alignment": "ContentAlignmentAgent",
                "ats_optimizer": "ATSOptimizerAgent",
                "latex_formatter": "LaTeXFormatterAgent"
            },
            "configuration": {
                "template_path": self.template_path,
                "output_directory": self.output_directory,
                "rag_database_path": self.rag_database_path
            },
            "workflow_steps": [
                "extract_job_data",
                "retrieve_profile", 
                "align_content",
                "optimize_ats",
                "generate_latex"
            ]
        }


def main():
    """
    Main function for testing the ResumeWorkflow.
    """
    print("Resume Workflow (LangGraph) Test")
    print("=" * 50)
    
    # Test data
    test_job_url = "https://example.com/job-posting"
    test_profile_id = "test_user_123"
    
    try:
        # Initialize workflow
        print("Initializing workflow...")
        workflow = ResumeWorkflow(
            template_path="templates/resume_template.tex",
            output_directory="output",
            enable_logging=True,
            log_level="INFO"
        )
        
        # Get workflow status
        status = workflow.get_workflow_status()
        print(f"Workflow: {status['workflow_name']} v{status['version']}")
        print(f"Agents: {len(status['agents'])} configured")
        print(f"Steps: {len(status['workflow_steps'])} defined")
        print()
        
        # Note: This is a demonstration - actual execution would require
        # valid job URL and existing profile data
        print("Workflow Configuration:")
        print(f"  Template Path: {status['configuration']['template_path']}")
        print(f"  Output Directory: {status['configuration']['output_directory']}")
        print(f"  RAG Database: {status['configuration']['rag_database_path']}")
        print()
        
        print("Workflow Steps:")
        for i, step in enumerate(status['workflow_steps'], 1):
            print(f"  {i}. {step}")
        print()
        
        print("To run the full workflow:")
        print(f"  result = workflow.run_workflow('{test_job_url}', '{test_profile_id}')")
        print("  print(f'Success: {{result[\"success\"]}}')")
        print("  print(f'LaTeX File: {{result[\"latex_file_path\"]}}')")
        
        print("\nWorkflow initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
