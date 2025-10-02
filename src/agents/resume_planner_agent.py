"""
ResumePlannerAgent - Coordinates the overall resume tailoring workflow.

This module contains the ResumePlannerAgent class that orchestrates the
multi-agent system for resume optimization, defining the workflow sequence
and generating task plans for each step in the process.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse


class ResumePlannerAgent:
    """
    Agent for coordinating the overall resume tailoring workflow.
    
    This agent defines the workflow sequence, accepts job description links
    and applicant profile IDs as input, and returns structured task plans
    for the multi-agent resume optimization system.
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize the ResumePlannerAgent.
        
        Args:
            workflow_id: Optional workflow identifier (generates UUID if None)
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.workflow_steps = [
            "JDExtractorAgent",
            "ProfileRAGAgent", 
            "ContentAlignmentAgent",
            "ATSOptimizerAgent",
            "LaTeXFormatterAgent"
        ]
        self.created_at = datetime.now().isoformat()
    
    def validate_inputs(self, job_url: str, profile_id: str) -> Dict[str, Any]:
        """
        Validate input parameters for workflow planning.
        
        Args:
            job_url: URL of the job description page
            profile_id: Unique identifier for the applicant profile
            
        Returns:
            Dictionary containing validation results
            
        Raises:
            ValueError: If inputs are invalid
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate job URL
        if not job_url or not isinstance(job_url, str):
            validation_result["valid"] = False
            validation_result["errors"].append("Job URL is required and must be a string")
        elif not self._is_valid_url(job_url):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Invalid job URL format: {job_url}")
        
        # Validate profile ID
        if not profile_id or not isinstance(profile_id, str):
            validation_result["valid"] = False
            validation_result["errors"].append("Profile ID is required and must be a string")
        elif len(profile_id.strip()) < 3:
            validation_result["valid"] = False
            validation_result["errors"].append("Profile ID must be at least 3 characters long")
        
        # Add warnings for best practices
        if job_url and len(job_url) > 500:
            validation_result["warnings"].append("Job URL is unusually long")
        
        if profile_id and not profile_id.replace("-", "").replace("_", "").isalnum():
            validation_result["warnings"].append("Profile ID contains special characters")
        
        return validation_result
    
    def generate_workflow_plan(self, job_url: str, profile_id: str) -> Dict[str, Any]:
        """
        Generate a complete workflow plan for resume tailoring.
        
        Args:
            job_url: URL of the job description page
            profile_id: Unique identifier for the applicant profile
            
        Returns:
            Dictionary containing the complete workflow plan
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs first
        validation = self.validate_inputs(job_url, profile_id)
        if not validation["valid"]:
            raise ValueError(f"Invalid inputs: {', '.join(validation['errors'])}")
        
        # Generate base workflow plan
        workflow_plan = {
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "inputs": {
                "job_url": job_url,
                "profile_id": profile_id
            },
            "validation": validation,
            "workflow": self._create_workflow_steps(job_url, profile_id),
            "estimated_duration_minutes": self._estimate_duration(),
            "dependencies": self._get_step_dependencies(),
            "outputs": {
                "final_resume": f"resume_{profile_id}_{self.workflow_id[:8]}.tex",
                "intermediate_files": self._get_intermediate_files()
            }
        }
        
        return workflow_plan
    
    def _create_workflow_steps(self, job_url: str, profile_id: str) -> List[Dict[str, Any]]:
        """
        Create the detailed workflow steps with inputs and outputs.
        
        Args:
            job_url: URL of the job description page
            profile_id: Unique identifier for the applicant profile
            
        Returns:
            List of workflow step dictionaries
        """
        steps = []
        
        # Step 1: JD Extraction
        steps.append({
            "step": 1,
            "agent": "JDExtractorAgent",
            "description": "Extract and parse job description from URL",
            "inputs": {
                "job_url": job_url,
                "timeout": 30,
                "extract_sections": ["title", "skills", "responsibilities", "requirements"]
            },
            "outputs": {
                "primary": "job_data.json",
                "metadata": "jd_extraction_metadata.json"
            },
            "estimated_duration_minutes": 2,
            "dependencies": [],
            "status": "pending"
        })
        
        # Step 2: Profile RAG Retrieval
        steps.append({
            "step": 2,
            "agent": "ProfileRAGAgent",
            "description": "Retrieve relevant applicant profile information from vector database",
            "inputs": {
                "profile_id": profile_id,
                "job_keywords": "{{job_data.skills + job_data.requirements}}",
                "similarity_threshold": 0.7,
                "max_chunks": 10
            },
            "outputs": {
                "primary": "relevant_profile.json",
                "metadata": "rag_retrieval_metadata.json"
            },
            "estimated_duration_minutes": 3,
            "dependencies": ["job_data.json"],
            "status": "pending"
        })
        
        # Step 3: Content Alignment
        steps.append({
            "step": 3,
            "agent": "ContentAlignmentAgent",
            "description": "Align resume content with job description keywords and requirements",
            "inputs": {
                "job_data": "{{job_data.json}}",
                "profile_data": "{{relevant_profile.json}}",
                "alignment_strategy": "keyword_optimization",
                "target_match_percentage": 85
            },
            "outputs": {
                "primary": "aligned_resume.json",
                "metadata": "alignment_analysis.json"
            },
            "estimated_duration_minutes": 4,
            "dependencies": ["job_data.json", "relevant_profile.json"],
            "status": "pending"
        })
        
        # Step 4: ATS Optimization
        steps.append({
            "step": 4,
            "agent": "ATSOptimizerAgent",
            "description": "Optimize resume for ATS systems and keyword density",
            "inputs": {
                "aligned_resume": "{{aligned_resume.json}}",
                "job_keywords": "{{job_data.skills + job_data.requirements}}",
                "target_ats_score": 90,
                "formatting_rules": "standard_ats"
            },
            "outputs": {
                "primary": "optimized_resume.json",
                "metadata": "ats_optimization_report.json"
            },
            "estimated_duration_minutes": 3,
            "dependencies": ["aligned_resume.json"],
            "status": "pending"
        })
        
        # Step 5: LaTeX Formatting
        steps.append({
            "step": 5,
            "agent": "LaTeXFormatterAgent",
            "description": "Generate final LaTeX resume ready for Overleaf",
            "inputs": {
                "optimized_resume": "{{optimized_resume.json}}",
                "template_style": "professional",
                "output_format": "overleaf_compatible",
                "include_metadata": True
            },
            "outputs": {
                "primary": f"resume_{profile_id}_{self.workflow_id[:8]}.tex",
                "metadata": "latex_generation_log.json"
            },
            "estimated_duration_minutes": 2,
            "dependencies": ["optimized_resume.json"],
            "status": "pending"
        })
        
        return steps
    
    def _estimate_duration(self) -> int:
        """
        Estimate total workflow duration in minutes.
        
        Returns:
            Estimated duration in minutes
        """
        base_duration = 14  # Sum of individual step durations
        overhead = 3  # Buffer for coordination and I/O
        return base_duration + overhead
    
    def _get_step_dependencies(self) -> Dict[str, List[str]]:
        """
        Get dependency mapping for workflow steps.
        
        Returns:
            Dictionary mapping step names to their dependencies
        """
        return {
            "JDExtractorAgent": [],
            "ProfileRAGAgent": ["JDExtractorAgent"],
            "ContentAlignmentAgent": ["JDExtractorAgent", "ProfileRAGAgent"],
            "ATSOptimizerAgent": ["ContentAlignmentAgent"],
            "LaTeXFormatterAgent": ["ATSOptimizerAgent"]
        }
    
    def _get_intermediate_files(self) -> List[str]:
        """
        Get list of intermediate files generated during workflow.
        
        Returns:
            List of intermediate file names
        """
        return [
            "job_data.json",
            "jd_extraction_metadata.json",
            "relevant_profile.json",
            "rag_retrieval_metadata.json",
            "aligned_resume.json",
            "alignment_analysis.json",
            "optimized_resume.json",
            "ats_optimization_report.json",
            "latex_generation_log.json"
        ]
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if the given string is a valid URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def update_step_status(self, step_number: int, status: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a specific workflow step.
        
        Args:
            step_number: Step number to update (1-based)
            status: New status ('pending', 'in_progress', 'completed', 'failed')
            metadata: Optional metadata to attach to the step
            
        Returns:
            True if update successful, False otherwise
        """
        valid_statuses = ['pending', 'in_progress', 'completed', 'failed']
        if status not in valid_statuses:
            return False
        
        if not (1 <= step_number <= len(self.workflow_steps)):
            return False
        
        # This would update the step status in a real implementation
        # For now, we just validate the inputs
        return True
    
    def get_next_step(self, current_step: int) -> Optional[Dict[str, Any]]:
        """
        Get the next step in the workflow sequence.
        
        Args:
            current_step: Current step number (1-based)
            
        Returns:
            Next step dictionary or None if at end of workflow
        """
        if current_step < len(self.workflow_steps):
            return {
                "step": current_step + 1,
                "agent": self.workflow_steps[current_step],
                "description": f"Execute {self.workflow_steps[current_step]}"
            }
        return None
    
    def to_json(self, workflow_plan: Dict[str, Any]) -> str:
        """
        Convert workflow plan to JSON string.
        
        Args:
            workflow_plan: Dictionary containing workflow plan
            
        Returns:
            JSON string representation
        """
        return json.dumps(workflow_plan, indent=2, ensure_ascii=False)
    
    def create_simple_plan(self, job_url: str, profile_id: str) -> Dict[str, Any]:
        """
        Create a simplified workflow plan matching the example format.
        
        Args:
            job_url: URL of the job description page
            profile_id: Unique identifier for the applicant profile
            
        Returns:
            Simplified workflow plan dictionary
        """
        # Validate inputs
        validation = self.validate_inputs(job_url, profile_id)
        if not validation["valid"]:
            raise ValueError(f"Invalid inputs: {', '.join(validation['errors'])}")
        
        return {
            "workflow": [
                {"step": 1, "agent": "JDExtractorAgent", "output": "job_data.json"},
                {"step": 2, "agent": "ProfileRAGAgent", "output": "relevant_profile.json"},
                {"step": 3, "agent": "ContentAlignmentAgent", "output": "aligned_resume.json"},
                {"step": 4, "agent": "ATSOptimizerAgent", "output": "optimized_resume.json"},
                {"step": 5, "agent": "LaTeXFormatterAgent", "output": "resume.tex"}
            ]
        }


def main():
    """
    Main function for testing the ResumePlannerAgent.
    """
    print("ResumePlannerAgent Test")
    print("=" * 50)
    
    # Initialize the agent
    planner = ResumePlannerAgent()
    
    # Sample inputs
    sample_job_url = "https://example.com/software-engineer-job"
    sample_profile_id = "user_12345"
    
    print(f"Job URL: {sample_job_url}")
    print(f"Profile ID: {sample_profile_id}")
    print()
    
    try:
        # Generate simple plan (matching example format)
        print("Simple Workflow Plan:")
        print("-" * 30)
        simple_plan = planner.create_simple_plan(sample_job_url, sample_profile_id)
        print(planner.to_json(simple_plan))
        print()
        
        # Generate detailed plan
        print("Detailed Workflow Plan:")
        print("-" * 30)
        detailed_plan = planner.generate_workflow_plan(sample_job_url, sample_profile_id)
        print(planner.to_json(detailed_plan))
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This uses sample data. Replace with real job URL and profile ID for testing.")


if __name__ == "__main__":
    main()
