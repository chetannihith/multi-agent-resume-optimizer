"""
JDExtractorAgent - Extracts job description data from URLs.

This module contains the JDExtractorAgent class that fetches and parses
job descriptions from web pages, extracting structured information like
job title, skills, responsibilities, and requirements.
"""

import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task


class JDExtractorAgent:
    """
    Agent for extracting job description data from web URLs.
    
    This agent fetches job description pages and extracts structured
    information including job title, skills, responsibilities, and
    requirements using web scraping techniques.
    """
    
    def __init__(self, timeout: int = 30, user_agent: str = None):
        """
        Initialize the JDExtractorAgent.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            user_agent: Custom user agent string (default: None)
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content from a given URL.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            HTML content as string, or None if fetch fails
            
        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract clean text content from HTML.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_job_title(self, text: str) -> Optional[str]:
        """
        Extract job title from text content.
        
        Args:
            text: Cleaned text content
            
        Returns:
            Extracted job title or None if not found
        """
        # Common patterns for job titles
        patterns = [
            r'<h1[^>]*>([^<]+)</h1>',  # HTML h1 tag (priority)
            r'<title[^>]*>([^<]+)</title>',  # HTML title tag
            r'(?:job title|position|role):\s*([^\n]+)',
            r'(?:hiring for|looking for|seeking)\s+([^\n]+)',
            r'^([A-Z][^.\n]{10,50})\s*(?:job|position|role)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 100:
                    return title
        
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text content.
        
        Args:
            text: Cleaned text content
            
        Returns:
            List of extracted skills
        """
        skills = []
        
        # Look for HTML list items under skills section first
        # Find the skills section - look for h3 with "Required Skills"
        skills_section_pattern = r'<h3[^>]*>Required Skills:</h3>\s*<ul[^>]*>(.*?)</ul>'
        skills_section_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_section_match:
            skills_section = skills_section_match.group(1)
            li_pattern = r'<li[^>]*>([^<]+)</li>'
            li_matches = re.findall(li_pattern, skills_section, re.IGNORECASE)
            
            for match in li_matches:
                skill = match.strip()
                if len(skill) > 2 and len(skill) < 100:
                    skills.append(skill)
        
        # If no HTML structure found, try text patterns
        if not skills:
            skill_patterns = [
                r'(?:skills|technologies|tools|languages?):\s*([^\n]+)',
                r'(?:required|preferred|experience with):\s*([^\n]+)',
                r'(?:proficient in|knowledge of|familiar with):\s*([^\n]+)',
            ]
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Split by common separators and clean
                    skill_list = re.split(r'[,;|•\n]', match)
                    for skill in skill_list:
                        skill = skill.strip()
                        if skill and len(skill) > 2:
                            skills.append(skill)
        
        # Remove duplicates and return
        return list(set(skills))[:20]  # Limit to top 20 skills
    
    def extract_responsibilities(self, text: str) -> List[str]:
        """
        Extract job responsibilities from text content.
        
        Args:
            text: Cleaned text content
            
        Returns:
            List of extracted responsibilities
        """
        responsibilities = []
        
        # Look for HTML list items under responsibilities section
        # Find the responsibilities section first - look for h3 with "Key Responsibilities"
        resp_section_pattern = r'<h3[^>]*>Key Responsibilities:</h3>\s*<ul[^>]*>(.*?)</ul>'
        resp_section_match = re.search(resp_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if resp_section_match:
            resp_section = resp_section_match.group(1)
            li_pattern = r'<li[^>]*>([^<]+)</li>'
            li_matches = re.findall(li_pattern, resp_section, re.IGNORECASE)
            
            for match in li_matches:
                resp = match.strip()
                if len(resp) > 10 and len(resp) < 200:
                    responsibilities.append(resp)
        
        # If no HTML structure found, try text patterns
        if not responsibilities:
            responsibility_patterns = [
                r'(?:responsibilities|duties|key tasks):\s*([^\n]+)',
                r'(?:you will|you\'ll|will be responsible for):\s*([^\n]+)',
                r'(?:main duties|primary responsibilities):\s*([^\n]+)',
            ]
            
            for pattern in responsibility_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    resp_list = re.split(r'[,;|•\n]', match)
                    for resp in resp_list:
                        resp = resp.strip()
                        if resp and len(resp) > 10:
                            responsibilities.append(resp)
        
        return responsibilities[:15]  # Limit to top 15 responsibilities
    
    def extract_requirements(self, text: str) -> List[str]:
        """
        Extract job requirements from text content.
        
        Args:
            text: Cleaned text content
            
        Returns:
            List of extracted requirements
        """
        requirements = []
        
        # Look for HTML list items under requirements section
        # Find the requirements section first - look for h3 with "Requirements"
        req_section_pattern = r'<h3[^>]*>Requirements:</h3>\s*<ul[^>]*>(.*?)</ul>'
        req_section_match = re.search(req_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if req_section_match:
            req_section = req_section_match.group(1)
            li_pattern = r'<li[^>]*>([^<]+)</li>'
            li_matches = re.findall(li_pattern, req_section, re.IGNORECASE)
            
            for match in li_matches:
                req = match.strip()
                if len(req) > 5 and len(req) < 200:
                    requirements.append(req)
        
        # If no HTML structure found, try text patterns
        if not requirements:
            requirement_patterns = [
                r'(?:requirements|qualifications|must have):\s*([^\n]+)',
                r'(?:minimum|required|essential):\s*([^\n]+)',
                r'(?:candidate must|applicant should):\s*([^\n]+)',
            ]
            
            for pattern in requirement_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    req_list = re.split(r'[,;|•\n]', match)
                    for req in req_list:
                        req = req.strip()
                        if req and len(req) > 5:
                            requirements.append(req)
        
        return requirements[:15]  # Limit to top 15 requirements
    
    def extract_job_data(self, url: str) -> Dict[str, Any]:
        """
        Extract complete job data from a URL.
        
        Args:
            url: URL of the job description page
            
        Returns:
            Dictionary containing extracted job data
            
        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails
        """
        html_content = self.fetch_page_content(url)
        if not html_content:
            return {
                "job_title": None,
                "skills": [],
                "responsibilities": [],
                "requirements": [],
                "url": url,
                "error": "Failed to fetch page content"
            }
        
        text = self.extract_text_from_html(html_content)
        
        return {
            "job_title": self.extract_job_title(html_content),  # Use HTML for title
            "skills": self.extract_skills(html_content),  # Use HTML for skills
            "responsibilities": self.extract_responsibilities(html_content),  # Use HTML for responsibilities
            "requirements": self.extract_requirements(html_content),  # Use HTML for requirements
            "url": url,
            "raw_text_length": len(text)
        }
    
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
    
    def to_json(self, job_data: Dict[str, Any]) -> str:
        """
        Convert job data to JSON string.
        
        Args:
            job_data: Dictionary containing job data
            
        Returns:
            JSON string representation
        """
        return json.dumps(job_data, indent=2, ensure_ascii=False)


def main():
    """
    Main function for testing the JDExtractorAgent.
    """
    # Sample job description URL for testing
    sample_url = "https://example.com/job-posting"
    
    # Initialize the agent
    agent = JDExtractorAgent()
    
    print("JDExtractorAgent Test")
    print("=" * 50)
    print(f"Testing with URL: {sample_url}")
    print()
    
    try:
        # Extract job data
        job_data = agent.extract_job_data(sample_url)
        
        # Display results
        print("Extracted Job Data:")
        print("-" * 30)
        print(agent.to_json(job_data))
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This is a sample URL. Replace with a real job posting URL for testing.")


if __name__ == "__main__":
    main()
