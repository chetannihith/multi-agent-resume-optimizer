"""
Test script for JDExtractorAgent.

This script demonstrates how to use the JDExtractorAgent with a local
HTML file for testing purposes.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.jd_extractor_agent import JDExtractorAgent


def test_with_local_file():
    """Test the JDExtractorAgent with a local HTML file."""
    # Get the path to the sample HTML file
    sample_file = Path(__file__).parent / "sample_job_description.html"
    
    if not sample_file.exists():
        print("Sample HTML file not found!")
        return
    
    # Initialize the agent
    agent = JDExtractorAgent()
    
    print("JDExtractorAgent Test with Local File")
    print("=" * 50)
    print(f"Testing with file: {sample_file}")
    print()
    
    try:
        # Read the HTML content
        with open(sample_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract text from HTML
        text = agent.extract_text_from_html(html_content)
        print(f"Extracted text length: {len(text)} characters")
        print()
        
        # Extract individual components using HTML content (not text)
        job_title = agent.extract_job_title(html_content)
        skills = agent.extract_skills(html_content)
        responsibilities = agent.extract_responsibilities(html_content)
        requirements = agent.extract_requirements(html_content)
        
        # Create job data structure
        job_data = {
            "job_title": job_title,
            "skills": skills,
            "responsibilities": responsibilities,
            "requirements": requirements,
            "url": str(sample_file),
            "raw_text_length": len(text)
        }
        
        # Display results
        print("Extracted Job Data:")
        print("-" * 30)
        print(agent.to_json(job_data))
        
        # Test individual extraction methods
        print("\nDetailed Extraction Results:")
        print("-" * 30)
        print(f"Job Title: {job_title}")
        print(f"Skills ({len(skills)}): {skills}")
        print(f"Responsibilities ({len(responsibilities)}): {responsibilities}")
        print(f"Requirements ({len(requirements)}): {requirements}")
        
    except Exception as e:
        print(f"Error: {e}")


def test_with_url():
    """Test the JDExtractorAgent with a real URL."""
    # Example URL (replace with actual job posting)
    test_url = "https://example.com/job-posting"
    
    agent = JDExtractorAgent()
    
    print("\nJDExtractorAgent Test with URL")
    print("=" * 50)
    print(f"Testing with URL: {test_url}")
    print()
    
    try:
        job_data = agent.extract_job_data(test_url)
        print("Extracted Job Data:")
        print("-" * 30)
        print(agent.to_json(job_data))
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This is a sample URL. Replace with a real job posting URL.")


if __name__ == "__main__":
    # Test with local file
    test_with_local_file()
    
    # Test with URL (commented out by default)
    # test_with_url()
