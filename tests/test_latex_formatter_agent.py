"""
Unit tests for LaTeXFormatterAgent.

This module contains comprehensive tests for the LaTeXFormatterAgent class,
covering LaTeX generation, template population, and Overleaf compatibility.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, mock_open
from src.agents.latex_formatter_agent import LaTeXFormatterAgent


class TestLaTeXFormatterAgent:
    """Test cases for LaTeXFormatterAgent class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.test_dir, "templates")
        self.output_dir = os.path.join(self.test_dir, "output")
        
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a simple test template
        self.template_path = os.path.join(self.template_dir, "test_template.tex")
        self.test_template = """\\documentclass{moderncv}
\\name{{{FIRST_NAME}}}{{{LAST_NAME}}}
\\title{{{JOB_TITLE}}}
\\begin{document}
\\section{Professional Summary}
\\cvitem{}{{{PROFESSIONAL_SUMMARY}}}
{{#SKILLS_CATEGORIES}}
\\cvitem{{{CATEGORY_NAME}}}{{{SKILLS_LIST}}}
{{/SKILLS_CATEGORIES}}
{{#EXPERIENCE_ENTRIES}}
\\cventry{{{START_DATE}}--{{END_DATE}}}{{{JOB_TITLE}}}{{{COMPANY_NAME}}}{{{LOCATION}}}{}{%
{{#JOB_DESCRIPTIONS}}
\\begin{itemize}
{{#DESCRIPTION_ITEMS}}
\\item {{DESCRIPTION_ITEM}}
{{/DESCRIPTION_ITEMS}}
\\end{itemize}
{{/JOB_DESCRIPTIONS}}
}
{{/EXPERIENCE_ENTRIES}}
{{#EDUCATION_ENTRIES}}
\\cventry{{{GRADUATION_YEAR}}}{{{DEGREE_TYPE}}}{{{INSTITUTION_NAME}}}{{{LOCATION}}}{{{GPA_INFO}}}{{{ADDITIONAL_INFO}}}
{{/EDUCATION_ENTRIES}}
{{#HAS_PROJECTS}}
\\section{Key Projects}
{{#PROJECT_ENTRIES}}
\\cventry{{{PROJECT_DATE}}}{{{PROJECT_NAME}}}{{{PROJECT_ORGANIZATION}}}{}{}{%
{{PROJECT_DESCRIPTION}}
}
{{/PROJECT_ENTRIES}}
{{/HAS_PROJECTS}}
\\end{document}"""
        
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(self.test_template)
        
        # Initialize agent with test directories
        self.agent = LaTeXFormatterAgent(
            template_path=self.template_path,
            output_directory=self.output_dir
        )
        
        # Sample resume data for testing
        self.sample_resume_data = {
            "profile_id": "test_user_123",
            "job_title": "Software Engineer",
            "name": "Jane Smith",
            "ats_analysis": {
                "ats_score": 92,
                "category": "Excellent"
            },
            "aligned_sections": {
                "summary": "Experienced software engineer with expertise in Python and web development.",
                "skills": {
                    "aligned_skills": ["Python", "JavaScript", "React", "Django", "PostgreSQL"],
                    "skill_categories": {
                        "programming": ["Python", "JavaScript"],
                        "frameworks": ["React", "Django"],
                        "databases": ["PostgreSQL"]
                    }
                },
                "experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Tech Company",
                        "duration": "2020-2024",
                        "location": "San Francisco, CA",
                        "description": "Developed web applications using Python and Django.",
                        "aligned_description": "Built scalable web applications using Python and Django framework."
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "field": "Computer Science",
                        "institution": "University of Technology",
                        "year": "2020",
                        "location": "California, USA",
                        "gpa": "3.8"
                    }
                ]
            },
            "relevant_projects": [
                {
                    "name": "Web Application",
                    "description": "Built a full-stack web application",
                    "technologies": "Python, Django, React",
                    "impact": "Improved user engagement by 50%",
                    "date": "2023"
                }
            ]
        }
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_agent_initialization(self):
        """Test LaTeXFormatterAgent initialization."""
        assert self.agent.template_path == self.template_path
        assert self.agent.output_directory == self.output_dir
        assert self.agent.default_template_style == "professional"
        assert os.path.exists(self.output_dir)
    
    def test_escape_latex_special_chars(self):
        """Test LaTeX special character escaping."""
        test_cases = [
            ("Hello & World", "Hello \\& World"),
            ("100% complete", "100\\% complete"),
            ("Cost: $50", "Cost: \\$50"),
            ("Section #1", "Section \\#1"),
            ("x^2 + y^2", "x\\textasciicircum\\{\\}2 + y\\textasciicircum\\{\\}2"),
            ("file_name.txt", "file\\_name.txt"),
            ("{key: value}", "\\{key: value\\}"),
            ("~username", "\\textasciitilde{}username"),
            ("C:\\path\\to\\file", "C:\\textbackslash\\{\\}path\\textbackslash\\{\\}to\\textbackslash\\{\\}file")
        ]
        
        for input_text, expected in test_cases:
            result = self.agent.escape_latex_special_chars(input_text)
            assert result == expected, f"Failed for input: {input_text}. Got: {result}"
        
        # Test empty and None inputs
        assert self.agent.escape_latex_special_chars("") == ""
        assert self.agent.escape_latex_special_chars(None) == ""
    
    def test_format_skills_by_category(self):
        """Test skills formatting by category."""
        skills_data = {
            "skill_categories": {
                "programming": ["Python", "JavaScript", "Java"],
                "frameworks": ["Django", "React", "Flask"],
                "databases": ["PostgreSQL", "MongoDB"],
                "other": ["Git", "Docker"]  # Should be skipped
            }
        }
        
        result = self.agent.format_skills_by_category(skills_data)
        
        assert len(result) == 3  # 'other' category should be skipped
        
        # Check that categories are properly formatted
        category_names = [cat['CATEGORY_NAME'] for cat in result]
        assert 'Programming' in category_names
        assert 'Frameworks' in category_names
        assert 'Databases' in category_names
        assert 'Other' not in category_names
        
        # Check skills formatting
        for category in result:
            assert 'CATEGORY_NAME' in category
            assert 'SKILLS_LIST' in category
            assert isinstance(category['SKILLS_LIST'], str)
    
    def test_format_skills_with_aligned_skills(self):
        """Test skills formatting with aligned_skills fallback."""
        skills_data = {
            "aligned_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker", "JavaScript"]
        }
        
        result = self.agent.format_skills_by_category(skills_data)
        
        assert len(result) >= 1
        
        # Should create technical and additional skills categories
        category_names = [cat['CATEGORY_NAME'] for cat in result]
        assert any('Technical' in name for name in category_names)
    
    def test_format_experience_entries(self):
        """Test experience entries formatting."""
        experience_data = [
            {
                "title": "Senior Developer",
                "company": "Tech Corp",
                "duration": "2021-2024",
                "location": "New York, NY",
                "aligned_description": "Led development of web applications. Mentored junior developers."
            },
            {
                "title": "Junior Developer",
                "company": "StartUp Inc",
                "duration": "2019-2021",
                "location": "Austin, TX",
                "description": "Built REST APIs and web services."
            }
        ]
        
        result = self.agent.format_experience_entries(experience_data)
        
        assert len(result) == 2
        
        # Check first entry
        first_entry = result[0]
        assert first_entry['JOB_TITLE'] == 'Senior Developer'
        assert first_entry['COMPANY_NAME'] == 'Tech Corp'
        assert first_entry['START_DATE'] == '2021'
        assert first_entry['END_DATE'] == '2024'
        assert first_entry['LOCATION'] == 'New York, NY'
        
        # Check that job descriptions are formatted
        assert 'JOB_DESCRIPTIONS' in first_entry
        if first_entry['JOB_DESCRIPTIONS']:
            assert 'DESCRIPTION_ITEMS' in first_entry['JOB_DESCRIPTIONS'][0]
    
    def test_parse_duration(self):
        """Test duration parsing."""
        test_cases = [
            ("2021-2024", ("2021", "2024")),
            ("2021 - 2024", ("2021", "2024")),
            ("2021-Present", ("2021", "Present")),
            ("2021 - Present", ("2021", "Present")),
            ("Jan 2021 - Dec 2024", ("Jan 2021", "Dec 2024")),
            ("2023", ("2023", "")),
            ("", ("Present", ""))
        ]
        
        for duration, expected in test_cases:
            result = self.agent._parse_duration(duration)
            assert result == expected, f"Failed for duration: {duration}"
    
    def test_format_education_entries(self):
        """Test education entries formatting."""
        education_data = [
            {
                "degree": "Master of Science",
                "field": "Computer Science",
                "institution": "MIT",
                "year": "2020",
                "location": "Cambridge, MA",
                "gpa": "3.9"
            }
        ]
        
        result = self.agent.format_education_entries(education_data)
        
        assert len(result) == 1
        
        entry = result[0]
        assert entry['DEGREE_TYPE'] == 'Master of Science in Computer Science'
        assert entry['INSTITUTION_NAME'] == 'MIT'
        assert entry['GRADUATION_YEAR'] == '2020'
        assert entry['LOCATION'] == 'Cambridge, MA'
        assert entry['GPA_INFO'] == 'GPA: 3.9'
    
    def test_format_projects_entries(self):
        """Test projects entries formatting."""
        projects_data = [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce application",
                "technologies": "Python, Django, React, PostgreSQL",
                "impact": "Increased sales by 30%",
                "date": "2023"
            }
        ]
        
        has_projects, result = self.agent.format_projects_entries(projects_data)
        
        assert has_projects is True
        assert len(result) == 1
        
        project = result[0]
        assert project['PROJECT_NAME'] == 'E-commerce Platform'
        assert project['PROJECT_DESCRIPTION'] == 'Built a full-stack e-commerce application'
        assert project['PROJECT_DATE'] == '2023'
        assert len(project['PROJECT_TECHNOLOGIES']) == 1
        assert len(project['PROJECT_IMPACT']) == 1
    
    def test_extract_personal_info(self):
        """Test personal information extraction."""
        resume_data = {
            "name": "John Doe",
            "job_title": "Software Engineer"
        }
        
        result = self.agent.extract_personal_info(resume_data)
        
        assert result['FIRST_NAME'] == 'John'
        assert result['LAST_NAME'] == 'Doe'
        assert result['JOB_TITLE'] == 'Software Engineer'
        
        # Check default values are present
        assert 'PHONE_NUMBER' in result
        assert 'EMAIL_ADDRESS' in result
        assert 'ADDRESS_LINE1' in result
    
    def test_replace_template_section(self):
        """Test template section replacement."""
        content = "Before {{#TEST}} old content {{/TEST}} After"
        result = self.agent._replace_template_section(
            content, '{{#TEST}}', '{{/TEST}}', 'new content'
        )
        
        assert result == "Before new content After"
        
        # Test with non-existent markers
        result2 = self.agent._replace_template_section(
            content, '{{#MISSING}}', '{{/MISSING}}', 'replacement'
        )
        assert result2 == content  # Should remain unchanged
    
    def test_populate_template(self):
        """Test template population with resume data."""
        result = self.agent.populate_template(self.test_template, self.sample_resume_data)
        
        # Check that personal information is populated
        assert 'Jane' in result
        assert 'Smith' in result
        assert 'Software Engineer' in result
        
        # Check that summary is included
        assert 'Experienced software engineer' in result
        
        # Check that skills are formatted
        assert '\\cvitem{' in result
        
        # Check that experience is included
        assert 'Tech Company' in result
        
        # Check that education is included
        assert 'University of Technology' in result
    
    def test_generate_latex_resume(self):
        """Test complete LaTeX resume generation."""
        output_path = self.agent.generate_latex_resume(
            self.sample_resume_data, 
            "test_resume.tex"
        )
        
        # Check that file was created
        assert os.path.exists(output_path)
        assert output_path.endswith("test_resume.tex")
        
        # Check file content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '\\documentclass{moderncv}' in content
        assert 'Jane' in content
        assert 'Smith' in content
        assert 'Software Engineer' in content
    
    def test_generate_latex_resume_with_auto_filename(self):
        """Test LaTeX resume generation with automatic filename."""
        output_path = self.agent.generate_latex_resume(self.sample_resume_data)
        
        # Check that file was created with profile_id in name
        assert os.path.exists(output_path)
        assert 'test_user_123' in os.path.basename(output_path)
        assert output_path.endswith('.tex')
    
    def test_validate_overleaf_compatibility(self):
        """Test Overleaf compatibility validation."""
        # Test compatible content
        compatible_content = "\\documentclass{moderncv}\\usepackage{geometry}\\begin{document}\\end{document}"
        result = self.agent.validate_overleaf_compatibility(compatible_content)
        
        assert result['is_compatible'] is True
        assert len(result['errors']) == 0
        
        # Test content with warnings
        warning_content = "\\documentclass{moderncv}\\usepackage{tikz-3dplot}\\newcommand{\\test}{}\\input{file.tex}"
        result = self.agent.validate_overleaf_compatibility(warning_content)
        
        assert len(result['warnings']) > 0
    
    def test_error_handling_missing_template(self):
        """Test error handling when template file is missing."""
        agent = LaTeXFormatterAgent(
            template_path="nonexistent_template.tex",
            output_directory=self.output_dir
        )
        
        with pytest.raises(FileNotFoundError):
            agent.generate_latex_resume(self.sample_resume_data)
    
    def test_error_handling_invalid_resume_data(self):
        """Test error handling with invalid resume data."""
        invalid_data = None
        
        # Should not crash, but handle gracefully
        try:
            result = self.agent.populate_template(self.test_template, invalid_data or {})
            assert isinstance(result, str)
        except Exception as e:
            # If it raises an exception, it should be logged
            assert "Error populating template" in str(e) or isinstance(e, (TypeError, AttributeError))
    
    def test_empty_sections_handling(self):
        """Test handling of empty resume sections."""
        empty_resume_data = {
            "profile_id": "empty_user",
            "job_title": "Position",
            "name": "Empty User",
            "aligned_sections": {
                "summary": "",
                "skills": {},
                "experience": [],
                "education": []
            }
        }
        
        result = self.agent.populate_template(self.test_template, empty_resume_data)
        
        # Should still generate valid LaTeX
        assert '\\documentclass{moderncv}' in result
        assert 'Empty' in result
        assert 'User' in result
    
    def test_special_characters_in_content(self):
        """Test handling of special characters in resume content."""
        special_char_data = {
            "profile_id": "special_user",
            "job_title": "C++ Developer & Data Scientist",
            "name": "José María",
            "aligned_sections": {
                "summary": "Expert in C++ & Python. Achieved 100% success rate. Salary: $120,000+",
                "skills": {
                    "aligned_skills": ["C++", "Python", "R&D", "Machine Learning"]
                },
                "experience": [
                    {
                        "title": "Senior C++ Developer",
                        "company": "Tech & Innovation Corp",
                        "duration": "2020-2024",
                        "location": "São Paulo, Brazil",
                        "description": "Developed high-performance applications using C++ & modern frameworks."
                    }
                ],
                "education": []
            }
        }
        
        result = self.agent.populate_template(self.test_template, special_char_data)
        
        # Check that special characters are properly escaped
        assert '\\&' in result  # & should be escaped
        assert '\\%' in result  # % should be escaped
        assert '\\$' in result  # $ should be escaped
        assert 'C++' in result  # Should handle ++ correctly


def test_latex_formatter_agent_main():
    """Test the main function execution."""
    # This test ensures the main function runs without errors
    with patch('builtins.print'):  # Suppress print output during testing
        try:
            from src.agents.latex_formatter_agent import main
            main()
        except Exception as e:
            pytest.fail(f"Main function failed with error: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
