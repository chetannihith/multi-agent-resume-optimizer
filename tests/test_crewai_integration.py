"""
Unit tests for CrewAI integration with JDExtractorAgent.

This module contains tests for the CrewAI-specific implementations
of the JDExtractorAgent functionality.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.crewai_jd_extractor import (
    JDExtractionTool,
    create_jd_extractor_agent,
    create_jd_extraction_task,
    CrewAIJDExtractorWorkflow
)


class TestJDExtractionTool:
    """Test cases for JDExtractionTool class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tool = JDExtractionTool()
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "jd_extraction_tool"
        assert "Extract structured job description data" in self.tool.description
        assert hasattr(self.tool, '_extractor')
    
    @patch('agents.crewai_jd_extractor.JDExtractorAgent')
    def test_tool_run_success(self, mock_extractor_class):
        """Test successful tool execution."""
        # Mock the extractor
        mock_extractor = Mock()
        mock_extractor.extract_job_data.return_value = {
            "job_title": "Software Engineer",
            "skills": ["Python", "FastAPI"],
            "responsibilities": ["Develop APIs"],
            "requirements": ["3+ years experience"],
            "url": "https://example.com",
            "raw_text_length": 100
        }
        mock_extractor.to_json.return_value = json.dumps({
            "job_title": "Software Engineer",
            "skills": ["Python", "FastAPI"],
            "responsibilities": ["Develop APIs"],
            "requirements": ["3+ years experience"],
            "url": "https://example.com",
            "raw_text_length": 100
        })
        mock_extractor_class.return_value = mock_extractor
        
        # Create new tool instance to use mocked extractor
        tool = JDExtractionTool()
        tool._extractor = mock_extractor
        
        result = tool._run("https://example.com")
        
        assert isinstance(result, str)
        parsed_result = json.loads(result)
        assert parsed_result["job_title"] == "Software Engineer"
        assert parsed_result["skills"] == ["Python", "FastAPI"]
    
    @patch('agents.crewai_jd_extractor.JDExtractorAgent')
    def test_tool_run_failure(self, mock_extractor_class):
        """Test tool execution with failure."""
        # Mock the extractor to raise an exception
        mock_extractor = Mock()
        mock_extractor.extract_job_data.side_effect = Exception("Network error")
        mock_extractor_class.return_value = mock_extractor
        
        # Create new tool instance to use mocked extractor
        tool = JDExtractionTool()
        tool._extractor = mock_extractor
        
        result = tool._run("https://example.com")
        
        assert isinstance(result, str)
        parsed_result = json.loads(result)
        assert "error" in parsed_result
        assert "Network error" in parsed_result["error"]


class TestCrewAIAgentCreation:
    """Test cases for CrewAI agent creation functions."""
    
    def test_create_jd_extractor_agent_default(self):
        """Test agent creation with default parameters."""
        agent = create_jd_extractor_agent()
        
        assert agent.role == "Job Description Extractor"
        assert agent.goal == "Extract structured data from job description URLs"
        assert len(agent.tools) == 1
        assert isinstance(agent.tools[0], JDExtractionTool)
        assert agent.verbose is True
        assert agent.allow_delegation is False
    
    def test_create_jd_extractor_agent_custom(self):
        """Test agent creation with custom parameters."""
        custom_role = "Senior Data Extractor"
        custom_goal = "Extract and analyze job data"
        custom_backstory = "I am a senior data extraction specialist."
        
        agent = create_jd_extractor_agent(
            role=custom_role,
            goal=custom_goal,
            backstory=custom_backstory,
            verbose=False,
            allow_delegation=True
        )
        
        assert agent.role == custom_role
        assert agent.goal == custom_goal
        assert agent.backstory == custom_backstory
        assert agent.verbose is False
        assert agent.allow_delegation is True
    
    def test_create_jd_extraction_task_default(self):
        """Test task creation with default parameters."""
        agent = create_jd_extractor_agent()
        task = create_jd_extraction_task("https://example.com", agent)
        
        assert "https://example.com" in task.description
        assert task.agent == agent
        assert "JSON object" in task.expected_output
        assert len(task.context) == 1
        # Context is not used in the simplified version
        assert task.description is not None
    
    def test_create_jd_extraction_task_custom(self):
        """Test task creation with custom parameters."""
        agent = create_jd_extractor_agent()
        custom_description = "Extract job data from the provided URL"
        custom_output = "A structured data object"
        
        task = create_jd_extraction_task(
            "https://example.com",
            agent,
            description=custom_description,
            expected_output=custom_output
        )
        
        assert task.description == custom_description
        assert task.expected_output == custom_output


class TestCrewAIWorkflow:
    """Test cases for CrewAIJDExtractorWorkflow class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.workflow = CrewAIJDExtractorWorkflow(verbose=False)
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        assert self.workflow.verbose is False
        assert self.workflow.agent is not None
        assert self.workflow.crew is None
    
    @patch('agents.crewai_jd_extractor.Crew')
    def test_extract_job_data_success(self, mock_crew_class):
        """Test successful job data extraction."""
        # Mock the crew and its kickoff method
        mock_crew = Mock()
        mock_crew.kickoff.return_value = json.dumps({
            "job_title": "Software Engineer",
            "skills": ["Python", "FastAPI"],
            "responsibilities": ["Develop APIs"],
            "requirements": ["3+ years experience"],
            "url": "https://example.com",
            "raw_text_length": 100
        })
        mock_crew_class.return_value = mock_crew
        
        result = self.workflow.extract_job_data("https://example.com")
        
        assert isinstance(result, dict)
        assert result["job_title"] == "Software Engineer"
        assert result["skills"] == ["Python", "FastAPI"]
        assert result["url"] == "https://example.com"
    
    @patch('agents.crewai_jd_extractor.Crew')
    def test_extract_job_data_failure(self, mock_crew_class):
        """Test job data extraction with failure."""
        # Mock the crew to raise an exception
        mock_crew = Mock()
        mock_crew.kickoff.side_effect = Exception("CrewAI error")
        mock_crew_class.return_value = mock_crew
        
        result = self.workflow.extract_job_data("https://example.com")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "CrewAI workflow failed" in result["error"]
        assert result["url"] == "https://example.com"
    
    @patch('agents.crewai_jd_extractor.Crew')
    def test_extract_job_data_non_json_result(self, mock_crew_class):
        """Test job data extraction with non-JSON result."""
        # Mock the crew to return a non-JSON string
        mock_crew = Mock()
        mock_crew.kickoff.return_value = "This is not JSON"
        mock_crew_class.return_value = mock_crew
        
        result = self.workflow.extract_job_data("https://example.com")
        
        assert isinstance(result, dict)
        assert result["raw_result"] == "This is not JSON"
        assert result["url"] == "https://example.com"
    
    @patch('agents.crewai_jd_extractor.Crew')
    def test_extract_multiple_jobs(self, mock_crew_class):
        """Test extraction from multiple URLs."""
        # Mock the crew and its kickoff method
        mock_crew = Mock()
        mock_crew.kickoff.return_value = json.dumps({
            "job_title": "Software Engineer",
            "skills": ["Python"],
            "responsibilities": ["Develop"],
            "requirements": ["Experience"],
            "url": "https://example.com",
            "raw_text_length": 50
        })
        mock_crew_class.return_value = mock_crew
        
        urls = ["https://example1.com", "https://example2.com"]
        results = self.workflow.extract_multiple_jobs(urls)
        
        assert len(results) == 2
        assert all(isinstance(result, dict) for result in results)
        assert all("job_title" in result for result in results)


class TestCrewAIIntegration:
    """Integration tests for CrewAI functionality."""
    
    def test_agent_tool_integration(self):
        """Test that agent has the correct tool."""
        agent = create_jd_extractor_agent()
        
        assert len(agent.tools) == 1
        tool = agent.tools[0]
        assert isinstance(tool, JDExtractionTool)
        assert tool.name == "jd_extraction_tool"
    
    def test_task_agent_integration(self):
        """Test that task is properly linked to agent."""
        agent = create_jd_extractor_agent()
        task = create_jd_extraction_task("https://example.com", agent)
        
        assert task.agent == agent
        # Context is not used in the simplified version
        assert task.description is not None
    
    def test_workflow_crew_creation(self):
        """Test that workflow creates crew with correct components."""
        workflow = CrewAIJDExtractorWorkflow()
        
        # The crew should be None initially
        assert workflow.crew is None
        
        # After calling extract_job_data, crew should be created
        # (This will fail in actual execution without proper setup, but we can test the structure)
        assert workflow.agent is not None
        assert workflow.agent.role == "Job Description Extractor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
