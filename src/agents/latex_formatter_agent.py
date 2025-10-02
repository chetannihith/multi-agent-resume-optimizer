"""
LaTeXFormatterAgent - Generates Overleaf-compatible LaTeX resumes.

This module contains the LaTeXFormatterAgent class that takes optimized resume
JSON data and generates professional LaTeX resumes using templates that are
fully compatible with Overleaf for easy rendering and editing.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging


class LaTeXFormatterAgent:
    """
    Agent for generating LaTeX resumes from optimized resume data.
    
    This agent processes optimized resume JSON data and generates professional
    LaTeX documents using customizable templates that are fully compatible
    with Overleaf for seamless online editing and compilation.
    """
    
    def __init__(
        self,
        template_path: str = "templates/resume_template.tex",
        output_directory: str = "output",
        default_template_style: str = "professional"
    ):
        """
        Initialize the LaTeXFormatterAgent.
        
        Args:
            template_path: Path to the LaTeX template file
            output_directory: Directory to save generated LaTeX files
            default_template_style: Default template style to use
        """
        self.template_path = template_path
        self.output_directory = output_directory
        self.default_template_style = default_template_style
        
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def escape_latex_special_chars(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Input text that may contain special characters
            
        Returns:
            Text with LaTeX special characters properly escaped
        """
        if not text:
            return ""
        
        # Convert to string and handle backslashes first to avoid double escaping
        escaped_text = str(text)
        
        # Replace backslashes first to avoid conflicts
        escaped_text = escaped_text.replace('\\', r'\textbackslash{}')
        
        # Dictionary of other LaTeX special characters and their escaped versions
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
        }
        
        # Escape each special character
        for char, escaped_char in latex_special_chars.items():
            escaped_text = escaped_text.replace(char, escaped_char)
        
        return escaped_text
    
    def format_skills_by_category(self, skills_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Format skills data into categorized format for LaTeX template.
        
        Args:
            skills_data: Skills data from optimized resume
            
        Returns:
            List of skill categories with formatted skill lists
        """
        categories = []
        
        if isinstance(skills_data, dict):
            # Check if we have categorized skills
            if 'skill_categories' in skills_data:
                skill_categories = skills_data['skill_categories']
                for category, skills in skill_categories.items():
                    if skills and category != 'other':  # Skip empty categories and 'other'
                        category_name = category.replace('_', ' ').title()
                        skills_list = ', '.join(skills[:8])  # Limit to 8 skills per category
                        categories.append({
                            'CATEGORY_NAME': self.escape_latex_special_chars(category_name),
                            'SKILLS_LIST': self.escape_latex_special_chars(skills_list)
                        })
            
            # If no categories or categories are empty, use aligned_skills
            if not categories and 'aligned_skills' in skills_data:
                aligned_skills = skills_data['aligned_skills']
                if aligned_skills:
                    # Group skills into technical and other
                    technical_keywords = {
                        'python', 'java', 'javascript', 'react', 'node', 'sql', 
                        'aws', 'docker', 'kubernetes', 'git', 'linux', 'mongodb'
                    }
                    
                    technical_skills = []
                    other_skills = []
                    
                    for skill in aligned_skills[:15]:  # Limit total skills
                        if any(tech in skill.lower() for tech in technical_keywords):
                            technical_skills.append(skill)
                        else:
                            other_skills.append(skill)
                    
                    if technical_skills:
                        categories.append({
                            'CATEGORY_NAME': 'Technical Skills',
                            'SKILLS_LIST': self.escape_latex_special_chars(', '.join(technical_skills))
                        })
                    
                    if other_skills:
                        categories.append({
                            'CATEGORY_NAME': 'Additional Skills',
                            'SKILLS_LIST': self.escape_latex_special_chars(', '.join(other_skills))
                        })
        
        # Default category if no skills found
        if not categories:
            categories.append({
                'CATEGORY_NAME': 'Skills',
                'SKILLS_LIST': 'Programming, Problem Solving, Team Collaboration'
            })
        
        return categories
    
    def format_experience_entries(self, experience_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format experience data for LaTeX template.
        
        Args:
            experience_data: Experience data from optimized resume
            
        Returns:
            List of formatted experience entries
        """
        formatted_entries = []
        
        for exp in experience_data[:5]:  # Limit to 5 most recent experiences
            if not isinstance(exp, dict):
                continue
            
            # Extract basic information
            job_title = exp.get('title', 'Position')
            company = exp.get('company', 'Company')
            duration = exp.get('duration', 'Dates')
            location = exp.get('location', '')
            
            # Parse duration into start and end dates
            start_date, end_date = self._parse_duration(duration)
            
            # Format job description
            description = exp.get('aligned_description') or exp.get('description', '')
            description_items = self._format_job_description(description)
            
            formatted_entry = {
                'START_DATE': self.escape_latex_special_chars(start_date),
                'END_DATE': self.escape_latex_special_chars(end_date),
                'JOB_TITLE': self.escape_latex_special_chars(job_title),
                'COMPANY_NAME': self.escape_latex_special_chars(company),
                'LOCATION': self.escape_latex_special_chars(location),
                'JOB_DESCRIPTIONS': [{
                    'DESCRIPTION_ITEMS': description_items
                }] if description_items else []
            }
            
            formatted_entries.append(formatted_entry)
        
        # Add default entry if no experience
        if not formatted_entries:
            formatted_entries.append({
                'START_DATE': 'Present',
                'END_DATE': '',
                'JOB_TITLE': 'Recent Graduate',
                'COMPANY_NAME': 'Seeking Opportunities',
                'LOCATION': '',
                'JOB_DESCRIPTIONS': [{
                    'DESCRIPTION_ITEMS': [
                        {'DESCRIPTION_ITEM': 'Completed relevant coursework and projects'},
                        {'DESCRIPTION_ITEM': 'Developed technical skills through academic and personal projects'}
                    ]
                }]
            })
        
        return formatted_entries
    
    def _parse_duration(self, duration: str) -> tuple:
        """
        Parse duration string into start and end dates.
        
        Args:
            duration: Duration string (e.g., "2021-2024", "Jan 2021 - Present")
            
        Returns:
            Tuple of (start_date, end_date)
        """
        if not duration:
            return "Present", ""
        
        # Common patterns for duration
        duration = str(duration).strip()
        
        # Pattern: "2021-2024" or "2021 - 2024"
        if re.match(r'\d{4}\s*-\s*\d{4}', duration):
            parts = re.split(r'\s*-\s*', duration)
            return parts[0], parts[1]
        
        # Pattern: "2021-Present" or "2021 - Present"
        if 'present' in duration.lower():
            start = re.search(r'\d{4}', duration)
            return start.group() if start else "Recent", "Present"
        
        # Pattern: "Jan 2021 - Dec 2024"
        if ' - ' in duration:
            parts = duration.split(' - ')
            return parts[0], parts[1]
        
        # Single year or other format
        return duration, ""
    
    def _format_job_description(self, description: str) -> List[Dict[str, str]]:
        """
        Format job description into bullet points.
        
        Args:
            description: Job description text
            
        Returns:
            List of description items for LaTeX template
        """
        if not description:
            return []
        
        # Split description into sentences or bullet points
        sentences = []
        
        # Check if already has bullet points
        if '•' in description or '*' in description or '-' in description:
            # Split by bullet point indicators
            lines = re.split(r'[•\*\-]\s*', description)
            sentences = [line.strip() for line in lines if line.strip()]
        else:
            # Split by periods and create bullet points
            sentences = [s.strip() + '.' for s in description.split('.') if s.strip()]
        
        # Format as LaTeX items
        description_items = []
        for sentence in sentences[:4]:  # Limit to 4 bullet points
            if sentence:
                description_items.append({
                    'DESCRIPTION_ITEM': self.escape_latex_special_chars(sentence)
                })
        
        return description_items
    
    def format_education_entries(self, education_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format education data for LaTeX template.
        
        Args:
            education_data: Education data from optimized resume
            
        Returns:
            List of formatted education entries
        """
        formatted_entries = []
        
        for edu in education_data[:3]:  # Limit to 3 education entries
            if not isinstance(edu, dict):
                continue
            
            degree = edu.get('degree', 'Degree')
            field = edu.get('field', '')
            institution = edu.get('institution', 'Institution')
            year = edu.get('year', 'Year')
            location = edu.get('location', '')
            gpa = edu.get('gpa', '')
            
            # Format degree and field
            degree_field = f"{degree} in {field}" if field else degree
            
            # Format GPA info
            gpa_info = f"GPA: {gpa}" if gpa else ""
            
            formatted_entry = {
                'GRADUATION_YEAR': self.escape_latex_special_chars(str(year)),
                'DEGREE_TYPE': self.escape_latex_special_chars(degree_field),
                'INSTITUTION_NAME': self.escape_latex_special_chars(institution),
                'LOCATION': self.escape_latex_special_chars(location),
                'GPA_INFO': self.escape_latex_special_chars(gpa_info),
                'ADDITIONAL_INFO': ''
            }
            
            formatted_entries.append(formatted_entry)
        
        # Add default entry if no education
        if not formatted_entries:
            formatted_entries.append({
                'GRADUATION_YEAR': 'Year',
                'DEGREE_TYPE': 'Degree in Field of Study',
                'INSTITUTION_NAME': 'University Name',
                'LOCATION': 'City, State',
                'GPA_INFO': '',
                'ADDITIONAL_INFO': ''
            })
        
        return formatted_entries
    
    def format_projects_entries(self, projects_data: List[Dict[str, Any]]) -> tuple:
        """
        Format projects data for LaTeX template.
        
        Args:
            projects_data: Projects data from optimized resume
            
        Returns:
            Tuple of (has_projects, formatted_projects)
        """
        if not projects_data:
            return False, []
        
        formatted_projects = []
        
        for project in projects_data[:3]:  # Limit to 3 projects
            if not isinstance(project, dict):
                continue
            
            name = project.get('name', 'Project Name')
            description = project.get('description', '')
            technologies = project.get('technologies', '')
            impact = project.get('impact', '')
            date = project.get('date', 'Recent')
            
            formatted_project = {
                'PROJECT_DATE': self.escape_latex_special_chars(str(date)),
                'PROJECT_NAME': self.escape_latex_special_chars(name),
                'PROJECT_ORGANIZATION': '',  # Can be added if available
                'PROJECT_DESCRIPTION': self.escape_latex_special_chars(description),
                'PROJECT_TECHNOLOGIES': [{'TECHNOLOGIES_LIST': self.escape_latex_special_chars(technologies)}] if technologies else [],
                'PROJECT_IMPACT': [{'IMPACT_DESCRIPTION': self.escape_latex_special_chars(impact)}] if impact else []
            }
            
            formatted_projects.append(formatted_project)
        
        return len(formatted_projects) > 0, formatted_projects
    
    def extract_personal_info(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract personal information from resume data.
        
        Args:
            resume_data: Complete resume data
            
        Returns:
            Dictionary with personal information placeholders
        """
        # Extract name
        name = resume_data.get('name', 'Your Name')
        name_parts = name.split(' ', 1) if name else ['Your', 'Name']
        first_name = name_parts[0] if len(name_parts) > 0 else 'Your'
        last_name = name_parts[1] if len(name_parts) > 1 else 'Name'
        
        # Extract job title
        job_title = resume_data.get('job_title', 'Professional Title')
        
        # Default personal information (can be customized)
        personal_info = {
            'FIRST_NAME': self.escape_latex_special_chars(first_name),
            'LAST_NAME': self.escape_latex_special_chars(last_name),
            'JOB_TITLE': self.escape_latex_special_chars(job_title),
            'ADDRESS_LINE1': '123 Main Street',
            'ADDRESS_LINE2': 'Apt 4B',
            'CITY_STATE_ZIP': 'City, State 12345',
            'PHONE_NUMBER': '+1 (555) 123-4567',
            'EMAIL_ADDRESS': 'your.email@example.com',
            'WEBSITE': 'www.yourwebsite.com',
            'LINKEDIN_USERNAME': 'yourlinkedin',
            'GITHUB_USERNAME': 'yourgithub',
            'OBJECTIVE_QUOTE': 'Dedicated professional seeking to contribute expertise and drive innovation.'
        }
        
        return personal_info
    
    def _replace_template_section(self, content: str, start_marker: str, end_marker: str, replacement: str) -> str:
        """
        Replace a template section with new content.
        
        Args:
            content: Template content
            start_marker: Start marker (e.g., '{{#SECTION}}')
            end_marker: End marker (e.g., '{{/SECTION}}')
            replacement: Replacement content
            
        Returns:
            Content with section replaced
        """
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            before = content[:start_pos]
            after = content[end_pos + len(end_marker):]
            return before + replacement + after
        
        return content
    
    def populate_template(self, template_content: str, resume_data: Dict[str, Any]) -> str:
        """
        Populate LaTeX template with resume data.
        
        Args:
            template_content: LaTeX template content
            resume_data: Optimized resume data
            
        Returns:
            LaTeX content with populated placeholders
        """
        try:
            # Extract data sections
            aligned_sections = resume_data.get('aligned_sections', {})
            
            # Get personal information
            personal_info = self.extract_personal_info(resume_data)
            
            # Get professional summary
            summary = aligned_sections.get('summary', 'Experienced professional with strong technical skills and proven track record of success.')
            
            # Format different sections
            skills_categories = self.format_skills_by_category(aligned_sections.get('skills', {}))
            experience_entries = self.format_experience_entries(aligned_sections.get('experience', []))
            education_entries = self.format_education_entries(aligned_sections.get('education', []))
            
            # Handle projects (optional)
            has_projects, project_entries = self.format_projects_entries(
                resume_data.get('relevant_projects', []) or aligned_sections.get('projects', [])
            )
            
            # Start with personal information
            populated_content = template_content
            for key, value in personal_info.items():
                populated_content = populated_content.replace(f'{{{{{key}}}}}', value)
            
            # Add professional summary
            populated_content = populated_content.replace(
                '{{{PROFESSIONAL_SUMMARY}}}', 
                self.escape_latex_special_chars(summary)
            )
            
            # Handle skills categories
            if skills_categories:
                skills_section = ""
                for category in skills_categories:
                    skills_section += f"\\cvitem{{{category['CATEGORY_NAME']}}}{{{category['SKILLS_LIST']}}}\n"
                
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#SKILLS_CATEGORIES}}', 
                    '{{/SKILLS_CATEGORIES}}',
                    skills_section.strip()
                )
            else:
                # Remove skills section if no skills
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#SKILLS_CATEGORIES}}', 
                    '{{/SKILLS_CATEGORIES}}',
                    ''
                )
            
            # Handle experience entries
            if experience_entries:
                experience_section = ""
                for exp in experience_entries:
                    exp_entry = f"\\cventry{{{exp['START_DATE']}--{exp['END_DATE']}}}{{{exp['JOB_TITLE']}}}{{{exp['COMPANY_NAME']}}}{{{exp['LOCATION']}}}{{}}{{%\n"
                    
                    if exp['JOB_DESCRIPTIONS']:
                        exp_entry += "\\begin{itemize}\n"
                        for desc in exp['JOB_DESCRIPTIONS']:
                            for item in desc['DESCRIPTION_ITEMS']:
                                exp_entry += f"\\item {item['DESCRIPTION_ITEM']}\n"
                        exp_entry += "\\end{itemize}\n"
                    
                    exp_entry += "}\n"
                    experience_section += exp_entry
                
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#EXPERIENCE_ENTRIES}}', 
                    '{{/EXPERIENCE_ENTRIES}}',
                    experience_section.strip()
                )
            else:
                # Remove experience section if no experience
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#EXPERIENCE_ENTRIES}}', 
                    '{{/EXPERIENCE_ENTRIES}}',
                    ''
                )
            
            # Handle education entries
            if education_entries:
                education_section = ""
                for edu in education_entries:
                    education_section += f"\\cventry{{{edu['GRADUATION_YEAR']}}}{{{edu['DEGREE_TYPE']}}}{{{edu['INSTITUTION_NAME']}}}{{{edu['LOCATION']}}}{{{edu['GPA_INFO']}}}{{{edu['ADDITIONAL_INFO']}}}\n"
                
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#EDUCATION_ENTRIES}}', 
                    '{{/EDUCATION_ENTRIES}}',
                    education_section.strip()
                )
            else:
                # Remove education section if no education
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#EDUCATION_ENTRIES}}', 
                    '{{/EDUCATION_ENTRIES}}',
                    ''
                )
            
            # Handle projects section
            if has_projects and project_entries:
                projects_section = ""
                for project in project_entries:
                    proj_entry = f"\\cventry{{{project['PROJECT_DATE']}}}{{{project['PROJECT_NAME']}}}{{{project['PROJECT_ORGANIZATION']}}}{{}}{{}}{{%\n"
                    proj_entry += f"{project['PROJECT_DESCRIPTION']}\n"
                    
                    if project['PROJECT_TECHNOLOGIES']:
                        proj_entry += f"\\newline\\textbf{{Technologies:}} {project['PROJECT_TECHNOLOGIES'][0]['TECHNOLOGIES_LIST']}\n"
                    
                    if project['PROJECT_IMPACT']:
                        proj_entry += f"\\newline\\textbf{{Impact:}} {project['PROJECT_IMPACT'][0]['IMPACT_DESCRIPTION']}\n"
                    
                    proj_entry += "}\n"
                    projects_section += proj_entry
                
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#HAS_PROJECTS}}', 
                    '{{/HAS_PROJECTS}}',
                    f"\\section{{Key Projects}}\n{projects_section.strip()}"
                )
            else:
                # Remove projects section
                populated_content = self._replace_template_section(
                    populated_content, 
                    '{{#HAS_PROJECTS}}', 
                    '{{/HAS_PROJECTS}}',
                    ''
                )
            
            # Remove unused optional sections
            optional_sections = [
                'HAS_CERTIFICATIONS', 'HAS_AWARDS', 'HAS_LANGUAGES', 'HAS_ADDITIONAL_INFO'
            ]
            
            for section in optional_sections:
                populated_content = self._replace_template_section(
                    populated_content, 
                    f'{{{{#{section}}}}}', 
                    f'{{{{/{section}}}}}',
                    ''
                )
            
            # Clean up any remaining template syntax (simple placeholders)
            import re
            populated_content = re.sub(r'{{[^}]*}}', '', populated_content)
            
            return populated_content
            
        except Exception as e:
            self.logger.error(f"Error populating template: {e}")
            raise
    
    def generate_latex_resume(self, optimized_resume: Dict[str, Any], output_filename: Optional[str] = None) -> str:
        """
        Generate LaTeX resume from optimized resume data.
        
        Args:
            optimized_resume: Optimized resume data from ATSOptimizerAgent
            output_filename: Optional custom filename for output
            
        Returns:
            Path to the generated LaTeX file
        """
        try:
            # Load template
            if not os.path.exists(self.template_path):
                raise FileNotFoundError(f"Template file not found: {self.template_path}")
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Populate template with resume data
            latex_content = self.populate_template(template_content, optimized_resume)
            
            # Generate output filename
            if not output_filename:
                profile_id = optimized_resume.get('profile_id', 'resume')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"{profile_id}_{timestamp}.tex"
            
            # Ensure .tex extension
            if not output_filename.endswith('.tex'):
                output_filename += '.tex'
            
            # Write to output file
            output_path = os.path.join(self.output_directory, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            self.logger.info(f"Generated LaTeX resume: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating LaTeX resume: {e}")
            raise
    
    def validate_overleaf_compatibility(self, latex_content: str) -> Dict[str, Any]:
        """
        Validate that LaTeX content is compatible with Overleaf.
        
        Args:
            latex_content: LaTeX content to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'is_compatible': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for unsupported packages
        unsupported_packages = [
            'pstricks', 'tikz-3dplot', 'asymptote', 'sagetex', 'pythontex'
        ]
        
        for package in unsupported_packages:
            if f'\\usepackage{{{package}}}' in latex_content:
                validation_results['warnings'].append(f"Package '{package}' may not be supported in all Overleaf configurations")
        
        # Check for custom commands that might cause issues
        if '\\newcommand' in latex_content:
            validation_results['warnings'].append("Custom commands detected - ensure they are compatible with Overleaf")
        
        # Check for file inclusions
        if '\\input{' in latex_content or '\\include{' in latex_content:
            validation_results['warnings'].append("File inclusions detected - ensure all referenced files are uploaded to Overleaf")
        
        return validation_results


def main():
    """
    Main function for testing the LaTeXFormatterAgent.
    """
    print("LaTeXFormatterAgent Test")
    print("=" * 50)
    
    # Create dummy optimized resume data
    dummy_optimized_resume = {
        "profile_id": "john_doe_2024",
        "job_title": "Senior Python Developer",
        "name": "John Doe",
        "ats_analysis": {
            "ats_score": 95,
            "category": "Excellent"
        },
        "aligned_sections": {
            "summary": "Experienced Python developer with 5+ years of expertise in web development, API design, and cloud deployment. Proven track record of building scalable applications using Django, Flask, and modern DevOps practices. Strong background in database design, system architecture, and team leadership.",
            "skills": {
                "aligned_skills": [
                    "Python", "Django", "Flask", "PostgreSQL", "Redis",
                    "AWS", "Docker", "Kubernetes", "Git", "REST APIs",
                    "JavaScript", "React", "Linux", "CI/CD", "Microservices"
                ],
                "skill_categories": {
                    "technical": ["Python", "Django", "Flask", "PostgreSQL", "JavaScript", "React"],
                    "tools": ["Git", "Docker", "Kubernetes", "AWS", "Linux"],
                    "other": ["REST APIs", "Microservices", "CI/CD", "Redis"]
                }
            },
            "experience": [
                {
                    "title": "Senior Python Developer",
                    "company": "TechCorp Inc.",
                    "duration": "2021-2024",
                    "location": "San Francisco, CA",
                    "description": "Led development of microservices architecture using Python and Django. Implemented REST APIs serving 1M+ requests daily. Deployed applications on AWS using Docker and Kubernetes. Mentored junior developers and conducted code reviews.",
                    "aligned_description": "Led development of scalable microservices architecture using Python and Django framework. Designed and implemented high-performance REST APIs serving over 1 million requests daily. Successfully deployed and managed applications on AWS cloud infrastructure using Docker containers and Kubernetes orchestration. Provided technical mentorship to junior developers and established code review best practices."
                },
                {
                    "title": "Python Developer",
                    "company": "WebSolutions Ltd.",
                    "duration": "2019-2021",
                    "location": "Austin, TX",
                    "description": "Built web applications using Flask framework. Integrated third-party APIs and payment systems. Optimized database queries and improved application performance by 40%.",
                    "aligned_description": "Developed robust web applications using Flask framework with focus on performance and scalability. Successfully integrated multiple third-party APIs and payment processing systems. Optimized PostgreSQL database queries and implemented caching strategies, resulting in 40% improvement in application performance."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "Tech University",
                    "year": "2019",
                    "location": "Boston, MA",
                    "gpa": "3.7"
                }
            ]
        },
        "relevant_projects": [
            {
                "name": "E-commerce API Platform",
                "description": "Developed comprehensive REST API for e-commerce platform handling product catalog, user management, and order processing",
                "technologies": "Python, Django, PostgreSQL, Redis, AWS, Docker",
                "impact": "Reduced API response time by 60% and supported 10x user growth",
                "date": "2023"
            },
            {
                "name": "Real-time Analytics Dashboard",
                "description": "Built real-time data processing pipeline and visualization dashboard for business metrics",
                "technologies": "Python, Flask, React, WebSocket, PostgreSQL",
                "impact": "Enabled real-time decision making for business stakeholders",
                "date": "2022"
            }
        ]
    }
    
    # Initialize the agent
    agent = LaTeXFormatterAgent(
        template_path="templates/resume_template.tex",
        output_directory="output"
    )
    
    print(f"Profile: {dummy_optimized_resume['name']} ({dummy_optimized_resume['profile_id']})")
    print(f"Job Title: {dummy_optimized_resume['job_title']}")
    print(f"ATS Score: {dummy_optimized_resume['ats_analysis']['ats_score']}/100")
    print()
    
    try:
        # Generate LaTeX resume
        print("Generating LaTeX resume...")
        output_path = agent.generate_latex_resume(dummy_optimized_resume, "resume.tex")
        
        # Get absolute path for display
        absolute_path = os.path.abspath(output_path)
        
        print("LaTeX Resume Generated Successfully!")
        print("=" * 40)
        print(f"File path: {absolute_path}")
        print()
        print("Instructions: Upload this file to Overleaf for rendering and editing.")
        print()
        print("Overleaf Setup Steps:")
        print("1. Go to https://www.overleaf.com")
        print("2. Create a new project or open existing one")
        print("3. Upload the generated .tex file")
        print("4. Compile to generate PDF")
        print("5. Edit and customize as needed")
        print()
        
        # Validate Overleaf compatibility
        with open(output_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        validation = agent.validate_overleaf_compatibility(latex_content)
        print("Overleaf Compatibility Check:")
        print(f"  Compatible: {'YES' if validation['is_compatible'] else 'NO'}")
        
        if validation['warnings']:
            print("  Warnings:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        
        if validation['errors']:
            print("  Errors:")
            for error in validation['errors']:
                print(f"    - {error}")
        
        if not validation['warnings'] and not validation['errors']:
            print("  No compatibility issues detected!")
        
        # Show file size and content preview
        file_size = os.path.getsize(output_path)
        print(f"\nFile Details:")
        print(f"  Size: {file_size} bytes")
        print(f"  Lines: {len(latex_content.splitlines())}")
        
        # Show first few lines of generated content
        print(f"\nContent Preview (first 10 lines):")
        print("-" * 30)
        for i, line in enumerate(latex_content.splitlines()[:10], 1):
            print(f"{i:2d}: {line}")
        print("...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("LaTeXFormatterAgent test completed!")


if __name__ == "__main__":
    main()
