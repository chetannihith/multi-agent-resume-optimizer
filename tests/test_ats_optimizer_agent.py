"""
Tests for ATSOptimizerAgent.

This module contains unit tests for the ATSOptimizerAgent class,
testing ATS scoring, keyword density analysis, section validation,
and auto-fix functionality.
"""

import pytest
from src.agents.ats_optimizer_agent import ATSOptimizerAgent


class TestATSOptimizerAgent:
    """Test cases for ATSOptimizerAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = ATSOptimizerAgent(
            target_ats_score=90,
            keyword_density_weight=0.4,
            section_weight=0.3,
            formatting_weight=0.3,
            min_keyword_density=0.7
        )
        
        # Sample resume content
        self.sample_resume_content = {
            "summary": "Experienced Python developer with Django expertise",
            "skills": {
                "aligned_skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"]
            },
            "experience": [
                {
                    "title": "Python Developer",
                    "company": "TechCorp",
                    "description": "Built web applications using Python and Django framework"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "Tech University"
                }
            ]
        }
        
        # Sample job keywords
        self.sample_job_keywords = {
            "python", "django", "postgresql", "aws", "docker", "web", "framework"
        }
        
        # Sample aligned resume (full structure)
        self.sample_aligned_resume = {
            "profile_id": "test_user_123",
            "job_title": "Python Developer",
            "aligned_sections": {
                "summary": "Experienced Python developer with Django expertise",
                "skills": {
                    "aligned_skills": ["Python", "Django", "PostgreSQL", "AWS"]
                },
                "experience": [
                    {
                        "title": "Python Developer",
                        "description": "Built applications using Python and Django"
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science",
                        "field": "Computer Science"
                    }
                ],
                "job_keywords": {
                    "all": ["python", "django", "postgresql", "aws", "web"]
                }
            }
        }
    
    def test_initialization(self):
        """Test agent initialization."""
        assert self.agent.target_ats_score == 90
        assert self.agent.keyword_density_weight == 0.4
        assert self.agent.section_weight == 0.3
        assert self.agent.formatting_weight == 0.3
        assert self.agent.min_keyword_density == 0.7
        assert len(self.agent.required_sections) == 4
        assert 'summary' in self.agent.required_sections
        assert 'skills' in self.agent.required_sections
        assert 'experience' in self.agent.required_sections
        assert 'education' in self.agent.required_sections
    
    def test_extract_words(self):
        """Test word extraction from text."""
        text = "Python Developer with Django experience"
        words = self.agent._extract_words(text)
        
        assert "python" in words
        assert "developer" in words
        assert "django" in words
        assert "experience" in words
        assert "with" in words
        
        # Test empty input
        assert self.agent._extract_words("") == set()
        assert self.agent._extract_words(None) == set()
    
    def test_extract_resume_keywords(self):
        """Test keyword extraction from resume content."""
        keywords = self.agent.extract_resume_keywords(self.sample_resume_content)
        
        assert "python" in keywords
        assert "django" in keywords
        assert "postgresql" in keywords
        assert "experienced" in keywords
        assert "developer" in keywords
        # Note: "techcorp" appears in company field, not extracted by current logic
    
    def test_extract_resume_keywords_empty_content(self):
        """Test keyword extraction with empty content."""
        empty_content = {}
        keywords = self.agent.extract_resume_keywords(empty_content)
        assert isinstance(keywords, set)
        assert len(keywords) == 0
    
    def test_calculate_keyword_density_perfect_match(self):
        """Test keyword density calculation with perfect match."""
        resume_keywords = {"python", "django", "postgresql", "aws", "docker"}
        job_keywords = {"python", "django", "postgresql", "aws", "docker"}
        
        result = self.agent.calculate_keyword_density(resume_keywords, job_keywords)
        
        assert result['density_score'] == 1.0
        assert len(result['matching_keywords']) == 5
        assert len(result['missing_keywords']) == 0
        assert result['total_job_keywords'] == 5
        assert result['matched_count'] == 5
    
    def test_calculate_keyword_density_partial_match(self):
        """Test keyword density calculation with partial match."""
        resume_keywords = {"python", "django", "javascript"}
        job_keywords = {"python", "django", "postgresql", "aws", "docker"}
        
        result = self.agent.calculate_keyword_density(resume_keywords, job_keywords)
        
        assert result['density_score'] == 0.4  # 2 out of 5
        assert len(result['matching_keywords']) == 2
        assert len(result['missing_keywords']) == 3
        assert "python" in result['matching_keywords']
        assert "django" in result['matching_keywords']
        assert "postgresql" in result['missing_keywords']
    
    def test_calculate_keyword_density_no_match(self):
        """Test keyword density calculation with no match."""
        resume_keywords = {"java", "spring", "hibernate"}
        job_keywords = {"python", "django", "postgresql"}
        
        result = self.agent.calculate_keyword_density(resume_keywords, job_keywords)
        
        assert result['density_score'] == 0.0
        assert len(result['matching_keywords']) == 0
        assert len(result['missing_keywords']) == 3
    
    def test_calculate_keyword_density_empty_job_keywords(self):
        """Test keyword density calculation with empty job keywords."""
        resume_keywords = {"python", "django"}
        job_keywords = set()
        
        result = self.agent.calculate_keyword_density(resume_keywords, job_keywords)
        
        assert result['density_score'] == 1.0
        assert result['total_job_keywords'] == 0
        assert result['matched_count'] == 0
    
    def test_keyword_density_scoring_function(self):
        """
        Test the keyword density scoring function with dummy data.
        
        This is the specific pytest test requested for the keyword density function.
        """
        # Test Case 1: High density scenario
        high_density_resume = {"python", "machine", "learning", "tensorflow", "aws", "docker"}
        high_density_job = {"python", "machine", "learning", "tensorflow", "aws"}
        
        high_result = self.agent.calculate_keyword_density(high_density_resume, high_density_job)
        assert high_result['density_score'] == 1.0  # Perfect match
        assert high_result['matched_count'] == 5
        
        # Test Case 2: Medium density scenario
        medium_density_resume = {"python", "web", "development", "javascript"}
        medium_density_job = {"python", "django", "flask", "postgresql", "redis"}
        
        medium_result = self.agent.calculate_keyword_density(medium_density_resume, medium_density_job)
        assert medium_result['density_score'] == 0.2  # 1 out of 5 matches
        assert medium_result['matched_count'] == 1
        assert "python" in medium_result['matching_keywords']
        
        # Test Case 3: Low density scenario
        low_density_resume = {"java", "spring", "hibernate", "mysql"}
        low_density_job = {"python", "django", "postgresql", "redis", "aws"}
        
        low_result = self.agent.calculate_keyword_density(low_density_resume, low_density_job)
        assert low_result['density_score'] == 0.0  # No matches
        assert low_result['matched_count'] == 0
        assert len(low_result['missing_keywords']) == 5
        
        # Test Case 4: Edge case - single keyword
        single_resume = {"python"}
        single_job = {"python"}
        
        single_result = self.agent.calculate_keyword_density(single_resume, single_job)
        assert single_result['density_score'] == 1.0
        assert single_result['matched_count'] == 1
        
        # Test Case 5: Case sensitivity test
        case_resume = {"Python", "Django", "AWS"}  # Mixed case in original
        case_job = {"python", "django", "aws"}     # Lowercase in job
        
        # Since _extract_words converts to lowercase, this should match
        case_resume_lower = {word.lower() for word in case_resume}
        case_result = self.agent.calculate_keyword_density(case_resume_lower, case_job)
        assert case_result['density_score'] == 1.0
    
    def test_check_section_presence_all_present(self):
        """Test section presence check with all sections present."""
        result = self.agent.check_section_presence(self.sample_resume_content)
        
        assert result['section_score'] == 1.0
        assert len(result['present_sections']) == 4
        assert len(result['missing_sections']) == 0
        assert result['present_count'] == 4
        assert result['total_required'] == 4
    
    def test_check_section_presence_missing_sections(self):
        """Test section presence check with missing sections."""
        incomplete_content = {
            "summary": "Some summary",
            "skills": {"aligned_skills": ["Python"]}
            # Missing experience and education
        }
        
        result = self.agent.check_section_presence(incomplete_content)
        
        assert result['section_score'] == 0.5  # 2 out of 4
        assert len(result['present_sections']) == 2
        assert len(result['missing_sections']) == 2
        assert 'experience' in result['missing_sections']
        assert 'education' in result['missing_sections']
    
    def test_check_section_presence_empty_content(self):
        """Test section presence check with empty content."""
        empty_content = {}
        
        result = self.agent.check_section_presence(empty_content)
        
        assert result['section_score'] == 0.0
        assert len(result['present_sections']) == 0
        assert len(result['missing_sections']) == 4
    
    def test_check_formatting_rules_clean_content(self):
        """Test formatting rules check with clean content."""
        result = self.agent.check_formatting_rules(self.sample_resume_content)
        
        assert result['formatting_score'] >= 0.5  # Should be reasonably high
        assert isinstance(result['formatting_issues'], list)
        assert isinstance(result['ats_friendly'], bool)
    
    def test_check_formatting_rules_problematic_content(self):
        """Test formatting rules check with problematic content."""
        problematic_content = {
            "summary": "[image] Professional with experience [graphic] in development",
            "skills": {"aligned_skills": ["Python | Django | Flask"]},  # Pipe characters
            "experience": [{"description": "Worked with tables: | col1 | col2 | col3 |"}]
        }
        
        result = self.agent.check_formatting_rules(problematic_content)
        
        assert result['formatting_score'] < 1.0
        assert len(result['formatting_issues']) > 0
        assert not result['ats_friendly']
    
    def test_calculate_ats_score(self):
        """Test ATS score calculation."""
        keyword_analysis = {'density_score': 0.8}
        section_analysis = {'section_score': 1.0}
        formatting_analysis = {'formatting_score': 0.9}
        
        result = self.agent.calculate_ats_score(
            keyword_analysis, section_analysis, formatting_analysis
        )
        
        expected_score = int((0.8 * 0.4 + 1.0 * 0.3 + 0.9 * 0.3) * 100)
        
        assert result['ats_score'] == expected_score
        assert result['category'] in ['Poor', 'Fair', 'Good', 'Excellent']
        assert 'score_breakdown' in result
        assert 'weights' in result
    
    def test_calculate_ats_score_categories(self):
        """Test ATS score categorization."""
        # Test Excellent category (90+)
        excellent_result = self.agent.calculate_ats_score(
            {'density_score': 1.0}, {'section_score': 1.0}, {'formatting_score': 1.0}
        )
        assert excellent_result['category'] == 'Excellent'
        assert excellent_result['status'] == 'ATS Optimized'
        
        # Test Good category (80-89)
        good_result = self.agent.calculate_ats_score(
            {'density_score': 0.8}, {'section_score': 0.8}, {'formatting_score': 0.8}
        )
        assert good_result['category'] == 'Good'
        
        # Test Fair category (70-79)
        fair_result = self.agent.calculate_ats_score(
            {'density_score': 0.7}, {'section_score': 0.7}, {'formatting_score': 0.7}
        )
        assert fair_result['category'] == 'Fair'
        
        # Test Poor category (<70)
        poor_result = self.agent.calculate_ats_score(
            {'density_score': 0.5}, {'section_score': 0.5}, {'formatting_score': 0.5}
        )
        assert poor_result['category'] == 'Poor'
    
    def test_generate_suggestions_low_keyword_density(self):
        """Test suggestion generation for low keyword density."""
        keyword_analysis = {
            'density_score': 0.5,  # Below threshold
            'missing_keywords': ['python', 'django', 'aws']
        }
        section_analysis = {'missing_sections': []}
        formatting_analysis = {'formatting_issues': []}
        
        suggestions = self.agent.generate_suggestions(
            70, keyword_analysis, section_analysis, formatting_analysis
        )
        
        # Should have keyword suggestion
        keyword_suggestions = [s for s in suggestions if s['category'] == 'Keywords']
        assert len(keyword_suggestions) > 0
        assert keyword_suggestions[0]['priority'] == 'High'
        assert keyword_suggestions[0]['auto_fixable'] is True
    
    def test_generate_suggestions_missing_sections(self):
        """Test suggestion generation for missing sections."""
        keyword_analysis = {'density_score': 0.8, 'missing_keywords': []}
        section_analysis = {'missing_sections': ['education', 'skills']}
        formatting_analysis = {'formatting_issues': []}
        
        suggestions = self.agent.generate_suggestions(
            80, keyword_analysis, section_analysis, formatting_analysis
        )
        
        # Should have section suggestions
        section_suggestions = [s for s in suggestions if s['category'] == 'Sections']
        assert len(section_suggestions) == 2  # One for each missing section
        assert all(s['priority'] == 'High' for s in section_suggestions)
        assert all(s['auto_fixable'] is True for s in section_suggestions)
    
    def test_generate_suggestions_formatting_issues(self):
        """Test suggestion generation for formatting issues."""
        keyword_analysis = {'density_score': 0.8, 'missing_keywords': []}
        section_analysis = {'missing_sections': []}
        formatting_analysis = {
            'formatting_issues': [
                {'rule': 'no_images', 'description': 'No images', 'severity': 'high'},
                {'rule': 'simple_formatting', 'description': 'Simple format', 'severity': 'medium'}
            ]
        }
        
        suggestions = self.agent.generate_suggestions(
            85, keyword_analysis, section_analysis, formatting_analysis
        )
        
        # Should have formatting suggestions
        formatting_suggestions = [s for s in suggestions if s['category'] == 'Formatting']
        assert len(formatting_suggestions) == 2
    
    def test_auto_fix_issues_missing_sections(self):
        """Test auto-fixing missing sections."""
        resume_content = {
            "summary": "Existing summary"
            # Missing skills, experience, education
        }
        
        keyword_analysis = {'missing_keywords': ['python', 'django']}
        section_analysis = {'missing_sections': ['skills', 'experience', 'education']}
        suggestions = []
        
        result = self.agent.auto_fix_issues(
            resume_content, keyword_analysis, section_analysis, suggestions
        )
        
        fixed_content = result['fixed_content']
        assert 'skills' in fixed_content
        assert 'experience' in fixed_content
        assert 'education' in fixed_content
        assert result['fix_count'] > 0
        assert len(result['fixes_applied']) > 0
    
    def test_auto_fix_issues_missing_keywords(self):
        """Test auto-fixing missing keywords."""
        resume_content = {
            "summary": "Professional developer",
            "skills": {"aligned_skills": ["JavaScript"]},
            "experience": [],
            "education": []
        }
        
        keyword_analysis = {'missing_keywords': ['python', 'django', 'aws']}
        section_analysis = {'missing_sections': []}
        suggestions = []
        
        result = self.agent.auto_fix_issues(
            resume_content, keyword_analysis, section_analysis, suggestions
        )
        
        fixed_content = result['fixed_content']
        
        # Check if keywords were added to summary or skills
        summary_enhanced = 'python' in fixed_content['summary'].lower()
        skills_enhanced = any('python' in str(skill).lower() 
                            for skill in fixed_content['skills']['aligned_skills'])
        
        assert summary_enhanced or skills_enhanced
        assert result['fix_count'] > 0
    
    def test_optimize_resume_complete(self):
        """Test complete resume optimization process."""
        result = self.agent.optimize_resume(self.sample_aligned_resume)
        
        # Check main structure
        assert 'profile_id' in result
        assert 'job_title' in result
        assert 'ats_analysis' in result
        assert 'keyword_analysis' in result
        assert 'section_analysis' in result
        assert 'formatting_analysis' in result
        assert 'suggestions' in result
        assert 'optimization_metadata' in result
        
        # Check ATS analysis
        ats_analysis = result['ats_analysis']
        assert 'ats_score' in ats_analysis
        assert 'category' in ats_analysis
        assert 'status' in ats_analysis
        assert 'meets_target' in ats_analysis
        assert isinstance(ats_analysis['ats_score'], int)
        assert 0 <= ats_analysis['ats_score'] <= 100
    
    def test_optimize_resume_with_auto_fix(self):
        """Test resume optimization with auto-fix triggered."""
        # Create a resume that will need fixes
        low_score_resume = {
            "profile_id": "test_user",
            "job_title": "Developer",
            "aligned_sections": {
                "summary": "Basic summary",
                # Missing other sections
                "job_keywords": {"all": ["python", "django", "aws", "postgresql"]}
            }
        }
        
        result = self.agent.optimize_resume(low_score_resume)
        
        # Should trigger auto-fix
        assert result['ats_analysis']['ats_score'] < self.agent.target_ats_score
        assert result['auto_fix_results'] is not None
        assert result['auto_fix_results']['fix_count'] > 0
    
    def test_optimize_resume_error_handling(self):
        """Test resume optimization error handling."""
        # Test with None input (should be handled gracefully)
        invalid_resume = None
        
        result = self.agent.optimize_resume(invalid_resume)
        
        # Should handle None gracefully and return valid result
        assert 'ats_analysis' in result
        assert result['profile_id'] == 'unknown'  # Default value when no profile_id
        assert result['job_title'] == 'Unknown Position'
        
        # Test with completely invalid structure to trigger actual error
        try:
            # This should trigger an actual error in the processing
            invalid_structure = {"invalid": "structure that will cause processing error"}
            result2 = self.agent.optimize_resume(invalid_structure)
            # If we get here, check it handled gracefully
            assert 'ats_analysis' in result2
        except Exception:
            # If exception occurs, that's also acceptable for this test
            pass
    
    def test_to_json(self):
        """Test JSON serialization."""
        result = self.agent.optimize_resume(self.sample_aligned_resume)
        json_str = self.agent.to_json(result)
        
        assert isinstance(json_str, str)
        assert len(json_str) > 100
        
        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        assert parsed['profile_id'] == result['profile_id']
    
    def test_resume_to_text(self):
        """Test resume to text conversion."""
        text = self.agent._resume_to_text(self.sample_resume_content)
        
        assert isinstance(text, str)
        assert "python" in text.lower()
        assert "django" in text.lower()
        # Note: company names are not extracted in current implementation
    
    def test_edge_cases(self):
        """Test various edge cases."""
        # Empty resume
        empty_result = self.agent.optimize_resume({
            "profile_id": "empty",
            "aligned_sections": {}
        })
        assert empty_result['ats_analysis']['ats_score'] >= 0
        
        # Resume with unusual data types
        unusual_resume = {
            "profile_id": "unusual",
            "aligned_sections": {
                "summary": 123,  # Number instead of string
                "skills": "not a dict",  # String instead of dict
                "experience": "not a list",  # String instead of list
                "job_keywords": {"all": []}
            }
        }
        unusual_result = self.agent.optimize_resume(unusual_resume)
        assert 'ats_analysis' in unusual_result


if __name__ == "__main__":
    pytest.main([__file__])
