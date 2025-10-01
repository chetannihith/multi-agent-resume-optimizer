"""
Unit tests for JDExtractorAgent.

This module contains comprehensive tests for the JDExtractorAgent class,
including tests for URL validation, HTML parsing, text extraction,
and error handling.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.jd_extractor_agent import JDExtractorAgent


class TestJDExtractorAgent:
    """Test cases for JDExtractorAgent class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = JDExtractorAgent()
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Software Engineer - AI/ML Team</title>
        </head>
        <body>
            <h1>Software Engineer - AI/ML Team</h1>
            <div class="job-description">
                <h3>Key Responsibilities:</h3>
                <ul>
                    <li>Develop AI workflows using Python and FastAPI</li>
                    <li>Integrate APIs and build scalable microservices</li>
                </ul>
                
                <h3>Required Skills:</h3>
                <ul>
                    <li>Python programming (3+ years experience)</li>
                    <li>FastAPI framework</li>
                </ul>
                
                <h3>Requirements:</h3>
                <ul>
                    <li>Bachelor's degree in Computer Science</li>
                    <li>3+ years of Python development experience</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    def test_agent_initialization(self):
        """Test agent initialization with default parameters."""
        agent = JDExtractorAgent()
        assert agent.timeout == 30
        assert "Mozilla" in agent.user_agent
        assert agent.session is not None
    
    def test_agent_initialization_custom_params(self):
        """Test agent initialization with custom parameters."""
        custom_agent = JDExtractorAgent(timeout=60, user_agent="Custom Agent")
        assert custom_agent.timeout == 60
        assert custom_agent.user_agent == "Custom Agent"
    
    def test_is_valid_url_valid_urls(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
            "https://example.com:8080/path?param=value"
        ]
        
        for url in valid_urls:
            assert self.agent._is_valid_url(url), f"URL {url} should be valid"
    
    def test_is_valid_url_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "example.com",  # Missing scheme
            "",
            None
        ]
        
        for url in invalid_urls:
            assert not self.agent._is_valid_url(url), f"URL {url} should be invalid"
    
    def test_extract_text_from_html(self):
        """Test HTML text extraction."""
        html_with_scripts = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is a paragraph.</p>
            <script>console.log('test');</script>
            <style>body { color: red; }</style>
        </body>
        </html>
        """
        
        result = self.agent.extract_text_from_html(html_with_scripts)
        
        assert "Main Title" in result
        assert "This is a paragraph" in result
        assert "console.log" not in result  # Scripts should be removed
        assert "color: red" not in result  # Styles should be removed
    
    def test_extract_job_title_from_h1(self):
        """Test job title extraction from H1 tag."""
        html = "<h1>Software Engineer - AI/ML Team</h1>"
        result = self.agent.extract_job_title(html)
        assert result == "Software Engineer - AI/ML Team"
    
    def test_extract_job_title_from_title_tag(self):
        """Test job title extraction from title tag."""
        html = "<title>Software Engineer - AI/ML Team</title>"
        result = self.agent.extract_job_title(html)
        assert result == "Software Engineer - AI/ML Team"
    
    def test_extract_job_title_no_match(self):
        """Test job title extraction when no title is found."""
        html = "<div>No title here</div>"
        result = self.agent.extract_job_title(html)
        assert result is None
    
    def test_extract_skills_from_html(self):
        """Test skills extraction from HTML structure."""
        html = """
        <h3>Required Skills:</h3>
        <ul>
            <li>Python programming (3+ years experience)</li>
            <li>FastAPI framework</li>
            <li>RAG implementation</li>
        </ul>
        """
        
        result = self.agent.extract_skills(html)
        
        assert len(result) == 3
        assert "Python programming (3+ years experience)" in result
        assert "FastAPI framework" in result
        assert "RAG implementation" in result
    
    def test_extract_responsibilities_from_html(self):
        """Test responsibilities extraction from HTML structure."""
        html = """
        <h3>Key Responsibilities:</h3>
        <ul>
            <li>Develop AI workflows using Python and FastAPI</li>
            <li>Integrate APIs and build scalable microservices</li>
            <li>Implement RAG systems</li>
        </ul>
        """
        
        result = self.agent.extract_responsibilities(html)
        
        assert len(result) == 3
        assert "Develop AI workflows using Python and FastAPI" in result
        assert "Integrate APIs and build scalable microservices" in result
        assert "Implement RAG systems" in result
    
    def test_extract_requirements_from_html(self):
        """Test requirements extraction from HTML structure."""
        html = """
        <h3>Requirements:</h3>
        <ul>
            <li>Bachelor's degree in Computer Science</li>
            <li>3+ years of Python development experience</li>
            <li>Experience with Large Language Models</li>
        </ul>
        """
        
        result = self.agent.extract_requirements(html)
        
        assert len(result) == 3
        assert "Bachelor's degree in Computer Science" in result
        assert "3+ years of Python development experience" in result
        assert "Experience with Large Language Models" in result
    
    def test_extract_skills_empty_section(self):
        """Test skills extraction when no skills section is found."""
        html = "<div>No skills section here</div>"
        result = self.agent.extract_skills(html)
        assert result == []
    
    def test_extract_responsibilities_empty_section(self):
        """Test responsibilities extraction when no responsibilities section is found."""
        html = "<div>No responsibilities section here</div>"
        result = self.agent.extract_responsibilities(html)
        assert result == []
    
    def test_extract_requirements_empty_section(self):
        """Test requirements extraction when no requirements section is found."""
        html = "<div>No requirements section here</div>"
        result = self.agent.extract_requirements(html)
        assert result == []
    
    def test_to_json_conversion(self):
        """Test JSON conversion of job data."""
        job_data = {
            "job_title": "Software Engineer",
            "skills": ["Python", "FastAPI"],
            "responsibilities": ["Develop APIs"],
            "requirements": ["3+ years experience"],
            "url": "https://example.com",
            "raw_text_length": 100
        }
        
        result = self.agent.to_json(job_data)
        parsed_result = json.loads(result)
        
        assert parsed_result["job_title"] == "Software Engineer"
        assert parsed_result["skills"] == ["Python", "FastAPI"]
        assert parsed_result["responsibilities"] == ["Develop APIs"]
        assert parsed_result["requirements"] == ["3+ years experience"]
    
    @patch('agents.jd_extractor_agent.requests.Session.get')
    def test_fetch_page_content_success(self, mock_get):
        """Test successful page content fetching."""
        mock_response = Mock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.agent.fetch_page_content("https://example.com")
        
        assert result == self.sample_html
        mock_get.assert_called_once_with("https://example.com", timeout=30)
    
    @patch('agents.jd_extractor_agent.requests.Session.get')
    def test_fetch_page_content_request_exception(self, mock_get):
        """Test page content fetching with request exception."""
        mock_get.side_effect = Exception("Network error")
        
        result = self.agent.fetch_page_content("https://example.com")
        
        assert result is None
    
    def test_fetch_page_content_invalid_url(self):
        """Test page content fetching with invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            self.agent.fetch_page_content("not-a-url")
    
    @patch('agents.jd_extractor_agent.requests.Session.get')
    def test_extract_job_data_success(self, mock_get):
        """Test complete job data extraction."""
        mock_response = Mock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.agent.extract_job_data("https://example.com")
        
        assert result["job_title"] == "Software Engineer - AI/ML Team"
        assert len(result["skills"]) == 2
        assert len(result["responsibilities"]) == 2
        assert len(result["requirements"]) == 2
        assert result["url"] == "https://example.com"
        assert "raw_text_length" in result
    
    @patch('agents.jd_extractor_agent.requests.Session.get')
    def test_extract_job_data_fetch_failure(self, mock_get):
        """Test job data extraction when page fetch fails."""
        mock_get.side_effect = Exception("Network error")
        
        result = self.agent.extract_job_data("https://example.com")
        
        assert result["job_title"] is None
        assert result["skills"] == []
        assert result["responsibilities"] == []
        assert result["requirements"] == []
        assert result["url"] == "https://example.com"
        assert "error" in result
    
    def test_extract_job_data_invalid_url(self):
        """Test job data extraction with invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            self.agent.extract_job_data("not-a-url")
    
    def test_skills_limit(self):
        """Test that skills extraction is limited to 20 items."""
        html = "<h3>Required Skills:</h3><ul>"
        for i in range(25):
            html += f"<li>Skill {i}</li>"
        html += "</ul>"
        
        result = self.agent.extract_skills(html)
        assert len(result) <= 20
    
    def test_responsibilities_limit(self):
        """Test that responsibilities extraction is limited to 15 items."""
        html = "<h3>Key Responsibilities:</h3><ul>"
        for i in range(20):
            html += f"<li>Responsibility {i}</li>"
        html += "</ul>"
        
        result = self.agent.extract_responsibilities(html)
        assert len(result) <= 15
    
    def test_requirements_limit(self):
        """Test that requirements extraction is limited to 15 items."""
        html = "<h3>Requirements:</h3><ul>"
        for i in range(20):
            html += f"<li>Requirement {i}</li>"
        html += "</ul>"
        
        result = self.agent.extract_requirements(html)
        assert len(result) <= 15


class TestJDExtractorAgentIntegration:
    """Integration tests for JDExtractorAgent."""
    
    def test_full_extraction_workflow(self):
        """Test the complete extraction workflow with sample data."""
        agent = JDExtractorAgent()
        
        # Sample HTML with all sections
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Senior Python Developer</title>
        </head>
        <body>
            <h1>Senior Python Developer</h1>
            <div class="job-description">
                <h3>Key Responsibilities:</h3>
                <ul>
                    <li>Design and implement scalable Python applications</li>
                    <li>Lead technical architecture decisions</li>
                    <li>Mentor junior developers</li>
                </ul>
                
                <h3>Required Skills:</h3>
                <ul>
                    <li>Python 3.8+</li>
                    <li>Django/FastAPI</li>
                    <li>PostgreSQL</li>
                    <li>Docker</li>
                </ul>
                
                <h3>Requirements:</h3>
                <ul>
                    <li>5+ years Python experience</li>
                    <li>Bachelor's degree in CS or related field</li>
                    <li>Experience with cloud platforms</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Test individual extraction methods
        job_title = agent.extract_job_title(sample_html)
        skills = agent.extract_skills(sample_html)
        responsibilities = agent.extract_responsibilities(sample_html)
        requirements = agent.extract_requirements(sample_html)
        
        # Verify results
        assert job_title == "Senior Python Developer"
        assert len(skills) == 4
        assert len(responsibilities) == 3
        assert len(requirements) == 3
        
        # Test JSON conversion
        job_data = {
            "job_title": job_title,
            "skills": skills,
            "responsibilities": responsibilities,
            "requirements": requirements,
            "url": "test_url",
            "raw_text_length": 100
        }
        
        json_output = agent.to_json(job_data)
        parsed_data = json.loads(json_output)
        
        assert parsed_data["job_title"] == "Senior Python Developer"
        assert len(parsed_data["skills"]) == 4
        assert len(parsed_data["responsibilities"]) == 3
        assert len(parsed_data["requirements"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
