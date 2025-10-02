"""
Comprehensive tests for ResumeWorkflow using LangGraph.

This module contains unit tests and integration tests for the workflow
orchestration system, including full pipeline execution with dummy data.
"""

import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from workflow.resume_workflow import ResumeWorkflow, WorkflowState
except ImportError:
    # Handle case where LangGraph is not installed
    pytest.skip("LangGraph dependencies not available", allow_module_level=True)


class TestResumeWorkflow:
    """Test cases for ResumeWorkflow class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.test_dir, "templates")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.rag_dir = os.path.join(self.test_dir, "data", "profiles")
        
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.rag_dir, exist_ok=True)
        
        # Create a simple test template
        self.template_path = os.path.join(self.template_dir, "test_template.tex")
        test_template = """\\documentclass{moderncv}
\\name{{{FIRST_NAME}}}{{{LAST_NAME}}}
\\title{{{JOB_TITLE}}}
\\begin{document}
\\section{Professional Summary}
\\cvitem{}{{{PROFESSIONAL_SUMMARY}}}
\\end{document}"""
        
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(test_template)
        
        # Sample test data
        self.test_job_url = "https://example.com/test-job"
        self.test_profile_id = "test_user_workflow"
        
        # Mock data for agents
        self.mock_job_data = {
            "job_title": "Software Engineer",
            "company": "Test Company",
            "keywords": ["Python", "Django", "REST API"],
            "requirements": ["3+ years experience", "Python expertise"],
            "description": "We are looking for a skilled software engineer..."
        }
        
        self.mock_profile_data = {
            "profile_id": "test_user_workflow",
            "relevance_score": 0.85,
            "relevant_data": {
                "skills": ["Python", "Django", "JavaScript"],
                "experience": [
                    {
                        "title": "Software Developer",
                        "company": "Previous Company",
                        "duration": "2020-2024",
                        "description": "Developed web applications using Python and Django"
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "field": "Computer Science",
                        "institution": "Test University",
                        "year": "2020"
                    }
                ]
            }
        }
        
        self.mock_aligned_data = {
            "profile_id": "test_user_workflow",
            "job_title": "Software Engineer",
            "alignment_analysis": {
                "overall_score": 0.78,
                "matched_keywords": ["Python", "Django"],
                "missing_keywords": ["REST API"]
            },
            "aligned_sections": {
                "summary": "Experienced software developer with Python and Django expertise",
                "skills": {
                    "aligned_skills": ["Python", "Django", "JavaScript"]
                },
                "experience": [
                    {
                        "title": "Software Developer",
                        "company": "Previous Company",
                        "duration": "2020-2024",
                        "aligned_description": "Developed scalable web applications using Python and Django framework"
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "field": "Computer Science",
                        "institution": "Test University",
                        "year": "2020"
                    }
                ]
            }
        }
        
        self.mock_optimized_data = {
            "profile_id": "test_user_workflow",
            "job_title": "Software Engineer",
            "ats_analysis": {
                "ats_score": 92,
                "category": "Excellent",
                "keyword_density": 0.85,
                "section_completeness": 1.0,
                "formatting_score": 0.95,
                "suggestions": ["Consider adding more REST API examples"]
            },
            "aligned_sections": self.mock_aligned_data["aligned_sections"],
            "auto_fixes_applied": ["Added missing Python keyword to summary"]
        }
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                # Files may be locked on Windows, ignore cleanup error
                pass
    
    def test_workflow_initialization(self):
        """Test ResumeWorkflow initialization."""
        with patch('src.workflow.resume_workflow.JDExtractorAgent'), \
             patch('src.workflow.resume_workflow.ProfileRAGAgent'), \
             patch('src.workflow.resume_workflow.ContentAlignmentAgent'), \
             patch('src.workflow.resume_workflow.ATSOptimizerAgent'), \
             patch('src.workflow.resume_workflow.LaTeXFormatterAgent'):
            
            workflow = ResumeWorkflow(
                template_path=self.template_path,
                output_directory=self.output_dir,
                rag_database_path=self.rag_dir,
                enable_logging=False
            )
            
            assert workflow.template_path == self.template_path
            assert workflow.output_directory == self.output_dir
            assert workflow.rag_database_path == self.rag_dir
            assert workflow.workflow_graph is not None
    
    def test_workflow_status(self):
        """Test workflow status reporting."""
        with patch('src.workflow.resume_workflow.JDExtractorAgent'), \
             patch('src.workflow.resume_workflow.ProfileRAGAgent'), \
             patch('src.workflow.resume_workflow.ContentAlignmentAgent'), \
             patch('src.workflow.resume_workflow.ATSOptimizerAgent'), \
             patch('src.workflow.resume_workflow.LaTeXFormatterAgent'):
            
            workflow = ResumeWorkflow(
                template_path=self.template_path,
                output_directory=self.output_dir,
                enable_logging=False
            )
            
            status = workflow.get_workflow_status()
            
            assert status["workflow_name"] == "ResumeOptimizationWorkflow"
            assert "version" in status
            assert len(status["agents"]) == 5
            assert len(status["workflow_steps"]) == 5
            assert "configuration" in status
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_extract_job_data_node(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test job data extraction node."""
        # Setup mocks
        mock_jd_instance = MagicMock()
        mock_jd_instance.extract_job_data.return_value = self.mock_job_data
        mock_jd.return_value = mock_jd_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Test state
        state = WorkflowState(
            job_url=self.test_job_url,
            profile_id=self.test_profile_id,
            job_data=None,
            profile_data=None,
            aligned_data=None,
            optimized_data=None,
            latex_file_path=None,
            current_step="initializing",
            step_count=0,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        # Execute node
        result_state = workflow._extract_job_data_node(state)
        
        # Verify results
        assert result_state["current_step"] == "extract_job_data"
        assert result_state["step_count"] == 1
        assert result_state["job_data"] == self.mock_job_data
        assert len(result_state["errors"]) == 0
        assert "extract_job_data" in result_state["execution_time"]
        
        # Verify agent was called
        mock_jd_instance.extract_job_data.assert_called_once_with(self.test_job_url)
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_retrieve_profile_node(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test profile retrieval node."""
        # Setup mocks
        mock_rag_instance = MagicMock()
        mock_rag_instance.retrieve_profile.return_value = self.mock_profile_data
        mock_rag.return_value = mock_rag_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Test state with job data
        state = WorkflowState(
            job_url=self.test_job_url,
            profile_id=self.test_profile_id,
            job_data=self.mock_job_data,
            profile_data=None,
            aligned_data=None,
            optimized_data=None,
            latex_file_path=None,
            current_step="extract_job_data",
            step_count=1,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        # Execute node
        result_state = workflow._retrieve_profile_node(state)
        
        # Verify results
        assert result_state["current_step"] == "retrieve_profile"
        assert result_state["step_count"] == 2
        assert result_state["profile_data"] == self.mock_profile_data
        assert len(result_state["errors"]) == 0
        
        # Verify agent was called
        mock_rag_instance.retrieve_profile.assert_called_once_with(
            self.mock_job_data, 
            self.test_profile_id
        )
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_align_content_node(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test content alignment node."""
        # Setup mocks
        mock_align_instance = MagicMock()
        mock_align_instance.align_content.return_value = self.mock_aligned_data
        mock_align.return_value = mock_align_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Test state with job and profile data
        state = WorkflowState(
            job_url=self.test_job_url,
            profile_id=self.test_profile_id,
            job_data=self.mock_job_data,
            profile_data=self.mock_profile_data,
            aligned_data=None,
            optimized_data=None,
            latex_file_path=None,
            current_step="retrieve_profile",
            step_count=2,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        # Execute node
        result_state = workflow._align_content_node(state)
        
        # Verify results
        assert result_state["current_step"] == "align_content"
        assert result_state["step_count"] == 3
        assert result_state["aligned_data"] == self.mock_aligned_data
        assert len(result_state["errors"]) == 0
        
        # Verify agent was called
        mock_align_instance.align_content.assert_called_once_with(
            self.mock_job_data,
            self.mock_profile_data
        )
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_optimize_ats_node(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test ATS optimization node."""
        # Setup mocks
        mock_ats_instance = MagicMock()
        mock_ats_instance.optimize_resume.return_value = self.mock_optimized_data
        mock_ats.return_value = mock_ats_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Test state with aligned data
        state = WorkflowState(
            job_url=self.test_job_url,
            profile_id=self.test_profile_id,
            job_data=self.mock_job_data,
            profile_data=self.mock_profile_data,
            aligned_data=self.mock_aligned_data,
            optimized_data=None,
            latex_file_path=None,
            current_step="align_content",
            step_count=3,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        # Execute node
        result_state = workflow._optimize_ats_node(state)
        
        # Verify results
        assert result_state["current_step"] == "optimize_ats"
        assert result_state["step_count"] == 4
        assert result_state["optimized_data"] == self.mock_optimized_data
        assert len(result_state["errors"]) == 0
        
        # Verify agent was called
        mock_ats_instance.optimize_resume.assert_called_once_with(self.mock_aligned_data)
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_generate_latex_node(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test LaTeX generation node."""
        # Create a test output file
        test_latex_file = os.path.join(self.output_dir, "test_resume.tex")
        with open(test_latex_file, 'w', encoding='utf-8') as f:
            f.write("\\documentclass{moderncv}\\begin{document}Test Resume\\end{document}")
        
        # Setup mocks
        mock_latex_instance = MagicMock()
        mock_latex_instance.generate_latex_resume.return_value = test_latex_file
        mock_latex_instance.validate_overleaf_compatibility.return_value = {
            'is_compatible': True,
            'warnings': [],
            'errors': []
        }
        mock_latex.return_value = mock_latex_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Test state with optimized data
        state = WorkflowState(
            job_url=self.test_job_url,
            profile_id=self.test_profile_id,
            job_data=self.mock_job_data,
            profile_data=self.mock_profile_data,
            aligned_data=self.mock_aligned_data,
            optimized_data=self.mock_optimized_data,
            latex_file_path=None,
            current_step="optimize_ats",
            step_count=4,
            errors=[],
            warnings=[],
            execution_time={},
            messages=[]
        )
        
        # Execute node
        result_state = workflow._generate_latex_node(state)
        
        # Verify results
        assert result_state["current_step"] == "generate_latex"
        assert result_state["step_count"] == 5
        assert result_state["latex_file_path"] == test_latex_file
        assert len(result_state["errors"]) == 0
        
        # Verify agent was called
        mock_latex_instance.generate_latex_resume.assert_called_once()
    
    def test_error_handling_missing_job_data(self):
        """Test error handling when job data extraction fails."""
        with patch('src.workflow.resume_workflow.JDExtractorAgent') as mock_jd, \
             patch('src.workflow.resume_workflow.ProfileRAGAgent'), \
             patch('src.workflow.resume_workflow.ContentAlignmentAgent'), \
             patch('src.workflow.resume_workflow.ATSOptimizerAgent'), \
             patch('src.workflow.resume_workflow.LaTeXFormatterAgent'):
            
            # Setup mock to return error
            mock_jd_instance = MagicMock()
            mock_jd_instance.extract_job_data.return_value = {"error": "Failed to fetch job data"}
            mock_jd.return_value = mock_jd_instance
            
            workflow = ResumeWorkflow(
                template_path=self.template_path,
                output_directory=self.output_dir,
                enable_logging=False
            )
            
            # Test state
            state = WorkflowState(
                job_url=self.test_job_url,
                profile_id=self.test_profile_id,
                job_data=None,
                profile_data=None,
                aligned_data=None,
                optimized_data=None,
                latex_file_path=None,
                current_step="initializing",
                step_count=0,
                errors=[],
                warnings=[],
                execution_time={},
                messages=[]
            )
            
            # Execute node
            result_state = workflow._extract_job_data_node(state)
            
            # Verify error handling
            assert len(result_state["errors"]) > 0
            assert "Failed to extract job data" in result_state["errors"][0]
    
    def test_error_handling_missing_dependencies(self):
        """Test error handling when required data is missing for subsequent steps."""
        with patch('src.workflow.resume_workflow.JDExtractorAgent'), \
             patch('src.workflow.resume_workflow.ProfileRAGAgent'), \
             patch('src.workflow.resume_workflow.ContentAlignmentAgent'), \
             patch('src.workflow.resume_workflow.ATSOptimizerAgent'), \
             patch('src.workflow.resume_workflow.LaTeXFormatterAgent'):
            
            workflow = ResumeWorkflow(
                template_path=self.template_path,
                output_directory=self.output_dir,
                enable_logging=False
            )
            
            # Test state without job data for profile retrieval
            state = WorkflowState(
                job_url=self.test_job_url,
                profile_id=self.test_profile_id,
                job_data=None,  # Missing job data
                profile_data=None,
                aligned_data=None,
                optimized_data=None,
                latex_file_path=None,
                current_step="extract_job_data",
                step_count=1,
                errors=[],
                warnings=[],
                execution_time={},
                messages=[]
            )
            
            # Execute profile retrieval node
            result_state = workflow._retrieve_profile_node(state)
            
            # Verify error handling
            assert len(result_state["errors"]) > 0
            assert "No job data available" in result_state["errors"][0]


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures for integration tests."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.test_dir, "templates")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.rag_dir = os.path.join(self.test_dir, "data", "profiles")
        
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.rag_dir, exist_ok=True)
        
        # Create test template
        self.template_path = os.path.join(self.template_dir, "integration_template.tex")
        template_content = """\\documentclass[11pt,a4paper,sans]{moderncv}
\\moderncvstyle{classic}
\\moderncvcolor{blue}
\\usepackage[utf8]{inputenc}
\\usepackage[scale=0.75]{geometry}

\\name{{{FIRST_NAME}}}{{{LAST_NAME}}}
\\title{{{JOB_TITLE}}}
\\address{123 Main St}{City, State}{12345}
\\phone{+1-555-123-4567}
\\email{test@example.com}

\\begin{document}
\\makecvtitle

\\section{Professional Summary}
\\cvitem{}{{{PROFESSIONAL_SUMMARY}}}

\\section{Technical Skills}
{{#SKILLS_CATEGORIES}}
\\cvitem{{{CATEGORY_NAME}}}{{{SKILLS_LIST}}}
{{/SKILLS_CATEGORIES}}

\\section{Professional Experience}
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

\\section{Education}
{{#EDUCATION_ENTRIES}}
\\cventry{{{GRADUATION_YEAR}}}{{{DEGREE_TYPE}}}{{{INSTITUTION_NAME}}}{{{LOCATION}}}{{{GPA_INFO}}}{{{ADDITIONAL_INFO}}}
{{/EDUCATION_ENTRIES}}

\\end{document}"""
        
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                pass
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_full_workflow_execution(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test complete workflow execution with mocked agents."""
        # Create test output file
        test_latex_file = os.path.join(self.output_dir, "integration_test_resume.tex")
        
        # Setup comprehensive mock data
        mock_job_data = {
            "job_title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "keywords": ["Python", "Django", "REST API", "PostgreSQL", "AWS"],
            "requirements": ["5+ years Python", "Django framework", "API development"],
            "description": "We seek a senior Python developer with Django expertise..."
        }
        
        mock_profile_data = {
            "profile_id": "integration_test_user",
            "relevance_score": 0.92,
            "relevant_data": {
                "skills": ["Python", "Django", "PostgreSQL", "JavaScript", "AWS"],
                "experience": [
                    {
                        "title": "Python Developer",
                        "company": "Previous Corp",
                        "duration": "2019-2024",
                        "description": "Developed web applications using Django and PostgreSQL"
                    }
                ],
                "education": [
                    {
                        "degree": "Master of Science",
                        "field": "Computer Science", 
                        "institution": "Tech University",
                        "year": "2019"
                    }
                ]
            }
        }
        
        mock_aligned_data = {
            "profile_id": "integration_test_user",
            "job_title": "Senior Python Developer",
            "alignment_analysis": {
                "overall_score": 0.88,
                "matched_keywords": ["Python", "Django", "PostgreSQL", "AWS"],
                "missing_keywords": ["REST API"]
            },
            "aligned_sections": {
                "summary": "Senior Python developer with 5+ years of Django and PostgreSQL experience",
                "skills": {
                    "aligned_skills": ["Python", "Django", "PostgreSQL", "AWS", "JavaScript"],
                    "skill_categories": {
                        "programming": ["Python", "JavaScript"],
                        "frameworks": ["Django"],
                        "databases": ["PostgreSQL"],
                        "cloud": ["AWS"]
                    }
                },
                "experience": [
                    {
                        "title": "Python Developer",
                        "company": "Previous Corp",
                        "duration": "2019-2024",
                        "aligned_description": "Developed scalable web applications using Django framework and PostgreSQL database with AWS deployment"
                    }
                ],
                "education": [
                    {
                        "degree": "Master of Science",
                        "field": "Computer Science",
                        "institution": "Tech University",
                        "year": "2019"
                    }
                ]
            }
        }
        
        mock_optimized_data = {
            "profile_id": "integration_test_user",
            "job_title": "Senior Python Developer",
            "ats_analysis": {
                "ats_score": 94,
                "category": "Excellent",
                "keyword_density": 0.89,
                "section_completeness": 1.0,
                "formatting_score": 0.96,
                "suggestions": ["Consider adding REST API project examples"]
            },
            "aligned_sections": mock_aligned_data["aligned_sections"],
            "auto_fixes_applied": [
                "Added REST API keyword to experience description",
                "Enhanced skills section with cloud technologies"
            ]
        }
        
        # Setup mocks
        mock_jd_instance = MagicMock()
        mock_jd_instance.extract_job_data.return_value = mock_job_data
        mock_jd.return_value = mock_jd_instance
        
        mock_rag_instance = MagicMock()
        mock_rag_instance.retrieve_profile.return_value = mock_profile_data
        mock_rag.return_value = mock_rag_instance
        
        mock_align_instance = MagicMock()
        mock_align_instance.align_content.return_value = mock_aligned_data
        mock_align.return_value = mock_align_instance
        
        mock_ats_instance = MagicMock()
        mock_ats_instance.optimize_resume.return_value = mock_optimized_data
        mock_ats.return_value = mock_ats_instance
        
        # Create actual LaTeX file for testing
        with open(test_latex_file, 'w', encoding='utf-8') as f:
            f.write("""\\documentclass[11pt,a4paper,sans]{moderncv}
\\moderncvstyle{classic}
\\moderncvcolor{blue}
\\name{Integration}{Test}
\\title{Senior Python Developer}
\\begin{document}
\\makecvtitle
\\section{Professional Summary}
\\cvitem{}{Senior Python developer with 5+ years of Django and PostgreSQL experience}
\\section{Technical Skills}
\\cvitem{Programming}{Python, JavaScript}
\\cvitem{Frameworks}{Django}
\\cvitem{Databases}{PostgreSQL}
\\cvitem{Cloud}{AWS}
\\end{document}""")
        
        mock_latex_instance = MagicMock()
        mock_latex_instance.generate_latex_resume.return_value = test_latex_file
        mock_latex_instance.validate_overleaf_compatibility.return_value = {
            'is_compatible': True,
            'warnings': [],
            'errors': []
        }
        mock_latex.return_value = mock_latex_instance
        
        # Initialize workflow
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            rag_database_path=self.rag_dir,
            enable_logging=False
        )
        
        # Execute full workflow
        result = workflow.run_workflow(
            job_url="https://example.com/senior-python-developer",
            profile_id="integration_test_user",
            return_intermediate_results=True
        )
        
        # Verify workflow success
        assert result["success"] is True
        assert result["latex_file_path"] == test_latex_file
        assert len(result["errors"]) == 0
        assert "execution_time" in result
        assert "total" in result["execution_time"]
        
        # Verify workflow metadata
        metadata = result["workflow_metadata"]
        assert metadata["job_url"] == "https://example.com/senior-python-developer"
        assert metadata["profile_id"] == "integration_test_user"
        assert metadata["total_steps"] == 5
        assert metadata["completed_steps"] == 5
        
        # Verify intermediate results
        intermediate = result["intermediate_results"]
        assert intermediate["job_data"] == mock_job_data
        assert intermediate["profile_data"] == mock_profile_data
        assert intermediate["aligned_data"] == mock_aligned_data
        assert intermediate["optimized_data"] == mock_optimized_data
        
        # Verify all agents were called
        mock_jd_instance.extract_job_data.assert_called_once()
        mock_rag_instance.retrieve_profile.assert_called_once()
        mock_align_instance.align_content.assert_called_once()
        mock_ats_instance.optimize_resume.assert_called_once()
        mock_latex_instance.generate_latex_resume.assert_called_once()
    
    @patch('src.workflow.resume_workflow.JDExtractorAgent')
    @patch('src.workflow.resume_workflow.ProfileRAGAgent')
    @patch('src.workflow.resume_workflow.ContentAlignmentAgent')
    @patch('src.workflow.resume_workflow.ATSOptimizerAgent')
    @patch('src.workflow.resume_workflow.LaTeXFormatterAgent')
    def test_workflow_with_errors(self, mock_latex, mock_ats, mock_align, mock_rag, mock_jd):
        """Test workflow behavior when errors occur."""
        # Setup mock to fail at job extraction
        mock_jd_instance = MagicMock()
        mock_jd_instance.extract_job_data.return_value = {"error": "Network timeout"}
        mock_jd.return_value = mock_jd_instance
        
        workflow = ResumeWorkflow(
            template_path=self.template_path,
            output_directory=self.output_dir,
            enable_logging=False
        )
        
        # Execute workflow
        result = workflow.run_workflow(
            job_url="https://invalid-url.com/job",
            profile_id="test_user"
        )
        
        # Verify error handling
        assert result["success"] is False
        assert result["latex_file_path"] is None
        assert len(result["errors"]) > 0
        assert "Failed to extract job data" in result["errors"][0]
        
        # Verify metadata shows partial completion
        metadata = result["workflow_metadata"]
        assert metadata["completed_steps"] < metadata["total_steps"]


def test_workflow_main_function():
    """Test the main function of the workflow module."""
    with patch('builtins.print'):  # Suppress print output during testing
        try:
            from src.workflow.resume_workflow import main
            main()
        except Exception as e:
            pytest.fail(f"Main function failed with error: {e}")


def run_full_pipeline_demo():
    """
    Demonstration function showing complete workflow execution.
    
    This function demonstrates how to use the ResumeWorkflow class
    to execute the complete resume optimization pipeline.
    """
    print("Resume Workflow Integration Demo")
    print("=" * 50)
    
    # Test parameters
    job_url = "https://example.com/senior-software-engineer"
    profile_id = "demo_user_2024"
    
    try:
        # Initialize workflow with test directories
        workflow = ResumeWorkflow(
            template_path="templates/resume_template.tex",
            output_directory="output",
            rag_database_path="data/profiles",
            enable_logging=True,
            log_level="INFO"
        )
        
        print("Workflow Configuration:")
        status = workflow.get_workflow_status()
        print(f"  Name: {status['workflow_name']}")
        print(f"  Version: {status['version']}")
        print(f"  Agents: {len(status['agents'])}")
        print(f"  Steps: {len(status['workflow_steps'])}")
        print()
        
        print("Workflow Steps:")
        for i, step in enumerate(status['workflow_steps'], 1):
            print(f"  {i}. {step}")
        print()
        
        print("Note: This is a demonstration with mock data.")
        print("For actual execution, ensure:")
        print("  1. Valid job URL is provided")
        print("  2. Profile data exists in RAG database")
        print("  3. All agent dependencies are installed")
        print("  4. Template and output directories exist")
        print()
        
        print("Example usage:")
        print("  result = workflow.run_workflow(job_url, profile_id)")
        print("  if result['success']:")
        print("      print(f'LaTeX file: {result[\"latex_file_path\"]}')")
        print("      print('Upload to Overleaf for PDF generation')")
        print("  else:")
        print("      print(f'Errors: {result[\"errors\"]}')")
        
    except Exception as e:
        print(f"Demo setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    run_full_pipeline_demo()
    
    # Run tests
    print("\n" + "=" * 50)
    print("Running workflow tests...")
    pytest.main([__file__, "-v"])
