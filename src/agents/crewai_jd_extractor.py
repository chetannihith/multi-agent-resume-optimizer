"""
CrewAI integration for JDExtractorAgent.

This module provides CrewAI-specific implementations of the JDExtractorAgent,
including Agent and Task definitions for use in CrewAI workflows.
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import json

from .jd_extractor_agent import JDExtractorAgent


class JDExtractionTool(BaseTool):
    """
    CrewAI tool wrapper for JDExtractorAgent functionality.
    
    This tool allows CrewAI agents to extract job description data
    from URLs using the JDExtractorAgent.
    """
    
    name: str = "jd_extraction_tool"
    description: str = (
        "Extract structured job description data from a URL. "
        "Returns job title, skills, responsibilities, and requirements."
    )
    
    def __init__(self, **kwargs):
        """Initialize the JD extraction tool."""
        super().__init__(**kwargs)
        # Store extractor as a private attribute
        self._extractor = JDExtractorAgent()
    
    def _run(self, url: str) -> str:
        """
        Extract job data from URL.
        
        Args:
            url: URL of the job description page
            
        Returns:
            JSON string containing extracted job data
        """
        try:
            job_data = self._extractor.extract_job_data(url)
            return self._extractor.to_json(job_data)
        except Exception as e:
            return json.dumps({
                "error": f"Failed to extract job data: {str(e)}",
                "url": url
            })


def create_jd_extractor_agent(
    role: str = "Job Description Extractor",
    goal: str = "Extract structured data from job description URLs",
    backstory: str = None,
    verbose: bool = True,
    allow_delegation: bool = False
) -> Agent:
    """
    Create a CrewAI Agent for job description extraction.
    
    Args:
        role: The role of the agent
        goal: The goal of the agent
        backstory: Background story for the agent
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow task delegation
        
    Returns:
        Configured CrewAI Agent
    """
    if backstory is None:
        backstory = (
            "You are an expert web scraper and data extraction specialist "
            "with extensive experience in parsing job descriptions from various "
            "websites. You excel at identifying key information like job titles, "
            "required skills, responsibilities, and qualifications from "
            "unstructured HTML content."
        )
    
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=[JDExtractionTool()],
        verbose=verbose,
        allow_delegation=allow_delegation
    )


def create_jd_extraction_task(
    url: str,
    agent: Agent,
    description: str = None,
    expected_output: str = None
) -> Task:
    """
    Create a CrewAI Task for job description extraction.
    
    Args:
        url: URL to extract job data from
        agent: Agent to perform the task
        description: Task description
        expected_output: Expected output format
        
    Returns:
        Configured CrewAI Task
    """
    if description is None:
        description = f"Extract structured job description data from the URL: {url}"
    
    if expected_output is None:
        expected_output = (
            "A JSON object containing the extracted job data with the following structure: "
            "{{'job_title': 'string', 'skills': ['list'], 'responsibilities': ['list'], "
            "'requirements': ['list'], 'url': 'string', 'raw_text_length': number}}"
        )
    
    return Task(
        description=description,
        agent=agent,
        expected_output=expected_output
    )


class CrewAIJDExtractorWorkflow:
    """
    CrewAI workflow for job description extraction.
    
    This class provides a complete workflow for extracting job description
    data using CrewAI agents and tasks.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the CrewAI JD extraction workflow.
        
        Args:
            verbose: Whether to enable verbose output
        """
        self.verbose = verbose
        self.agent = create_jd_extractor_agent(verbose=verbose)
        self.crew = None
    
    def extract_job_data(self, url: str) -> Dict[str, Any]:
        """
        Extract job data using CrewAI workflow.
        
        Args:
            url: URL of the job description page
            
        Returns:
            Dictionary containing extracted job data
        """
        task = create_jd_extraction_task(url, self.agent)
        self.crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=self.verbose
        )
        
        try:
            result = self.crew.kickoff()
            
            # Parse the result if it's a JSON string
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"raw_result": result, "url": url}
            else:
                return result
                
        except Exception as e:
            return {
                "error": f"CrewAI workflow failed: {str(e)}",
                "url": url
            }
    
    def extract_multiple_jobs(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract job data from multiple URLs.
        
        Args:
            urls: List of URLs to extract job data from
            
        Returns:
            List of dictionaries containing extracted job data
        """
        results = []
        
        for url in urls:
            result = self.extract_job_data(url)
            results.append(result)
        
        return results


def main():
    """
    Main function for testing the CrewAI integration.
    """
    print("CrewAI JDExtractorAgent Integration Test")
    print("=" * 50)
    
    # Test with sample URL (this will fail without a real URL)
    sample_url = "https://example.com/job-posting"
    
    try:
        # Create workflow
        workflow = CrewAIJDExtractorWorkflow(verbose=True)
        
        # Extract job data
        result = workflow.extract_job_data(sample_url)
        
        print("Extraction Result:")
        print("-" * 30)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This is a sample URL. Replace with a real job posting URL for testing.")


if __name__ == "__main__":
    main()
