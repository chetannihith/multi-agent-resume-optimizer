"""
ContentAlignmentAgent - Rewrites applicant information to match job requirements.

This module contains the ContentAlignmentAgent class that processes applicant
profile data and job descriptions to create aligned resume content that
emphasizes relevant skills and experiences matching job requirements.
"""

import json
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import logging


class ContentAlignmentAgent:
    """
    Agent for aligning applicant content with job description requirements.
    
    This agent takes job description data and applicant profile information
    to create rewritten content that emphasizes alignment with job requirements
    through keyword matching and strategic rephrasing.
    """
    
    def __init__(
        self,
        keyword_weight: float = 1.0,
        experience_weight: float = 1.5,
        skills_weight: float = 1.2,
        min_keyword_length: int = 3
    ):
        """
        Initialize the ContentAlignmentAgent.
        
        Args:
            keyword_weight: Base weight for keyword matching
            experience_weight: Weight multiplier for experience matches
            skills_weight: Weight multiplier for skills matches
            min_keyword_length: Minimum length for keywords to consider
        """
        self.keyword_weight = keyword_weight
        self.experience_weight = experience_weight
        self.skills_weight = skills_weight
        self.min_keyword_length = min_keyword_length
        
        # Common stop words to exclude from keyword matching
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'or', 'but', 'not', 'this', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extract keywords from text, excluding stop words and short terms.
        
        Args:
            text: Input text to extract keywords from
            
        Returns:
            Set of extracted keywords in lowercase
        """
        if not text:
            return set()
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = {
            word for word in words 
            if len(word) >= self.min_keyword_length and word not in self.stop_words
        }
        
        return keywords
    
    def extract_job_keywords(self, job_data: Dict[str, Any]) -> Dict[str, Set[str]]:
        """
        Extract keywords from different sections of job description.
        
        Args:
            job_data: Dictionary containing job description data
            
        Returns:
            Dictionary with keywords categorized by section
        """
        job_keywords = {
            'title': set(),
            'skills': set(),
            'requirements': set(),
            'responsibilities': set(),
            'all': set()
        }
        
        # Handle None input
        if job_data is None:
            return job_keywords
        
        # Extract from job title
        if 'job_title' in job_data and job_data['job_title']:
            title_keywords = self.extract_keywords(job_data['job_title'])
            job_keywords['title'] = title_keywords
            job_keywords['all'].update(title_keywords)
        
        # Extract from skills
        if 'skills' in job_data and job_data['skills']:
            skills_text = ' '.join(job_data['skills']) if isinstance(job_data['skills'], list) else str(job_data['skills'])
            skills_keywords = self.extract_keywords(skills_text)
            job_keywords['skills'] = skills_keywords
            job_keywords['all'].update(skills_keywords)
        
        # Extract from requirements
        if 'requirements' in job_data and job_data['requirements']:
            req_text = ' '.join(job_data['requirements']) if isinstance(job_data['requirements'], list) else str(job_data['requirements'])
            req_keywords = self.extract_keywords(req_text)
            job_keywords['requirements'] = req_keywords
            job_keywords['all'].update(req_keywords)
        
        # Extract from responsibilities
        if 'responsibilities' in job_data and job_data['responsibilities']:
            resp_text = ' '.join(job_data['responsibilities']) if isinstance(job_data['responsibilities'], list) else str(job_data['responsibilities'])
            resp_keywords = self.extract_keywords(resp_text)
            job_keywords['responsibilities'] = resp_keywords
            job_keywords['all'].update(resp_keywords)
        
        return job_keywords
    
    def calculate_alignment_score(self, text: str, job_keywords: Set[str]) -> float:
        """
        Calculate alignment score between text and job keywords.
        
        Args:
            text: Text to analyze
            job_keywords: Set of job keywords to match against
            
        Returns:
            Alignment score between 0 and 1
        """
        if not text or not job_keywords:
            return 0.0
        
        text_keywords = self.extract_keywords(text)
        if not text_keywords:
            return 0.0
        
        # Calculate intersection
        matching_keywords = text_keywords.intersection(job_keywords)
        
        # Score based on percentage of job keywords found
        score = len(matching_keywords) / len(job_keywords) if job_keywords else 0.0
        
        return min(score, 1.0)  # Cap at 1.0
    
    def highlight_matching_experiences(
        self, 
        experiences: List[Dict[str, Any]], 
        job_keywords: Dict[str, Set[str]]
    ) -> List[Dict[str, Any]]:
        """
        Highlight and prioritize experiences that match job requirements.
        
        Args:
            experiences: List of experience dictionaries
            job_keywords: Job keywords categorized by section
            
        Returns:
            List of experiences with alignment scores and highlights
        """
        highlighted_experiences = []
        
        for exp in experiences:
            if not isinstance(exp, dict):
                continue
            
            # Create enhanced experience entry
            enhanced_exp = exp.copy()
            
            # Calculate alignment scores
            title_score = self.calculate_alignment_score(
                exp.get('title', ''), job_keywords['all']
            )
            desc_score = self.calculate_alignment_score(
                exp.get('description', ''), job_keywords['all']
            )
            
            # Overall alignment score
            alignment_score = (title_score + desc_score * 2) / 3  # Weight description more
            enhanced_exp['alignment_score'] = alignment_score
            
            # Find matching keywords
            exp_text = f"{exp.get('title', '')} {exp.get('description', '')}"
            exp_keywords = self.extract_keywords(exp_text)
            matching_keywords = exp_keywords.intersection(job_keywords['all'])
            enhanced_exp['matching_keywords'] = list(matching_keywords)
            
            # Rephrase description to emphasize alignment
            if 'description' in exp and exp['description']:
                enhanced_exp['aligned_description'] = self.rephrase_for_alignment(
                    exp['description'], job_keywords['all'], matching_keywords
                )
            
            highlighted_experiences.append(enhanced_exp)
        
        # Sort by alignment score (highest first)
        highlighted_experiences.sort(key=lambda x: x.get('alignment_score', 0), reverse=True)
        
        return highlighted_experiences
    
    def rephrase_for_alignment(
        self, 
        text: str, 
        job_keywords: Set[str], 
        matching_keywords: Set[str]
    ) -> str:
        """
        Rephrase text to emphasize alignment with job keywords.
        
        Args:
            text: Original text to rephrase
            job_keywords: All job keywords
            matching_keywords: Keywords that match in the text
            
        Returns:
            Rephrased text with emphasized alignment
        """
        if not text or not matching_keywords:
            return text
        
        rephrased = text
        
        # Emphasize matching keywords by ensuring they appear prominently
        for keyword in matching_keywords:
            # Find the keyword in text (case-insensitive)
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            
            # If keyword is found, ensure it's emphasized in context
            if pattern.search(rephrased):
                # Add emphasis phrases around matching keywords
                emphasis_phrases = [
                    f"specialized in {keyword}",
                    f"extensive experience with {keyword}",
                    f"proficient in {keyword}",
                    f"expertise in {keyword}"
                ]
                
                # Choose appropriate emphasis based on context
                if any(tech_word in keyword.lower() for tech_word in ['python', 'java', 'javascript', 'react', 'node']):
                    emphasis = f"extensive experience with {keyword}"
                elif any(skill_word in keyword.lower() for skill_word in ['machine', 'learning', 'data', 'analysis']):
                    emphasis = f"specialized in {keyword}"
                else:
                    emphasis = f"proficient in {keyword}"
                
                # Only add emphasis if not already present
                if emphasis.lower() not in rephrased.lower():
                    # Try to integrate naturally into existing text
                    if keyword.lower() in rephrased.lower():
                        continue  # Keyword already well-integrated
        
        # Add quantifiable achievements if missing
        if not any(char.isdigit() for char in rephrased):
            # Add generic quantifiable impact
            if 'developed' in rephrased.lower() or 'built' in rephrased.lower():
                rephrased += " resulting in improved system performance and efficiency"
            elif 'managed' in rephrased.lower() or 'led' in rephrased.lower():
                rephrased += " leading to successful project delivery and team productivity gains"
        
        return rephrased
    
    def align_skills_section(
        self, 
        applicant_skills: List[str], 
        job_keywords: Dict[str, Set[str]]
    ) -> Dict[str, Any]:
        """
        Align skills section with job requirements.
        
        Args:
            applicant_skills: List of applicant skills
            job_keywords: Job keywords categorized by section
            
        Returns:
            Dictionary with aligned skills information
        """
        if not applicant_skills:
            return {
                'aligned_skills': [],
                'matching_skills': [],
                'skill_categories': {},
                'alignment_score': 0.0
            }
        
        # Find matching skills
        applicant_skill_keywords = set()
        for skill in applicant_skills:
            applicant_skill_keywords.update(self.extract_keywords(skill))
        
        matching_skills = []
        skill_alignment_scores = {}
        
        for skill in applicant_skills:
            skill_keywords = self.extract_keywords(skill)
            alignment_score = self.calculate_alignment_score(skill, job_keywords['all'])
            skill_alignment_scores[skill] = alignment_score
            
            if alignment_score > 0 or any(kw in job_keywords['all'] for kw in skill_keywords):
                matching_skills.append(skill)
        
        # Sort skills by alignment score
        aligned_skills = sorted(applicant_skills, 
                              key=lambda s: skill_alignment_scores.get(s, 0), 
                              reverse=True)
        
        # Categorize skills
        skill_categories = {
            'technical': [],
            'soft': [],
            'tools': [],
            'other': []
        }
        
        technical_keywords = {'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes'}
        tool_keywords = {'git', 'jenkins', 'jira', 'confluence', 'slack', 'trello'}
        soft_keywords = {'leadership', 'communication', 'teamwork', 'problem', 'analytical'}
        
        for skill in aligned_skills:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in technical_keywords):
                skill_categories['technical'].append(skill)
            elif any(tool in skill_lower for tool in tool_keywords):
                skill_categories['tools'].append(skill)
            elif any(soft in skill_lower for soft in soft_keywords):
                skill_categories['soft'].append(skill)
            else:
                skill_categories['other'].append(skill)
        
        # Calculate overall alignment score
        total_alignment = sum(skill_alignment_scores.values())
        avg_alignment = total_alignment / len(applicant_skills) if applicant_skills else 0.0
        
        return {
            'aligned_skills': aligned_skills,
            'matching_skills': matching_skills,
            'skill_categories': skill_categories,
            'alignment_score': avg_alignment,
            'skill_scores': skill_alignment_scores
        }
    
    def generate_aligned_summary(
        self, 
        profile_data: Dict[str, Any], 
        job_data: Dict[str, Any],
        job_keywords: Dict[str, Set[str]]
    ) -> str:
        """
        Generate a professional summary aligned with job requirements.
        
        Args:
            profile_data: Applicant profile data
            job_data: Job description data
            job_keywords: Job keywords categorized by section
            
        Returns:
            Aligned professional summary
        """
        # Extract key information
        name = profile_data.get('name', 'Professional')
        job_title = job_data.get('job_title', 'the position')
        
        # Get top skills that match
        skills = profile_data.get('relevant_skills', profile_data.get('skills', []))
        if isinstance(skills, list) and len(skills) > 0:
            top_skills = skills[:3]  # Top 3 skills
        else:
            top_skills = []
        
        # Get years of experience (estimate from experience data)
        experiences = profile_data.get('relevant_experience', profile_data.get('experience', []))
        years_experience = len(experiences) * 2 if experiences else 3  # Rough estimate
        
        # Build summary components
        summary_parts = []
        
        # Opening statement
        if top_skills:
            skills_text = ', '.join(top_skills[:2])
            summary_parts.append(
                f"Experienced professional with {years_experience}+ years of expertise in {skills_text}"
            )
        else:
            summary_parts.append(
                f"Experienced professional with {years_experience}+ years in the field"
            )
        
        # Add job-specific alignment
        if 'machine learning' in job_keywords['all'] or 'ml' in job_keywords['all']:
            summary_parts.append(
                "Specialized in developing and deploying machine learning solutions"
            )
        elif 'web' in job_keywords['all'] or 'frontend' in job_keywords['all']:
            summary_parts.append(
                "Focused on building scalable web applications and user interfaces"
            )
        elif 'devops' in job_keywords['all'] or 'infrastructure' in job_keywords['all']:
            summary_parts.append(
                "Expert in cloud infrastructure and DevOps practices"
            )
        else:
            summary_parts.append(
                "Proven track record of delivering high-quality technical solutions"
            )
        
        # Add achievement statement
        summary_parts.append(
            "Demonstrated ability to work in collaborative environments and drive project success"
        )
        
        # Combine into coherent summary
        summary = '. '.join(summary_parts) + '.'
        
        return summary
    
    def align_content(
        self, 
        job_data: Dict[str, Any], 
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Align applicant content with job description requirements.
        
        Args:
            job_data: Dictionary containing job description data
            profile_data: Dictionary containing applicant profile data
            
        Returns:
            Dictionary containing aligned content sections
        """
        try:
            # Extract job keywords
            job_keywords = self.extract_job_keywords(job_data)
            
            # Get applicant data
            applicant_skills = profile_data.get('relevant_skills', profile_data.get('skills', []))
            applicant_experience = profile_data.get('relevant_experience', profile_data.get('experience', []))
            
            # Align skills section
            aligned_skills = self.align_skills_section(applicant_skills, job_keywords)
            
            # Highlight matching experiences
            highlighted_experiences = self.highlight_matching_experiences(
                applicant_experience, job_keywords
            )
            
            # Generate aligned summary
            aligned_summary = self.generate_aligned_summary(
                profile_data, job_data, job_keywords
            )
            
            # Calculate overall alignment score
            skills_score = aligned_skills.get('alignment_score', 0.0)
            exp_scores = [exp.get('alignment_score', 0.0) for exp in highlighted_experiences]
            avg_exp_score = sum(exp_scores) / len(exp_scores) if exp_scores else 0.0
            
            overall_alignment = (skills_score * self.skills_weight + avg_exp_score * self.experience_weight) / (self.skills_weight + self.experience_weight)
            
            # Prepare aligned content
            aligned_content = {
                'profile_id': profile_data.get('profile_id', 'unknown'),
                'job_title': job_data.get('job_title', 'Unknown Position'),
                'alignment_metadata': {
                    'overall_alignment_score': overall_alignment,
                    'skills_alignment_score': skills_score,
                    'experience_alignment_score': avg_exp_score,
                    'job_keywords_count': len(job_keywords['all']),
                    'matching_keywords': list(job_keywords['all'].intersection(
                        self.extract_keywords(' '.join(applicant_skills) if applicant_skills else '')
                    )),
                    'processed_at': datetime.now().isoformat()
                },
                'aligned_sections': {
                    'summary': aligned_summary,
                    'skills': aligned_skills,
                    'experience': highlighted_experiences[:5],  # Top 5 experiences
                    'job_keywords': {k: list(v) for k, v in job_keywords.items()}
                },
                'recommendations': self._generate_recommendations(
                    overall_alignment, aligned_skills, highlighted_experiences
                )
            }
            
            return aligned_content
            
        except Exception as e:
            self.logger.error(f"Error aligning content: {e}")
            return {
                'profile_id': profile_data.get('profile_id', 'error') if profile_data else 'error',
                'job_title': job_data.get('job_title', 'Unknown Position') if job_data else 'Unknown Position',
                'error': str(e),
                'alignment_metadata': {
                    'overall_alignment_score': 0.0,
                    'processed_at': datetime.now().isoformat()
                },
                'aligned_sections': {
                    'summary': 'Error generating summary',
                    'skills': {'aligned_skills': [], 'alignment_score': 0.0},
                    'experience': []
                },
                'recommendations': []
            }
    
    def _generate_recommendations(
        self, 
        overall_alignment: float,
        aligned_skills: Dict[str, Any],
        highlighted_experiences: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate recommendations for improving alignment.
        
        Args:
            overall_alignment: Overall alignment score
            aligned_skills: Aligned skills data
            highlighted_experiences: Highlighted experiences
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if overall_alignment < 0.3:
            recommendations.append("Consider emphasizing more relevant skills and experiences")
        elif overall_alignment < 0.6:
            recommendations.append("Good alignment - consider quantifying achievements")
        else:
            recommendations.append("Excellent alignment with job requirements")
        
        if aligned_skills.get('alignment_score', 0) < 0.4:
            recommendations.append("Add more technical skills that match job requirements")
        
        if not any(exp.get('alignment_score', 0) > 0.5 for exp in highlighted_experiences):
            recommendations.append("Rephrase experience descriptions to better match job keywords")
        
        if len(highlighted_experiences) < 2:
            recommendations.append("Include more relevant work experiences")
        
        return recommendations
    
    def to_json(self, aligned_content: Dict[str, Any]) -> str:
        """
        Convert aligned content to JSON string.
        
        Args:
            aligned_content: Dictionary containing aligned content
            
        Returns:
            JSON string representation
        """
        return json.dumps(aligned_content, indent=2, ensure_ascii=False)


def main():
    """
    Main function for testing the ContentAlignmentAgent.
    """
    print("ContentAlignmentAgent Test")
    print("=" * 50)
    
    # Sample job description data
    sample_job_data = {
        "job_title": "Senior Python Developer",
        "skills": [
            "Python", "Django", "Flask", "PostgreSQL", "Redis",
            "AWS", "Docker", "Kubernetes", "REST APIs", "Git"
        ],
        "requirements": [
            "5+ years Python development experience",
            "Experience with web frameworks like Django or Flask",
            "Knowledge of database systems (PostgreSQL, MySQL)",
            "Cloud platform experience (AWS, GCP, or Azure)",
            "Containerization experience with Docker"
        ],
        "responsibilities": [
            "Develop scalable web applications using Python",
            "Design and implement REST APIs",
            "Collaborate with cross-functional teams",
            "Optimize application performance and scalability",
            "Mentor junior developers"
        ]
    }
    
    # Sample applicant profile data (from ProfileRAGAgent)
    sample_profile_data = {
        "profile_id": "john_doe_2024",
        "name": "John Doe",
        "relevant_skills": [
            "Python", "JavaScript", "Django", "PostgreSQL", 
            "AWS", "Docker", "Git", "REST APIs", "Redis"
        ],
        "relevant_experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "duration": "2021-2024",
                "description": "Led development of web applications using Python and Django. Implemented REST APIs and managed PostgreSQL databases. Deployed applications on AWS using Docker containers."
            },
            {
                "title": "Python Developer",
                "company": "WebSolutions Ltd.",
                "duration": "2019-2021",
                "description": "Built scalable web services using Flask framework. Worked with Redis for caching and session management. Collaborated with frontend teams on API design."
            }
        ],
        "relevant_projects": [
            {
                "name": "E-commerce API Platform",
                "description": "Developed comprehensive REST API for e-commerce platform using Django and PostgreSQL",
                "technologies": "Python, Django, PostgreSQL, Redis, AWS"
            }
        ]
    }
    
    # Initialize the agent
    agent = ContentAlignmentAgent(
        keyword_weight=1.0,
        experience_weight=1.5,
        skills_weight=1.2
    )
    
    print(f"Job: {sample_job_data['job_title']}")
    print(f"Applicant: {sample_profile_data['name']} ({sample_profile_data['profile_id']})")
    print()
    
    try:
        # Test keyword extraction
        print("Job Keywords Extraction:")
        job_keywords = agent.extract_job_keywords(sample_job_data)
        for category, keywords in job_keywords.items():
            if keywords and category != 'all':
                print(f"  {category.title()}: {', '.join(list(keywords)[:5])}")
        print(f"  Total unique keywords: {len(job_keywords['all'])}")
        print()
        
        # Test content alignment
        print("Content Alignment Results:")
        print("-" * 30)
        
        aligned_content = agent.align_content(sample_job_data, sample_profile_data)
        
        # Display results
        metadata = aligned_content['alignment_metadata']
        print(f"Overall Alignment Score: {metadata['overall_alignment_score']:.3f}")
        print(f"Skills Alignment Score: {metadata['skills_alignment_score']:.3f}")
        print(f"Experience Alignment Score: {metadata['experience_alignment_score']:.3f}")
        print()
        
        # Show aligned summary
        print("Aligned Summary:")
        print(f"  {aligned_content['aligned_sections']['summary']}")
        print()
        
        # Show top aligned skills
        skills_data = aligned_content['aligned_sections']['skills']
        print(f"Top Aligned Skills ({len(skills_data['matching_skills'])} matching):")
        for skill in skills_data['aligned_skills'][:5]:
            score = skills_data['skill_scores'].get(skill, 0)
            print(f"  - {skill} (score: {score:.3f})")
        print()
        
        # Show top aligned experiences
        experiences = aligned_content['aligned_sections']['experience']
        print(f"Top Aligned Experiences:")
        for i, exp in enumerate(experiences[:2], 1):
            print(f"  {i}. {exp.get('title', 'N/A')} (score: {exp.get('alignment_score', 0):.3f})")
            print(f"     Matching keywords: {', '.join(exp.get('matching_keywords', []))}")
            if 'aligned_description' in exp:
                print(f"     Aligned description: {exp['aligned_description'][:100]}...")
        print()
        
        # Show recommendations
        print("Recommendations:")
        for rec in aligned_content['recommendations']:
            print(f"  - {rec}")
        print()
        
        # Show JSON output sample
        print("Sample JSON Output (truncated):")
        sample_output = {
            "profile_id": aligned_content["profile_id"],
            "overall_alignment_score": metadata["overall_alignment_score"],
            "aligned_summary": aligned_content["aligned_sections"]["summary"][:100] + "...",
            "top_skills": skills_data["aligned_skills"][:3],
            "recommendations_count": len(aligned_content["recommendations"])
        }
        print(json.dumps(sample_output, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("ContentAlignmentAgent test completed!")


if __name__ == "__main__":
    main()
