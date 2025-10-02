"""
Groq API Helper for Multi-Agent Resume Optimizer.

This module provides utilities for integrating Groq's fast LLM inference
into the resume optimization agents for enhanced content generation and analysis.
"""

import os
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

from config import config


class GroqHelper:
    """
    Helper class for Groq API integration.
    
    Provides methods for content enhancement, keyword analysis,
    and intelligent resume optimization using Groq's LLM models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq helper.
        
        Args:
            api_key: Groq API key (uses config if not provided)
            model: Model name (uses config if not provided)
        """
        if not GROQ_AVAILABLE:
            raise ImportError("Groq package not available. Install with: pip install groq")
        
        self.api_key = api_key or config.GROQ_API_KEY
        self.model = model or config.GROQ_MODEL
        
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.client = Groq(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def enhance_resume_summary(self, current_summary: str, job_requirements: List[str]) -> str:
        """
        Enhance resume summary using Groq LLM.
        
        Args:
            current_summary: Current resume summary
            job_requirements: List of job requirements to align with
            
        Returns:
            Enhanced summary text
        """
        prompt = f"""
        You are an expert resume writer. Enhance the following resume summary to better align with the job requirements while maintaining authenticity and professionalism.

        Current Summary:
        {current_summary}

        Job Requirements:
        {', '.join(job_requirements)}

        Instructions:
        1. Keep the enhanced summary concise (2-3 sentences)
        2. Incorporate relevant keywords from job requirements naturally
        3. Maintain the candidate's authentic voice and experience
        4. Focus on quantifiable achievements when possible
        5. Ensure ATS-friendly language

        Enhanced Summary:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            enhanced_summary = response.choices[0].message.content.strip()
            self.logger.info("Successfully enhanced resume summary using Groq")
            return enhanced_summary
            
        except Exception as e:
            self.logger.error(f"Error enhancing summary with Groq: {e}")
            return current_summary
    
    def optimize_job_descriptions(self, job_descriptions: List[Dict[str, Any]], target_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Optimize job descriptions for better ATS alignment.
        
        Args:
            job_descriptions: List of job description dictionaries
            target_keywords: Keywords to incorporate
            
        Returns:
            List of optimized job descriptions
        """
        optimized_descriptions = []
        
        for job_desc in job_descriptions:
            original_desc = job_desc.get('description', '')
            
            prompt = f"""
            You are an expert resume optimizer. Rewrite the following job description to better align with ATS systems and target keywords while maintaining accuracy and authenticity.

            Original Description:
            {original_desc}

            Target Keywords to Incorporate:
            {', '.join(target_keywords)}

            Instructions:
            1. Incorporate target keywords naturally where relevant
            2. Use action verbs and quantifiable achievements
            3. Maintain truthfulness - don't add false information
            4. Keep the same general length and structure
            5. Use ATS-friendly language and formatting
            6. Focus on impact and results

            Optimized Description:
            """
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=800
                )
                
                optimized_desc = response.choices[0].message.content.strip()
                
                # Create optimized job description
                optimized_job = job_desc.copy()
                optimized_job['description'] = optimized_desc
                optimized_job['optimized_by_groq'] = True
                optimized_job['optimization_timestamp'] = datetime.now().isoformat()
                
                optimized_descriptions.append(optimized_job)
                self.logger.info(f"Optimized job description for {job_desc.get('title', 'Unknown')}")
                
            except Exception as e:
                self.logger.error(f"Error optimizing job description with Groq: {e}")
                optimized_descriptions.append(job_desc)
        
        return optimized_descriptions
    
    def generate_skill_recommendations(self, current_skills: List[str], job_requirements: List[str]) -> Dict[str, Any]:
        """
        Generate skill recommendations based on job requirements.
        
        Args:
            current_skills: List of current skills
            job_requirements: List of job requirements
            
        Returns:
            Dictionary with skill recommendations
        """
        prompt = f"""
        You are a career advisor analyzing skill gaps. Based on the current skills and job requirements, provide recommendations for skill development.

        Current Skills:
        {', '.join(current_skills)}

        Job Requirements:
        {', '.join(job_requirements)}

        Provide a JSON response with the following structure:
        {{
            "missing_critical_skills": ["skill1", "skill2"],
            "recommended_additions": ["skill3", "skill4"],
            "skill_priorities": {{
                "high": ["urgent_skill1"],
                "medium": ["important_skill1"],
                "low": ["nice_to_have1"]
            }},
            "learning_suggestions": {{
                "skill_name": "learning_resource_or_method"
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                recommendations = json.loads(recommendations_text)
            except json.JSONDecodeError:
                # Fallback to basic recommendations if JSON parsing fails
                recommendations = {
                    "missing_critical_skills": [],
                    "recommended_additions": [],
                    "skill_priorities": {"high": [], "medium": [], "low": []},
                    "learning_suggestions": {}
                }
            
            self.logger.info("Generated skill recommendations using Groq")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating skill recommendations with Groq: {e}")
            return {
                "missing_critical_skills": [],
                "recommended_additions": [],
                "skill_priorities": {"high": [], "medium": [], "low": []},
                "learning_suggestions": {},
                "error": str(e)
            }
    
    def analyze_job_posting(self, job_posting_text: str) -> Dict[str, Any]:
        """
        Analyze job posting to extract key information.
        
        Args:
            job_posting_text: Raw job posting text
            
        Returns:
            Dictionary with analyzed job information
        """
        prompt = f"""
        You are an expert job market analyzer. Analyze the following job posting and extract key information in JSON format.

        Job Posting:
        {job_posting_text}

        Provide a JSON response with the following structure:
        {{
            "job_title": "extracted job title",
            "company": "company name",
            "location": "job location",
            "employment_type": "full-time/part-time/contract",
            "experience_level": "entry/mid/senior/executive",
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill3", "skill4"],
            "key_responsibilities": ["responsibility1", "responsibility2"],
            "qualifications": ["qualification1", "qualification2"],
            "salary_range": "salary information if available",
            "benefits": ["benefit1", "benefit2"],
            "company_culture_keywords": ["keyword1", "keyword2"],
            "ats_keywords": ["important keyword1", "important keyword2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback analysis if JSON parsing fails
                analysis = {
                    "job_title": "Unknown",
                    "company": "Unknown",
                    "required_skills": [],
                    "ats_keywords": [],
                    "error": "Failed to parse analysis"
                }
            
            analysis["analyzed_by_groq"] = True
            analysis["analysis_timestamp"] = datetime.now().isoformat()
            
            self.logger.info("Successfully analyzed job posting using Groq")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing job posting with Groq: {e}")
            return {
                "job_title": "Unknown",
                "company": "Unknown", 
                "required_skills": [],
                "ats_keywords": [],
                "error": str(e)
            }
    
    def generate_cover_letter_points(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[str]:
        """
        Generate cover letter talking points.
        
        Args:
            resume_data: Resume information
            job_data: Job posting information
            
        Returns:
            List of cover letter talking points
        """
        prompt = f"""
        You are an expert career counselor. Generate 3-5 compelling talking points for a cover letter based on the resume and job posting.

        Resume Summary:
        Name: {resume_data.get('name', 'Candidate')}
        Experience: {len(resume_data.get('experience', []))} positions
        Skills: {', '.join(resume_data.get('skills', {}).get('programming_languages', [])[:5])}

        Job Information:
        Title: {job_data.get('job_title', 'Position')}
        Company: {job_data.get('company', 'Company')}
        Requirements: {', '.join(job_data.get('keywords', [])[:10])}

        Generate 3-5 specific talking points that:
        1. Connect candidate's experience to job requirements
        2. Highlight relevant achievements
        3. Show enthusiasm for the role/company
        4. Demonstrate value proposition
        5. Are specific and quantifiable when possible

        Format as a simple list of talking points.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=800
            )
            
            points_text = response.choices[0].message.content.strip()
            
            # Split into individual points
            points = [point.strip() for point in points_text.split('\n') if point.strip()]
            
            self.logger.info("Generated cover letter points using Groq")
            return points
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter points with Groq: {e}")
            return [
                "Highlight relevant experience and skills",
                "Demonstrate enthusiasm for the role",
                "Show alignment with company values",
                "Quantify achievements where possible"
            ]
    
    def check_api_status(self) -> Dict[str, Any]:
        """
        Check Groq API status and connectivity.
        
        Returns:
            Dictionary with API status information
        """
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            return {
                "status": "connected",
                "model": self.model,
                "response_time": "< 1s",
                "test_successful": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "model": self.model,
                "error": str(e),
                "test_successful": False
            }


# Global helper instance (initialized when needed)
_groq_helper = None


def get_groq_helper() -> Optional[GroqHelper]:
    """
    Get global Groq helper instance.
    
    Returns:
        GroqHelper instance or None if not available
    """
    global _groq_helper
    
    if _groq_helper is None:
        try:
            if config.GROQ_API_KEY:
                _groq_helper = GroqHelper()
            else:
                logging.warning("Groq API key not configured")
                return None
        except Exception as e:
            logging.error(f"Failed to initialize Groq helper: {e}")
            return None
    
    return _groq_helper


def enhance_with_groq(content: str, enhancement_type: str, context: Dict[str, Any] = None) -> str:
    """
    Convenience function to enhance content using Groq.
    
    Args:
        content: Content to enhance
        enhancement_type: Type of enhancement (summary, description, etc.)
        context: Additional context for enhancement
        
    Returns:
        Enhanced content or original if enhancement fails
    """
    helper = get_groq_helper()
    if not helper:
        return content
    
    context = context or {}
    
    try:
        if enhancement_type == "summary":
            job_requirements = context.get("job_requirements", [])
            return helper.enhance_resume_summary(content, job_requirements)
        
        elif enhancement_type == "job_description":
            target_keywords = context.get("target_keywords", [])
            job_data = {"description": content}
            optimized = helper.optimize_job_descriptions([job_data], target_keywords)
            return optimized[0]["description"] if optimized else content
        
        else:
            logging.warning(f"Unknown enhancement type: {enhancement_type}")
            return content
    
    except Exception as e:
        logging.error(f"Error enhancing content with Groq: {e}")
        return content


def main():
    """
    Test function for Groq helper.
    """
    print("Groq Helper Test")
    print("=" * 30)
    
    if not GROQ_AVAILABLE:
        print("❌ Groq package not available")
        return
    
    if not config.GROQ_API_KEY:
        print("❌ Groq API key not configured")
        return
    
    try:
        helper = GroqHelper()
        
        # Test API status
        status = helper.check_api_status()
        print(f"API Status: {status}")
        
        if status["test_successful"]:
            print("✅ Groq API connection successful")
            
            # Test enhancement
            test_summary = "Software engineer with experience in web development."
            test_requirements = ["React", "Node.js", "AWS", "Agile"]
            
            enhanced = helper.enhance_resume_summary(test_summary, test_requirements)
            print(f"\nOriginal: {test_summary}")
            print(f"Enhanced: {enhanced}")
        else:
            print("❌ Groq API connection failed")
    
    except Exception as e:
        print(f"❌ Error testing Groq helper: {e}")


if __name__ == "__main__":
    main()
