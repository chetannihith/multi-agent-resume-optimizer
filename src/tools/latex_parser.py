"""LaTeX Resume Parser - Extract structured data from LaTeX resume files.

This module provides tools to parse LaTeX resume content and convert it into
structured Pydantic models for validation and further processing.
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ResumeSection(BaseModel):
    """Base model for resume sections."""
    content: str
    items: List[str] = Field(default_factory=list)


class PersonalInfo(BaseModel):
    """Personal information from LaTeX resume."""
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    address: List[str] = Field(default_factory=list)
    website: str = ""
    linkedin: str = ""
    github: str = ""
    quote: str = ""


class Experience(BaseModel):
    """Work experience entry."""
    title: str
    company: str
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""
    degree: str
    institution: str
    location: str = ""
    graduation_year: str = ""
    gpa: str = ""
    additional_info: str = ""


class Project(BaseModel):
    """Project entry."""
    name: str
    date: str = ""
    organization: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    impact: str = ""


class SkillCategory(BaseModel):
    """Skill category with list of skills."""
    category: str
    skills: List[str]


class ParsedLatexResume(BaseModel):
    """Complete structured representation of a parsed LaTeX resume."""
    personal_info: PersonalInfo
    professional_summary: str = ""
    skills: List[SkillCategory] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    parsed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    raw_latex: str = ""


class LaTeXResumeParser:
    """Parser for extracting structured data from LaTeX resume files."""
    
    def __init__(self):
        """Initialize the LaTeX parser."""
        pass
    
    def parse_latex_file(self, latex_path: str) -> ParsedLatexResume:
        """Parse a LaTeX file and return structured data.
        
        Args:
            latex_path: Path to the .tex file
            
        Returns:
            ParsedLatexResume object with structured data
        """
        with open(latex_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        return self.parse_latex_content(latex_content)
    
    def parse_latex_content(self, latex_content: str) -> ParsedLatexResume:
        """Parse LaTeX content string and return structured data.
        
        Args:
            latex_content: Raw LaTeX content as string
            
        Returns:
            ParsedLatexResume object with structured data
        """
        personal_info = self._extract_personal_info(latex_content)
        professional_summary = self._extract_professional_summary(latex_content)
        skills = self._extract_skills(latex_content)
        experience = self._extract_experience(latex_content)
        education = self._extract_education(latex_content)
        projects = self._extract_projects(latex_content)
        certifications = self._extract_certifications(latex_content)
        awards = self._extract_awards(latex_content)
        languages = self._extract_languages(latex_content)
        
        return ParsedLatexResume(
            personal_info=personal_info,
            professional_summary=professional_summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            awards=awards,
            languages=languages,
            raw_latex=latex_content
        )
    
    def _extract_personal_info(self, content: str) -> PersonalInfo:
        """Extract personal information from LaTeX header."""
        info = PersonalInfo()
        
        # Extract name
        name_match = re.search(r'\\name\{([^}]*)\}\{([^}]*)\}', content)
        if name_match:
            info.first_name = name_match.group(1).strip()
            info.last_name = name_match.group(2).strip()
        
        # Extract title
        title_match = re.search(r'\\title\{([^}]*)\}', content)
        if title_match:
            info.title = title_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'\\email\{([^}]*)\}', content)
        if email_match:
            info.email = email_match.group(1).strip()
        
        # Extract phone
        phone_match = re.search(r'\\phone\[mobile\]\{([^}]*)\}', content)
        if phone_match:
            info.phone = phone_match.group(1).strip()
        
        # Extract address (multiple lines)
        address_matches = re.findall(r'\\address\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}', content)
        if address_matches:
            for match in address_matches:
                info.address.extend([m.strip() for m in match if m.strip()])
        
        # Extract website
        website_match = re.search(r'\\homepage\{([^}]*)\}', content)
        if website_match:
            info.website = website_match.group(1).strip()
        
        # Extract LinkedIn
        linkedin_match = re.search(r'\\social\[linkedin\]\{([^}]*)\}', content)
        if linkedin_match:
            info.linkedin = linkedin_match.group(1).strip()
        
        # Extract GitHub
        github_match = re.search(r'\\social\[github\]\{([^}]*)\}', content)
        if github_match:
            info.github = github_match.group(1).strip()
        
        # Extract quote/objective
        quote_match = re.search(r'\\quote\{([^}]*)\}', content)
        if quote_match:
            info.quote = quote_match.group(1).strip()
        
        return info
    
    def _extract_professional_summary(self, content: str) -> str:
        """Extract professional summary section."""
        summary_pattern = r'\\section\{Professional Summary\}.*?\\cvitem\{\}([^\\]*)'
        match = re.search(summary_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_skills(self, content: str) -> List[SkillCategory]:
        """Extract skills section with categories."""
        skills = []
        
        # Match technical skills section
        skills_section = re.search(
            r'\\section\{(?:Technical )?Skills\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not skills_section:
            return skills
        
        skills_content = skills_section.group(1)
        
        # Extract skill items: \cvitem{Category}{Skill1, Skill2, ...}
        skill_items = re.findall(r'\\cvitem\{([^}]*)\}\{([^}]*)\}', skills_content)
        
        for category, skill_list in skill_items:
            if category and skill_list:
                skill_names = [s.strip() for s in skill_list.split(',') if s.strip()]
                if skill_names:
                    skills.append(SkillCategory(
                        category=category.strip(),
                        skills=skill_names
                    ))
        
        return skills
    
    def _extract_experience(self, content: str) -> List[Experience]:
        """Extract work experience entries."""
        experiences = []
        
        # Match experience section
        exp_section = re.search(
            r'\\section\{Professional Experience\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not exp_section:
            return experiences
        
        exp_content = exp_section.group(1)
        
        # Extract cventry items: \cventry{dates}{title}{company}{location}{}{description}
        cventry_pattern = r'\\cventry\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{[^}]*\}\{(.*?)\}'
        entries = re.findall(cventry_pattern, exp_content, re.DOTALL)
        
        for dates, title, company, location, description in entries:
            # Parse dates (e.g., "2020--2023" or "Present--")
            date_parts = dates.split('--')
            end_date = date_parts[0].strip() if len(date_parts) > 0 else ""
            start_date = date_parts[1].strip() if len(date_parts) > 1 else ""
            
            # Extract bullet points from description
            bullet_items = re.findall(r'\\item\s+([^\n\\]*)', description)
            
            experiences.append(Experience(
                title=title.strip(),
                company=company.strip(),
                location=location.strip(),
                start_date=start_date,
                end_date=end_date,
                description=[item.strip() for item in bullet_items if item.strip()]
            ))
        
        return experiences
    
    def _extract_education(self, content: str) -> List[Education]:
        """Extract education entries."""
        education = []
        
        # Match education section
        edu_section = re.search(
            r'\\section\{Education\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not edu_section:
            return education
        
        edu_content = edu_section.group(1)
        
        # Extract cventry items for education
        cventry_pattern = r'\\cventry\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}'
        entries = re.findall(cventry_pattern, edu_content)
        
        for year, degree, institution, location, gpa, additional in entries:
            education.append(Education(
                degree=degree.strip(),
                institution=institution.strip(),
                location=location.strip(),
                graduation_year=year.strip(),
                gpa=gpa.strip(),
                additional_info=additional.strip()
            ))
        
        return education
    
    def _extract_projects(self, content: str) -> List[Project]:
        """Extract project entries."""
        projects = []
        
        # Match projects section
        proj_section = re.search(
            r'\\section\{Projects\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not proj_section:
            return projects
        
        proj_content = proj_section.group(1)
        
        # Extract cventry items for projects
        cventry_pattern = r'\\cventry\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{[^}]*\}\{[^}]*\}\{(.*?)\}'
        entries = re.findall(cventry_pattern, proj_content, re.DOTALL)
        
        for date, name, org, description in entries:
            # Extract technologies and impact from description
            tech_match = re.search(r'\\textbf\{Technologies:\}\s*([^\n\\]*)', description)
            technologies = []
            if tech_match:
                technologies = [t.strip() for t in tech_match.group(1).split(',') if t.strip()]
            
            impact_match = re.search(r'\\textbf\{Impact:\}\s*([^\n\\]*)', description)
            impact = impact_match.group(1).strip() if impact_match else ""
            
            # Extract main description
            main_desc = re.sub(r'\\textbf\{[^}]*\}', '', description).strip()
            
            projects.append(Project(
                name=name.strip(),
                date=date.strip(),
                organization=org.strip(),
                description=main_desc,
                technologies=technologies,
                impact=impact
            ))
        
        return projects
    
    def _extract_certifications(self, content: str) -> List[str]:
        """Extract certifications."""
        certs = []
        
        cert_section = re.search(
            r'\\section\{Certifications\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not cert_section:
            return certs
        
        cert_content = cert_section.group(1)
        cert_items = re.findall(r'\\cvitem\{[^}]*\}\{([^}]*)\}', cert_content)
        
        return [cert.strip() for cert in cert_items if cert.strip()]
    
    def _extract_awards(self, content: str) -> List[str]:
        """Extract awards and achievements."""
        awards = []
        
        awards_section = re.search(
            r'\\section\{Awards[^}]*\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not awards_section:
            return awards
        
        awards_content = awards_section.group(1)
        award_items = re.findall(r'\\cvitem\{[^}]*\}\{([^}]*)\}', awards_content)
        
        return [award.strip() for award in award_items if award.strip()]
    
    def _extract_languages(self, content: str) -> List[str]:
        """Extract languages."""
        languages = []
        
        lang_section = re.search(
            r'\\section\{Languages\}(.*?)(?:\\section|\\end\{document\})',
            content,
            re.DOTALL
        )
        
        if not lang_section:
            return languages
        
        lang_content = lang_section.group(1)
        lang_items = re.findall(r'\\cvitem\{[^}]*\}\{([^}]*)\}', lang_content)
        
        return [lang.strip() for lang in lang_items if lang.strip()]
    
    def to_json(self, parsed_resume: ParsedLatexResume) -> Dict[str, Any]:
        """Convert parsed resume to JSON-serializable dict.
        
        Args:
            parsed_resume: ParsedLatexResume object
            
        Returns:
            Dictionary representation
        """
        return parsed_resume.model_dump(mode='json')
    
    def to_json_string(self, parsed_resume: ParsedLatexResume, indent: int = 2) -> str:
        """Convert parsed resume to JSON string.
        
        Args:
            parsed_resume: ParsedLatexResume object
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        import json
        return json.dumps(self.to_json(parsed_resume), indent=indent, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    parser = LaTeXResumeParser()
    
    # Example: Parse a LaTeX file
    sample_latex = r"""
    \documentclass[11pt,a4paper,sans]{moderncv}
    \moderncvstyle{classic}
    \moderncvcolor{blue}
    
    \name{John}{Doe}
    \title{Software Engineer}
    \email{john.doe@example.com}
    \phone[mobile]{+1 (555) 123-4567}
    
    \begin{document}
    \makecvtitle
    
    \section{Technical Skills}
    \cvitem{Programming}{Python, Java, JavaScript}
    \cvitem{Frameworks}{React, Django, FastAPI}
    
    \section{Professional Experience}
    \cventry{2023--Present}{Senior Software Engineer}{Tech Corp}{San Francisco, CA}{}{
    \begin{itemize}
    \item Led development of microservices architecture
    \item Improved system performance by 40\%
    \end{itemize}
    }
    
    \section{Education}
    \cventry{2019}{Bachelor of Science in Computer Science}{University Name}{City, State}{GPA: 3.8}{}
    
    \end{document}
    """
    
    parsed = parser.parse_latex_content(sample_latex)
    print(parser.to_json_string(parsed))
