"""
Tests for ResumePlannerAgent.

This module contains unit tests for the ResumePlannerAgent class,
testing workflow planning, input validation, and JSON generation.
"""

import json
import pytest
from src.agents.resume_planner_agent import ResumePlannerAgent


class TestResumePlannerAgent:
    """Test cases for ResumePlannerAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = ResumePlannerAgent(workflow_id="test-workflow-123")
        self.valid_job_url = "https://example.com/software-engineer-job"
        self.valid_profile_id = "user_12345"
        
    def test_initialization(self):
        """Test agent initialization."""
        assert self.agent.workflow_id == "test-workflow-123"
        assert len(self.agent.workflow_steps) == 5
        assert self.agent.workflow_steps[0] == "JDExtractorAgent"
        assert self.agent.workflow_steps[-1] == "LaTeXFormatterAgent"
        
    def test_initialization_with_auto_id(self):
        """Test agent initialization with auto-generated ID."""
        agent = ResumePlannerAgent()
        assert agent.workflow_id is not None
        assert len(agent.workflow_id) > 10  # UUID should be longer
        
    def test_validate_inputs_valid(self):
        """Test input validation with valid inputs."""
        result = self.agent.validate_inputs(self.valid_job_url, self.valid_profile_id)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
    def test_validate_inputs_invalid_url(self):
        """Test input validation with invalid URL."""
        result = self.agent.validate_inputs("not-a-url", self.valid_profile_id)
        assert result["valid"] is False
        assert any("Invalid job URL format" in error for error in result["errors"])
        
    def test_validate_inputs_empty_url(self):
        """Test input validation with empty URL."""
        result = self.agent.validate_inputs("", self.valid_profile_id)
        assert result["valid"] is False
        assert any("Job URL is required" in error for error in result["errors"])
        
    def test_validate_inputs_invalid_profile_id(self):
        """Test input validation with invalid profile ID."""
        result = self.agent.validate_inputs(self.valid_job_url, "ab")
        assert result["valid"] is False
        assert any("at least 3 characters" in error for error in result["errors"])
        
    def test_validate_inputs_empty_profile_id(self):
        """Test input validation with empty profile ID."""
        result = self.agent.validate_inputs(self.valid_job_url, "")
        assert result["valid"] is False
        assert any("Profile ID is required" in error for error in result["errors"])
        
    def test_create_simple_plan(self):
        """Test simple workflow plan creation."""
        plan = self.agent.create_simple_plan(self.valid_job_url, self.valid_profile_id)
        
        assert "workflow" in plan
        assert len(plan["workflow"]) == 5
        
        # Check first step
        first_step = plan["workflow"][0]
        assert first_step["step"] == 1
        assert first_step["agent"] == "JDExtractorAgent"
        assert first_step["output"] == "job_data.json"
        
        # Check last step
        last_step = plan["workflow"][-1]
        assert last_step["step"] == 5
        assert last_step["agent"] == "LaTeXFormatterAgent"
        assert last_step["output"] == "resume.tex"
        
    def test_generate_workflow_plan(self):
        """Test detailed workflow plan generation."""
        plan = self.agent.generate_workflow_plan(self.valid_job_url, self.valid_profile_id)
        
        # Check main structure
        assert "workflow_id" in plan
        assert "created_at" in plan
        assert "inputs" in plan
        assert "workflow" in plan
        assert "estimated_duration_minutes" in plan
        assert "dependencies" in plan
        assert "outputs" in plan
        
        # Check inputs
        assert plan["inputs"]["job_url"] == self.valid_job_url
        assert plan["inputs"]["profile_id"] == self.valid_profile_id
        
        # Check workflow steps
        workflow = plan["workflow"]
        assert len(workflow) == 5
        
        # Check step structure
        for i, step in enumerate(workflow, 1):
            assert step["step"] == i
            assert "agent" in step
            assert "description" in step
            assert "inputs" in step
            assert "outputs" in step
            assert "estimated_duration_minutes" in step
            assert "dependencies" in step
            assert "status" in step
            
    def test_generate_workflow_plan_invalid_inputs(self):
        """Test workflow plan generation with invalid inputs."""
        with pytest.raises(ValueError):
            self.agent.generate_workflow_plan("invalid-url", self.valid_profile_id)
            
    def test_update_step_status_valid(self):
        """Test updating step status with valid parameters."""
        result = self.agent.update_step_status(1, "in_progress")
        assert result is True
        
        result = self.agent.update_step_status(3, "completed", {"duration": 120})
        assert result is True
        
    def test_update_step_status_invalid_step(self):
        """Test updating step status with invalid step number."""
        result = self.agent.update_step_status(0, "in_progress")
        assert result is False
        
        result = self.agent.update_step_status(10, "completed")
        assert result is False
        
    def test_update_step_status_invalid_status(self):
        """Test updating step status with invalid status."""
        result = self.agent.update_step_status(1, "invalid_status")
        assert result is False
        
    def test_get_next_step(self):
        """Test getting next step in workflow."""
        next_step = self.agent.get_next_step(1)
        assert next_step is not None
        assert next_step["step"] == 2
        assert next_step["agent"] == "ProfileRAGAgent"
        
        # Test last step
        next_step = self.agent.get_next_step(5)
        assert next_step is None
        
    def test_to_json(self):
        """Test JSON serialization."""
        plan = self.agent.create_simple_plan(self.valid_job_url, self.valid_profile_id)
        json_str = self.agent.to_json(plan)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed == plan
        
    def test_workflow_dependencies(self):
        """Test workflow step dependencies."""
        dependencies = self.agent._get_step_dependencies()
        
        # JDExtractorAgent has no dependencies
        assert dependencies["JDExtractorAgent"] == []
        
        # ProfileRAGAgent depends on JDExtractorAgent
        assert "JDExtractorAgent" in dependencies["ProfileRAGAgent"]
        
        # ContentAlignmentAgent depends on both JD and Profile
        assert "JDExtractorAgent" in dependencies["ContentAlignmentAgent"]
        assert "ProfileRAGAgent" in dependencies["ContentAlignmentAgent"]
        
        # ATSOptimizerAgent depends on ContentAlignmentAgent
        assert "ContentAlignmentAgent" in dependencies["ATSOptimizerAgent"]
        
        # LaTeXFormatterAgent depends on ATSOptimizerAgent
        assert "ATSOptimizerAgent" in dependencies["LaTeXFormatterAgent"]
        
    def test_estimate_duration(self):
        """Test duration estimation."""
        duration = self.agent._estimate_duration()
        assert isinstance(duration, int)
        assert duration > 0
        assert duration < 60  # Should be reasonable (less than 1 hour)
        
    def test_intermediate_files(self):
        """Test intermediate files list."""
        files = self.agent._get_intermediate_files()
        assert isinstance(files, list)
        assert len(files) > 0
        assert "job_data.json" in files
        assert "resume.tex" not in files  # Final output, not intermediate


if __name__ == "__main__":
    pytest.main([__file__])
